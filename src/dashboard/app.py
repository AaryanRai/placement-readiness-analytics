import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from sqlalchemy import func, distinct, and_, or_
from src.database.connection import get_db_session
from src.database.models import *

# Page Configuration
st.set_page_config(
    page_title="Placement Readiness Analytics",
    page_icon=None,  # No icon for professional look
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS STYLING
# ============================================================================

st.markdown("""
<style>
    /* Global Styles */
    .main {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Header Styles */
    .dashboard-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2rem 2.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .dashboard-title {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .dashboard-subtitle {
        color: rgba(255, 255, 255, 0.9);
        font-size: 0.95rem;
        margin-top: 0.5rem;
        font-weight: 400;
    }
    
    .last-updated {
        color: rgba(255, 255, 255, 0.75);
        font-size: 0.85rem;
        margin-top: 0.75rem;
    }
    
    /* KPI Card Styles */
    .kpi-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border-left: 4px solid #3b82f6;
        transition: transform 0.2s, box-shadow 0.2s;
        height: 100%;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
    }
    
    .kpi-value {
        font-size: 2.25rem;
        font-weight: 700;
        color: #1e293b;
        margin: 0.5rem 0;
        line-height: 1.2;
    }
    
    .kpi-label {
        font-size: 0.875rem;
        color: #64748b;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .kpi-trend {
        font-size: 0.75rem;
        color: #10b981;
        margin-top: 0.5rem;
    }
    
    /* Section Styles */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1e293b;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
    }
    
    .insight-box {
        background: #f8fafc;
        padding: 1rem 1.25rem;
        border-radius: 8px;
        border-left: 3px solid #3b82f6;
        margin-top: 1rem;
        font-size: 0.9rem;
        color: #475569;
        line-height: 1.6;
    }
    
    /* Sidebar Styles */
    .sidebar .sidebar-content {
        background: #ffffff;
    }
    
    /* Chart Container */
    .chart-container {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        margin-bottom: 1.5rem;
    }
    
    /* Table Styles */
    .data-table-container {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }
    
    /* Color Palette */
    :root {
        --primary-blue: #1e3a8a;
        --accent-blue: #3b82f6;
        --success-green: #059669;
        --warning-amber: #d97706;
        --risk-red: #dc2626;
        --bg-light: #f8fafc;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CACHED DATA FUNCTIONS
# ============================================================================

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_cohort_metrics():
    """Load high-level cohort metrics."""
    session = get_db_session()
    try:
        total_students = session.query(Student).count()
        avg_readiness = session.query(func.avg(MarketReadinessScores.readiness_score)).scalar() or 0.0
        
        # Count by readiness level
        readiness_counts = session.query(
            MarketReadinessScores.readiness_level,
            func.count(func.distinct(MarketReadinessScores.student_id)).label('count')
        ).group_by(MarketReadinessScores.readiness_level).all()
        
        ready_count = next((c[1] for c in readiness_counts if c[0] == 'Ready'), 0)
        developing_count = next((c[1] for c in readiness_counts if c[0] == 'Developing'), 0)
        entry_count = next((c[1] for c in readiness_counts if c[0] == 'Entry-Level'), 0)
        
        total_skills = session.query(SkillsMaster).count()
        total_roles = session.query(JobRole).count()
        
        return {
            'total_students': total_students,
            'avg_readiness': avg_readiness,
            'ready_count': ready_count,
            'developing_count': developing_count,
            'entry_count': entry_count,
            'total_skills': total_skills,
            'total_roles': total_roles
        }
    finally:
        session.close()

@st.cache_data(ttl=300)
def load_readiness_distribution():
    """Load readiness distribution data."""
    session = get_db_session()
    try:
        data = session.query(
            MarketReadinessScores.readiness_level,
            func.count(MarketReadinessScores.id).label('count')
        ).group_by(MarketReadinessScores.readiness_level).all()
        
        return pd.DataFrame(data, columns=['Level', 'Count'])
    finally:
        session.close()

@st.cache_data(ttl=300)
def load_program_comparison():
    """Load program comparison data."""
    session = get_db_session()
    try:
        data = session.query(
            Student.program,
            func.avg(MarketReadinessScores.readiness_score).label('avg_score'),
            func.count(func.distinct(Student.student_id)).label('student_count')
        ).join(MarketReadinessScores).group_by(Student.program).all()
        
        return pd.DataFrame(data, columns=['Program', 'Avg Readiness', 'Students'])
    finally:
        session.close()

@st.cache_data(ttl=300)
def load_career_role_intelligence():
    """Load career role readiness data."""
    session = get_db_session()
    try:
        data = session.query(
            JobRole.role_name,
            func.count(func.distinct(
                MarketReadinessScores.student_id
            )).filter(
                MarketReadinessScores.readiness_level == 'Ready'
            ).label('ready_count'),
            func.avg(MarketReadinessScores.readiness_score).label('avg_score')
        ).join(
            MarketReadinessScores, JobRole.role_id == MarketReadinessScores.role_id
        ).group_by(JobRole.role_name).all()
        
        return pd.DataFrame(data, columns=['Role', 'Ready Students', 'Avg Score'])
    finally:
        session.close()

@st.cache_data(ttl=300)
def load_skill_gap_data():
    """Load skill gap analysis data."""
    session = get_db_session()
    try:
        # Get all required skills from job roles
        required_skills = session.query(
            JobRoleSkills.skill_id,
            func.count(func.distinct(JobRoleSkills.role_id)).label('role_count'),
            func.avg(JobRoleSkills.importance_weight).label('avg_weight')
        ).group_by(JobRoleSkills.skill_id).all()
        
        # Get skills that students have
        student_skills = session.query(
            StudentSkills.skill_id,
            func.count(func.distinct(StudentSkills.student_id)).label('student_count')
        ).group_by(StudentSkills.skill_id).all()
        
        student_skill_dict = {skill_id: count for skill_id, count in student_skills}
        total_students = session.query(Student).count()
        
        # Calculate missing counts
        gaps = []
        for skill_id, role_count, avg_weight in required_skills:
            skill = session.query(SkillsMaster).filter_by(skill_id=skill_id).first()
            if skill:
                students_with_skill = student_skill_dict.get(skill_id, 0)
                missing_count = total_students - students_with_skill
                gaps.append({
                    'Skill': skill.skill_name,
                    'Category': skill.category or 'Other',
                    'Missing Count': missing_count,
                    'Role Count': role_count,
                    'Importance': float(avg_weight) if avg_weight else 0.5
                })
        
        # Sort by missing count
        gaps.sort(key=lambda x: x['Missing Count'], reverse=True)
        
        return pd.DataFrame(gaps[:20])
    finally:
        session.close()

@st.cache_data(ttl=300)
def load_student_table_data():
    """Load student table data for drill-down."""
    session = get_db_session()
    try:
        data = session.query(
            Student.name,
            Student.program,
            Student.year_of_study,
            JobRole.role_name,
            MarketReadinessScores.readiness_score,
            MarketReadinessScores.readiness_level
        ).join(
            MarketReadinessScores, Student.student_id == MarketReadinessScores.student_id
        ).join(
            JobRole, MarketReadinessScores.role_id == JobRole.role_id
        ).all()
        
        return pd.DataFrame(data, columns=[
            'Name', 'Program', 'Year', 'Role', 'Score', 'Level'
        ])
    finally:
        session.close()

# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_header():
    """Render dashboard header."""
    metrics = load_cohort_metrics()
    current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    st.markdown(f"""
    <div class="dashboard-header">
        <h1 class="dashboard-title">Placement Readiness Analytics</h1>
        <p class="dashboard-subtitle">Comprehensive workforce readiness intelligence for university placement administration</p>
        <p class="last-updated">Last updated: {current_time}</p>
    </div>
    """, unsafe_allow_html=True)

def render_kpi_cards():
    """Render KPI metric cards."""
    metrics = load_cohort_metrics()
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Total Students</div>
            <div class="kpi-value">{metrics['total_students']:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        ready_pct = (metrics['ready_count'] / metrics['total_students'] * 100) if metrics['total_students'] > 0 else 0
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #059669;">
            <div class="kpi-label">Placement Ready</div>
            <div class="kpi-value">{ready_pct:.1f}%</div>
            <div class="kpi-trend">{metrics['ready_count']:,} students</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        dev_pct = (metrics['developing_count'] / metrics['total_students'] * 100) if metrics['total_students'] > 0 else 0
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #d97706;">
            <div class="kpi-label">Developing</div>
            <div class="kpi-value">{dev_pct:.1f}%</div>
            <div class="kpi-trend">{metrics['developing_count']:,} students</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        entry_pct = (metrics['entry_count'] / metrics['total_students'] * 100) if metrics['total_students'] > 0 else 0
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #dc2626;">
            <div class="kpi-label">Entry Level</div>
            <div class="kpi-value">{entry_pct:.1f}%</div>
            <div class="kpi-trend">{metrics['entry_count']:,} students</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #3b82f6;">
            <div class="kpi-label">Skills Tracked</div>
            <div class="kpi-value">{metrics['total_skills']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #3b82f6;">
            <div class="kpi-label">Career Roles</div>
            <div class="kpi-value">{metrics['total_roles']}</div>
        </div>
        """, unsafe_allow_html=True)

def render_cohort_section():
    """Render cohort health overview section."""
    st.markdown('<div class="section-header">Cohort Health Overview</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        df_readiness = load_readiness_distribution()
        if not df_readiness.empty:
            fig = px.pie(
                df_readiness,
                values='Count',
                names='Level',
                hole=0.5,
                color='Level',
                color_discrete_map={
                    'Ready': '#059669',
                    'Developing': '#d97706',
                    'Entry-Level': '#dc2626'
                }
            )
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                textfont_size=13,
                marker=dict(line=dict(color='#ffffff', width=2))
            )
            fig.update_layout(
                height=400,
                showlegend=True,
                legend=dict(orientation="v", yanchor="middle", y=0.5, x=1.05),
                font=dict(family="Arial, sans-serif", size=12),
                margin=dict(l=20, r=20, t=40, b=20),
                title=dict(
                    text="Readiness Distribution",
                    font=dict(size=16, color='#1e293b'),
                    x=0.5,
                    xanchor='center'
                )
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Insight
            total = df_readiness['Count'].sum()
            ready_pct = (df_readiness[df_readiness['Level'] == 'Ready']['Count'].sum() / total * 100) if total > 0 else 0
            st.markdown(f"""
            <div class="insight-box">
                <strong>Insight:</strong> {ready_pct:.1f}% of student-role assessments indicate readiness for placement. 
                Focus intervention programs on the {df_readiness[df_readiness['Level'] == 'Entry-Level']['Count'].sum()} entry-level assessments.
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        df_program = load_program_comparison()
        if not df_program.empty:
            fig = px.bar(
                df_program,
                x='Program',
                y='Avg Readiness',
                text='Avg Readiness',
                color='Avg Readiness',
                color_continuous_scale='Blues',
                labels={'Avg Readiness': 'Average Readiness (%)'}
            )
            fig.update_traces(
                texttemplate='%{text:.1f}%',
                textposition='outside',
                marker=dict(line=dict(color='#ffffff', width=1))
            )
            fig.update_layout(
                height=400,
                showlegend=False,
                xaxis=dict(title="Academic Program", titlefont=dict(size=13)),
                yaxis=dict(title="Average Readiness (%)", titlefont=dict(size=13)),
                font=dict(family="Arial, sans-serif", size=12),
                margin=dict(l=20, r=20, t=40, b=20),
                title=dict(
                    text="Program Performance Comparison",
                    font=dict(size=16, color='#1e293b'),
                    x=0.5,
                    xanchor='center'
                )
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Insight
            best_program = df_program.loc[df_program['Avg Readiness'].idxmax()]
            st.markdown(f"""
            <div class="insight-box">
                <strong>Insight:</strong> {best_program['Program']} program shows highest average readiness at {best_program['Avg Readiness']:.1f}%. 
                Consider cross-program learning initiatives to elevate performance across all programs.
            </div>
            """, unsafe_allow_html=True)

def render_career_section():
    """Render career role intelligence section."""
    st.markdown('<div class="section-header">Career Role Intelligence</div>', unsafe_allow_html=True)
    
    df_roles = load_career_role_intelligence()
    if not df_roles.empty:
        df_roles = df_roles.sort_values('Ready Students', ascending=True)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=df_roles['Role'],
            x=df_roles['Ready Students'],
            orientation='h',
            marker=dict(
                color=df_roles['Avg Score'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Avg Score")
            ),
            text=[f"{int(x)} students" for x in df_roles['Ready Students']],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Ready Students: %{x}<br>Avg Score: %{customdata:.1f}%<extra></extra>',
            customdata=df_roles['Avg Score']
        ))
        
        fig.update_layout(
            height=350,
            xaxis=dict(title="Number of Ready Students", titlefont=dict(size=13)),
            yaxis=dict(title="", titlefont=dict(size=13)),
            font=dict(family="Arial, sans-serif", size=12),
            margin=dict(l=20, r=20, t=40, b=20),
            title=dict(
                text="Student Readiness by Career Path",
                font=dict(size=16, color='#1e293b'),
                x=0.5,
                xanchor='center'
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Insight
        top_role = df_roles.loc[df_roles['Ready Students'].idxmax()]
        st.markdown(f"""
        <div class="insight-box">
            <strong>Insight:</strong> {top_role['Role']} has the highest number of ready students ({int(top_role['Ready Students'])}). 
            This indicates strong alignment between curriculum and industry demand for this role.
        </div>
        """, unsafe_allow_html=True)

def render_skill_gap_section():
    """Render skill gap intelligence section."""
    st.markdown('<div class="section-header">Skill Gap Intelligence</div>', unsafe_allow_html=True)
    
    df_gaps = load_skill_gap_data()
    if not df_gaps.empty and len(df_gaps) > 0:
        # Create treemap
        fig = px.treemap(
            df_gaps.head(15),
            path=[px.Constant("Skills"), 'Category', 'Skill'],
            values='Missing Count',
            color='Missing Count',
            color_continuous_scale='Reds',
            hover_data={'Missing Count': True, 'Category': True}
        )
        
        fig.update_traces(
            textinfo="label+value",
            textfont_size=12,
            hovertemplate='<b>%{label}</b><br>Missing: %{value} students<extra></extra>'
        )
        
        fig.update_layout(
            height=500,
            font=dict(family="Arial, sans-serif", size=11),
            margin=dict(l=20, r=20, t=40, b=20),
            title=dict(
                text="Critical Skill Gaps Across Student Population",
                font=dict(size=16, color='#1e293b'),
                x=0.5,
                xanchor='center'
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Insight
        top_gap = df_gaps.iloc[0]
        st.markdown(f"""
        <div class="insight-box">
            <strong>Insight:</strong> {top_gap['Skill']} is the most critical skill gap, affecting {int(top_gap['Missing Count'])} students. 
            Prioritize curriculum enhancement or targeted training programs to address this gap.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Skill gap analysis data is being processed. Please check back shortly.")

def render_data_table():
    """Render filterable student data table."""
    st.markdown('<div class="section-header">Student Data Explorer</div>', unsafe_allow_html=True)
    
    df_students = load_student_table_data()
    
    if not df_students.empty:
        # Filters
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            programs = ['All'] + sorted(df_students['Program'].unique().tolist())
            selected_program = st.selectbox("Program", programs)
        
        with col2:
            years = ['All'] + sorted(df_students['Year'].unique().tolist())
            selected_year = st.selectbox("Academic Year", years)
        
        with col3:
            roles = ['All'] + sorted(df_students['Role'].unique().tolist())
            selected_role = st.selectbox("Career Role", roles)
        
        with col4:
            levels = ['All'] + sorted(df_students['Level'].unique().tolist())
            selected_level = st.selectbox("Readiness Level", levels)
        
        # Apply filters
        filtered_df = df_students.copy()
        if selected_program != 'All':
            filtered_df = filtered_df[filtered_df['Program'] == selected_program]
        if selected_year != 'All':
            filtered_df = filtered_df[filtered_df['Year'] == selected_year]
        if selected_role != 'All':
            filtered_df = filtered_df[filtered_df['Role'] == selected_role]
        if selected_level != 'All':
            filtered_df = filtered_df[filtered_df['Level'] == selected_level]
        
        # Format score
        filtered_df['Score'] = filtered_df['Score'].apply(lambda x: f"{x:.1f}%")
        
        # Color code readiness level
        def color_level(val):
            if val == 'Ready':
                return 'background-color: #d1fae5; color: #065f46'
            elif val == 'Developing':
                return 'background-color: #fed7aa; color: #92400e'
            else:
                return 'background-color: #fee2e2; color: #991b1b'
        
        styled_df = filtered_df.style.applymap(color_level, subset=['Level'])
        
        st.dataframe(
            styled_df,
            use_container_width=True,
            height=400,
            column_config={
                "Name": st.column_config.TextColumn("Student Name", width="medium"),
                "Program": st.column_config.TextColumn("Program", width="small"),
                "Year": st.column_config.NumberColumn("Year", width="small"),
                "Role": st.column_config.TextColumn("Career Role", width="medium"),
                "Score": st.column_config.TextColumn("Readiness Score", width="small"),
                "Level": st.column_config.TextColumn("Level", width="small")
            }
        )
        
        st.caption(f"Showing {len(filtered_df)} of {len(df_students)} records")

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    # Sidebar Navigation
    with st.sidebar:
        st.markdown("## Navigation")
        page = st.radio(
            "Select Section",
            [
                "Overview",
                "Cohort Analytics",
                "Career Readiness",
                "Skill Gap Analysis",
                "Data Explorer"
            ],
            label_visibility="collapsed"
        )
    
    # Render header and KPIs
    render_header()
    render_kpi_cards()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Render selected section
    if page == "Overview":
        render_cohort_section()
    elif page == "Cohort Analytics":
        render_cohort_section()
    elif page == "Career Readiness":
        render_career_section()
    elif page == "Skill Gap Analysis":
        render_skill_gap_section()
    elif page == "Data Explorer":
        render_data_table()

if __name__ == "__main__":
    main()
