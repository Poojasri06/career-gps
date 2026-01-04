import streamlit as st
import pandas as pd
from services.career_matcher import CareerMatcher
from services.skill_gap import SkillGapAnalyzer
from utils.helpers import load_data, get_risk_color, format_timeline_estimate

# ---------- Page Config ----------
st.set_page_config(
    page_title="Career GPS – Simplified",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Futuristic Theme (CSS only, no JS) ----------
st.markdown(
    """
    <style>
    .stApp {  
        background: radial-gradient(1200px 800px at 80% 20%, rgba(100,181,246,.08) 0%, rgba(10,25,41,0) 60%),
                    radial-gradient(900px 600px at 20% 85%, rgba(121,134,203,.08) 0%, rgba(10,25,41,0) 60%),
                    linear-gradient(135deg, #0a1929 0%, #0c1f36 45%, #0d2544 100%) !important;
        min-height: 100vh;
    }
    .stApp::after { /* neural grid */
        content: '';
        position: fixed; inset: 0; pointer-events: none; z-index: 0;
        background-image:
            linear-gradient(rgba(66,165,245,0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(66,165,245,0.05) 1px, transparent 1px);
        background-size: 42px 42px;
        animation: gridPulse 6s ease-in-out infinite;
    }
    @keyframes gridPulse { 0%,100%{opacity:.25} 50%{opacity:.45} }

    /* keep app content above backgrounds */
    .main .block-container { position: relative; z-index: 1; }

    /* cards */
    .glass { 
        background: rgba(13,71,161,0.25); 
        border: 1px solid rgba(100,181,246,0.18);
        border-radius: 12px; padding: 1rem; 
        box-shadow: 0 10px 30px rgba(0,0,0,.35);
        backdrop-filter: blur(10px);
    }

    /* typography on dark */
    h1, h2, h3, h4, h5, h6, p, span, label, div, li { color: #e3f2fd !important; }
    .caption { color: #90caf9 !important; }

    /* inputs */
    input, textarea, select { color: #e3f2fd !important; }
    [data-baseweb="input"] input { background: rgba(13,71,161,.25); }
    [data-baseweb="select"] { background: rgba(13,71,161,.25); }

    /* buttons */
    .stButton>button { 
        background: linear-gradient(135deg, #1976d2 0%, #42a5f5 100%);
        color: #fff; border: 0; border-radius: 10px; padding: .6rem 1rem;
        box-shadow: 0 8px 25px rgba(33,150,243,.35); transition: all .2s ease;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 10px 30px rgba(33,150,243,.5); }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Debug Heartbeat ----------
st.title("Career GPS is Live 🚀")
st.write("App loaded successfully")

# ---------- Cache data/services ----------
@st.cache_data(show_spinner=False)
def _load():
    return load_data()

careers_df, skills_df, resources_df = _load()

@st.cache_resource(show_spinner=False)
def _services():
    return CareerMatcher(careers_df), SkillGapAnalyzer(skills_df)

matcher, gapper = _services()

# ---------- Session State ----------
ss = st.session_state
ss.setdefault("page", "Home")
ss.setdefault("profile", None)
ss.setdefault("matches", [])
ss.setdefault("selected_index", None)

# ---------- Sidebar Navigation ----------
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Go to", ["Home", "Profile", "Matches", "Gap Analysis"], index=["Home","Profile","Matches","Gap Analysis"].index(ss.get("page","Home")))
ss.page = page

# ---------- Pages ----------
if page == "Home":
    st.subheader("Your Real-Time AI Career Readiness Mentor")
    col1, col2 = st.columns([3,2])
    with col1:
        st.markdown(
            """
            - Smart matching based on your skills
            - Clear skill gaps and priorities
            - Simple, actionable learning path
            """
        )
        if st.button("Start with your Profile →"):
            ss.page = "Profile"
            st.rerun()
    with col2:
        st.markdown("<div class='glass'><b>Dataset</b><br/>" 
                    f"Careers: {len(careers_df)}<br/>Skills: {len(skills_df)}<br/>Resources: {len(resources_df)}</div>",
                    unsafe_allow_html=True)

elif page == "Profile":
    st.subheader("Create Your Profile")
    cols = st.columns(2)
    skill_names = sorted(skills_df["skill_name"].dropna().unique().tolist())
    with cols[0]:
        picked = st.multiselect("Select your skills", skill_names, max_selections=40)
        experience = st.selectbox("Experience", ["Student","Fresher","1-3 years","3-5 years","5+ years"], index=0)
    with cols[1]:
        education = st.selectbox("Education", ["High School","Associate","Bachelor's","Master's","PhD","Bootcamp","Self-Taught"], index=2)
        interests = st.text_input("Interests (optional)", placeholder="e.g., data science, cloud, fintech")
    if st.button("Save Profile", type="primary"):
        ss.profile = {"skills": picked, "experience": experience, "education": education, "interests": interests}
        st.success("Profile saved. Head to Matches →")

    if ss.profile:
        st.markdown("### Preview")
        st.markdown(f"Skills: {len(ss.profile['skills'])} selected")
        st.caption(", ".join(ss.profile["skills"][:20]) + (" ..." if len(ss.profile["skills"])>20 else ""))

elif page == "Matches":
    st.subheader("Top Career Matches")
    if not ss.profile or not ss.profile["skills"]:
        st.info("Please create your profile first in the Profile tab.")
    else:
        if st.button("Find Matches", type="primary"):
            ss.matches = matcher.match_careers(ss.profile["skills"], ss.profile.get("interests"), top_n=5)
            ss.selected_index = 0 if ss.matches else None
        if ss.matches:
            for i, m in enumerate(ss.matches):
                with st.container(border=True):
                    cols = st.columns([3,1,1,1])
                    cols[0].markdown(f"**{m['role_name']}** · {m['category']}\n\n{m['description']}")
                    cols[1].metric("Match", f"{m['match_score']:.0f}%")
                    cols[2].metric("Overlap", f"{m['skill_overlap_score']:.0f}%")
                    cols[3].metric("Similarity", f"{m['similarity_score']:.0f}%")
                st.caption("Matched: " + ", ".join(m['matched_skills'][:8]))
                st.caption("Missing: " + ", ".join(m['missing_skills'][:8]))
                st.radio("Select", ["Select"], key=f"pick_{i}", index=0 if ss.selected_index==i else 0, label_visibility="collapsed")
                if st.button(f"Use this career", key=f"use_{i}"):
                    ss.selected_index = i
                    st.success(f"Selected: {m['role_name']}")
        else:
            st.caption("No matches yet. Click 'Find Matches'.")

elif page == "Gap Analysis":
    st.subheader("Skill Gap Analysis")
    if not ss.profile or not ss.profile["skills"]:
        st.info("Please create your profile and pick a match first.")
    elif ss.selected_index is None or not ss.matches:
        st.info("Please generate matches and select a career in the Matches tab.")
    else:
        match = ss.matches[ss.selected_index]
        analysis = gapper.analyze_gap(ss.profile["skills"], match)
        cols = st.columns(4)
        cols[0].metric("Required Skills", analysis['total_required_skills'])
        cols[1].metric("Known", analysis['known_skills_count'])
        cols[2].metric("Partial", analysis['partial_skills_count'])
        cols[3].metric("Missing", analysis['missing_skills_count'])
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Missing")
            st.write(", ".join(analysis['missing_skills']) or "—")
            st.markdown("#### Partial")
            st.write(", ".join(analysis['partial_skills']) or "—")
        with c2:
            st.markdown("#### Known")
            st.write(", ".join(analysis['matched_skills']) or "—")
            st.markdown("#### Estimated Learning Time")
            st.write(format_timeline_estimate(analysis['estimated_learning_time_weeks']))

st.markdown("---")
st.caption("🎯 Career GPS – Simplified • Futuristic theme • No JS • Core features only")
