from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, func, or_

from src.api.mappings import (
    map_program_db_to_ui,
    map_role_db_to_ui,
)
from src.database.models import (
    JobRole,
    JobRoleSkills,
    MarketReadinessScores,
    Student,
    StudentSkills,
    SkillsMaster,
)
from sqlalchemy.orm import Session


def _to_float(x: Any) -> float:
    if x is None:
        return 0.0
    try:
        return float(x)
    except Exception:
        return 0.0


LEVELS = ["Ready", "Developing", "Entry-Level"]


def get_cohort_kpis(session: Session) -> Dict[str, Any]:
    total_students = session.query(Student).count()
    avg_readiness = _to_float(session.query(func.avg(MarketReadinessScores.readiness_score)).scalar())

    readiness_counts = (
        session.query(
            MarketReadinessScores.readiness_level,
            func.count(func.distinct(MarketReadinessScores.student_id)).label("count"),
        )
        .filter(MarketReadinessScores.readiness_level.in_(LEVELS))
        .group_by(MarketReadinessScores.readiness_level)
        .all()
    )

    counts_map = {lvl: 0 for lvl in LEVELS}
    for lvl, cnt in readiness_counts:
        counts_map.get(lvl, 0)
        counts_map[lvl] = int(cnt)

    total_skills = session.query(SkillsMaster).count()
    total_roles = session.query(JobRole).count()

    return {
        "totalStudents": int(total_students),
        "jobReadyStudents": int(counts_map["Ready"]),
        "developingStudents": int(counts_map["Developing"]),
        "entryLevelStudents": int(counts_map["Entry-Level"]),
        "avgReadinessScore": float(avg_readiness),
        "skillsTracked": int(total_skills),
        "rolesTracked": int(total_roles),
    }


def get_cohort_kpis_for_program(session: Session, program_db: str) -> Dict[str, Any]:
    total_students = session.query(Student).filter(Student.program == program_db).count()
    avg_readiness = _to_float(
        session.query(func.avg(MarketReadinessScores.readiness_score))
        .join(Student, Student.student_id == MarketReadinessScores.student_id)
        .filter(Student.program == program_db)
        .scalar()
    )

    readiness_counts = (
        session.query(
            MarketReadinessScores.readiness_level,
            func.count(func.distinct(MarketReadinessScores.student_id)).label("count"),
        )
        .join(Student, Student.student_id == MarketReadinessScores.student_id)
        .filter(Student.program == program_db)
        .filter(MarketReadinessScores.readiness_level.in_(LEVELS))
        .group_by(MarketReadinessScores.readiness_level)
        .all()
    )

    counts_map = {lvl: 0 for lvl in LEVELS}
    for lvl, cnt in readiness_counts:
        if lvl in counts_map:
            counts_map[lvl] = int(cnt)

    total_skills = session.query(SkillsMaster).count()
    total_roles = session.query(JobRole).count()

    return {
        "totalStudents": int(total_students),
        "jobReadyStudents": int(counts_map["Ready"]),
        "developingStudents": int(counts_map["Developing"]),
        "entryLevelStudents": int(counts_map["Entry-Level"]),
        "avgReadinessScore": float(avg_readiness),
        "skillsTracked": int(total_skills),
        "rolesTracked": int(total_roles),
    }


def get_readiness_distribution_by_program(
    session: Session,
    program_db_values: Optional[List[str]] = None,
) -> Dict[str, List[int]]:
    programs = program_db_values or ["Btech", "BBA", "B.Com"]
    result: Dict[str, List[int]] = {}

    for prog_db in programs:
        rows = (
            session.query(
                MarketReadinessScores.readiness_level,
                func.count(func.distinct(MarketReadinessScores.student_id)).label("count"),
            )
            .join(Student, Student.student_id == MarketReadinessScores.student_id)
            .filter(Student.program == prog_db)
            .filter(MarketReadinessScores.readiness_level.in_(LEVELS))
            .group_by(MarketReadinessScores.readiness_level)
            .all()
        )
        counts = {lvl: 0 for lvl in LEVELS}
        for lvl, cnt in rows:
            counts[lvl] = int(cnt)

        result[map_program_db_to_ui(prog_db)] = [counts["Ready"], counts["Developing"], counts["Entry-Level"]]

    return result


