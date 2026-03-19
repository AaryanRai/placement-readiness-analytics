from __future__ import annotations

from typing import Any, Dict, List, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.scoring import PROFICIENCY_MAP
from src.ml_models.model_info import get_model_feature_importance, get_model_performance_metrics
from src.database.models import JobRoleSkills, MarketReadinessScores, StudentSkills


def get_feature_importance_top(
    model: str = "random_forest",
    top_n: int = 12,
) -> Dict[str, Any]:
    """
    Returns a normalized list of top feature importances for the frontend.
    """
    info = get_model_feature_importance()

    # Choose which DataFrame to use.
    if model in ("random_forest", "regressor"):
        df = info.get("regressor")
    elif model in ("decision_tree", "classifier"):
        df = info.get("classifier")
    elif model in ("gradient_boosting", "gb", "gradient_boosting_classifier"):
        df = info.get("gradient_boosting")
    else:
        df = info.get("regressor")

    if df is None or df.empty:
        return {"items": []}

    df = df.head(int(top_n)).copy()
    max_imp = float(df["Importance"].max()) or 1.0

    def display_feature(name: str) -> str:
        # Keep it short and readable for a chart/list.
        return name.replace("_", " ").title()

    items: List[Dict[str, Any]] = []
    for _, row in df.iterrows():
        imp = float(row["Importance"])
        items.append(
            {
                "name": display_feature(str(row["Feature"])),
                # Normalize to 0..100 for chart widths.
                "p": round((imp / max_imp) * 100.0, 1),
            }
        )

    return {"items": items}


def get_confusion_matrix(model: str = "decision_tree") -> Dict[str, Any]:
    perf = get_model_performance_metrics()

    if model in ("decision_tree", "classifier", "dt"):
        cm = perf.get("decision_tree", {}).get("confusion_matrix", [])
        classes = perf.get("decision_tree", {}).get("classes", [])
    elif model in ("gradient_boosting", "gb"):
        cm = perf.get("gradient_boosting", {}).get("confusion_matrix", [])
        classes = perf.get("gradient_boosting", {}).get("classes", [])
    else:
        cm = perf.get("decision_tree", {}).get("confusion_matrix", [])
        classes = perf.get("decision_tree", {}).get("classes", [])

    return {"classes": classes, "matrix": cm}


def get_score_distribution(bins: List[Tuple[int, int]] | None = None) -> Dict[str, Any]:
    # Used by the frontend histogram-like bar chart.
    if bins is None:
        bins = [(20, 30), (30, 40), (40, 50), (50, 60), (60, 70), (70, 80), (80, 90), (90, 100)]

    return bins


def compute_rule_based_score_fast(
    student_skill_map: Dict[int, float],
    required_skills: List[Tuple[int, str, float]],
) -> float:
    """
    Rule-based score = sum(min(student_prof / required_prof, 1) * importance) / sum(importance) * 100.
    """
    total_weight = 0.0
    matched_score = 0.0

    for skill_id, required_prof_level, importance in required_skills:
        required_prof = float(PROFICIENCY_MAP[required_prof_level])
        w = float(importance)
        total_weight += w
        if skill_id in student_skill_map:
            student_prof = float(student_skill_map[skill_id])
            factor = min(student_prof / required_prof, 1.0) if required_prof else 0.0
            matched_score += factor * w

    if total_weight <= 0:
        return 0.0
    return (matched_score / total_weight) * 100.0


def get_correlation_sample(session: Session, sample_size: int = 120) -> Dict[str, Any]:
    """
    Returns scatter points (rule_score, ml_score) for a sample of student-role pairs.
    Uses stored ML score from MarketReadinessScores to avoid repeated model inference.
    """
    sample_size = max(10, int(sample_size))

    sample_rows = (
        session.query(
            MarketReadinessScores.student_id,
            MarketReadinessScores.role_id,
            MarketReadinessScores.readiness_score,
        )
        .limit(sample_size)
        .all()
    )
    if not sample_rows:
        return {"points": []}

    student_ids = sorted({int(r.student_id) for r in sample_rows})
    role_ids = sorted({int(r.role_id) for r in sample_rows})

    # Prefetch required skills per role.
    req_rows = (
        session.query(
            JobRoleSkills.role_id,
            JobRoleSkills.skill_id,
            JobRoleSkills.required_proficiency,
            JobRoleSkills.importance_weight,
        )
        .filter(JobRoleSkills.role_id.in_(role_ids))
        .all()
    )
    required_map: Dict[int, List[Tuple[int, str, float]]] = {rid: [] for rid in role_ids}
    for rid, skill_id, req_prof, importance in req_rows:
        required_map[int(rid)].append((int(skill_id), str(req_prof), float(importance or 0.0)))

    # Prefetch student skills (proficiency_score).
    student_skill_rows = (
        session.query(
            StudentSkills.student_id,
            StudentSkills.skill_id,
            StudentSkills.proficiency_score,
        )
        .filter(StudentSkills.student_id.in_(student_ids))
        .all()
    )
    student_skill_map: Dict[int, Dict[int, float]] = {sid: {} for sid in student_ids}
    for sid, skill_id, prof_score in student_skill_rows:
        student_skill_map[int(sid)][int(skill_id)] = float(prof_score or 0.0)

    points: List[Dict[str, float]] = []
    for r in sample_rows:
        sid = int(r.student_id)
        rid = int(r.role_id)
        ml_score = float(r.readiness_score or 0.0)
        rule_score = compute_rule_based_score_fast(
            student_skill_map.get(sid, {}),
            required_map.get(rid, []),
        )
        points.append({"x": round(rule_score, 2), "y": round(ml_score, 2)})

    return {"points": points}


def get_ml_score_distribution(session: Session) -> Dict[str, Any]:
    """
    Histogram of stored ML readiness scores (0..100) for the frontend.
    """
    scores = session.query(MarketReadinessScores.readiness_score).all()
    values = [float(s.readiness_score or 0.0) for s in scores]

    bins = [(20, 30), (30, 40), (40, 50), (50, 60), (60, 70), (70, 80), (80, 90), (90, 100)]
    labels = [f"{a}-{b}" for a, b in bins]
    counts = [0 for _ in bins]

    for v in values:
        vv = max(0.0, min(100.0, v))
        for i, (a, b) in enumerate(bins):
            if (i < len(bins) - 1 and vv >= a and vv < b) or (i == len(bins) - 1 and vv >= a and vv <= b):
                counts[i] += 1
                break

    return {"labels": labels, "counts": counts}

