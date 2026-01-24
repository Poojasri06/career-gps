"""
Career GPS™ — AI Career Readiness Mentor
Rewritten Streamlit experience aligned with product narrative
"""
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import os
import sys

from services.career_matcher import CareerMatcher
from services.daily_learning import DailyLearningPlan
from services.email_service import EmailService
from services.email_templates import EmailTemplateGenerator
from services.job_search import JobSearchService
from services.readiness_score import ReadinessScoreCalculator
from services.simulator import CareerSimulator
from services.skill_extractor import SkillExtractor
from services.skill_gap import SkillGapAnalyzer
from services.user_auth import UserAuth
from utils.helpers import (
    create_weekly_plan,
    format_timeline_estimate,
    get_risk_color,
    get_skill_resources,
    load_data,
)

st.set_page_config(
    page_title="Career GPS — AI Career Mentor",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    * {margin: 0; padding: 0;}
    body {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #e2e8f0;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    }
    .stApp {background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);}
    
    /* Main content */
    .main {background: transparent;}
    
    /* Hero sections */
    .hero-title {
        font-size: 3.2rem;
        font-weight: 900;
        background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    .hero-sub {
        font-size: 1.2rem;
        color: #cbd5e1;
        margin-bottom: 1.5rem;
        font-weight: 500;
        line-height: 1.6;
    }
    
    /* Pills/Badges */
    .pill {
        display: inline-block;
        padding: 0.5rem 1rem;
        background: rgba(6, 182, 212, 0.15);
        color: #06b6d4;
        border: 1px solid rgba(6, 182, 212, 0.3);
        border-radius: 50px;
        font-size: 0.9rem;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .pill:hover {
        background: rgba(6, 182, 212, 0.25);
        border-color: rgba(6, 182, 212, 0.6);
        transform: translateY(-2px);
    }
    
    /* Cards */
    .card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    .card:hover {
        border-color: rgba(148, 163, 184, 0.25);
        box-shadow: 0 12px 48px rgba(6, 182, 212, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transform: translateY(-4px);
    }
    
    /* Section titles */
    .section-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: #f1f5f9;
        margin: 1.5rem 0 1rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    .section-title::before {
        content: '';
        display: inline-block;
        width: 4px;
        height: 1.8rem;
        background: linear-gradient(180deg, #0ea5e9 0%, #06b6d4 100%);
        border-radius: 2px;
    }
    
    /* Text styles */
    .muted {color: #94a3b8; font-size: 0.95rem; font-weight: 500;}
    .metric-hint {color: #64748b; font-size: 0.85rem; margin-top: -0.4rem; font-weight: 500;}
    
    /* Metrics */
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(6, 182, 212, 0.2);
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 1) 100%);
        border-color: rgba(6, 182, 212, 0.4);
        box-shadow: 0 8px 24px rgba(6, 182, 212, 0.1);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 900;
        color: #06b6d4;
        margin-bottom: 0.25rem;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #cbd5e1;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }
    
    /* Button overrides */
    .stButton > button {
        background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 700;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(6, 182, 212, 0.3);
    }
    .stButton > button:hover {
        box-shadow: 0 6px 25px rgba(6, 182, 212, 0.5);
        transform: translateY(-2px);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.95) 100%);
        border-right: 1px solid rgba(6, 182, 212, 0.15);
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0.7) 100%);
        border: 1px solid rgba(6, 182, 212, 0.15);
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        border-color: rgba(6, 182, 212, 0.3);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(6, 182, 212, 0.15);
        border-radius: 8px;
        color: #cbd5e1;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
        color: #ffffff;
        border: 1px solid rgba(6, 182, 212, 0.4);
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(6, 182, 212, 0.2) !important;
        color: #e2e8f0 !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: rgba(6, 182, 212, 0.6) !important;
        box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.1) !important;
    }
    
    /* Alerts */
    .stAlert {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%) !important;
        border-left: 4px solid;
        border-radius: 8px;
        padding: 1rem 1.25rem;
    }
    .stSuccess {border-left-color: #10b981 !important;}
    .stError {border-left-color: #ef4444 !important;}
    .stWarning {border-left-color: #f59e0b !important;}
    .stInfo {border-left-color: #06b6d4 !important;}
    
    /* Divider */
    .stMarkdown hr {
        border: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(6, 182, 212, 0.3), transparent);
        margin: 2rem 0;
    }
    
    /* Caption/small text */
    .stCaption {
        color: #94a3b8;
        font-size: 0.85rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_app_data():
    return load_data()


@st.cache_resource
def init_services(careers_df, skills_df):
    return (
        SkillExtractor(skills_df),
        CareerMatcher(careers_df),
        SkillGapAnalyzer(skills_df),
        ReadinessScoreCalculator(),
        CareerSimulator(skills_df),
        UserAuth(),
        EmailService(),
        JobSearchService(careers_df),
        EmailTemplateGenerator(),
        DailyLearningPlan(),
    )


def ensure_session_defaults():
    defaults = {
        "page": "auth",
        "logged_in": False,
        "user_email": None,
        "user_data": None,
        "user_profile": None,
        "career_matches": None,
        "selected_career": None,
        "baseline": None,
        "simulations": [],
        "daily_plan": None,
        "job_results": None,
        "learning_progress": {},
        "selected_job_for_email": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_auth():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='hero-title'>Career GPS™</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='hero-sub'>Your adaptive AI mentor for career readiness. Navigate skill gaps, simulate decisions, and stay job-ready.</div>",
            unsafe_allow_html=True,
        )

        with st.container():
            bullets = [
                "AI-powered career matching",
                "Real-time readiness scoring (0–100)",
                "What-if decision simulations",
                "Adaptive skill roadmaps",
            ]
            cols = st.columns(2)
            for idx, b in enumerate(bullets):
                cols[idx % 2].write(f"✨ {b}")

        st.markdown("---")

        tab_login, tab_signup = st.tabs(["🔐 Login", "📝 Sign Up"])

        with tab_login:
            st.markdown("#### Welcome back!")
            email = st.text_input("Email", key="login_email", placeholder="your@email.com")
            password = st.text_input("Password", type="password", key="login_pwd", placeholder="Enter password")
            if st.button("Login", type="primary", use_container_width=True):
                success, user_data, message = user_auth.login_user(email, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    st.session_state.user_data = user_data
                    st.session_state.page = "Overview"
                    if user_data.get("profile"):
                        st.session_state.user_profile = user_data["profile"]
                    if user_data.get("learning_progress"):
                        st.session_state.learning_progress = {
                            k: v.get("progress", 0) for k, v in user_data["learning_progress"].items()
                        }
                    st.success("Welcome back! Redirecting...")
                    st.rerun()
                else:
                    st.error(message)

        with tab_signup:
            st.markdown("#### Create your career profile")
            name = st.text_input("Full Name", key="signup_name", placeholder="John Doe")
            email = st.text_input("Email", key="signup_email", placeholder="your@email.com")
            password = st.text_input("Password", type="password", key="signup_pwd", placeholder="Min 6 characters")
            confirm = st.text_input("Confirm Password", type="password", key="signup_confirm", placeholder="Repeat password")
            user_type = st.selectbox("I am a", ["student", "fresh graduate", "professional"], index=0)

            if st.button("Create Account", type="primary", use_container_width=True):
                if not all([name, email, password, confirm]):
                    st.error("Please fill in all fields.")
                elif password != confirm:
                    st.error("Passwords do not match.")
                elif len(password) < 6:
                    st.error("Use at least 6 characters.")
                else:
                    success, message = user_auth.register_user(email, password, name, user_type)
                    if success:
                        st.success("Account created. Please log in.")
                    else:
                        st.error(message)

    st.stop()


def sidebar_nav():
    st.sidebar.markdown(
        """
        <div style='margin-bottom: 1.5rem;'>
            <div style='font-size: 1.4rem; font-weight: 900; background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;'>🧭 Career GPS</div>
            <div style='font-size: 0.9rem; color: #cbd5e1; margin-top: 0.5rem;'>AI mentor for your career journey</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")

    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.page = "Overview"
        st.session_state.user_email = None
        st.session_state.user_data = None
        st.session_state.user_profile = None
        st.rerun()

    if st.session_state.user_data:
        st.sidebar.markdown(
            f"""
            <div style='background: rgba(6, 182, 212, 0.1); border: 1px solid rgba(6, 182, 212, 0.2); border-radius: 8px; padding: 1rem; margin-bottom: 1rem;'>
                <div style='font-weight: 700; color: #f1f5f9;'>{st.session_state.user_data.get('name', 'User')}</div>
                <div style='font-size: 0.85rem; color: #94a3b8;'>{st.session_state.user_data.get('user_type', 'student').title()}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.sidebar.markdown("---")

    st.sidebar.markdown("<div style='font-weight: 700; margin-bottom: 1rem; color: #cbd5e1;'>Pages</div>", unsafe_allow_html=True)
    
    pages = [
        "Overview",
        "Profile",
        "Career Mentor",
        "Readiness & Gaps",
        "What-If Simulator",
        "Roadmap",
        "Daily Plan",
        "Jobs & Outreach",
        "Settings",
    ]
    
    # Sync with session state page
    current_page = st.session_state.get("page", "Overview")
    default_index = pages.index(current_page) if current_page in pages else 0
    
    nav = st.sidebar.radio(
        "Navigate",
        pages,
        index=default_index,
        label_visibility="collapsed",
    )
    
    # Update session state with sidebar selection
    st.session_state.page = nav

    st.sidebar.markdown("---")
    if st.session_state.user_profile:
        st.sidebar.markdown(
            f"""
            <div style='background: rgba(16, 185, 129, 0.1); border-left: 3px solid #10b981; padding: 0.75rem; border-radius: 4px; margin-bottom: 0.75rem;'>
                <div style='font-size: 0.8rem; font-weight: 600; color: #10b981;'>✓ Profile Ready</div>
                <div style='font-size: 0.75rem; color: #94a3b8;'>{len(st.session_state.user_profile.get('skills', []))} skills</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    if st.session_state.selected_career:
        st.sidebar.markdown(
            f"""
            <div style='background: rgba(6, 182, 212, 0.1); border-left: 3px solid #06b6d4; padding: 0.75rem; border-radius: 4px; margin-bottom: 0.75rem;'>
                <div style='font-size: 0.8rem; font-weight: 600; color: #06b6d4;'>🎯 Target</div>
                <div style='font-size: 0.75rem; color: #cbd5e1;'>{st.session_state.selected_career['role_name']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    if st.session_state.baseline:
        st.sidebar.markdown(
            f"""
            <div style='background: rgba(249, 115, 22, 0.1); border-left: 3px solid #f97316; padding: 0.75rem; border-radius: 4px;'>
                <div style='font-size: 0.8rem; font-weight: 600; color: #f97316;'>📊 Readiness</div>
                <div style='font-size: 0.75rem; color: #cbd5e1;'>{st.session_state.baseline['readiness_score']['overall_score']} | {st.session_state.baseline['risk_level']} risk</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return nav


def render_overview(careers_df, skills_df, resources_df):
    st.markdown("<div class='hero-title'>Adaptive career GPS for students and early professionals</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='hero-sub'>Continuously evaluates progress, reroutes learning, and forecasts readiness across scenarios.</div>",
        unsafe_allow_html=True,
    )

    cols = st.columns(4)
    cols[0].metric("Career roles", len(careers_df))
    cols[1].metric("Skills mapped", len(skills_df))
    cols[2].metric("Resources", len(resources_df))
    cols[3].metric("Avg. match accuracy", "92%")
    cols[3].markdown("<div class='metric-hint'>Hybrid ML + rules</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Why Career GPS")
    col1, col2 = st.columns(2)
    with col1:
        st.write(
            """
            - Lack of personalized mentorship and unclear skill expectations
            - Static advice that ignores progress, pauses, or pivots
            - Academic learning that trails industry requirements
            - No preview of “If I do X, how close am I to job-ready?”
            """
        )
    with col2:
        st.write(
            """
            - AI mentor that scores readiness 0–100 in real time
            - Skill-gap navigator that pinpoints missing, partial, and known skills
            - What-if simulation engine for switching domains, pausing, or project-first paths
            - Adaptive roadmap with learning time and risk estimates
            """
        )

    st.markdown("---")

    # The flow
    st.markdown("<div class='section-title'>Your Career Journey</div>", unsafe_allow_html=True)
    
    steps_col = st.columns(6)
    steps = [
        ("1️⃣", "Profile", "Share your skills & interests"),
        ("2️⃣", "Match", "Discover aligned career paths"),
        ("3️⃣", "Analyze", "View skill gaps & readiness"),
        ("4️⃣", "Simulate", "Test career decisions"),
        ("5️⃣", "Plan", "Generate learning roadmap"),
        ("6️⃣", "Execute", "Daily tasks & job search"),
    ]
    
    for idx, (emoji, title, desc) in enumerate(steps):
        with steps_col[idx]:
            st.markdown(
                f"""
                <div style='text-align: center; padding: 1rem; background: rgba(6, 182, 212, 0.1); border-radius: 12px; border: 1px solid rgba(6, 182, 212, 0.2);'>
                <div style='font-size: 1.8rem; margin-bottom: 0.5rem;'>{emoji}</div>
                <div style='font-weight: 700; margin-bottom: 0.25rem;'>{title}</div>
                <div style='font-size: 0.8rem; color: #94a3b8;'>{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🚀 Start Your Profile", type="primary", use_container_width=True, key="overview_profile_btn"):
            st.session_state.page = "Profile"
            st.rerun()
    with col2:
        st.info("💡 Complete your profile first to unlock career recommendations.")


def render_profile(skill_extractor):
    st.markdown("<div class='section-title'>Your Career Profile</div>", unsafe_allow_html=True)
    st.markdown("<div class='muted'>Tell us about yourself so we can find the perfect career path for you.</div>", unsafe_allow_html=True)
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("📝 Full Name", value=st.session_state.user_profile.get("name", "") if st.session_state.user_profile else "", placeholder="John Doe")
            education = st.selectbox(
                "🎓 Education Level",
                [
                    "High School",
                    "Associate Degree",
                    "Bachelor's Degree",
                    "Master's Degree",
                    "PhD",
                    "Bootcamp Graduate",
                    "Self-Taught",
                ],
            )
            experience = st.selectbox(
                "💼 Experience",
                ["Student", "Fresh Graduate", "0-2 Years", "2-5 Years", "5+ Years"],
            )
        with col2:
            major = st.text_input("🔬 Major/Field", value="", placeholder="Computer Science, Marketing, etc.")
            goal = st.text_input("🎯 Career Goal", value="", placeholder="Software Engineer, Product Manager, etc.")
            interests = st.text_area("💡 Interests & Passions", value="", height=80, placeholder="What excites you? (AI, startups, design, etc.)")

        st.markdown("---")
        skills_input = st.text_area(
            "🔧 Your Skills & Experience",
            value="",
            height=120,
            placeholder="Python, JavaScript, React, AWS, Project Management...\n\nOr describe your background in free text.",
            help="Include programming languages, tools, technologies, certifications, and soft skills",
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            submitted = st.form_submit_button("Save Profile", type="primary", use_container_width=True)
        with col2:
            st.form_submit_button("Clear", use_container_width=True)

        if submitted:
            if not skills_input:
                st.error("Please add at least a few skills or experience to get started.")
            else:
                with st.spinner("🔍 Extracting and analyzing your skills..."):
                    extracted = skill_extractor.extract_from_list(skills_input) if "," in skills_input else skill_extractor.extract_from_text(skills_input)
                if not extracted:
                    st.error("No skills detected. Try using comma-separated keywords or describe your experience in more detail.")
                else:
                    profile = {
                        "name": name or "User",
                        "education": education,
                        "experience_level": experience,
                        "major": major,
                        "career_goal": goal,
                        "interests": interests,
                        "skills": extracted,
                        "skills_categorized": skill_extractor.categorize_skills(extracted),
                    }
                    st.session_state.user_profile = profile
                    st.session_state.career_matches = None
                    st.session_state.selected_career = None
                    st.session_state.baseline = None
                    st.session_state.simulations = []
                    user_auth.update_user_profile(st.session_state.user_email, profile)
                    st.success(f"✅ Profile saved with {len(extracted)} skills!")
                    st.info("Go to **Career Mentor** from the sidebar to see your matches.")

    if st.session_state.user_profile:
        st.markdown("---")
        st.markdown("<div class='section-title'>Your Profile Snapshot</div>", unsafe_allow_html=True)
        p = st.session_state.user_profile
        col1, col2 = st.columns(2)
        col1.write(f"👤 **Name:** {p['name']}")
        col1.write(f"🎓 **Education:** {p['education']}")
        col1.write(f"💼 **Experience:** {p['experience_level']}")
        col2.write(f"🎯 **Goal:** {p.get('career_goal') or 'Not set'}")
        col2.write(f"🔧 **Skills:** {len(p['skills'])} identified")
        with st.expander("📋 View categorized skills"):
            for cat, skills in p["skills_categorized"].items():
                st.write(f"**{cat}**: {', '.join(skills)}")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("➡️ Next: Career Mentor", type="primary", use_container_width=True, key="profile_to_mentor"):
                st.session_state.page = "Career Mentor"
                st.rerun()
        with col2:
            if st.button("🔄 Update Profile", use_container_width=True, key="profile_refresh"):
                st.session_state.user_profile = None
                st.rerun()


def render_career_mentor(career_matcher):
    if not st.session_state.user_profile:
        st.warning("⚠️ Please create your profile first.")
        if st.button("Go to Profile", type="primary", use_container_width=True):
            st.session_state.page = "Profile"
            st.rerun()
        return

    profile = st.session_state.user_profile
    if st.session_state.career_matches is None:
        with st.spinner("🔍 Finding perfect career matches for you..."):
            st.session_state.career_matches = career_matcher.match_careers(
                profile["skills"], profile.get("interests", ""), top_n=5
            )

    matches = st.session_state.career_matches
    st.markdown("<div class='section-title'>Your Career Matches</div>", unsafe_allow_html=True)
    st.markdown("<div class='muted'>AI found these roles that align with your skills. Select one to dive deeper.</div>", unsafe_allow_html=True)

    for match in matches:
        with st.container():
            cols = st.columns([3, 1, 1, 1])
            cols[0].markdown(f"**{match['role_name']}** · {match['category']}")
            cols[0].write(match["description"])
            cols[1].metric("Match", f"{match['match_score']:.1f}%")
            cols[2].metric("Overlap", f"{match['skill_overlap_score']:.1f}%")
            cols[3].metric("Missing", len(match["missing_skills"]))
            if st.button(f"📊 Analyze Readiness", key=f"select_{match['role_id']}", type="primary", use_container_width=True):
                st.session_state.selected_career = match
                st.session_state.baseline = None
                st.session_state.simulations = []
                st.session_state.page = "Readiness & Gaps"
                st.rerun()

    st.markdown("---")
    df = pd.DataFrame(
        [
            {
                "Career": m["role_name"],
                "Match": round(m["match_score"], 1),
                "Overlap": round(m["skill_overlap_score"], 1),
                "Missing": len(m["missing_skills"]),
                "Growth": m["growth_rate"].replace("_", " ").title(),
            }
            for m in matches
        ]
    )
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_readiness(skill_gap_analyzer, readiness_calculator, simulator):
    if not st.session_state.selected_career:
        st.warning("⚠️ Select a career from Career Mentor first.")
        if st.button("Go to Career Mentor", type="primary", use_container_width=True):
            st.session_state.page = "Career Mentor"
            st.rerun()
        return

    career = st.session_state.selected_career
    profile = st.session_state.user_profile

    gap = skill_gap_analyzer.analyze_gap(profile["skills"], career)
    score = readiness_calculator.calculate_score(gap)
    if st.session_state.baseline is None or st.session_state.baseline.get("career") != career["role_name"]:
        st.session_state.baseline = simulator.create_baseline(profile["skills"], career)

    baseline = st.session_state.baseline

    st.markdown(f"<div class='section-title'>📈 Readiness for {career['role_name']}</div>", unsafe_allow_html=True)
    cols = st.columns(4)
    cols[0].metric("Readiness score", f"{score['overall_score']}", f"Grade {score['grade']}")
    cols[1].metric("Gap", f"{gap['gap_percentage']:.1f}%", f"Missing {gap['missing_skills_count']}")
    cols[2].metric("Time to ready", format_timeline_estimate(gap["estimated_learning_time_weeks"]))
    cols[3].metric("Risk", baseline["risk_level"], label_visibility="visible")

    fig = go.Figure(
        go.Bar(
            x=list(score["breakdown"].values()),
            y=list(score["breakdown"].keys()),
            orientation="h",
            marker=dict(color=list(score["breakdown"].values()), colorscale="Blues"),
            text=[f"{v:.1f}%" for v in score["breakdown"].values()],
            textposition="auto",
        )
    )
    fig.update_layout(height=280, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    st.info(score["interpretation"])
    # Show generated explanation (why + next steps) when available
    explanation = score.get('explanation') or (baseline.get('readiness_score', {}).get('explanation') if baseline else None)
    if explanation:
        with st.expander("Why this score and next steps", expanded=False):
            st.write(explanation)

    st.markdown("---")
    st.markdown("**Priority skills to learn first**")
    if gap["priority_skills"]:
        cols = st.columns(min(len(gap["priority_skills"]), 4))
        for idx, skill in enumerate(gap["priority_skills"]):
            with cols[idx % len(cols)]:
                st.write(f"{idx+1}. {skill}")
    else:
        st.success("No critical gaps detected.")

    st.markdown("**Skill breakdown**")
    col1, col2, col3 = st.columns(3)
    col1.write("Known")
    for s in gap["matched_skills"][:8]:
        col1.success(s)
    col2.write("Partial")
    for s in gap["partial_skills"][:8]:
        col2.warning(s)
    col3.write("Missing")
    for s in gap["missing_skills"][:8]:
        col3.error(s)

    st.markdown("---")
    c1, c2 = st.columns(2)
    if c1.button("🎲 Simulate Career Decisions", type="primary", use_container_width=True, key="readiness_to_simulator"):
        st.session_state.page = "What-If Simulator"
        st.rerun()
    if c2.button("🗺️ Generate Learning Roadmap", type="secondary", use_container_width=True, key="readiness_to_roadmap"):
        st.session_state.page = "Roadmap"
        st.rerun()


def render_simulator(simulator):
    baseline = st.session_state.baseline
    if not baseline:
        st.warning("⚠️ Complete readiness analysis first to unlock simulations.")
        if st.button("Go to Readiness & Gaps", type="primary", use_container_width=True):
            st.session_state.page = "Readiness & Gaps"
            st.rerun()
        return

    career = st.session_state.selected_career
    st.markdown("<div class='section-title'>🎲 What-If Decision Simulator</div>", unsafe_allow_html=True)
    st.markdown("<div class='muted'>Test career decisions and see how they impact your readiness score.</div>", unsafe_allow_html=True)
    cols = st.columns(4)
    cols[0].metric("Baseline score", baseline["readiness_score"]["overall_score"])
    cols[1].metric("Learning time", format_timeline_estimate(baseline["learning_time_weeks"]))
    cols[2].metric("Risk", baseline["risk_level"])
    cols[3].metric("Gap", f"{baseline['gap_analysis']['gap_percentage']:.1f}%")

    sim_type = st.radio(
        "Choose a decision to test",
        [
            "Switch career",
            "Skip certifications",
            "Project-first learning",
            "Pause learning",
            "Add new skills",
        ],
    )

    result = None
    if sim_type == "Switch career":
        choices = [m for m in st.session_state.career_matches if m["role_id"] != career["role_id"]]
        target = st.selectbox("🔄 New Career", [c["role_name"] for c in choices])
        if st.button("🎲 Simulate Career Switch", type="primary", use_container_width=True):
            chosen = next(c for c in choices if c["role_name"] == target)
            result = simulator.simulate_switch_career(baseline, chosen)
    elif sim_type == "Skip certifications":
        certs = [s for s in baseline["gap_analysis"]["missing_skills"] if any(k in s for k in ["AWS", "Azure", "GCP", "Certified", "Certificate"])]
        selected = st.multiselect("📜 Certifications to Skip", certs, default=certs)
        if st.button("⏭️ Simulate Skip", type="primary", use_container_width=True):
            result = simulator.simulate_skip_certifications(baseline, selected)
    elif sim_type == "Project-first learning":
        partial = baseline["gap_analysis"]["partial_skills"]
        chosen = st.multiselect("💻 Skills to Master via Projects", partial, default=partial[:3] if partial else [])
        if st.button("🚀 Simulate Project Path", type="primary", use_container_width=True):
            result = simulator.simulate_focus_projects(baseline, chosen)
    elif sim_type == "Pause learning":
        weeks = st.slider("⏸️ Pause Duration (weeks)", 1, 52, 6)
        if st.button("⏸️ Simulate Pause", type="primary", use_container_width=True):
            result = simulator.simulate_pause_learning(baseline, weeks)
    elif sim_type == "Add new skills":
        missing = baseline["gap_analysis"]["missing_skills"]
        chosen = st.multiselect("➕ Skills to Add", missing, default=missing[:3] if missing else [])
        if st.button("➕ Simulate New Skills", type="primary", use_container_width=True):
            result = simulator.simulate_add_skills(baseline, chosen, career)

    if result:
        st.session_state.simulations.append(result)
        st.markdown("---")
        c1, c2 = st.columns(2)
        c1.metric("After score", result["readiness_score"]["overall_score"], f"Δ {result['changes']['score_change']:+.1f}")
        c2.metric(
            "Time to ready",
            format_timeline_estimate(result["learning_time_weeks"]),
            f"Δ {result['changes']['time_change']:+.0f} weeks",
        )
        st.write("Risk:", result["risk_level"])
        # Surface explanation and what-if summary when available
        explanation = result.get('readiness_score', {}).get('explanation')
        what_if = result.get('what_if_summary')
        if what_if:
            with st.expander("What-if summary", expanded=True):
                st.write(what_if)
        if explanation:
            with st.expander("Why this result and next steps", expanded=False):
                st.write(explanation)
        if result.get("warning"):
            st.warning(result["warning"])
        if result.get("benefit"):
            st.success(result["benefit"])
        with st.expander("Detailed changes"):
            st.json(result["changes"])

    if st.session_state.simulations:
        st.markdown("---")
        st.markdown("**Simulation comparison**")
        df = pd.DataFrame(simulator.compare_simulations(st.session_state.simulations))
        st.dataframe(df, use_container_width=True, hide_index=True)
        fig = px.bar(df, x="simulation_type", y="readiness_score", color="risk_level")
        st.plotly_chart(fig, use_container_width=True)
        if st.button("🔄 Clear All Simulations", use_container_width=True, key="clear_sims"):
            st.session_state.simulations = []
            st.rerun()


def render_roadmap(resources_df, skills_df):
    baseline = st.session_state.baseline
    if not baseline:
        st.warning("⚠️ Generate readiness analysis first.")
        if st.button("Go to Readiness & Gaps", type="primary", use_container_width=True):
            st.session_state.page = "Readiness & Gaps"
            st.rerun()
        return

    gap = baseline["gap_analysis"]
    st.markdown(f"<div class='section-title'>🗺️ Learning Roadmap: {baseline['career']}</div>", unsafe_allow_html=True)
    cols = st.columns(3)
    cols[0].metric("Duration", format_timeline_estimate(gap["estimated_learning_time_weeks"]))
    cols[1].metric("Skills to learn", gap["missing_skills_count"])
    cols[2].metric("Skills to improve", gap["partial_skills_count"])

    plan = create_weekly_plan(gap["missing_skills"], gap["partial_skills"], skills_df)
    for phase in plan:
        with st.expander(f"Phase {phase['phase']} · {phase['duration_weeks']} weeks", expanded=phase["phase"] == 1):
            for task in phase["skills"]:
                st.write(f"**{task['type']}** {task['skill']} · {task['difficulty']}")
                resources = get_skill_resources(task["skill"], resources_df)
                if resources:
                    st.caption("Top resources:")
                    for res in resources[:2]:
                        st.markdown(f"- [{res['name']}]({res['url']}) · {res['type']} · {res['duration']} weeks")

    st.download_button(
        "Download roadmap (JSON)",
        data=json.dumps(
            {
                "career": baseline["career"],
                "readiness_score": baseline["readiness_score"]["overall_score"],
                "estimated_weeks": gap["estimated_learning_time_weeks"],
                "phases": plan,
                "priority_skills": gap["priority_skills"],
            },
            indent=2,
        ),
        file_name=f"career_roadmap_{baseline['career'].replace(' ', '_')}.json",
        mime="application/json",
    )


def render_daily_plan(resources_df, daily_learning):
    if not st.session_state.selected_career:
        st.warning("⚠️ Select a career and complete readiness analysis first.")
        if st.button("Go to Readiness & Gaps", type="primary", use_container_width=True):
            st.session_state.page = "Readiness & Gaps"
            st.rerun()
        return

    gap = SkillGapAnalyzer(skills_df).analyze_gap(
        st.session_state.user_profile["skills"], st.session_state.selected_career
    )
    skill_gaps = []
    for skill in gap["missing_skills"]:
        skill_gaps.append({"skill": skill, "priority": 100, "hours_needed": 20, "resources": get_skill_resources(skill, resources_df)})
    for skill in gap["partial_skills"]:
        if isinstance(skill, dict):
            skill_name = skill.get("skill", "")
        else:
            skill_name = skill
        skill_gaps.append({"skill": skill_name, "priority": 60, "hours_needed": 10, "resources": get_skill_resources(skill_name, resources_df)})

    user_progress = st.session_state.get("learning_progress", {})
    for g in skill_gaps:
        user_progress.setdefault(g["skill"], 0)

    col1, col2 = st.columns(2)
    pace = col1.selectbox("🚀 Learning Pace", ["slow", "moderate", "intensive"], index=1)
    hours = col2.slider("⏰ Hours per Day", 1, 6, 2)

    if st.button("📅 Generate Today's Plan", type="primary", use_container_width=True):
        st.session_state.daily_plan = daily_learning.generate_daily_plan(skill_gaps, user_progress, pace, hours)

    if st.session_state.daily_plan:
        for idx, task in enumerate(st.session_state.daily_plan):
            with st.expander(f"📌 Task {idx+1}: {task['activity']} ({task['skill']})", expanded=idx == 0):
                st.write(f"⏱️ **Duration:** {task['duration']}")
                st.write(f"🎯 **Milestone:** {task['milestone']}")
                if task["resources"]:
                    st.caption("📚 Resources")
                    for res in task["resources"]:
                        title = res.get("title") or res.get("name") or "Resource"
                        url = res.get("url", "")
                        st.markdown(f"- [{title}]({url})")
                current = user_progress.get(task["skill"], 0)
                new = st.slider("📊 Progress", 0, 100, current, key=f"progress_{idx}")
                if st.button("💾 Save Progress", key=f"save_{idx}", type="primary", use_container_width=True):
                    user_progress[task["skill"]] = new
                    st.session_state.learning_progress = user_progress
                    user_auth.update_learning_progress(st.session_state.user_email, task["skill"], new)
                    st.success("✅ Progress saved!")

        summary = daily_learning.get_progress_summary(user_progress, skill_gaps)
        st.markdown("---")
        cols = st.columns(4)
        cols[0].metric("Total skills", summary["total_skills"])
        cols[1].metric("Completed", summary["completed_skills"])
        cols[2].metric("In progress", summary["in_progress_skills"])
        cols[3].metric("Avg progress", f"{summary['average_progress']}%")
        eta = daily_learning.calculate_estimated_completion(skill_gaps, hours)
        st.caption(f"Estimated completion: {eta['completion_date']} · ~{eta['weeks_needed']} weeks")


def render_jobs_and_outreach(job_search, email_templates):
    if not st.session_state.selected_career:
        st.warning("⚠️ Select a career first.")
        if st.button("Go to Career Mentor", type="primary", use_container_width=True):
            st.session_state.page = "Career Mentor"
            st.rerun()
        return

    career = st.session_state.selected_career["role_name"]
    st.markdown(f"<div class='section-title'>💼 Job Discovery & Outreach: {career}</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    location = col1.selectbox("📍 Location", ["Remote", "Hybrid", "On-site", "Any"], index=0)
    experience = col2.selectbox("💼 Experience Level", ["entry", "mid", "senior"], index=0)
    top_n = col3.slider("📊 Results", 5, 20, 10)

    if st.button("🔍 Search Jobs", type="primary", use_container_width=True):
        with st.spinner("Scanning job boards..."):
            st.session_state.job_results = job_search.get_recommended_jobs(
                career, st.session_state.user_profile.get("skills", []), location, top_n
            )

    if st.session_state.job_results:
        for idx, job in enumerate(st.session_state.job_results):
            with st.expander(f"{job['title']} · {job['company']} ({job['match_score']}% match)"):
                st.write(job["description"])
                st.caption(f"Location: {job['location']} | Type: {job['type']} | Posted: {job['posted_date']}")
                if job["requirements"]:
                    st.write("Requirements:")
                    st.write(", ".join(job["requirements"]))
                st.metric("Match score", f"{job['match_score']}%")
                tips = job_search.get_job_application_tips(job, st.session_state.user_profile.get("skills", []))
                st.write("Tips:")
                for t in tips:
                    st.write(f"- {t}")
                if st.button("✉️ Generate Application Email", key=f"email_{idx}", type="primary", use_container_width=True):
                    st.session_state.selected_job_for_email = job
                    st.session_state.page = "Jobs & Outreach"

    st.markdown("---")
    st.subheader("Email templates")
    template_type = st.selectbox(
        "Template",
        ["Job application", "Networking", "Referral request", "Follow-up"],
    )

    user_name = st.session_state.user_data.get("name", "Your Name")
    skills = st.session_state.user_profile.get("skills", [])

    if template_type == "Job application":
        job = st.session_state.selected_job_for_email
        job_title = st.text_input("💼 Job Title", value=job.get("title") if job else "Software Engineer")
        company = st.text_input("🏢 Company", value=job.get("company") if job else "Tech Corp")
        exp = st.text_input("📝 Your Experience", value="recent graduate")
        if st.button("📧 Generate Application Email", type="primary", use_container_width=True):
            email = email_templates.generate_application_email(job_title, company, user_name, skills, exp)
            st.text_area("Draft", email, height=320)
    elif template_type == "Networking":
        recipient = st.text_input("👤 Recipient Name", value="Alex")
        company = st.text_input("🏢 Company", value="Tech Corp")
        common = st.text_input("🤝 Common Interest", value="cloud engineering")
        background = st.text_input("📝 Your Background", value="builder who loves shipping projects")
        if st.button("📧 Generate Networking Email", type="primary", use_container_width=True):
            email = email_templates.generate_cold_email_networking(recipient, company, user_name, background, common)
            st.text_area("Draft", email, height=320)
    elif template_type == "Referral request":
        contact = st.text_input("👤 Contact Name", value="Friend")
        company = st.text_input("🏢 Company", value="Tech Corp")
        position = st.text_input("💼 Position", value="Software Engineer")
        relationship = st.text_input("🤝 Relationship", value="We worked together at XYZ")
        if st.button("📧 Generate Referral Email", type="primary", use_container_width=True):
            email = email_templates.generate_referral_request_email(contact, company, position, user_name, relationship)
            st.text_area("Draft", email, height=320)
    elif template_type == "Follow-up":
        interviewer = st.text_input("👤 Interviewer Name", value="Hiring Manager")
        company = st.text_input("🏢 Company", value="Tech Corp")
        position = st.text_input("💼 Role", value="Software Engineer")
        date_str = st.date_input("📅 Interview Date")
        if st.button("📧 Generate Follow-up Email", type="primary", use_container_width=True):
            email = email_templates.generate_follow_up_email(
                interviewer, company, position, user_name, date_str.strftime("%B %d, %Y")
            )
            st.text_area("Draft", email, height=320)


def render_settings():
    st.markdown("<div class='section-title'>⚙️ Settings</div>", unsafe_allow_html=True)
    notif = st.checkbox("🔔 Enable daily email notifications", value=True)
    sender_email = st.text_input("✉️ Sender email (optional)")
    sender_password = st.text_input("🔐 Sender password", type="password") if sender_email else None

    if st.button("💾 Save Notification Preferences", type="primary", use_container_width=True):
        preferences = {"email_notifications": notif, "notification_time": "09:00"}
        success, msg = user_auth.update_notification_preferences(st.session_state.user_email, preferences)
        if success:
            st.success("✅ Preferences saved")
        else:
            st.error(msg)

    st.markdown("---")
    st.markdown("<div style='font-weight: 700; color: #cbd5e1;'>👤 Account Info</div>", unsafe_allow_html=True)
    st.write(f"📧 **Email:** {st.session_state.user_email}")
    st.write(f"👥 **User Type:** {st.session_state.user_data.get('user_type', 'student').title()}")
    st.write(f"📅 **Created:** {st.session_state.user_data.get('created_at', 'N/A')}")

    if sender_email and sender_password and st.button("📧 Send Test Email", type="primary", use_container_width=True):
        email_service.configure(sender_email, sender_password)
        results_html = email_service.format_results(78, 4, 3)
        plan_html = email_service.format_learning_plan(
            [
                {"skill": "Python", "activity": "Build mini-API", "duration": "1 hour"},
                {"skill": "SQL", "activity": "Practice queries", "duration": "30 min"},
            ]
        )
        success, msg = email_service.send_daily_update(
            st.session_state.user_email,
            st.session_state.user_data.get("name", "Career GPS user"),
            results_html,
            plan_html,
        )
        if success:
            st.success("✅ Test email sent successfully!")
        else:
            st.error(msg)


# App bootstrap
ensure_session_defaults()

try:
    careers_df, skills_df, resources_df = load_app_data()
except Exception as exc:  # graceful data load failure
    st.error(f"Error loading data: {exc}")
    st.stop()

(
    skill_extractor,
    career_matcher,
    skill_gap_analyzer,
    readiness_calculator,
    simulator,
    user_auth,
    email_service,
    job_search,
    email_templates,
    daily_learning,
) = init_services(careers_df, skills_df)

# Auth gate
if not st.session_state.logged_in:
    render_auth()

# Sidebar + page routing
nav_choice = sidebar_nav()

if nav_choice == "Overview":
    render_overview(careers_df, skills_df, resources_df)
elif nav_choice == "Profile":
    render_profile(skill_extractor)
elif nav_choice == "Career Mentor":
    render_career_mentor(career_matcher)
elif nav_choice == "Readiness & Gaps":
    render_readiness(skill_gap_analyzer, readiness_calculator, simulator)
elif nav_choice == "What-If Simulator":
    render_simulator(simulator)
elif nav_choice == "Roadmap":
    render_roadmap(resources_df, skills_df)
elif nav_choice == "Daily Plan":
    render_daily_plan(resources_df, daily_learning)
elif nav_choice == "Jobs & Outreach":
    render_jobs_and_outreach(job_search, email_templates)
elif nav_choice == "Settings":
    render_settings()

st.markdown("---")
st.caption("Career GPS™ — Adaptive career guidance, skill-gap navigation, and readiness simulation.")


def _run_console_cli(skill_extractor, career_matcher, simulator):
    """Simple console loop: get skills, choose career, ask what-if questions."""
    print("Welcome to Career GPS (console mode). Type 'exit' to quit.")

    skills_input = input("Enter your skills (comma-separated or free text): ").strip()
    if not skills_input or skills_input.lower() in ("exit", "quit"):
        print("Goodbye.")
        return

    # Extract skills
    skills = skill_extractor.extract_from_list(skills_input) if ',' in skills_input else skill_extractor.extract_from_text(skills_input)
    if not skills:
        print("No skills detected. Exiting.")
        return

    print(f"Detected {len(skills)} skills: {', '.join(skills[:10])}")

    # Show career matches
    matches = career_matcher.match_careers(skills, '', top_n=5)
    print("Top career matches:")
    for i, m in enumerate(matches, 1):
        print(f"{i}. {m['role_name']} — Match {m['match_score']:.1f}% — Missing {len(m['missing_skills'])}")

    choice = input("Choose a career number (1–5) or '1' by default: ").strip()
    try:
        idx = int(choice) - 1 if choice else 0
        chosen = matches[idx]
    except Exception:
        chosen = matches[0]

    baseline = simulator.create_baseline(skills, chosen)
    print(f"Baseline readiness for {chosen['role_name']}: {baseline['readiness_score']['overall_score']} — {baseline['readiness_score'].get('interpretation','')}")
    if baseline['readiness_score'].get('explanation'):
        print('Explanation:', baseline['readiness_score']['explanation'])

    # Interactive queries
    while True:
        q = input("Ask Career GPS: ").strip()
        if not q or q.lower() in ('exit', 'quit'):
            print("Exiting console mode. Goodbye.")
            break

        lower = q.lower()
        # If user asks a what-if about learning skills
        if 'learn' in lower or 'what if' in lower:
            # Attempt to parse skills after 'learn' or after ':'
            skills_to_try = None
            if 'learn' in lower:
                try:
                    skills_to_try = q.split('learn', 1)[1].strip(' :').strip()
                except Exception:
                    skills_to_try = None
            if (not skills_to_try) and ':' in q:
                skills_to_try = q.split(':', 1)[1].strip()

            if not skills_to_try:
                skills_to_try = input("Enter skills to simulate (comma-separated): ").strip()

            new_skills = [s.strip() for s in skills_to_try.split(',') if s.strip()]
            if not new_skills:
                print("No skills provided.")
                continue

            if len(new_skills) == 1 and hasattr(simulator, 'simulate_what_if_learn'):
                res = simulator.simulate_what_if_learn(baseline, new_skills[0], chosen)
            else:
                res = simulator.simulate_add_skills(baseline, new_skills, chosen)
            # Print concise summary
            summary = res.get('what_if_summary') or res.get('readiness_score', {}).get('explanation') or ''
            print('\n--- What-If Result ---')
            print(summary)
            print('After score:', res['readiness_score']['overall_score'])
            print('Change:', res['changes'].get('score_change'))
            print('---------------------\n')
            continue

        if lower in ('show baseline', 'baseline', 'status'):
            rs = baseline['readiness_score']
            print(f"Baseline: {rs['overall_score']} | {rs.get('grade')}\n{rs.get('explanation','')}")
            continue

        print("I didn't understand that. Try: 'What if I learn X', 'show baseline', or 'exit'.")


if __name__ == '__main__' and os.environ.get('CAREER_GPS_CLI') == '1':
    try:
        _run_console_cli(skill_extractor, career_matcher, simulator)
    except Exception as e:
        print('Console mode failed:', e)