def get_program_average_readiness(session: Session) -> Dict[str, Any]:
    rows = (
        session.query(
            Student.program,
            func.avg(MarketReadinessScores.readiness_score).label("avg_score"),
        )
        .join(MarketReadinessScores, MarketReadinessScores.student_id == Student.student_id)
        .group_by(Student.program)
        .all()
    )
    # Stable ordering expected by the frontend
    program_order_db = ["Btech", "BBA", "B.Com"]
    program_order_ui = [map_program_db_to_ui(p) for p in program_order_db]
    values: List[float] = []
    for p_db in program_order_db:
        avg_val = next((r[1] for r in rows if r[0] == p_db), 0.0)
        values.append(_to_float(avg_val))

    return {
        "labels": program_order_ui,
        "values": values,
    }


def get_yearwise_readiness_progression(session: Session) -> Dict[str, Any]:
    # Returns avg score by program/year, used as 3 line series.
    rows = (
        session.query(
            Student.year_of_study,
            Student.program,
            func.avg(MarketReadinessScores.readiness_score).label("avg_score"),
        )
        .join(MarketReadinessScores, MarketReadinessScores.student_id == Student.student_id)
        .group_by(Student.year_of_study, Student.program)
        .all()
    )

    program_order_db = ["Btech", "BBA", "B.Com"]
    series_by_program_ui: Dict[str, List[float]] = {
        map_program_db_to_ui(p_db): [0.0, 0.0, 0.0, 0.0] for p_db in program_order_db
    }

    for year, prog_db, avg_val in rows:
        idx = max(1, min(4, int(year))) - 1
        series_by_program_ui[map_program_db_to_ui(prog_db)][idx] = _to_float(avg_val)

    return {
        "labels": ["Year 1", "Year 2", "Year 3", "Year 4"],
        "series": series_by_program_ui,
    }


def _score_to_level(score_pct: float) -> str:
    if score_pct >= 70:
        return "Ready"
    if score_pct >= 50:
        return "Developing"
    return "Entry-Level"


def get_role_program_matrix(session: Session) -> Dict[str, Any]:
    roles_db = [r.role_name for r in session.query(JobRole).all()]
    # Stable frontend ordering
    role_order_ui = [
        "Data Analyst",
        "Full-Stack Dev",
        "Digital Marketer",
        "Business Analyst",
        "UX/UI Designer",
    ]
    role_order_db = [
        "Data Analyst",
        "Full-Stack Developer",
        "Digital Marketer",
        "Business Analyst",
        "UX/UI Designer",
    ]

    programs_db = ["Btech", "BBA", "B.Com"]
    matrix: Dict[str, Any] = {}

    for prog_db in programs_db:
        prog_ui = map_program_db_to_ui(prog_db)
        row: Dict[str, Any] = {}

        # Compute per-role avg
        role_rows = (
            session.query(
                JobRole.role_name,
                func.avg(MarketReadinessScores.readiness_score).label("avg_score"),
            )
            .join(Student, Student.student_id == MarketReadinessScores.student_id)
            .join(JobRole, JobRole.role_id == MarketReadinessScores.role_id)
            .filter(Student.program == prog_db)
            .filter(JobRole.role_name.in_(role_order_db))
            .group_by(JobRole.role_name)
            .all()
        )
        role_avg_map = {db_role: _to_float(avg) for db_role, avg in role_rows}

        # Program average across the 5 roles
        program_avg = 0.0
        for db_role in role_order_db:
            program_avg += role_avg_map.get(db_role, 0.0)
        program_avg = program_avg / max(1, len(role_order_db))

        for db_role in role_order_db:
            role_ui = map_role_db_to_ui(db_role)
            score = role_avg_map.get(db_role, 0.0)
            row[role_ui] = {
                "score": float(score),
                "level": _score_to_level(float(score)),
            }

        row["programAvg"] = {
            "score": float(program_avg),
            "level": _score_to_level(float(program_avg)),
        }
        matrix[prog_ui] = row

    return {
        "programs": [map_program_db_to_ui(p) for p in programs_db],
        "roles": role_order_ui,
        "matrix": matrix,
    }


