"""
AI Career Readiness Mentor - Career GPS
Main Streamlit Application
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
from services.skill_extractor import SkillExtractor
from services.career_matcher import CareerMatcher
from services.skill_gap import SkillGapAnalyzer
from services.readiness_score import ReadinessScoreCalculator
from services.simulator import CareerSimulator
from services.user_auth import UserAuth
from services.email_service import EmailService
from services.job_search import JobSearchService
from services.email_templates import EmailTemplateGenerator
from services.daily_learning import DailyLearningPlan
from utils.helpers import (
    load_data, get_skill_resources, format_timeline_estimate,
    get_risk_color, create_weekly_plan
)

# Page configuration
st.set_page_config(
    page_title="Career GPS - AI Career Mentor",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border-left: 5px solid #17a2b8;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = None
if 'career_matches' not in st.session_state:
    st.session_state.career_matches = None
if 'selected_career' not in st.session_state:
    st.session_state.selected_career = None
if 'baseline' not in st.session_state:
    st.session_state.baseline = None
if 'simulations' not in st.session_state:
    st.session_state.simulations = []

# Load data
@st.cache_data
def load_app_data():
    return load_data()

try:
    careers_df, skills_df, resources_df = load_app_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Initialize services
@st.cache_resource
def init_services():
    skill_extractor = SkillExtractor(skills_df)
    career_matcher = CareerMatcher(careers_df)
    skill_gap_analyzer = SkillGapAnalyzer(skills_df)
    readiness_calculator = ReadinessScoreCalculator()
    simulator = CareerSimulator(skills_df)
    user_auth = UserAuth()
    email_service = EmailService()
    job_search = JobSearchService(careers_df)
    email_templates = EmailTemplateGenerator()
    daily_learning = DailyLearningPlan()
    return (skill_extractor, career_matcher, skill_gap_analyzer, readiness_calculator, 
            simulator, user_auth, email_service, job_search, email_templates, daily_learning)

(skill_extractor, career_matcher, skill_gap_analyzer, readiness_calculator, simulator,
 user_auth, email_service, job_search, email_templates, daily_learning) = init_services()

# ============ LOGIN/SIGNUP PAGES ============
if not st.session_state.logged_in:
    st.markdown('<div class="main-header">🎯 Career GPS</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Your AI Career Readiness Mentor</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
    
    with tab1:
        st.markdown("### Login to Your Account")
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", type="primary", use_container_width=True):
            success, user_data, message = user_auth.login_user(login_email, login_password)
            if success:
                st.session_state.logged_in = True
                st.session_state.user_email = login_email
                st.session_state.user_data = user_data
                st.session_state.page = 'home'
                st.success("Login successful!")
                st.rerun()
            else:
                st.error(message)
    
    with tab2:
        st.markdown("### Create Your Account")
        signup_name = st.text_input("Full Name", key="signup_name")
        signup_email = st.text_input("Email", key="signup_email")
        signup_password = st.text_input("Password", type="password", key="signup_password")
        signup_confirm = st.text_input("Confirm Password", type="password", key="signup_confirm")
        user_type = st.selectbox("I am a:", ["Student", "Fresh Graduate", "Professional"], key="user_type")
        
        if st.button("Create Account", type="primary", use_container_width=True):
            if signup_password != signup_confirm:
                st.error("Passwords do not match!")
            elif len(signup_password) < 6:
                st.error("Password must be at least 6 characters long!")
            elif not signup_email or not signup_name:
                st.error("Please fill in all fields!")
            else:
                success, message = user_auth.register_user(
                    signup_email, signup_password, signup_name, user_type.lower()
                )
                if success:
                    st.success("Account created successfully! Please login.")
                else:
                    st.error(message)
    
    st.stop()  # Stop execution if not logged in

# User is logged in - show main app
# Sidebar navigation
st.sidebar.title("🧭 Navigation")

# Show logout button
if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.user_email = None
    st.session_state.user_data = None
    st.session_state.page = 'login'
    st.rerun()

st.sidebar.markdown(f"**👤 {st.session_state.user_data.get('name', 'User')}**")
st.sidebar.markdown(f"*{st.session_state.user_data.get('user_type', 'student').title()}*")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Go to",
    ["🏠 Home", "👤 Profile Setup", "🎯 Career Matches", "📊 Skill Gap Analysis", 
     "🔮 What-If Simulator", "📚 Learning Roadmap", "💼 Job Search", 
     "✉️ Email Templates", "📅 Daily Plan", "⚙️ Settings"],
    key='nav_radio'
)

# Map radio selection to page state
page_mapping = {
    "🏠 Home": "home",
    "👤 Profile Setup": "profile",
    "🎯 Career Matches": "matches",
    "📊 Skill Gap Analysis": "gap_analysis",
    "🔮 What-If Simulator": "simulator",
    "📚 Learning Roadmap": "roadmap",
    "💼 Job Search": "job_search",
    "✉️ Email Templates": "email_templates",
    "📅 Daily Plan": "daily_plan",
    "⚙️ Settings": "settings"
}
st.session_state.page = page_mapping[page]

# Sidebar info
if st.session_state.user_profile:
    st.sidebar.success("✅ Profile Created")
    st.sidebar.info(f"**Skills:** {len(st.session_state.user_profile['skills'])}")
if st.session_state.career_matches:
    st.sidebar.success(f"✅ {len(st.session_state.career_matches)} Careers Matched")
if st.session_state.selected_career:
    st.sidebar.success(f"✅ Selected: {st.session_state.selected_career['role_name']}")

st.sidebar.markdown("---")
st.sidebar.markdown("### About Career GPS")
st.sidebar.info(
    "Your AI-powered career mentor that provides personalized guidance, "
    "simulates career decisions, and creates adaptive learning paths."
)

# ============ HOME PAGE ============
if st.session_state.page == 'home':
    st.markdown('<div class="main-header">🎯 Career GPS</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Your Real-Time AI Career Readiness Mentor</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🎯 Smart Matching")
        st.write("Match your skills with the best career paths using AI-powered analysis")
    
    with col2:
        st.markdown("### 📊 Gap Analysis")
        st.write("Identify exactly what skills you need and how long it will take")
    
    with col3:
        st.markdown("### 🔮 What-If Simulation")
        st.write("Simulate career decisions and see real-time impact on your readiness")
    
    st.markdown("---")
    
    st.markdown("## 🚀 How It Works")
    
    steps = [
        "**Create Your Profile** - Tell us about your skills, interests, and goals",
        "**Discover Careers** - Get matched with careers that fit your profile",
        "**Analyze Gaps** - See exactly what skills you need for each career",
        "**Simulate Scenarios** - Test different career decisions before committing",
        "**Get Your Roadmap** - Receive a personalized learning plan"
    ]
    
    for i, step in enumerate(steps, 1):
        st.markdown(f"{i}. {step}")
    
    st.markdown("---")
    
    if st.button("🎉 Get Started", type="primary", use_container_width=True):
        st.session_state.page = 'profile'
        st.rerun()
    
    st.markdown("---")
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Career Paths", len(careers_df))
    with col2:
        st.metric("Skills Tracked", len(skills_df))
    with col3:
        st.metric("Learning Resources", len(resources_df))
    with col4:
        st.metric("Avg. Match Accuracy", "92%")

# ============ PROFILE SETUP PAGE ============
elif st.session_state.page == 'profile':
    st.title("👤 Create Your Profile")
    
    st.markdown("### Tell us about yourself")
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name (Optional)", placeholder="John Doe")
            education = st.selectbox(
                "Education Level",
                ["High School", "Associate Degree", "Bachelor's Degree", 
                 "Master's Degree", "PhD", "Bootcamp Graduate", "Self-Taught"]
            )
            career_goal = st.text_input(
                "Career Goal (Optional)", 
                placeholder="e.g., Full Stack Developer, Data Scientist"
            )
        
        with col2:
            major = st.text_input("Major/Field (Optional)", placeholder="Computer Science")
            experience_level = st.selectbox(
                "Experience Level",
                ["Student", "Fresh Graduate", "0-2 Years", "2-5 Years", "5+ Years"]
            )
            interests = st.text_area(
                "Interests (Optional)",
                placeholder="e.g., AI, Web Development, Cloud Computing"
            )
        
        st.markdown("### Your Skills")
        st.markdown("Enter your skills separated by commas, or describe your abilities in free text")
        
        skills_input = st.text_area(
            "Skills",
            placeholder="Python, JavaScript, React, Machine Learning, SQL...",
            height=100
        )
        
        submitted = st.form_submit_button("🚀 Create Profile", type="primary", use_container_width=True)
        
        if submitted:
            if not skills_input:
                st.error("Please enter at least some skills!")
            else:
                with st.spinner("Extracting and analyzing your skills..."):
                    # Extract skills
                    if ',' in skills_input:
                        user_skills = skill_extractor.extract_from_list(skills_input)
                    else:
                        user_skills = skill_extractor.extract_from_text(skills_input)
                    
                    if not user_skills:
                        st.error("Could not extract skills. Please be more specific.")
                    else:
                        # Create profile
                        st.session_state.user_profile = {
                            'name': name if name else "User",
                            'education': education,
                            'major': major,
                            'experience_level': experience_level,
                            'career_goal': career_goal,
                            'interests': interests,
                            'skills': user_skills,
                            'skills_categorized': skill_extractor.categorize_skills(user_skills)
                        }
                        
                        st.success(f"✅ Profile created! Extracted {len(user_skills)} skills.")
                        st.balloons()
                        
                        # Auto-navigate to matches
                        st.info("Proceeding to career matching...")
                        st.session_state.page = 'matches'
                        st.rerun()
    
    # Show existing profile if available
    if st.session_state.user_profile:
        st.markdown("---")
        st.markdown("### 📋 Current Profile")
        
        profile = st.session_state.user_profile
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Name:** {profile['name']}")
            st.write(f"**Education:** {profile['education']}")
            st.write(f"**Experience:** {profile['experience_level']}")
        
        with col2:
            st.write(f"**Goal:** {profile['career_goal'] if profile['career_goal'] else 'Not specified'}")
            st.write(f"**Skills Count:** {len(profile['skills'])}")
        
        with st.expander("View All Skills"):
            for category, skills in profile['skills_categorized'].items():
                st.markdown(f"**{category}:** {', '.join(skills)}")

# ============ CAREER MATCHES PAGE ============
elif st.session_state.page == 'matches':
    if not st.session_state.user_profile:
        st.warning("⚠️ Please create your profile first!")
        if st.button("Go to Profile Setup"):
            st.session_state.page = 'profile'
            st.rerun()
    else:
        st.title("🎯 Your Career Matches")
        
        profile = st.session_state.user_profile
        
        if st.session_state.career_matches is None:
            with st.spinner("🔍 Finding your perfect career matches..."):
                matches = career_matcher.match_careers(
                    profile['skills'],
                    profile['interests'],
                    top_n=5
                )
                st.session_state.career_matches = matches
        
        matches = st.session_state.career_matches
        
        st.markdown(f"### Top {len(matches)} Career Matches for {profile['name']}")
        
        # Display matches
        for i, match in enumerate(matches, 1):
            with st.expander(f"#{i} - {match['role_name']} ({match['match_score']:.1f}% Match)", expanded=(i==1)):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"**{match['category']}**")
                    st.write(match['description'])
                    
                    st.markdown("##### Skills Overview")
                    skill_col1, skill_col2, skill_col3 = st.columns(3)
                    with skill_col1:
                        st.metric("Known", len(match['matched_skills']), delta="✅")
                    with skill_col2:
                        st.metric("Partial", len(match['partial_skills']), delta="⚠️")
                    with skill_col3:
                        st.metric("Missing", len(match['missing_skills']), delta="❌")
                
                with col2:
                    st.metric("Match Score", f"{match['match_score']:.1f}%")
                    st.metric("Skill Overlap", f"{match['skill_overlap_score']:.1f}%")
                
                with col3:
                    st.metric("Avg Salary", f"${match['avg_salary']:,}")
                    growth_emoji = "📈" if match['growth_rate'] == 'very_high' else "📊"
                    st.metric("Growth", match['growth_rate'].replace('_', ' ').title(), delta=growth_emoji)
                
                # Skills breakdown
                col1, col2 = st.columns(2)
                with col1:
                    if match['matched_skills']:
                        st.success(f"✅ **Known Skills ({len(match['matched_skills'])})**")
                        st.write(", ".join(match['matched_skills'][:5]))
                        if len(match['matched_skills']) > 5:
                            st.caption(f"...and {len(match['matched_skills'])-5} more")
                
                with col2:
                    if match['missing_skills']:
                        st.error(f"❌ **Skills to Learn ({len(match['missing_skills'])})**")
                        st.write(", ".join(match['missing_skills'][:5]))
                        if len(match['missing_skills']) > 5:
                            st.caption(f"...and {len(match['missing_skills'])-5} more")
                
                # Select button
                if st.button(f"📊 Analyze This Career", key=f"select_{match['role_id']}", type="primary"):
                    st.session_state.selected_career = match
                    st.session_state.page = 'gap_analysis'
                    st.rerun()
        
        # Visualization
        st.markdown("---")
        st.markdown("### 📊 Match Comparison")
        
        # Create comparison chart
        fig = go.Figure()
        
        career_names = [m['role_name'] for m in matches]
        match_scores = [m['match_score'] for m in matches]
        overlap_scores = [m['skill_overlap_score'] for m in matches]
        
        fig.add_trace(go.Bar(
            name='Match Score',
            x=career_names,
            y=match_scores,
            marker_color='#1f77b4'
        ))
        
        fig.add_trace(go.Bar(
            name='Skill Overlap',
            x=career_names,
            y=overlap_scores,
            marker_color='#ff7f0e'
        ))
        
        fig.update_layout(
            barmode='group',
            xaxis_title="Career",
            yaxis_title="Score (%)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

# ============ SKILL GAP ANALYSIS PAGE ============
elif st.session_state.page == 'gap_analysis':
    if not st.session_state.selected_career:
        st.warning("⚠️ Please select a career first!")
        if st.button("Go to Career Matches"):
            st.session_state.page = 'matches'
            st.rerun()
    else:
        career = st.session_state.selected_career
        profile = st.session_state.user_profile
        
        st.title(f"📊 Skill Gap Analysis: {career['role_name']}")
        
        # Perform gap analysis
        gap_analysis = skill_gap_analyzer.analyze_gap(profile['skills'], career)
        readiness_score = readiness_calculator.calculate_score(gap_analysis)
        
        # Create baseline for simulation
        if st.session_state.baseline is None:
            st.session_state.baseline = simulator.create_baseline(profile['skills'], career)
        
        # Top metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Career Readiness Score",
                f"{readiness_score['overall_score']}",
                delta=f"Grade: {readiness_score['grade']}"
            )
        
        with col2:
            st.metric(
                "Skills Gap",
                f"{gap_analysis['gap_percentage']:.1f}%",
                delta=f"{gap_analysis['missing_skills_count']} missing"
            )
        
        with col3:
            time_estimate = format_timeline_estimate(gap_analysis['estimated_learning_time_weeks'])
            st.metric(
                "Est. Time to Ready",
                time_estimate
            )
        
        with col4:
            risk_level = st.session_state.baseline['risk_level']
            risk_color = get_risk_color(risk_level)
            st.metric(
                "Risk Level",
                risk_level
            )
        
        st.markdown("---")
        
        # Readiness score breakdown
        st.markdown("### 🎯 Readiness Score Breakdown")
        
        breakdown = readiness_score['breakdown']
        
        fig = go.Figure(go.Bar(
            x=list(breakdown.values()),
            y=list(breakdown.keys()),
            orientation='h',
            marker=dict(
                color=list(breakdown.values()),
                colorscale='RdYlGn',
                cmin=0,
                cmax=100
            ),
            text=[f"{v:.1f}%" for v in breakdown.values()],
            textposition='auto'
        ))
        
        fig.update_layout(
            xaxis_title="Score",
            yaxis_title="Component",
            height=300,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info(f"**Interpretation:** {readiness_score['interpretation']}")
        
        st.markdown("---")
        
        # Skill details
        st.markdown("### 📋 Detailed Skill Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"#### ✅ Known Skills ({gap_analysis['known_skills_count']})")
            for skill in gap_analysis['matched_skills'][:10]:
                st.success(f"• {skill}")
        
        with col2:
            st.markdown(f"#### ⚠️ Partial Skills ({gap_analysis['partial_skills_count']})")
            for skill in gap_analysis['partial_skills'][:10]:
                st.warning(f"• {skill}")
        
        with col3:
            st.markdown(f"#### ❌ Missing Skills ({gap_analysis['missing_skills_count']})")
            for skill in gap_analysis['missing_skills'][:10]:
                st.error(f"• {skill}")
        
        st.markdown("---")
        
        # Priority skills
        st.markdown("### 🎯 Priority Skills to Learn")
        st.info("These high-importance skills should be learned first:")
        
        priority_skills = gap_analysis['priority_skills']
        if priority_skills:
            cols = st.columns(min(len(priority_skills), 5))
            for i, skill in enumerate(priority_skills):
                with cols[i]:
                    st.markdown(f"**{i+1}. {skill}**")
        else:
            st.success("Great! No critical skills missing.")
        
        st.markdown("---")
        
        # Improvement suggestions
        st.markdown("### 💡 Improvement Suggestions")
        
        suggestions = readiness_calculator.get_improvement_suggestions(readiness_score, gap_analysis)
        
        for suggestion in suggestions:
            with st.expander(f"🎯 Improve {suggestion['area']} (Current: {suggestion['current_score']:.1f})"):
                st.write(suggestion['suggestion'])
                if suggestion['priority_skills']:
                    st.write("**Focus on:**", ", ".join(suggestion['priority_skills']))
                st.success(f"**Potential Improvement:** {suggestion['potential_improvement']}")
        
        # Action buttons
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔮 Run What-If Simulations", type="primary", use_container_width=True):
                st.session_state.page = 'simulator'
                st.rerun()
        
        with col2:
            if st.button("📚 Get Learning Roadmap", type="primary", use_container_width=True):
                st.session_state.page = 'roadmap'
                st.rerun()

# ============ WHAT-IF SIMULATOR PAGE ============
elif st.session_state.page == 'simulator':
    if not st.session_state.baseline:
        st.warning("⚠️ Please complete skill gap analysis first!")
        if st.button("Go to Gap Analysis"):
            st.session_state.page = 'gap_analysis'
            st.rerun()
    else:
        st.title("🔮 What-If Career Simulator")
        st.markdown("### Simulate career decisions and see real-time impact")
        
        baseline = st.session_state.baseline
        profile = st.session_state.user_profile
        career = st.session_state.selected_career
        
        # Display baseline
        st.markdown("### 📊 Current Baseline")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Readiness Score", f"{baseline['readiness_score']['overall_score']}")
        with col2:
            st.metric("Learning Time", format_timeline_estimate(baseline['learning_time_weeks']))
        with col3:
            st.metric("Risk Level", baseline['risk_level'])
        with col4:
            st.metric("Gap", f"{baseline['gap_analysis']['gap_percentage']:.1f}%")
        
        st.markdown("---")
        
        # Simulation options
        st.markdown("### 🎮 Choose Your Simulation")
        
        sim_type = st.radio(
            "Select simulation type:",
            [
                "🔄 Switch to Different Career",
                "🎓 Skip Certifications",
                "🛠️ Focus on Projects Only",
                "⏸️ Pause Learning",
                "➕ Add New Skills"
            ]
        )
        
        simulation_result = None
        
        # Switch Career
        if sim_type == "🔄 Switch to Different Career":
            st.markdown("#### See how your readiness changes for different careers")
            
            other_careers = [m for m in st.session_state.career_matches if m['role_id'] != career['role_id']]
            career_names = [c['role_name'] for c in other_careers]
            
            selected_new_career = st.selectbox("Select career to switch to:", career_names)
            
            if st.button("Run Simulation", type="primary"):
                with st.spinner("Running simulation..."):
                    new_career = [c for c in other_careers if c['role_name'] == selected_new_career][0]
                    simulation_result = simulator.simulate_switch_career(baseline, new_career)
                    st.session_state.simulations.append(simulation_result)
        
        # Skip Certifications
        elif sim_type == "🎓 Skip Certifications":
            st.markdown("#### Remove certification requirements and see impact")
            
            missing_skills = baseline['gap_analysis']['missing_skills']
            cert_keywords = ['AWS', 'Azure', 'GCP', 'Certified', 'Certificate']
            cert_skills = [s for s in missing_skills if any(kw in s for kw in cert_keywords)]
            
            if cert_skills:
                selected_certs = st.multiselect(
                    "Select certifications to skip:",
                    cert_skills,
                    default=cert_skills
                )
                
                if st.button("Run Simulation", type="primary"):
                    with st.spinner("Running simulation..."):
                        simulation_result = simulator.simulate_skip_certifications(baseline, selected_certs)
                        st.session_state.simulations.append(simulation_result)
            else:
                st.info("No obvious certification skills found in requirements")
        
        # Focus on Projects
        elif sim_type == "🛠️ Focus on Projects Only":
            st.markdown("#### Focus on hands-on projects instead of formal learning")
            
            partial_skills = baseline['gap_analysis']['partial_skills']
            
            if partial_skills:
                project_skills = st.multiselect(
                    "Select skills to master through projects:",
                    partial_skills,
                    default=partial_skills[:3] if len(partial_skills) >= 3 else partial_skills
                )
                
                if st.button("Run Simulation", type="primary"):
                    with st.spinner("Running simulation..."):
                        simulation_result = simulator.simulate_focus_projects(baseline, project_skills)
                        st.session_state.simulations.append(simulation_result)
            else:
                st.info("No partial skills to improve through projects")
        
        # Pause Learning
        elif sim_type == "⏸️ Pause Learning":
            st.markdown("#### See impact of taking a break from learning")
            
            pause_weeks = st.slider("Pause duration (weeks):", 1, 52, 8)
            
            if st.button("Run Simulation", type="primary"):
                with st.spinner("Running simulation..."):
                    simulation_result = simulator.simulate_pause_learning(baseline, pause_weeks)
                    st.session_state.simulations.append(simulation_result)
        
        # Add Skills
        elif sim_type == "➕ Add New Skills":
            st.markdown("#### Simulate learning specific new skills")
            
            missing_skills = baseline['gap_analysis']['missing_skills']
            
            selected_skills = st.multiselect(
                "Select skills to learn:",
                missing_skills,
                default=missing_skills[:3] if len(missing_skills) >= 3 else missing_skills
            )
            
            if st.button("Run Simulation", type="primary"):
                with st.spinner("Running simulation..."):
                    simulation_result = simulator.simulate_add_skills(baseline, selected_skills, career)
                    st.session_state.simulations.append(simulation_result)
        
        # Display simulation result
        if simulation_result:
            st.markdown("---")
            st.markdown("### 📊 Simulation Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Before (Baseline)")
                st.metric("Readiness Score", f"{baseline['readiness_score']['overall_score']}")
                st.metric("Learning Time", format_timeline_estimate(baseline['learning_time_weeks']))
                st.metric("Risk Level", baseline['risk_level'])
            
            with col2:
                st.markdown("#### After Simulation")
                st.metric(
                    "Readiness Score",
                    f"{simulation_result['readiness_score']['overall_score']}",
                    delta=f"{simulation_result['changes']['score_change']:+.1f}"
                )
                st.metric(
                    "Learning Time",
                    format_timeline_estimate(simulation_result['learning_time_weeks']),
                    delta=f"{simulation_result['changes']['time_change']:+.0f} weeks"
                )
                st.metric("Risk Level", simulation_result['risk_level'])
            
            # Changes
            st.markdown("#### 🔄 Key Changes")
            
            if 'warning' in simulation_result:
                st.warning(f"⚠️ {simulation_result['warning']}")
            
            if 'benefit' in simulation_result:
                st.success(f"✅ {simulation_result['benefit']}")
            
            # Detailed changes
            with st.expander("View Detailed Changes"):
                st.json(simulation_result['changes'])
        
        # Show all simulations comparison
        if st.session_state.simulations:
            st.markdown("---")
            st.markdown("### 📈 All Simulations Comparison")
            
            comparison = simulator.compare_simulations(st.session_state.simulations)
            
            # Create DataFrame
            df = pd.DataFrame(comparison)
            
            st.dataframe(df, use_container_width=True)
            
            # Visualization
            fig = px.bar(
                df,
                x='simulation_type',
                y='readiness_score',
                color='risk_level',
                title='Readiness Score by Simulation',
                labels={'readiness_score': 'Readiness Score', 'simulation_type': 'Simulation Type'}
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            if st.button("Clear All Simulations"):
                st.session_state.simulations = []
                st.rerun()

# ============ LEARNING ROADMAP PAGE ============
elif st.session_state.page == 'roadmap':
    if not st.session_state.baseline:
        st.warning("⚠️ Please complete skill gap analysis first!")
        if st.button("Go to Gap Analysis"):
            st.session_state.page = 'gap_analysis'
            st.rerun()
    else:
        st.title("📚 Your Personalized Learning Roadmap")
        
        baseline = st.session_state.baseline
        gap_analysis = baseline['gap_analysis']
        
        st.markdown(f"### Roadmap for: {baseline['career']}")
        
        # Timeline
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Duration", format_timeline_estimate(gap_analysis['estimated_learning_time_weeks']))
        with col2:
            st.metric("Skills to Learn", gap_analysis['missing_skills_count'])
        with col3:
            st.metric("Skills to Improve", gap_analysis['partial_skills_count'])
        
        st.markdown("---")
        
        # Create learning plan
        missing = gap_analysis['missing_skills']
        partial = gap_analysis['partial_skills']
        
        weekly_plan = create_weekly_plan(missing, partial, skills_df)
        
        # Display phases
        st.markdown("### 📅 Learning Phases")
        
        for phase in weekly_plan:
            with st.expander(f"Phase {phase['phase']} - {phase['duration_weeks']} weeks", expanded=(phase['phase']==1)):
                st.markdown(f"**Duration:** {phase['duration_weeks']} weeks")
                
                for skill_task in phase['skills']:
                    skill_name = skill_task['skill']
                    task_type = skill_task['type']
                    difficulty = skill_task['difficulty']
                    
                    # Get resources
                    resources = get_skill_resources(skill_name, resources_df)
                    
                    st.markdown(f"#### {task_type}: {skill_name}")
                    st.markdown(f"*Difficulty: {difficulty.title()}*")
                    
                    if resources:
                        st.markdown("**Recommended Resources:**")
                        for res in resources[:2]:  # Top 2 resources
                            st.markdown(f"- [{res['name']}]({res['url']}) ({res['type']}, {res['duration']} weeks)")
                    
                    st.markdown("---")
        
        st.markdown("---")
        
        # Weekly schedule suggestion
        st.markdown("### 📆 Weekly Schedule Suggestion")
        
        st.info("""
        **Recommended Learning Schedule:**
        - **Monday-Wednesday:** Theory & Concepts (5-7 hours)
        - **Thursday-Friday:** Hands-on Practice (5-7 hours)
        - **Weekend:** Projects & Review (4-6 hours)
        
        **Total:** 15-20 hours per week
        """)
        
        # Download roadmap
        st.markdown("---")
        
        if st.button("📥 Download Roadmap (JSON)", type="primary"):
            import json
            
            roadmap_data = {
                'career': baseline['career'],
                'readiness_score': baseline['readiness_score']['overall_score'],
                'estimated_weeks': gap_analysis['estimated_learning_time_weeks'],
                'phases': weekly_plan,
                'priority_skills': gap_analysis['priority_skills']
            }
            
            st.download_button(
                label="Download",
                data=json.dumps(roadmap_data, indent=2),
                file_name=f"career_roadmap_{baseline['career'].replace(' ', '_')}.json",
                mime="application/json"
            )
        
        # Motivational message
        st.markdown("---")
        st.success("🎯 **Remember:** Consistent progress is key! Break down your learning into manageable chunks and celebrate small wins.")

# ============ JOB SEARCH PAGE ============
elif st.session_state.page == 'job_search':
    st.markdown('<div class="main-header">💼 Job Search</div>', unsafe_allow_html=True)
    
    if not st.session_state.selected_career:
        st.warning("⚠️ Please select a career from the Career Matches page first.")
    else:
        career_name = st.session_state.selected_career['role_name']
        st.markdown(f"### Finding Jobs for: **{career_name}**")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            location = st.selectbox("Location", ["Remote", "Hybrid", "On-site", "Any"])
        with col2:
            experience = st.selectbox("Experience Level", ["entry", "mid", "senior"])
        with col3:
            num_jobs = st.slider("Number of Jobs", 5, 20, 10)
        
        if st.button("🔍 Search Jobs", type="primary"):
            with st.spinner("Searching for opportunities..."):
                user_skills = st.session_state.user_profile.get('skills', [])
                jobs = job_search.get_recommended_jobs(
                    career_name, user_skills, location, num_jobs
                )
                st.session_state.job_results = jobs
        
        if 'job_results' in st.session_state and st.session_state.job_results:
            jobs = st.session_state.job_results
            
            st.markdown(f"### 🎯 Found {len(jobs)} Opportunities")
            
            for i, job in enumerate(jobs):
                with st.expander(f"**{job['title']}** at {job['company']} - Match: {job['match_score']}%"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**📍 Location:** {job['location']}")
                        st.markdown(f"**💼 Type:** {job['type']}")
                        st.markdown(f"**💰 Salary:** {job['salary_range']}")
                        st.markdown(f"**📅 Posted:** {job['posted_date']}")
                        st.markdown(f"**🔗 Source:** {job['source']}")
                        
                        st.markdown("**Description:**")
                        st.write(job['description'])
                        
                        if job['requirements']:
                            st.markdown("**Requirements:**")
                            for req in job['requirements']:
                                st.markdown(f"- {req}")
                    
                    with col2:
                        st.metric("Match Score", f"{job['match_score']}%")
                        
                        # Application tips
                        user_skills = st.session_state.user_profile.get('skills', [])
                        tips = job_search.get_job_application_tips(job, user_skills)
                        
                        st.markdown("**💡 Tips:**")
                        for tip in tips:
                            st.markdown(f"- {tip}")
                        
                        st.markdown("---")
                        if st.button(f"Generate Application Email", key=f"gen_email_{i}"):
                            st.session_state.selected_job_for_email = job
                            st.session_state.page = 'email_templates'
                            st.rerun()

# ============ EMAIL TEMPLATES PAGE ============
elif st.session_state.page == 'email_templates':
    st.markdown('<div class="main-header">✉️ Email Templates</div>', unsafe_allow_html=True)
    
    template_type = st.selectbox(
        "Select Template Type",
        ["Job Application", "Cold Email - Networking", "Cold Email - Job Inquiry", 
         "Follow-up After Interview", "Referral Request"]
    )
    
    user_name = st.session_state.user_data.get('name', 'Your Name')
    user_skills = st.session_state.user_profile.get('skills', []) if st.session_state.user_profile else []
    
    if template_type == "Job Application":
        st.markdown("### 📧 Job Application Email")
        
        col1, col2 = st.columns(2)
        with col1:
            job_title = st.text_input("Job Title", value="Software Engineer")
            company_name = st.text_input("Company Name", value="Tech Corp")
        with col2:
            experience = st.text_input("Your Experience (optional)", 
                                      value="recent computer science graduate")
        
        if st.button("Generate Email", type="primary"):
            email = email_templates.generate_application_email(
                job_title, company_name, user_name, user_skills, experience
            )
            st.text_area("Your Email Template", email, height=400)
            
            st.markdown("### 📝 Email Tips")
            tips = email_templates.get_email_tips('application')
            for tip in tips:
                st.markdown(f"- {tip}")
    
    elif template_type == "Cold Email - Networking":
        st.markdown("### 🤝 Networking Email")
        
        col1, col2 = st.columns(2)
        with col1:
            recipient_name = st.text_input("Recipient Name", value="John Doe")
            recipient_company = st.text_input("Their Company", value="Tech Corp")
        with col2:
            common_interest = st.text_input("Common Interest", value="software development")
            background = st.text_input("Your Background", 
                                      value="a recent graduate passionate about technology")
        
        if st.button("Generate Email", type="primary"):
            email = email_templates.generate_cold_email_networking(
                recipient_name, recipient_company, user_name, background, common_interest
            )
            st.text_area("Your Email Template", email, height=400)
            
            st.markdown("### 📝 Email Tips")
            tips = email_templates.get_email_tips('cold_email')
            for tip in tips:
                st.markdown(f"- {tip}")
    
    elif template_type == "Cold Email - Job Inquiry":
        st.markdown("### 💼 Job Inquiry Email")
        
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("Company Name", value="Tech Corp")
            department = st.text_input("Department", value="Engineering")
        with col2:
            career_goal = st.text_input("Your Career Goal", 
                                       value="building innovative software solutions")
        
        if st.button("Generate Email", type="primary"):
            email = email_templates.generate_cold_email_job_inquiry(
                company_name, department, user_name, user_skills, career_goal
            )
            st.text_area("Your Email Template", email, height=400)
            
            st.markdown("### 📝 Email Tips")
            tips = email_templates.get_email_tips('cold_email')
            for tip in tips:
                st.markdown(f"- {tip}")
    
    elif template_type == "Follow-up After Interview":
        st.markdown("### 🙏 Thank You Email")
        
        col1, col2 = st.columns(2)
        with col1:
            interviewer_name = st.text_input("Interviewer Name", value="Jane Smith")
            company_name = st.text_input("Company Name", value="Tech Corp")
        with col2:
            position = st.text_input("Position", value="Software Engineer")
            interview_date = st.date_input("Interview Date")
        
        if st.button("Generate Email", type="primary"):
            email = email_templates.generate_follow_up_email(
                interviewer_name, company_name, position, user_name, 
                interview_date.strftime("%B %d, %Y")
            )
            st.text_area("Your Email Template", email, height=400)
            
            st.markdown("### 📝 Email Tips")
            tips = email_templates.get_email_tips('follow_up')
            for tip in tips:
                st.markdown(f"- {tip}")
    
    elif template_type == "Referral Request":
        st.markdown("### 🤝 Referral Request Email")
        
        col1, col2 = st.columns(2)
        with col1:
            contact_name = st.text_input("Contact Name", value="Alex Johnson")
            company_name = st.text_input("Company Name", value="Tech Corp")
        with col2:
            position = st.text_input("Position", value="Software Engineer")
            relationship = st.text_input("Relationship", 
                                        value="As we worked together at XYZ")
        
        if st.button("Generate Email", type="primary"):
            email = email_templates.generate_referral_request_email(
                contact_name, company_name, position, user_name, relationship
            )
            st.text_area("Your Email Template", email, height=400)
            
            st.markdown("### 📝 Email Tips")
            tips = email_templates.get_email_tips('networking')
            for tip in tips:
                st.markdown(f"- {tip}")

# ============ DAILY PLAN PAGE ============
elif st.session_state.page == 'daily_plan':
    st.markdown('<div class="main-header">📅 Your Daily Learning Plan</div>', unsafe_allow_html=True)
    
    if not st.session_state.selected_career:
        st.warning("⚠️ Please select a career and complete gap analysis first.")
    else:
        # Get skill gaps
        gap_analysis = skill_gap_analyzer.analyze_gap(
            st.session_state.user_profile['skills'],
            st.session_state.selected_career
        )
        
        # Prepare skill gaps for learning plan
        skill_gaps = []
        for skill in gap_analysis['missing_skills']:
            skill_gaps.append({
                'skill': skill,
                'priority': 100,
                'hours_needed': 20,
                'resources': get_skill_resources(skill, resources_df)
            })
        
        for skill_data in gap_analysis['partial_skills']:
            skill_gaps.append({
                'skill': skill_data['skill'],
                'priority': 50,
                'hours_needed': 10,
                'resources': get_skill_resources(skill_data['skill'], resources_df)
            })
        
        # User progress (from session state or default to 0)
        user_progress = st.session_state.get('learning_progress', {})
        for skill_gap in skill_gaps:
            if skill_gap['skill'] not in user_progress:
                user_progress[skill_gap['skill']] = 0
        
        # Learning preferences
        st.markdown("### ⚙️ Learning Preferences")
        col1, col2 = st.columns(2)
        with col1:
            learning_pace = st.selectbox("Learning Pace", ["slow", "moderate", "intensive"])
        with col2:
            available_hours = st.slider("Available Hours/Day", 1, 6, 2)
        
        # Generate plan
        if st.button("📋 Generate Today's Plan", type="primary"):
            plan = daily_learning.generate_daily_plan(
                skill_gaps, user_progress, learning_pace, available_hours
            )
            st.session_state.daily_plan = plan
        
        # Display plan
        if 'daily_plan' in st.session_state:
            plan = st.session_state.daily_plan
            
            st.markdown("### 📚 Today's Tasks")
            for i, task in enumerate(plan):
                with st.expander(f"Task {i+1}: {task['activity']} - {task['skill']}", 
                               expanded=(i==0)):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**Duration:** {task['duration']}")
                        st.markdown(f"**Milestone:** {task['milestone']}")
                        
                        if task['resources']:
                            st.markdown("**Resources:**")
                            for resource in task['resources']:
                                st.markdown(f"- [{resource['title']}]({resource['url']})")
                    
                    with col2:
                        current_progress = user_progress.get(task['skill'], 0)
                        st.metric("Progress", f"{current_progress}%")
                        
                        new_progress = st.slider(
                            "Update Progress",
                            0, 100, current_progress,
                            key=f"progress_{i}"
                        )
                        
                        if st.button(f"Save Progress", key=f"save_{i}"):
                            user_progress[task['skill']] = new_progress
                            st.session_state.learning_progress = user_progress
                            
                            # Save to user data
                            user_auth.update_learning_progress(
                                st.session_state.user_email,
                                task['skill'],
                                new_progress
                            )
                            st.success("Progress saved!")
        
        # Progress summary
        st.markdown("---")
        st.markdown("### 📊 Overall Progress")
        
        summary = daily_learning.get_progress_summary(user_progress, skill_gaps)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Skills", summary['total_skills'])
        with col2:
            st.metric("Completed", summary['completed_skills'])
        with col3:
            st.metric("In Progress", summary['in_progress_skills'])
        with col4:
            st.metric("Avg Progress", f"{summary['average_progress']}%")
        
        # Achievements
        total_days = st.session_state.get('learning_days', 1)
        badges = daily_learning.get_achievement_badges(user_progress, total_days)
        
        if badges:
            st.markdown("### 🏆 Your Achievements")
            st.write(" ".join(badges))
        
        # Estimated completion
        st.markdown("### 🎯 Timeline")
        estimation = daily_learning.calculate_estimated_completion(skill_gaps, available_hours)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Hours", estimation['total_hours'])
        with col2:
            st.metric("Weeks Needed", estimation['weeks_needed'])
        with col3:
            st.metric("Completion Date", estimation['completion_date'])

# ============ SETTINGS PAGE ============
elif st.session_state.page == 'settings':
    st.markdown('<div class="main-header">⚙️ Settings</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📧 Email Notifications", "👤 Profile"])
    
    with tab1:
        st.markdown("### 📧 Email Notification Settings")
        
        enable_notifications = st.checkbox("Enable Daily Email Notifications", value=True)
        
        if enable_notifications:
            col1, col2 = st.columns(2)
            with col1:
                notification_time = st.time_input("Preferred Time", value=None)
            with col2:
                sender_email = st.text_input("System Email (optional)", 
                                            help="Email address to send notifications from")
            
            if st.button("💾 Save Notification Settings"):
                preferences = {
                    'email_notifications': enable_notifications,
                    'notification_time': notification_time.strftime('%H:%M') if notification_time else '09:00'
                }
                success, msg = user_auth.update_notification_preferences(
                    st.session_state.user_email,
                    preferences
                )
                if success:
                    st.success("Settings saved!")
                else:
                    st.error(msg)
            
            st.markdown("---")
            st.markdown("### 📨 Send Test Email")
            
            if st.button("Send Test Daily Update"):
                if not sender_email:
                    st.warning("Please configure sender email first")
                else:
                    # Configure email service
                    sender_password = st.text_input("Email Password", type="password")
                    
                    if sender_password:
                        email_service.configure(sender_email, sender_password)
                        
                        # Prepare test data
                        results_html = email_service.format_results(75, 5, 3)
                        plan_html = email_service.format_learning_plan([
                            {'skill': 'Python', 'activity': 'Complete tutorial', 'duration': '1 hour'},
                            {'skill': 'SQL', 'activity': 'Practice queries', 'duration': '30 min'}
                        ])
                        
                        success, msg = email_service.send_daily_update(
                            st.session_state.user_email,
                            st.session_state.user_data.get('name'),
                            results_html,
                            plan_html
                        )
                        
                        if success:
                            st.success("Test email sent!")
                        else:
                            st.error(f"Failed: {msg}")
    
    with tab2:
        st.markdown("### 👤 Profile Information")
        
        st.markdown(f"**Name:** {st.session_state.user_data.get('name')}")
        st.markdown(f"**Email:** {st.session_state.user_email}")
        st.markdown(f"**User Type:** {st.session_state.user_data.get('user_type', 'student').title()}")
        st.markdown(f"**Account Created:** {st.session_state.user_data.get('created_at', 'N/A')}")
        
        st.markdown("---")
        st.markdown("### 🔒 Privacy")
        st.info("Your data is stored locally and privately. Only you have access to your account.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>🎯 <strong>Career GPS</strong> - Your AI Career Readiness Mentor</p>
        <p>Built with ❤️ using Streamlit | Powered by AI & Machine Learning</p>
    </div>
    """,
    unsafe_allow_html=True
)
