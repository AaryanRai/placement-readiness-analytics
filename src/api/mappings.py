from __future__ import annotations

from typing import Dict


PROG_UI_TO_DB: Dict[str, str] = {
    "BTech (CSE)": "Btech",
    "BTech (IT)": "Btech",
    "BBA": "BBA",
    "B.Com": "B.Com",
}

PROG_DB_TO_UI: Dict[str, str] = {
    "Btech": "BTech",
    "BBA": "BBA",
    "B.Com": "B.Com",
}

ROLE_UI_TO_DB: Dict[str, str] = {
    "Data Analyst": "Data Analyst",
    "Full-Stack Dev": "Full-Stack Developer",
    "Digital Marketer": "Digital Marketer",
    "Business Analyst": "Business Analyst",
    "UX/UI Designer": "UX/UI Designer",
}

ROLE_DB_TO_UI: Dict[str, str] = {
    "Data Analyst": "Data Analyst",
    "Full-Stack Developer": "Full-Stack Dev",
    "Digital Marketer": "Digital Marketer",
    "Business Analyst": "Business Analyst",
    "UX/UI Designer": "UX/UI Designer",
}

SOURCE_UI_TO_DB: Dict[str, str] = {
    "Courses": "Course",
    "Certifications": "Certification",
    "Projects": "Project",
    "Workshops": "Workshop",
}

PROF_UI_TO_LEVEL_AND_SCORE: Dict[str, tuple[str, float]] = {
    "Beginner (0.25)": ("Beginner", 0.25),
    "Intermediate (0.50)": ("Intermediate", 0.50),
    "Advanced (0.75)": ("Advanced", 0.75),
    "Expert (1.00)": ("Expert", 1.00),
}


def map_program_ui_to_db(program_ui: str) -> str:
    return PROG_UI_TO_DB.get(program_ui, program_ui)


def map_program_db_to_ui(program_db: str) -> str:
    # DB stores Btech (lowercase t) but UI uses BTech
    return PROG_DB_TO_UI.get(program_db, program_db)


def map_role_ui_to_db(role_ui: str) -> str:
    return ROLE_UI_TO_DB.get(role_ui, role_ui)


def map_role_db_to_ui(role_db: str) -> str:
    return ROLE_DB_TO_UI.get(role_db, role_db)


def map_source_ui_to_db(source_ui: str) -> str:
    return SOURCE_UI_TO_DB.get(source_ui, source_ui)


def map_proficiency_ui_to_level_and_score(proficiency_ui: str) -> tuple[str, float]:
    if proficiency_ui not in PROF_UI_TO_LEVEL_AND_SCORE:
        raise ValueError(f"Unknown proficiency option: {proficiency_ui}")
    return PROF_UI_TO_LEVEL_AND_SCORE[proficiency_ui]

