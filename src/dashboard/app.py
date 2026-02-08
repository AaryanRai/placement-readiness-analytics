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
        color: #ffffff;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #475569;
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
    
    /* Text color fixes for dark theme */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #ffffff !important;
    }
    
    /* Info card styles */
    .info-card {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        color: #ffffff;
    }
    
    .info-card h3 {
        color: #ffffff;
        margin-top: 0;
        font-size: 1.25rem;
    }
    
    .info-card p, .info-card li {
        color: rgba(255, 255, 255, 0.9);
        line-height: 1.6;
    }
    
    .model-card {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        padding: 2rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        color: #ffffff;
    }
    
    .model-card h3 {
        color: #ffffff;
        margin-top: 0;
        font-size: 1.25rem;
    }
    
    .model-card code {
        background: rgba(0, 0, 0, 0.2);
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        color: #ffffff;
        font-family: 'Courier New', monospace;
    }
    
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

@st.cache_data(ttl=0)  # No cache - always fetch fresh data
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

@st.cache_data(ttl=0)  # No cache - always fetch fresh data
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

@st.cache_data(ttl=0)  # No cache - always fetch fresh data
def load_program_comparison():
    """Load program comparison data."""
    session = get_db_session()
    try:
        data = session.query(
            Student.program,
            func.avg(MarketReadinessScores.readiness_score).label('avg_score'),
            func.count(func.distinct(Student.student_id)).label('student_count')
        ).join(MarketReadinessScores).group_by(Student.program).all()
        
        df = pd.DataFrame(data, columns=['Program', 'Avg Readiness', 'Students'])
        # Ensure BCA is replaced with Btech if it exists
        df['Program'] = df['Program'].str.replace('BCA', 'Btech', regex=False)
        return df
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

@st.cache_data(ttl=0)  # No cache - always fetch fresh data
def load_student_table_data():
    """Load student table data for drill-down - one record per student showing best score."""
    session = get_db_session()
    try:
        # Get all students with their best readiness scores
        students = session.query(Student).all()
        results = []
        
        for student in students:
            # Get all scores for this student
            scores = session.query(
                MarketReadinessScores.readiness_score,
                MarketReadinessScores.readiness_level,
                JobRole.role_name
            ).join(
                JobRole, MarketReadinessScores.role_id == JobRole.role_id
            ).filter(
                MarketReadinessScores.student_id == student.student_id
            ).all()
            
            if scores:
                # Find the best score
                best_score = max(scores, key=lambda x: x[0])
                results.append({
                    'Name': student.name,
                    'Program': student.program,
                    'Year': student.year_of_study,
                    'Best Role': best_score[2],
                    'Score': float(best_score[0]),
                    'Level': best_score[1]
                })
        
        return pd.DataFrame(results)
    finally:
        session.close()

@st.cache_data(ttl=0)  # No cache - always fetch fresh data
def load_year_progression():
    """Load readiness progression by academic year."""
    session = get_db_session()
    try:
        data = session.query(
            Student.year_of_study,
            MarketReadinessScores.readiness_level,
            func.count(func.distinct(MarketReadinessScores.student_id)).label('count')
        ).join(
            MarketReadinessScores, Student.student_id == MarketReadinessScores.student_id
        ).group_by(
            Student.year_of_study, MarketReadinessScores.readiness_level
        ).all()
        
        return pd.DataFrame(data, columns=['Year', 'Level', 'Count'])
    finally:
        session.close()