def get_cohort_page_data(session: Session) -> Dict[str, Any]:
    # KPI cards for the cohort page.
    program_counts = (
        session.query(Student.program, func.count(Student.student_id).label("count"))
        .group_by(Student.program)
        .all()
    )
    program_count_map = {p: int(c) for p, c in program_counts}

    total_students = session.query(Student).count()
    total_skills = session.query(StudentSkills).count()
    avg_skills_per_student = float(total_skills) / float(total_students) if total_students else 0.0

    # Radar: avg proficiency score by category + avg proficiency score for certs/projects sources.
    radar_labels = ["Technical", "Business", "Design", "Soft Skills", "Certs", "Projects"]
    radar_series: Dict[str, List[float]] = {}

    program_order_db = ["Btech", "BBA", "B.Com"]
    for prog_db in program_order_db:
        prog_ui = map_program_db_to_ui(prog_db)

        # category averages
        def avg_proficiency_where(where_clause) -> float:
            avg_val = (
                session.query(func.avg(StudentSkills.proficiency_score))
                .join(SkillsMaster, SkillsMaster.skill_id == StudentSkills.skill_id)
                .join(Student, Student.student_id == StudentSkills.student_id)
                .filter(where_clause)
                .scalar()
            )
            return _to_float(avg_val) * 100.0

        technical = avg_proficiency_where(and_(Student.program == prog_db, SkillsMaster.category == "Technical"))
        business = avg_proficiency_where(and_(Student.program == prog_db, SkillsMaster.category == "Business"))
        design = avg_proficiency_where(and_(Student.program == prog_db, SkillsMaster.category == "Design"))
        soft = avg_proficiency_where(and_(Student.program == prog_db, SkillsMaster.category == "Soft Skills"))

        certs = avg_proficiency_where(and_(Student.program == prog_db, StudentSkills.source == "Certification"))
        projects = avg_proficiency_where(and_(Student.program == prog_db, StudentSkills.source == "Project"))

        radar_series[prog_ui] = [technical, business, design, soft, certs, projects]

    # Doughnut: source distribution across all student skills.
    source_labels = ["Courses (55%)", "Certifications (25%)", "Projects (15%)", "Workshops (5%)"]
    source_map = {
        "Course": 0,
        "Certification": 0,
        "Project": 0,
        "Workshop": 0,
    }
    total_skill_records = session.query(StudentSkills).count()
    src_rows = (
        session.query(StudentSkills.source, func.count(StudentSkills.id).label("cnt"))
        .group_by(StudentSkills.source)
        .all()
    )
    for src, cnt in src_rows:
        if src in source_map:
            source_map[src] = int(cnt)

    denom = total_skill_records if total_skill_records else 1
    # Return values only; frontend can rebuild labels.
    src_percent = [
        (source_map["Course"] / denom) * 100.0,
        (source_map["Certification"] / denom) * 100.0,
        (source_map["Project"] / denom) * 100.0,
        (source_map["Workshop"] / denom) * 100.0,
    ]

    # Stacked proficiency counts by year (counts, not percents).
    year_labels = ["Year 1", "Year 2", "Year 3", "Year 4"]
    proficiency_order = ["Expert", "Advanced", "Intermediate", "Beginner"]
    # We'll return as counts per proficiency level across year 1..4.
    proficiency_series: Dict[str, List[int]] = {p: [0, 0, 0, 0] for p in proficiency_order}

    rows = (
        session.query(
            Student.year_of_study,
            StudentSkills.proficiency_level,
            func.count(StudentSkills.id).label("cnt"),
        )
        .join(Student, Student.student_id == StudentSkills.student_id)
        .group_by(Student.year_of_study, StudentSkills.proficiency_level)
        .all()
    )
    for year, prof_level, cnt in rows:
        idx = max(1, min(4, int(year))) - 1
        if prof_level in proficiency_series:
            proficiency_series[prof_level][idx] = int(cnt)

    return {
        "kpis": {
            "btechStudents": program_count_map.get("Btech", 0),
            "bbaStudents": program_count_map.get("BBA", 0),
            "bcomStudents": program_count_map.get("B.Com", 0),
            "avgSkillsPerStudent": avg_skills_per_student,
        },
        "radar": {"labels": radar_labels, "series": radar_series},
        "source": {"labels": source_labels, "percentages": src_percent},
        "proficiency": {
            "labels": year_labels,
            "series": proficiency_series,
        },
    }


