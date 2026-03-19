from __future__ import annotations

import random
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Set, Tuple

from sqlalchemy.orm import Session

from src.api.mappings import (
    map_program_ui_to_db,
    map_role_ui_to_db,
    map_source_ui_to_db,
    map_proficiency_ui_to_level_and_score,
)
from src.database.models import JobRole, JobRoleSkills, MarketReadinessScores, Student, StudentSkills, SkillsMaster
from src.ml_models.predict import predict_readiness_ml


def _choose_total_skills(total_skills_ui: str) -> int:
    # Mirror the dropdown ranges in the HTML UI.
    s = (total_skills_ui or "").strip()
    if s == "1–5 skills":
        return 4
    if s == "6–10 skills":
        return 8
    if s == "11–20 skills":
        return 15
    if s == "21–30 skills":
        return 25
    if s == "30+ skills":
        return 35
    # Fallback
    return 15


def generate_temp_student_and_predict(session: Session, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a temporary student portfolio based on aggregated UI inputs and run ML predictions.
    The temp data is deleted after inference.
    """
    program_db = map_program_ui_to_db(str(payload.get("program", "")))

    year_ui = str(payload.get("year", "Year 3")).strip()
    try:
        year_of_study = int(year_ui.replace("Year", "").strip())
    except Exception:
        year_of_study = 3

    role_ui = str(payload.get("role", "Data Analyst"))
    role_db = map_role_ui_to_db(role_ui)
    role = session.query(JobRole).filter_by(role_name=role_db).first()
    if not role:
        return {"error": f"Unknown target role: {role_ui}"}

    total_skills = _choose_total_skills(str(payload.get("totalSkills", payload.get("total_skills", "11–20 skills"))))
    proficiency_ui = str(payload.get("highestProficiency", payload.get("highest_proficiency", "Advanced (0.75)")))
    proficiency_level, proficiency_score = map_proficiency_ui_to_level_and_score(proficiency_ui)

    source_db = map_source_ui_to_db(str(payload.get("primarySource", payload.get("primary_source", "Courses"))))

    categories_present = payload.get("categoriesPresent", payload.get("categories_present", {})) or {}
    selected_categories = [c for c in ["Technical", "Business", "Design", "Soft Skills"] if bool(categories_present.get(c, False))]
    if not selected_categories:
        selected_categories = ["Technical"]

    # Enrollment year: keep it deterministic and consistent with the synthetic generator.
    current_year = datetime.now().year
    enrollment_year = int(current_year - (year_of_study - 1))

    # Prepare required skills for the role, grouped by category.
    required_rows = (
        session.query(
            JobRoleSkills.skill_id,
            JobRoleSkills.importance_weight,
            JobRoleSkills.required_proficiency,
            SkillsMaster.skill_name,
            SkillsMaster.category,
        )
        .join(SkillsMaster, SkillsMaster.skill_id == JobRoleSkills.skill_id)
        .filter(JobRoleSkills.role_id == role.role_id)
        .all()
    )

    required_by_category: Dict[str, List[int]] = {c: [] for c in selected_categories}
    all_required_skill_ids: Set[int] = set()
    for skill_id, _importance, _req_prof, _skill_name, category in required_rows:
        all_required_skill_ids.add(int(skill_id))
        if category in required_by_category:
            required_by_category[category].append(int(skill_id))

    # Pool of all skills per selected category (for non-required picks).
    skills_by_category: Dict[str, List[int]] = {c: [] for c in selected_categories}
    all_skills_rows = (
        session.query(SkillsMaster.skill_id, SkillsMaster.category)
        .filter(SkillsMaster.category.in_(selected_categories))
        .all()
    )
    for sid, cat in all_skills_rows:
        skills_by_category[cat].append(int(sid))

    # Allocate total skills across selected categories.
    per_cat_base = total_skills // len(selected_categories)
    remainder = total_skills % len(selected_categories)

    skills_to_add: List[int] = []
    for idx, cat in enumerate(selected_categories):
        cat_target = per_cat_base + (1 if idx < remainder else 0)
        if cat_target <= 0:
            continue

        required_ids = required_by_category.get(cat, [])
        required_ids = list(set(required_ids))

        matched_count = min(cat_target, len(required_ids))
        chosen_required = random.sample(required_ids, matched_count) if matched_count > 0 else []

        non_required_pool = [sid for sid in skills_by_category.get(cat, []) if sid not in set(chosen_required)]
        # Also ensure non-required picks exclude required ids (to keep matched count meaningful).
        non_required_pool = [sid for sid in non_required_pool if sid not in set(required_ids)]
        non_matched_target = cat_target - matched_count
        chosen_non_required = (
            random.sample(non_required_pool, min(non_matched_target, len(non_required_pool)))
            if non_matched_target > 0
            else []
        )

        skills_to_add.extend(chosen_required)
        skills_to_add.extend(chosen_non_required)

    # Deduplicate in case pools overlap.
    skills_to_add = list(dict.fromkeys(skills_to_add))

    temp_uuid = uuid.uuid4().hex
    temp_name = f"Temp Student {temp_uuid[:6]}"
    temp_email = f"temp_{temp_uuid}@temp.com"

    temp_student = Student(
        name=temp_name,
        email=temp_email,
        program=program_db,
        year_of_study=year_of_study,
        enrollment_year=enrollment_year,
        target_role=role_db,
    )

    session.add(temp_student)
    session.flush()  # assign student_id

    try:
        for skill_id in skills_to_add:
            session.add(
                StudentSkills(
                    student_id=temp_student.student_id,
                    skill_id=skill_id,
                    proficiency_level=proficiency_level,
                    proficiency_score=Decimal(str(proficiency_score)),
                    acquisition_date=date.today(),
                    source=source_db,
                )
            )
        session.flush()

        pred = predict_readiness_ml(temp_student.student_id, role.role_id, session)

        # Build an explanation payload: which required skills are missing vs matched.
        required_skill_ids_set: Set[int] = set(int(r.skill_id) for r in required_rows)
        student_skill_ids_set: Set[int] = set(int(sid) for sid in skills_to_add)

        missing_required = []
        matched_required = []
        for r in required_rows:
            sid = int(r.skill_id)
            item = {
                "skillId": sid,
                "skillName": str(r.skill_name),
                "category": str(r.category),
                "requiredProficiency": str(r.required_proficiency),
                "importanceWeight": float(r.importance_weight or 0.0),
            }
            if sid in student_skill_ids_set:
                matched_required.append(item)
            else:
                missing_required.append(item)

        missing_required.sort(key=lambda x: x["importanceWeight"], reverse=True)
        matched_required.sort(key=lambda x: x["importanceWeight"], reverse=True)

        explainability = {
            "requiredSkillsCount": int(len(required_skill_ids_set)),
            "matchedSkillsCount": int(len(student_skill_ids_set.intersection(required_skill_ids_set))),
            "missingSkillsCount": int(len(required_skill_ids_set.difference(student_skill_ids_set))),
            "missingSkills": missing_required[:8],
            "matchedSkills": matched_required[:8],
        }

        pred["explainability"] = explainability
        return pred
    finally:
        # Cleanup temp portfolio rows.
        session.query(StudentSkills).filter_by(student_id=temp_student.student_id).delete()
        session.query(Student).filter_by(student_id=temp_student.student_id).delete()
        session.commit()

