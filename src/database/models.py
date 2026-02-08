"""
SQLAlchemy ORM models for Placement Analytics System
"""
from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, Date, TIMESTAMP, ForeignKey, CheckConstraint, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database.connection import Base


class Student(Base):
    """Student table model"""
    __tablename__ = 'students'
    
    student_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    program = Column(String(50), nullable=False)
    year_of_study = Column(Integer)
    enrollment_year = Column(Integer, nullable=False)
    target_role = Column(String(100))
    created_at = Column(TIMESTAMP, default=func.now())
    
    __table_args__ = (
        CheckConstraint('program IN (\'BBA\', \'Btech\', \'B.Com\')', name='check_program'),
        CheckConstraint('year_of_study BETWEEN 1 AND 4', name='check_year'),
        Index('idx_students_program', 'program'),
        Index('idx_students_year', 'year_of_study'),
    )


class SkillsMaster(Base):
    """Skills master table model"""
    __tablename__ = 'skills_master'
    
    skill_id = Column(Integer, primary_key=True, autoincrement=True)
    skill_name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50), nullable=False)
    subcategory = Column(String(50))
    created_at = Column(TIMESTAMP, default=func.now())
    
    __table_args__ = (
        CheckConstraint('category IN (\'Technical\', \'Business\', \'Design\', \'Soft Skills\')', name='check_category'),
        Index('idx_skills_category', 'category'),
    )


class StudentSkills(Base):
    """Student skills junction table"""
    __tablename__ = 'student_skills'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False)
    skill_id = Column(Integer, ForeignKey('skills_master.skill_id', ondelete='CASCADE'), nullable=False)
    proficiency_level = Column(String(20))
    proficiency_score = Column(DECIMAL(3, 2))
    acquisition_date = Column(Date, nullable=False)
    source = Column(String(50))
    created_at = Column(TIMESTAMP, default=func.now())
    
    __table_args__ = (
        UniqueConstraint('student_id', 'skill_id', name='unique_student_skill'),
        CheckConstraint('proficiency_level IN (\'Beginner\', \'Intermediate\', \'Advanced\', \'Expert\')', name='check_proficiency'),
        CheckConstraint('proficiency_score BETWEEN 0 AND 1', name='check_proficiency_score'),
        CheckConstraint('source IN (\'Course\', \'Certification\', \'Project\', \'Workshop\')', name='check_source'),
        Index('idx_student_skills_student', 'student_id'),
        Index('idx_student_skills_skill', 'skill_id'),
    )


class JobRole(Base):
    """Job roles table model"""
    __tablename__ = 'job_roles'
    
    role_id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(100), unique=True, nullable=False)
    role_category = Column(String(50))
    description = Column(String)
    created_at = Column(TIMESTAMP, default=func.now())


class JobRoleSkills(Base):
    """Job role skills requirements table"""
    __tablename__ = 'job_role_skills'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey('job_roles.role_id', ondelete='CASCADE'), nullable=False)
    skill_id = Column(Integer, ForeignKey('skills_master.skill_id', ondelete='CASCADE'), nullable=False)
    required_proficiency = Column(String(20), nullable=False)
    importance_weight = Column(DECIMAL(3, 2), default=1.0)
    is_core_skill = Column(Boolean, default=False)
    
    # Relationships
    skill = relationship("SkillsMaster", backref="job_role_skills")
    role = relationship("JobRole", backref="job_role_skills")
    
    __table_args__ = (
        UniqueConstraint('role_id', 'skill_id', name='unique_role_skill'),
        CheckConstraint('importance_weight BETWEEN 0 AND 1', name='check_weight'),
        Index('idx_job_role_skills_role', 'role_id'),
    )


class MarketReadinessScores(Base):
    """Market readiness scores table"""
    __tablename__ = 'market_readiness_scores'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False)
    role_id = Column(Integer, ForeignKey('job_roles.role_id', ondelete='CASCADE'), nullable=False)
    readiness_score = Column(DECIMAL(5, 2))
    matched_skills_count = Column(Integer, default=0)
    required_skills_count = Column(Integer, default=0)
    skill_gap_count = Column(Integer, default=0)
    readiness_level = Column(String(20))
    calculated_at = Column(TIMESTAMP, default=func.now())
    
    __table_args__ = (
        UniqueConstraint('student_id', 'role_id', name='unique_student_role'),
        CheckConstraint('readiness_score BETWEEN 0 AND 100', name='check_score'),
        CheckConstraint('readiness_level IN (\'Ready\', \'Developing\', \'Entry-Level\')', name='check_level'),
        Index('idx_readiness_student', 'student_id'),
        Index('idx_readiness_level', 'readiness_level'),
        Index('idx_readiness_score', 'readiness_score'),
    )