def get_career_page_data(session: Session) -> Dict[str, Any]:
    role_order_db = [
        "Data Analyst",
        "Full-Stack Developer",
        "Digital Marketer",
        "Business Analyst",
        "UX/UI Designer",
    ]
    role_order_ui = [map_role_db_to_ui(r) for r in role_order_db]

    total_students = session.query(Student).count()

    role_cards: List[Dict[str, Any]] = []

    for role_db, role_ui in zip(role_order_db, role_order_ui):
        role = session.query(JobRole).filter_by(role_name=role_db).first()
        if not role:
            continue

        required_skills_count = session.query(JobRoleSkills).filter_by(role_id=role.role_id).count()

        ready_students = (
            session.query(func.count(func.distinct(MarketReadinessScores.student_id)))
            .filter(MarketReadinessScores.role_id == role.role_id)
            .filter(MarketReadinessScores.readiness_level == "Ready")
            .scalar()
        )
        developing_students = (
            session.query(func.count(func.distinct(MarketReadinessScores.student_id)))
            .filter(MarketReadinessScores.role_id == role.role_id)
            .filter(MarketReadinessScores.readiness_level == "Developing")
            .scalar()
        )

        avg_score = (
            session.query(func.avg(MarketReadinessScores.readiness_score))
            .filter(MarketReadinessScores.role_id == role.role_id)
            .scalar()
        )

        avg_score_f = _to_float(avg_score)
        readiness_level = _score_to_level(avg_score_f)

        role_cards.append(
            {
                "role": role_ui,
                "readinessPercent": avg_score_f,
                "readinessLevel": readiness_level,
                "readyStudents": int(ready_students or 0),
                "developingStudents": int(developing_students or 0),
                "requiredSkills": int(required_skills_count or 0),
            }
        )

    # Chart data: Ready% and Developing% across roles.
    ready_pcts: List[float] = []
    developing_pcts: List[float] = []
    roles_for_chart: List[str] = []
    # total_students is used as denominator; approximate if not perfect.
    denom = total_students if total_students else 1
    for card in role_cards:
        roles_for_chart.append(card["role"])
        ready_pcts.append((card["readyStudents"] / denom) * 100.0)
        developing_pcts.append((card["developingStudents"] / denom) * 100.0)

    # Key insight: best role by readinessPercent, weakest by readinessPercent.
    best_role = max(role_cards, key=lambda r: r["readinessPercent"]) if role_cards else None
    worst_role = min(role_cards, key=lambda r: r["readinessPercent"]) if role_cards else None

    key_insight = ""
    if best_role and worst_role:
        key_insight = (
            f"{best_role['role']} has the strongest pipeline at "
            f"{best_role['readinessPercent']:.0f}%. "
            f"{worst_role['role']} shows the weakest readiness at "
            f"{worst_role['readinessPercent']:.0f}%. "
        )

    return {
        "roleCards": role_cards,
        "roleReadinessChart": {
            "labels": roles_for_chart,
            "readyPercentages": ready_pcts,
            "developingPercentages": developing_pcts,
        },
        "keyInsight": key_insight,
    }


def get_skills_page_data(session: Session) -> Dict[str, Any]:
    total_students = session.query(Student).count() or 1

    # Gap list: missing skills sorted by missing count.
    required_skills = (
        session.query(
            JobRoleSkills.skill_id,
            func.count(func.distinct(JobRoleSkills.role_id)).label("role_count"),
            func.avg(JobRoleSkills.importance_weight).label("avg_weight"),
        )
        .group_by(JobRoleSkills.skill_id)
        .all()
    )

    student_skills = (
        session.query(
            StudentSkills.skill_id,
            func.count(func.distinct(StudentSkills.student_id)).label("student_count"),
        )
        .group_by(StudentSkills.skill_id)
        .all()
    )

    student_skill_map = {sid: int(cnt) for sid, cnt in student_skills}

    gaps: List[Dict[str, Any]] = []
    for skill_id, role_count, avg_weight in required_skills:
        skill = session.query(SkillsMaster).filter_by(skill_id=skill_id).first()
        if not skill:
            continue
        students_with_skill = student_skill_map.get(skill_id, 0)
        missing_count = int(total_students - students_with_skill)
        importance = float(avg_weight) if avg_weight is not None else 0.5
        missing_pct = (missing_count / float(total_students)) * 100.0
        # Scale by importance so "critical" skills show higher leverage.
        pct_weighted = min(100.0, missing_pct * max(0.1, importance))
        imp = "Critical" if importance >= 0.7 else "High"
        gaps.append(
            {
                "name": skill.skill_name,
                "pct": round(pct_weighted, 1),
                "imp": imp,
            }
        )

    gaps.sort(key=lambda x: x["pct"], reverse=True)
    gaps = gaps[:20]

    # Category coverage: distinct skills in role requirements by category.
    cat_counts = (
        session.query(SkillsMaster.category, func.count(func.distinct(JobRoleSkills.skill_id)).label("cnt"))
        .join(JobRoleSkills, JobRoleSkills.skill_id == SkillsMaster.skill_id)
        .group_by(SkillsMaster.category)
        .all()
    )
    cat_map = {c: int(cnt) for c, cnt in cat_counts}
    categories_order = ["Technical", "Business", "Design", "Soft Skills"]
    cat_values = [cat_map.get(c, 0) for c in categories_order]

    # Skill cloud: all skills with their category.
    skills = session.query(SkillsMaster).all()
    cloud = [{"name": s.skill_name, "category": s.category} for s in skills]

    # Gap by role: average matched skills and average gap skills from MarketReadinessScores.
    role_order_db = [
        "Data Analyst",
        "Full-Stack Developer",
        "Digital Marketer",
        "Business Analyst",
        "UX/UI Designer",
    ]
    labels = [map_role_db_to_ui(r) for r in role_order_db]

    role_cards_matched: List[float] = []
    role_cards_gap: List[float] = []
    for role_db in role_order_db:
        role = session.query(JobRole).filter_by(role_name=role_db).first()
        if not role:
            role_cards_matched.append(0.0)
            role_cards_gap.append(0.0)
            continue
        avg_matched = session.query(func.avg(MarketReadinessScores.matched_skills_count)).filter(
            MarketReadinessScores.role_id == role.role_id
        ).scalar()
        avg_gap = session.query(func.avg(MarketReadinessScores.skill_gap_count)).filter(
            MarketReadinessScores.role_id == role.role_id
        ).scalar()
        role_cards_matched.append(_to_float(avg_matched))
        role_cards_gap.append(_to_float(avg_gap))

    return {
        "gaps": gaps,
        "skillCategoryCoverage": {
            "labels": categories_order,
            "values": cat_values,
        },
        "skillCloud": cloud,
        "gapByRole": {
            "labels": labels,
            "avgMatched": role_cards_matched,
            "avgGap": role_cards_gap,
        },
    }


