import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from sqlalchemy import func
from src.database.connection import get_db_session
from src.database.models import *

st.set_page_config(
    page_title="Placement Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.metric-card {
    background: #f0f2f6;
    padding: 1.5rem;
    border-radius: 0.5rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

def main():
    session = get_db_session()
    
    st.markdown('<h1 class="main-header">📊 University Placement Readiness Dashboard</h1>', 
                unsafe_allow_html=True)
    
    # === KEY METRICS ===
    st.subheader("Cohort Overview")
    
    total_students = session.query(Student).count()
    avg_readiness = session.query(func.avg(MarketReadinessScores.readiness_score)).scalar()
    ready_students = session.query(Student).join(MarketReadinessScores).filter(
        MarketReadinessScores.readiness_level == 'Ready'
    ).distinct().count()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Students", f"{total_students:,}")
    with col2:
        st.metric("Avg Readiness", f"{avg_readiness:.1f}%")
    with col3:
        st.metric("Job-Ready Students", ready_students)
    
    st.divider()
    
    # === CHART 1: PIE CHART - READINESS DISTRIBUTION ===
    st.subheader("🎯 Cohort Readiness Distribution")
    
    readiness_counts = session.query(
        MarketReadinessScores.readiness_level,
        func.count(MarketReadinessScores.id)
    ).group_by(MarketReadinessScores.readiness_level).all()
    
    df_readiness = pd.DataFrame(readiness_counts, columns=['Level', 'Count'])
    
    fig_pie = px.pie(
        df_readiness,
        values='Count',
        names='Level',
        color='Level',
        color_discrete_map={
            'Ready': '#28a745',
            'Developing': '#ffc107',
            'Entry-Level': '#dc3545'
        },
        hole=0.3  # Donut chart
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(height=400)
    
    st.plotly_chart(fig_pie, use_container_width=True)
    
    st.divider()
    
    # === CHART 2: BAR CHART - PROGRAM COMPARISON ===
    st.subheader("📚 Average Readiness by Program")
    
    program_stats = session.query(
        Student.program,
        func.avg(MarketReadinessScores.readiness_score).label('avg_score'),
        func.count(func.distinct(Student.student_id)).label('student_count')
    ).join(MarketReadinessScores).group_by(Student.program).all()
    
    df_program = pd.DataFrame(program_stats, columns=['Program', 'Avg Readiness', 'Students'])
    
    fig_bar = px.bar(
        df_program,
        x='Program',
        y='Avg Readiness',
        text='Avg Readiness',
        color='Avg Readiness',
        color_continuous_scale='Blues',
        labels={'Avg Readiness': 'Average Readiness (%)'}
    )
    fig_bar.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_bar.update_layout(height=400, showlegend=False)
    
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # Show student counts
    for _, row in df_program.iterrows():
        st.caption(f"{row['Program']}: {row['Students']} students")
    
    st.divider()
    
    # === CHART 3: TABLE - TOP 10 STUDENTS ===
    st.subheader("🏆 Top 10 Students by Readiness Score")
    
    # Get best score for each student (across all roles, or for their target role)
    # Using subquery to get max score per student
    from sqlalchemy import and_
    
    top_students = session.query(
        Student.name,
        Student.program,
        Student.year_of_study,
        JobRole.role_name,
        MarketReadinessScores.readiness_score
    ).join(
        MarketReadinessScores, Student.student_id == MarketReadinessScores.student_id
    ).join(
        JobRole, MarketReadinessScores.role_id == JobRole.role_id
    ).filter(
        (Student.target_role == JobRole.role_name) | (Student.target_role.is_(None))
    ).order_by(
        MarketReadinessScores.readiness_score.desc()
    ).limit(10).all()
    
    # If no results with target_role filter, get top scores regardless
    if not top_students:
        top_students = session.query(
            Student.name,
            Student.program,
            Student.year_of_study,
            JobRole.role_name,
            MarketReadinessScores.readiness_score
        ).join(
            MarketReadinessScores, Student.student_id == MarketReadinessScores.student_id
        ).join(
            JobRole, MarketReadinessScores.role_id == JobRole.role_id
        ).order_by(
            MarketReadinessScores.readiness_score.desc()
        ).limit(10).all()
    
    df_top = pd.DataFrame(top_students, columns=['Name', 'Program', 'Year', 'Target Role', 'Score'])
    df_top['Score'] = df_top['Score'].apply(lambda x: f"{x:.1f}%")
    df_top.index = range(1, len(df_top) + 1)  # 1-indexed
    
    st.dataframe(
        df_top,
        use_container_width=True,
        column_config={
            "Name": st.column_config.TextColumn("Student Name", width="medium"),
            "Score": st.column_config.TextColumn("Readiness", width="small")
        }
    )
    
    session.close()

if __name__ == "__main__":
    main()
