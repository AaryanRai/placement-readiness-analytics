"""
University Placement Analytics Dashboard
Administrator View
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from sqlalchemy import func
from src.database.connection import get_db_session
from src.database.models import Student, JobRole, MarketReadinessScores

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
    margin-bottom: 1rem;
}
.metric-card {
    background: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)


def main():
    session = get_db_session()
    
    try:
        st.markdown('<h1 class="main-header">University Placement Readiness Dashboard</h1>', 
                    unsafe_allow_html=True)
        
        # === SECTION 1: KEY METRICS ===
        st.subheader("📊 Cohort Overview")
        
        total_students = session.query(Student).count()
        avg_readiness = session.query(func.avg(MarketReadinessScores.readiness_score)).scalar() or 0
        ready_count = session.query(MarketReadinessScores).filter(
            MarketReadinessScores.readiness_level == 'Ready'
        ).count()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Students", total_students)
        with col2:
            st.metric("Avg Readiness", f"{avg_readiness:.1f}%")
        with col3:
            st.metric("Job-Ready Students", ready_count)
        with col4:
            last_updated = "2 hours ago"  # From ETL
            st.metric("Last Updated", last_updated)
        
        st.divider()
        
        # === SECTION 2: READINESS DISTRIBUTION (PIE CHART) ===
        st.subheader("🎯 Cohort Readiness Distribution")
        
        readiness_counts = session.query(
            MarketReadinessScores.readiness_level,
            func.count(MarketReadinessScores.id)
        ).group_by(MarketReadinessScores.readiness_level).all()
        
        if readiness_counts:
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
                hole=0.3
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No readiness data available. Please run the scoring algorithm first.")
        
        st.divider()
        
        # === SECTION 3: PROGRAM COMPARISON (BAR CHART) ===
        st.subheader("📚 Average Readiness by Program")
        
        program_stats = session.query(
            Student.program,
            func.avg(MarketReadinessScores.readiness_score).label('avg_score'),
            func.count(Student.student_id).label('student_count')
        ).join(
            MarketReadinessScores, Student.student_id == MarketReadinessScores.student_id
        ).group_by(Student.program).all()
        
        if program_stats:
            df_program = pd.DataFrame(program_stats, columns=['Program', 'Avg Readiness', 'Students'])
            
            fig_bar = px.bar(
                df_program,
                x='Program',
                y='Avg Readiness',
                text='Avg Readiness',
                color='Avg Readiness',
                color_continuous_scale='Blues'
            )
            fig_bar.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No program comparison data available.")
        
        st.divider()
        
        # === SECTION 4: TOP STUDENTS TABLE ===
        st.subheader("🏆 Top 10 Students by Readiness")
        
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
        
        if top_students:
            df_top = pd.DataFrame(top_students, columns=['Name', 'Program', 'Year', 'Best Role', 'Score'])
            df_top['Score'] = df_top['Score'].apply(lambda x: f"{float(x):.1f}%")
            
            st.dataframe(df_top, use_container_width=True, hide_index=True)
        else:
            st.info("No student data available. Please populate the database first.")
    
    finally:
        session.close()


if __name__ == "__main__":
    main()