def get_students_page(
    session: Session,
    q: str = "",
    program_ui: str = "",
    level: str = "",
    role_ui: str = "",
    limit: int = 20,
    offset: int = 0,
) -> Dict[str, Any]:
    from sqlalchemy import distinct

    # Filters mapping.
    program_db = {
        "BTech": "Btech",
        "BBA": "BBA",
        "B.Com": "B.Com",
        "": "",
    }.get(program_ui, program_ui)

    role_db = {
        "Full-Stack Dev": "Full-Stack Developer",
        "": "",
        "Data Analyst": "Data Analyst",
        "Digital Marketer": "Digital Marketer",
        "Business Analyst": "Business Analyst",
        "UX/UI Designer": "UX/UI Designer",
    }.get(role_ui, role_ui)

    # Best readiness per student (max readiness_score).
    best = (
        session.query(
            MarketReadinessScores.student_id.label("student_id"),
            MarketReadinessScores.role_id.label("role_id"),
            MarketReadinessScores.readiness_score.label("readiness_score"),
            MarketReadinessScores.readiness_level.label("readiness_level"),
            func.row_number()
            .over(
                partition_by=MarketReadinessScores.student_id,
                order_by=MarketReadinessScores.readiness_score.desc(),
            )
            .label("rn"),
        )
        .subquery()
    )

    skills_count = (
        session.query(
            StudentSkills.student_id.label("student_id"),
            func.count(distinct(StudentSkills.skill_id)).label("skills_count"),
        )
        .group_by(StudentSkills.student_id)
        .subquery()
    )

    base_q = (
        session.query(
            Student.student_id,
            Student.name,
            Student.email,
            Student.program,
            Student.year_of_study,
            JobRole.role_name,
            best.c.readiness_score,
            best.c.readiness_level,
            skills_count.c.skills_count,
        )
        .join(best, best.c.student_id == Student.student_id)
        .join(JobRole, JobRole.role_id == best.c.role_id)
        .outerjoin(skills_count, skills_count.c.student_id == Student.student_id)
        .filter(best.c.rn == 1)
    )

    if q:
        q_l = f"%{q.lower()}%"
        base_q = base_q.filter(or_(func.lower(Student.name).like(q_l), func.lower(Student.email).like(q_l)))

    if program_db:
        base_q = base_q.filter(Student.program == program_db)

    if level:
        base_q = base_q.filter(best.c.readiness_level == level)

    if role_db:
        base_q = base_q.filter(JobRole.role_name == role_db)

    # Total count.
    count_q = base_q.with_entities(func.count()).order_by(None)
    total = int(count_q.scalar() or 0)

    rows = base_q.order_by(Student.student_id).offset(int(offset)).limit(int(limit)).all()

    records: List[Dict[str, Any]] = []
    for r in rows:
        records.append(
            {
                "id": int(r.student_id),
                "name": r.name,
                "email": r.email,
                "prog": map_program_db_to_ui(r.program),
                "year": int(r.year_of_study or 0),
                "role": map_role_db_to_ui(r.role_name),
                "skills": int(r.skills_count or 0),
                "score": _to_float(r.readiness_score),
                "level": r.readiness_level,
            }
        )

    return {"total": total, "records": records}

