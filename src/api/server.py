from __future__ import annotations

import os
import json
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, Depends, Query
from fastapi.responses import FileResponse, JSONResponse

from sqlalchemy.orm import Session

from src.api.queries import (
    get_cohort_kpis,
    get_cohort_kpis_for_program,
    get_readiness_distribution_by_program,
    get_program_average_readiness,
    get_yearwise_readiness_progression,
    get_role_program_matrix,
    get_cohort_page_data,
    get_career_page_data,
    get_skills_page_data,
    get_students_page,
)
from src.api.ml_service import (
    get_confusion_matrix,
    get_correlation_sample,
    get_feature_importance_top,
    get_ml_score_distribution,
)
from src.api.predict_service import generate_temp_student_and_predict
from src.database.connection import get_db_session
from src.ml_models.drift import compute_drift_report
from src.ml_models.model_info import get_model_performance_metrics


def get_session():
    session = get_db_session()
    try:
        yield session
    finally:
        session.close()


app = FastAPI(title="Placement Readiness Analytics API")


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = PROJECT_ROOT / "frontend"
MODELS_DIR = PROJECT_ROOT / "models"
FRONTEND_INDEX = FRONTEND_DIR / "index.html"


def _try_mount_frontend() -> None:
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        return

    from fastapi.staticfiles import StaticFiles

    # Serve the frontend assets at `/` so Chart.js + the dashboard HTML works.
    app.mount(
        "/",
        StaticFiles(directory=str(FRONTEND_DIR), html=True),
        name="frontend",
    )


@app.get("/api/overview")
def api_overview(
    program: str = Query("all", description="all|BTech|BBA|B.Com"),
    session: Session = Depends(get_session),
) -> Dict[str, Any]:
    program = (program or "all").strip()
    # Only map UI filter values for now.
    program_db = {"BTech": "Btech", "BBA": "BBA", "B.Com": "B.Com"}.get(program, program)

    if program_db and program_db != "all":
        kpis = get_cohort_kpis_for_program(session, program_db)
    else:
        kpis = get_cohort_kpis(session)

    dist_by_prog = get_readiness_distribution_by_program(session)
    program_avg = get_program_average_readiness(session)
    yprog = get_yearwise_readiness_progression(session)
    matrix = get_role_program_matrix(session)

    # Optional filter reduction: keep only one program's series/table.
    if program != "all":
        selected_ui = program
        dist_by_prog = {selected_ui: dist_by_prog.get(selected_ui, [0, 0, 0])}

        if selected_ui in program_avg["labels"]:
            idx = program_avg["labels"].index(selected_ui)
            program_avg = {"labels": [selected_ui], "values": [program_avg["values"][idx]]}

        if selected_ui in yprog["series"]:
            yprog = {"labels": yprog["labels"], "series": {selected_ui: yprog["series"][selected_ui]}}

        if selected_ui in matrix["matrix"]:
            matrix = {
                "programs": [selected_ui],
                "roles": matrix["roles"],
                "matrix": {selected_ui: matrix["matrix"][selected_ui]},
            }

    return {
        "kpis": kpis,
        "readinessDistribution": {
            "levels": ["Ready", "Developing", "Entry-Level"],
            "seriesByProgram": dist_by_prog,
        },
        "programAverageReadiness": program_avg,
        "yearWiseReadinessProgression": yprog,
        "roleProgramMatrix": matrix,
    }


@app.get("/api/cohort")
def api_cohort(session: Session = Depends(get_session)) -> Dict[str, Any]:
    return get_cohort_page_data(session)


@app.get("/api/career")
def api_career(session: Session = Depends(get_session)) -> Dict[str, Any]:
    return get_career_page_data(session)


@app.get("/api/skills")
def api_skills(session: Session = Depends(get_session)) -> Dict[str, Any]:
    return get_skills_page_data(session)


@app.get("/api/ml/feature-importance")
def api_ml_feature_importance(
    model: str = Query("random_forest", description="random_forest|decision_tree|gradient_boosting"),
    top_n: int = Query(12, ge=1, le=50),
) -> Dict[str, Any]:
    # No DB session required: uses model artifacts.
    return get_feature_importance_top(model=model, top_n=top_n)


@app.get("/api/ml/confusion-matrix")
def api_ml_confusion_matrix(
    model: str = Query("decision_tree", description="decision_tree|gradient_boosting"),
) -> Dict[str, Any]:
    return get_confusion_matrix(model=model)


@app.get("/api/ml/correlation")
def api_ml_correlation(
    sample_size: int = Query(120, ge=10, le=800),
    session: Session = Depends(get_session),
) -> Dict[str, Any]:
    return get_correlation_sample(session, sample_size=sample_size)


@app.get("/api/ml/score-distribution")
def api_ml_score_distribution(session: Session = Depends(get_session)) -> Dict[str, Any]:
    return get_ml_score_distribution(session)


@app.get("/api/ml/metrics")
def api_ml_metrics() -> Dict[str, Any]:
    """
    Returns stored model performance metrics (accuracy, F1, confusion matrix, regression RMSE/R², etc.)
    """
    return get_model_performance_metrics()


@app.get("/api/ml/drift")
def api_ml_drift(session: Session = Depends(get_session)) -> Dict[str, Any]:
    """
    Computes a lightweight drift report for stored readiness score distribution.
    Requires `models/drift_baseline.json` to have been saved during training.
    """
    return compute_drift_report(session=session, models_dir=MODELS_DIR)


@app.get("/api/ml/post-mortem")
def api_ml_post_mortem(session: Session = Depends(get_session)) -> Dict[str, Any]:
    """
    Aggregates training metadata, data quality snapshot, and the latest drift report
    for dashboard explainability / defense.
    """
    metrics = get_model_performance_metrics()
    drift = compute_drift_report(session=session, models_dir=MODELS_DIR)

    data_quality = None
    dq_path = MODELS_DIR / "data_quality_report.json"
    if dq_path.exists():
        try:
            data_quality = json.loads(dq_path.read_text())
        except Exception:
            data_quality = None

    return {"metrics": metrics, "drift": drift, "dataQuality": data_quality}


@app.post("/api/predict")
def api_predict(payload: Dict[str, Any], session: Session = Depends(get_session)) -> Dict[str, Any]:
    # Returns directly whatever predict_readiness_ml returns (plus error if temp build fails).
    return generate_temp_student_and_predict(session, payload)


@app.get("/api/students")
def api_students(
    q: str = Query("", description="Search by name or email"),
    program: str = Query("", description="BTech|BBA|B.Com"),
    level: str = Query("", description="Ready|Developing|Entry-Level"),
    role: str = Query("", description="Role label as used by the frontend"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
) -> Dict[str, Any]:
    return get_students_page(
        session=session,
        q=q,
        program_ui=program,
        level=level,
        role_ui=role,
        limit=limit,
        offset=offset,
    )


@app.get("/api/health")
def api_health() -> Dict[str, Any]:
    return {"ok": True}


# If frontend isn't mounted, provide a small JSON message for sanity checks.
@app.get("/")
def root():
    # Explicitly serve the SPA entrypoint so `/` doesn't depend on mount precedence.
    if FRONTEND_INDEX.exists():
        return FileResponse(str(FRONTEND_INDEX))
    return JSONResponse(
        {
            "message": "Frontend not found. Add `frontend/index.html` and static assets, or open /api/health to verify the backend.",
        },
    )


# Mount frontend only after API routes are registered, so `/api/*` endpoints win
# route matching over the static catch-all.
_try_mount_frontend()

