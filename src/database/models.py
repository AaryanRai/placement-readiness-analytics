"""
SQLAlchemy ORM models for the placement analytics system
"""
from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, Date, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Student(Base):
    """Student information table"""
    __tablename__ = 'students'
    
    student_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    program = Column(String(50), nullable=False)
    year_of_study = Column(Integer)
    enrollment_year = Column(Integer, nullable=False)
    target_role = Column(String(100))
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    skills = relationship("StudentSkills", back_populates="student", cascade="all, delete-orphan")
    readiness_scores = relationship("MarketReadinessScores", back_populates="student", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("program IN ('BBA', 'BCA', 'B.Com')", name='check_program'),
        CheckConstraint("year_of_study BETWEEN 1 AND 4", name='check_year'),
    )


class SkillsMaster(Base):
    """Master skills catalog"""
    __tablename__ = 'skills_master'
    
    skill_id = Column(Integer, primary_key=True, autoincrement=True)
    skill_name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50), nullable=False)
    subcategory = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    student_skills = relationship("StudentSkills", back_populates="skill", cascade="all, delete-orphan")
    job_role_skills = relationship("JobRoleSkills", back_populates="skill", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("category IN ('Technical', 'Business', 'Design', 'Soft Skills')", name='check_category'),
    )


class StudentSkills(Base):
    """Student-skill mappings with proficiency levels"""
    __tablename__ = 'student_skills'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False)
    skill_id = Column(Integer, ForeignKey('skills_master.skill_id', ondelete='CASCADE'), nullable=False)
    proficiency_level = Column(String(20))
    proficiency_score = Column(DECIMAL(3, 2))
    acquisition_date = Column(Date, nullable=False)
    source = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="skills")
    skill = relationship("SkillsMaster", back_populates="student_skills")
    
    __table_args__ = (
        CheckConstraint("proficiency_level IN ('Beginner', 'Intermediate', 'Advanced', 'Expert')", name='check_proficiency'),
        CheckConstraint("proficiency_score BETWEEN 0 AND 1", name='check_proficiency_score'),
        CheckConstraint("source IN ('Course', 'Certification', 'Project', 'Workshop')", name='check_source'),
        {'extend_existing': True},
    )


class JobRole(Base):
    """Available job roles"""
    __tablename__ = 'job_roles'
    
    role_id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(100), unique=True, nullable=False)
    role_category = Column(String(50))
    description = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    required_skills = relationship("JobRoleSkills", back_populates="role", cascade="all, delete-orphan")
    readiness_scores = relationship("MarketReadinessScores", back_populates="role", cascade="all, delete-orphan")


class JobRoleSkills(Base):
    """Required skills for each job role"""
    __tablename__ = 'job_role_skills'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey('job_roles.role_id', ondelete='CASCADE'), nullable=False)
    skill_id = Column(Integer, ForeignKey('skills_master.skill_id', ondelete='CASCADE'), nullable=False)
    required_proficiency = Column(String(20), nullable=False)
    importance_weight = Column(DECIMAL(3, 2), default=1.0)
    is_core_skill = Column(Boolean, default=False)
    
    # Relationships
    role = relationship("JobRole", back_populates="required_skills")
    skill = relationship("SkillsMaster", back_populates="job_role_skills")
    
    __table_args__ = (
        CheckConstraint("required_proficiency IN ('Beginner', 'Intermediate', 'Advanced', 'Expert')", name='check_required_proficiency'),
        CheckConstraint("importance_weight BETWEEN 0 AND 1", name='check_importance_weight'),
        {'extend_existing': True},
    )


class MarketReadinessScores(Base):
    """Calculated market readiness scores"""
    __tablename__ = 'market_readiness_scores'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False)
    role_id = Column(Integer, ForeignKey('job_roles.role_id', ondelete='CASCADE'), nullable=False)
    readiness_score = Column(DECIMAL(5, 2))
    matched_skills_count = Column(Integer, default=0)
    required_skills_count = Column(Integer, default=0)
    skill_gap_count = Column(Integer, default=0)
    readiness_level = Column(String(20))
    calculated_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="readiness_scores")
    role = relationship("JobRole", back_populates="readiness_scores")
    
    __table_args__ = (
        CheckConstraint("readiness_score BETWEEN 0 AND 100", name='check_readiness_score'),
        CheckConstraint("readiness_level IN ('Ready', 'Developing', 'Entry-Level')", name='check_readiness_level'),
        {'extend_existing': True},
    )