@st.cache_data(ttl=300)
def load_skill_acquisition_trends():
    """Load skill acquisition trends over time."""
    session = get_db_session()
    try:
        data = session.query(
            func.date_trunc('month', StudentSkills.acquisition_date).label('month'),
            func.count(StudentSkills.id).label('skill_count')
        ).group_by(
            func.date_trunc('month', StudentSkills.acquisition_date)
        ).order_by('month').all()
        
        return pd.DataFrame(data, columns=['Month', 'Skills Acquired'])
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
    # #region agent log
    import json
    with open('/Users/aaryanrai/Downloads/Career Readiness Prediction/.cursor/debug.log', 'a') as f:
        f.write(json.dumps({"location":"app.py:413","message":"render_cohort_section called","data":{},"timestamp":int(__import__('time').time()*1000)}) + '\n')
    # #endregion
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
                font=dict(size=16, color='#ffffff'),
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
            # #region agent log
            import json
            import traceback
            try:
                with open('/Users/aaryanrai/Downloads/Career Readiness Prediction/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({"location":"app.py:487","message":"Before update_layout","data":{"xaxis_config":"title=dict(text=..., font=dict(size=13))"},"timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
            try:
                fig.update_layout(
                    height=400,
                    showlegend=False,
                    xaxis=dict(title=dict(text="Academic Program", font=dict(size=13))),
                    yaxis=dict(title=dict(text="Average Readiness (%)", font=dict(size=13))),
                    font=dict(family="Arial, sans-serif", size=12),
                    margin=dict(l=20, r=20, t=40, b=20),
                title=dict(
                    text="Program Performance Comparison",
                    font=dict(size=16, color='#ffffff'),
                    x=0.5,
                    xanchor='center'
                )
                )
                # #region agent log
                try:
                    with open('/Users/aaryanrai/Downloads/Career Readiness Prediction/.cursor/debug.log', 'a') as f:
                        f.write(json.dumps({"location":"app.py:492","message":"update_layout succeeded","data":{},"timestamp":int(__import__('time').time()*1000)}) + '\n')
                except: pass
                # #endregion
            except Exception as e:
                # #region agent log
                try:
                    with open('/Users/aaryanrai/Downloads/Career Readiness Prediction/.cursor/debug.log', 'a') as f:
                        f.write(json.dumps({"location":"app.py:492","message":"update_layout ERROR","data":{"error":str(e),"traceback":traceback.format_exc()},"timestamp":int(__import__('time').time()*1000)}) + '\n')
                except: pass
                # #endregion
                raise
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
    # #region agent log
    import json
    with open('/Users/aaryanrai/Downloads/Career Readiness Prediction/.cursor/debug.log', 'a') as f:
        f.write(json.dumps({"location":"app.py:507","message":"render_career_section called","data":{},"timestamp":int(__import__('time').time()*1000)}) + '\n')
    # #endregion
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
        
        # #region agent log
        import json
        import traceback
        try:
            with open('/Users/aaryanrai/Downloads/Career Readiness Prediction/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({"location":"app.py:547","message":"Before career update_layout","data":{"xaxis_config":"title=dict(text=..., font=dict(size=13))"},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion
        try:
            fig.update_layout(
                height=350,
                xaxis=dict(title=dict(text="Number of Ready Students", font=dict(size=13))),
                yaxis=dict(title=""),
                font=dict(family="Arial, sans-serif", size=12),
                margin=dict(l=20, r=20, t=40, b=20),
            title=dict(
                text="Student Readiness by Career Path",
                font=dict(size=16, color='#ffffff'),
                x=0.5,
                xanchor='center'
            ),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            # #region agent log
            try:
                with open('/Users/aaryanrai/Downloads/Career Readiness Prediction/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({"location":"app.py:552","message":"career update_layout succeeded","data":{},"timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
        except Exception as e:
            # #region agent log
            try:
                with open('/Users/aaryanrai/Downloads/Career Readiness Prediction/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({"location":"app.py:552","message":"career update_layout ERROR","data":{"error":str(e),"traceback":traceback.format_exc()},"timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
            raise
        
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
                font=dict(size=16, color='#ffffff'),
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
    """Render filterable student data table - showing unique students only."""
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
            roles = ['All'] + sorted(df_students['Best Role'].unique().tolist())
            selected_role = st.selectbox("Best Career Role", roles)
        
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
            filtered_df = filtered_df[filtered_df['Best Role'] == selected_role]
        if selected_level != 'All':
            filtered_df = filtered_df[filtered_df['Level'] == selected_level]
        
        # Format score and drop Target Role column for display
        filtered_df = filtered_df[['Name', 'Program', 'Year', 'Best Role', 'Score', 'Level']].copy()
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
                "Best Role": st.column_config.TextColumn("Best Career Role", width="medium"),
                "Score": st.column_config.TextColumn("Readiness Score", width="small"),
                "Level": st.column_config.TextColumn("Level", width="small")
            }
        )
        
        st.caption(f"Showing {len(filtered_df)} of {len(df_students)} students (each student shown once with their best readiness score)")

def run_complete_pipeline():
    """Run the complete pipeline: data generation, scoring, and model training."""
    import subprocess
    import sys
    from pathlib import Path
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Clear and regenerate data
        status_text.text("Step 1/5: Clearing existing data and generating new students...")
        progress_bar.progress(0.1)
        
        result = subprocess.run(
            [sys.executable, 'src/data_generation/populate_db.py', '--clear'],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent.parent)
        )
        
        if result.returncode != 0:
            st.error(f"Data generation failed: {result.stderr}")
            return
        
        # Step 2: Calculate scores
        status_text.text("Step 2/5: Calculating readiness scores...")
        progress_bar.progress(0.3)
        
        result = subprocess.run(
            [sys.executable, 'src/core/scoring.py'],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent.parent)
        )
        
        if result.returncode != 0:
            st.warning(f"Score calculation had issues: {result.stderr}")
        
        # Step 3: Train ML models
        status_text.text("Step 3/5: Training ML models with new data...")
        progress_bar.progress(0.5)
        
        result = subprocess.run(
            [sys.executable, 'src/ml_models/train_models.py'],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent.parent)
        )
        
        if result.returncode != 0:
            st.error(f"Model training failed: {result.stderr}")
            return
        
        # Step 4: Update scores with ML predictions
        status_text.text("Step 4/5: Updating scores with ML predictions...")
        progress_bar.progress(0.8)
        
        result = subprocess.run(
            [sys.executable, 'src/core/scoring_ml.py'],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent.parent)
        )
        
        if result.returncode != 0:
            st.warning(f"ML score update had issues: {result.stderr}")
        
        # Step 5: Complete
        status_text.text("Step 5/5: Pipeline complete!")
        progress_bar.progress(1.0)
        
        st.success("✅ Pipeline completed successfully! Data regenerated, models retrained, and scores updated.")
        st.info("💡 Refreshing page to show updated results...")
        
        # Clear ALL caches to force reload
        st.cache_data.clear()
        
        # Wait a moment for database to update
        import time
        time.sleep(1)
        
        # Force page refresh
        st.rerun()
        
    except Exception as e:
        st.error(f"Pipeline error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
    finally:
        progress_bar.empty()
        status_text.empty()

def render_ml_section():
    """Render ML predictions and model comparison section."""
    st.markdown('<div class="section-header">ML-Based Readiness Prediction System</div>', unsafe_allow_html=True)
    
    # Model Explanation Section
    st.markdown("""
    <div class="info-card" style="margin-bottom: 2rem;">
        <h3>🤖 Machine Learning Models at the Core</h3>
        <p>This system uses <strong>two trained ML models</strong> as the primary method for predicting student readiness:</p>
        <ol>
            <li><strong>Decision Tree Classifier</strong> - Classifies students into readiness levels (Ready/Developing/Entry-Level)</li>
            <li><strong>Random Forest Regressor</strong> - Predicts exact readiness scores (0-100%)</li>
        </ol>
        <p><strong>Why These Models?</strong></p>
        <ul>
            <li><strong>Decision Tree:</strong> Interpretable, handles non-linear relationships, works well with categorical features</li>
            <li><strong>Random Forest:</strong> High accuracy, reduces overfitting, captures complex feature interactions</li>
        </ul>
        <p><strong>How They Work:</strong> The models learn from 2,500 student-role combinations, analyzing 30 features including skill portfolios, proficiency levels, program types, and role requirements to make predictions.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if models exist
    from pathlib import Path
    from src.ml_models.model_info import get_model_feature_importance, get_model_performance_metrics
    
    models_dir = Path(__file__).parent.parent.parent / 'models'
    classifier_path = models_dir / 'readiness_classifier.pkl'
    regressor_path = models_dir / 'readiness_regressor.pkl'
    
    if not classifier_path.exists() or not regressor_path.exists():
        st.warning("⚠ ML models not trained yet. Please run: `python src/ml_models/train_models.py`")
        if st.button("Train Models Now"):
            with st.spinner("Training ML models... This may take a few minutes."):
                import subprocess
                result = subprocess.run(
                    ['python3', 'src/ml_models/train_models.py'],
                    capture_output=True,
                    text=True,
                    cwd=str(Path(__file__).parent.parent.parent)
                )
                if result.returncode == 0:
                    st.success("✓ Models trained successfully! Please refresh the page.")
                    st.code(result.stdout)
                else:
                    st.error("Training failed. Check the error below:")
                    st.code(result.stderr)
        return
    
    # Get actual model data
    model_info = get_model_feature_importance()
    perf_metrics = get_model_performance_metrics()
    
    # Model Performance Metrics
    st.markdown("### Model Performance Metrics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #3b82f6;">
            <div class="kpi-label">Classifier Accuracy</div>
            <div class="kpi-value">{perf_metrics['classifier']['accuracy']*100:.1f}%</div>
            <div class="kpi-trend">{perf_metrics['classifier']['model_type']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #059669;">
            <div class="kpi-label">Regressor R² Score</div>
            <div class="kpi-value">{perf_metrics['regressor']['r2_score']*100:.1f}%</div>
            <div class="kpi-trend">{perf_metrics['regressor']['model_type']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #d97706;">
            <div class="kpi-label">RMSE</div>
            <div class="kpi-value">{perf_metrics['regressor']['rmse']:.2f}</div>
            <div class="kpi-trend">Score Prediction Error</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Comparison: Rule-based vs ML
    st.markdown("### Rule-Based vs ML Prediction Comparison")
    
    session = get_db_session()
    try:
        # Get sample predictions for comparison
        from src.core.scoring import calculate_readiness_score
        from src.ml_models.predict import predict_readiness_ml
        
        # Get a few students for comparison
        students = session.query(Student).limit(10).all()
        roles = session.query(JobRole).all()
        
        comparison_data = []
        for student in students[:5]:  # Compare first 5 students
            for role in roles[:2]:  # Compare first 2 roles
                # Rule-based prediction (explicitly request rule-based)
                rule_result = calculate_readiness_score(student.student_id, role.role_id, session, use_ml=False)
                
                # ML prediction
                ml_result = predict_readiness_ml(student.student_id, role.role_id, session)
                
                if not ml_result.get('error'):
                    comparison_data.append({
                        'Student': student.name,
                        'Program': student.program,
                        'Role': role.role_name,
                        'Rule-Based Score': f"{rule_result['readiness_score']:.1f}%",
                        'ML Score': f"{ml_result['readiness_score_ml']:.1f}%",
                        'Rule-Based Level': rule_result['readiness_level'],
                        'ML Level': ml_result['readiness_level_ml'],
                        'Difference': f"{abs(rule_result['readiness_score'] - ml_result['readiness_score_ml']):.1f}%"
                    })
        
        if comparison_data:
            df_comparison = pd.DataFrame(comparison_data)
            st.dataframe(df_comparison, use_container_width=True, height=300)
            
            # Insight
            avg_diff = sum(float(row['Difference'].replace('%', '')) for row in comparison_data) / len(comparison_data)
            st.markdown(f"""
            <div class="insight-box">
                <strong>Insight:</strong> Average difference between rule-based and ML predictions is {avg_diff:.1f}%. 
                ML models provide more nuanced predictions by learning from patterns in skill portfolios and student characteristics.
            </div>
            """, unsafe_allow_html=True)
        
        # Feature Importance Visualization - Using Actual Model Data
        st.markdown("### Feature Importance Analysis")
        st.markdown("""
        <div class="insight-box" style="margin-bottom: 1rem;">
            <strong>Understanding Feature Importance:</strong> These charts show which features the ML models consider most important when making predictions. 
            Higher importance means the feature has more influence on the model's decision.
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Classifier feature importance - using actual model data
            st.markdown("**Decision Tree Classifier - Top 10 Features**")
            if model_info['classifier'] is not None:
                classifier_top = model_info['classifier'].head(10).copy()
                # Clean feature names for display
                classifier_top['Feature_Display'] = classifier_top['Feature'].str.replace('_', ' ').str.title()
                fig = px.bar(
                    classifier_top,
                    x='Importance',
                    y='Feature_Display',
                    orientation='h',
                    color='Importance',
                    color_continuous_scale='Blues',
                    labels={'Importance': 'Feature Importance', 'Feature_Display': 'Feature'}
                )
                fig.update_layout(
                    height=400,
                    showlegend=False,
                    title=dict(text="Classifier Feature Importance", font=dict(size=14, color='#ffffff')),
                    font=dict(family="Arial, sans-serif", size=11, color='#ffffff'),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(title=dict(text="Importance", font=dict(size=12, color='#ffffff'))),
                    yaxis=dict(title="", autorange='reversed')
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Feature importance data not available")
        
        with col2:
            # Regressor feature importance - using actual model data
            st.markdown("**Random Forest Regressor - Top 10 Features**")
            if model_info['regressor'] is not None:
                regressor_top = model_info['regressor'].head(10).copy()
                # Clean feature names for display
                regressor_top['Feature_Display'] = regressor_top['Feature'].str.replace('_', ' ').str.title()
                fig = px.bar(
                    regressor_top,
                    x='Importance',
                    y='Feature_Display',
                    orientation='h',
                    color='Importance',
                    color_continuous_scale='Greens',
                    labels={'Importance': 'Feature Importance', 'Feature_Display': 'Feature'}
                )
                fig.update_layout(
                    height=400,
                    showlegend=False,
                    title=dict(text="Regressor Feature Importance", font=dict(size=14, color='#ffffff')),
                    font=dict(family="Arial, sans-serif", size=11, color='#ffffff'),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(title=dict(text="Importance", font=dict(size=12, color='#ffffff'))),
                    yaxis=dict(title="", autorange='reversed')
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Feature importance data not available")
        
        # ML Prediction Distribution
        st.markdown("### ML Prediction Distribution")
        
        # Get ML predictions for all students
        from src.ml_models.predict import predict_batch_ml
        ml_predictions = predict_batch_ml(session)
        
        if not ml_predictions.empty:
            # Distribution by level
            level_counts = ml_predictions['readiness_level_ml'].value_counts()
            df_ml_levels = pd.DataFrame({
                'Level': level_counts.index,
                'Count': level_counts.values
            })
            
            fig = px.pie(
                df_ml_levels,
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
                legend=dict(font=dict(color='#ffffff')),
                font=dict(family="Arial, sans-serif", size=12),
                title=dict(
                    text="ML Predicted Readiness Distribution",
                    font=dict(size=16, color='#ffffff'),
                    x=0.5,
                    xanchor='center'
                )
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Score distribution histogram
            fig = px.histogram(
                ml_predictions,
                x='readiness_score_ml',
                nbins=20,
                labels={'readiness_score_ml': 'ML Predicted Score (%)', 'count': 'Number of Predictions'},
                color_discrete_sequence=['#3b82f6']
            )
            fig.update_layout(
                height=350,
                font=dict(family="Arial, sans-serif", size=12),
                title=dict(
                    text="ML Score Distribution",
                    font=dict(size=16, color='#ffffff'),
                    x=0.5,
                    xanchor='center'
                ),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(title=dict(text="Predicted Score (%)", font=dict(size=13, color='#ffffff'))),
                yaxis=dict(title=dict(text="Count", font=dict(size=13, color='#ffffff')))
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Summary statistics
            st.markdown("### ML Prediction Statistics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Mean Score", f"{ml_predictions['readiness_score_ml'].mean():.1f}%")
            with col2:
                st.metric("Median Score", f"{ml_predictions['readiness_score_ml'].median():.1f}%")
            with col3:
                st.metric("Std Deviation", f"{ml_predictions['readiness_score_ml'].std():.1f}%")
            with col4:
                st.metric("Total Predictions", len(ml_predictions))
    
    finally:
        session.close()

def render_year_progression():
    """Render readiness progression by academic year."""
    st.markdown('<div class="section-header">Readiness Progression by Academic Year</div>', unsafe_allow_html=True)
    
    df_progression = load_year_progression()
    if not df_progression.empty:
        fig = px.bar(
            df_progression,
            x='Year',
            y='Count',
            color='Level',
            barmode='group',
            color_discrete_map={
                'Ready': '#059669',
                'Developing': '#d97706',
                'Entry-Level': '#dc2626'
            },
            labels={'Count': 'Number of Students', 'Year': 'Academic Year'}
        )
        fig.update_layout(
            height=400,
            font=dict(family="Arial, sans-serif", size=12),
            margin=dict(l=20, r=20, t=40, b=20),
            title=dict(
                text="Readiness Distribution Across Academic Years",
                font=dict(size=16, color='#ffffff'),
                x=0.5,
                xanchor='center'
            ),
            legend=dict(font=dict(color='#ffffff')),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(title=dict(text="Academic Year", font=dict(size=13, color='#ffffff'))),
            yaxis=dict(title=dict(text="Number of Students", font=dict(size=13, color='#ffffff')))
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Insight
        st.markdown("""
        <div class="insight-box">
            <strong>Insight:</strong> This chart shows how readiness levels are distributed across different academic years. 
            Higher years typically show improved readiness as students gain more skills and experience.
        </div>
        """, unsafe_allow_html=True)

def render_about_section():
    """Render about section with data information."""
    st.markdown('<div class="section-header">About the System</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h3>Dataset Overview</h3>
            <p><strong>Student Population:</strong> 500 students across 3 academic programs</p>
            <ul>
                <li><strong>BBA:</strong> Business Administration</li>
                <li><strong>Btech:</strong> Technology</li>
                <li><strong>B.Com:</strong> Commerce</li>
            </ul>
            <p><strong>Skills Tracked:</strong> 47 skills across 4 major categories:</p>
            <ul>
                <li>Technical Skills (Programming, Data Analysis, Web Development, Database, Cloud)</li>
                <li>Business Skills (Analysis, Marketing, Management)</li>
                <li>Design Skills (UI/UX, Graphics)</li>
                <li>Soft Skills (Communication, Leadership, Problem Solving)</li>
            </ul>
            <p><strong>Career Roles Analyzed:</strong> 5 high-demand roles</p>
            <ul>
                <li>Data Analyst</li>
                <li>Full-Stack Developer</li>
                <li>Digital Marketer</li>
                <li>Business Analyst</li>
                <li>UX/UI Designer</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card">
            <h3>Key Features</h3>
            <ul>
                <li><strong>Real-time Readiness Scoring:</strong> Calculated for each student-role combination</li>
                <li><strong>Skill Gap Analysis:</strong> Identifies critical missing skills across the cohort</li>
                <li><strong>Program Comparison:</strong> Compare readiness across different academic programs</li>
                <li><strong>Career Path Intelligence:</strong> Understand which roles students are most prepared for</li>
                <li><strong>Progress Tracking:</strong> Monitor readiness progression by academic year</li>
                <li><strong>Individual Student Insights:</strong> Drill down into specific student readiness profiles</li>
            </ul>
            <p><strong>Data Updates:</strong> Scores are recalculated regularly to reflect latest skill acquisitions and role requirements.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="model-card">
        <h3>How the Readiness Scoring Model Works</h3>
        <p>The Market Readiness Score is calculated using a <strong>weighted skill matching algorithm</strong>:</p>
        <ol>
            <li><strong>Skill Matching:</strong> For each career role, the system identifies required skills and their importance weights</li>
            <li><strong>Proficiency Assessment:</strong> Student skills are evaluated at four levels:
                <ul>
                    <li>Beginner (25% proficiency)</li>
                    <li>Intermediate (50% proficiency)</li>
                    <li>Advanced (75% proficiency)</li>
                    <li>Expert (100% proficiency)</li>
                </ul>
            </li>
            <li><strong>Weighted Calculation:</strong> The score formula is:
                <br><code>Score = (Σ matched_proficiency × importance_weight) / Σ required_weights × 100</code>
            </li>
            <li><strong>Partial Credit:</strong> Students receive partial credit if their proficiency is lower than required</li>
            <li><strong>Readiness Classification:</strong>
                <ul>
                    <li><strong>Ready (80-100%):</strong> Student is job-ready for this role</li>
                    <li><strong>Developing (50-79%):</strong> Student needs moderate skill development</li>
                    <li><strong>Entry-Level (0-49%):</strong> Student requires significant skill building</li>
                </ul>
            </li>
        </ol>
        <p><strong>Example:</strong> If a role requires Python (weight: 1.0) and SQL (weight: 0.9), and a student has Python at Advanced (75%) and SQL at Intermediate (50%), the score would be: ((0.75 × 1.0) + (0.50 × 0.9)) / (1.0 + 0.9) × 100 = 63.2% (Developing level)</p>
    </div>
    """, unsafe_allow_html=True)

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
                "ML Predictions",
                "Data Explorer"
            ],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("## Pipeline Control")
        
        if st.button("🔄 Run Complete Pipeline", type="primary", use_container_width=True):
            run_complete_pipeline()
    
    # Render header and KPIs
    render_header()
    render_kpi_cards()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Render selected section
    if page == "Overview":
        render_cohort_section()
        st.markdown("<br>", unsafe_allow_html=True)
        render_year_progression()
    elif page == "Cohort Analytics":
        render_cohort_section()
        st.markdown("<br>", unsafe_allow_html=True)
        render_year_progression()
    elif page == "Career Readiness":
        render_career_section()
    elif page == "Skill Gap Analysis":
        render_skill_gap_section()
    elif page == "ML Predictions":
        render_ml_section()
    elif page == "Data Explorer":
        render_data_table()

if __name__ == "__main__":
    main()
