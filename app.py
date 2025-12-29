"""
Career GPS™ — AI Career Readiness Mentor
Rewritten Streamlit experience aligned with product narrative
"""
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

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
    body {background-color: #f7f9fb;}
    .hero-title {font-size: 2.6rem; font-weight: 800; color: #0f172a; margin-bottom: 0.25rem;}
    .hero-sub {font-size: 1.1rem; color: #475569; margin-bottom: 1rem;}
    .pill {display: inline-block; padding: 0.35rem 0.8rem; background: #e0f2fe; color: #0369a1; border-radius: 999px; font-size: 0.85rem; margin-right: 0.35rem;}
    .card {background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1rem 1.2rem; box-shadow: 0 6px 20px rgba(15, 23, 42, 0.04);}
    .section-title {font-size: 1.3rem; font-weight: 700; color: #0f172a; margin: 0.25rem 0 0.35rem;}
    .muted {color: #64748b; font-size: 0.95rem;}
    .metric-hint {color: #475569; font-size: 0.85rem; margin-top: -0.4rem;}
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
    st.markdown("<div class='hero-title'>Career GPS™</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='hero-sub'>Adaptive, data-driven career readiness mentor that reroutes with you.</div>",
        unsafe_allow_html=True,
    )

    bullets = [
        "AI career matches built on your skills and interests",
        "Dynamic readiness score (0–100) that updates with every decision",
        "What-if simulations for switching paths, pausing, or fast-tracking",
        "Skill-gap navigator and adaptive learning roadmap",
    ]
    st.write("".join([f"<span class='pill'>{b}</span>" for b in bullets]), unsafe_allow_html=True)
    st.markdown("---")

    tab_login, tab_signup = st.tabs(["🔐 Login", "📝 Sign Up"])

    with tab_login:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pwd")
        if st.button("Login", type="primary", use_container_width=True):
            success, user_data, message = user_auth.login_user(email, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.user_data = user_data
                st.session_state.page = "overview"
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
        name = st.text_input("Full Name", key="signup_name")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_pwd")
        confirm = st.text_input("Confirm Password", type="password", key="signup_confirm")
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
    st.sidebar.title("🧭 Career GPS")
    st.sidebar.markdown(
        "Navigates your career like a GPS: assess, reroute, and keep moving toward readiness."
    )
    st.sidebar.markdown("---")

    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.page = "auth"
        st.session_state.user_email = None
        st.session_state.user_data = None
        st.session_state.user_profile = None
        st.rerun()

    if st.session_state.user_data:
        st.sidebar.markdown(f"**{st.session_state.user_data.get('name', 'User')}**")
        st.sidebar.markdown(f"*{st.session_state.user_data.get('user_type', 'student').title()}*")
        st.sidebar.markdown("---")

    nav = st.sidebar.radio(
        "Navigate",
        [
            "Overview",
            "Profile",
            "Career Mentor",
            "Readiness & Gaps",
            "What-If Simulator",
            "Roadmap",
            "Daily Plan",
            "Jobs & Outreach",
            "Settings",
        ],
    )

    if st.session_state.user_profile:
        st.sidebar.success("Profile ready")
        st.sidebar.info(f"Skills: {len(st.session_state.user_profile.get('skills', []))}")
    if st.session_state.selected_career:
        st.sidebar.success(f"Target: {st.session_state.selected_career['role_name']}")
    if st.session_state.baseline:
        st.sidebar.info(
            f"Readiness: {st.session_state.baseline['readiness_score']['overall_score']} | Risk: {st.session_state.baseline['risk_level']}"
        )

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Core loop**")
    st.sidebar.write("Profile → Matches → Readiness → Simulate → Roadmap → Execute")
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
    st.subheader("How it works")
    steps = [
        "Profile: capture skills, interests, and goals",
        "Match: rank roles with skill overlap and market signals",
        "Gap: categorize known / partial / missing skills",
        "Simulate: run what-if decisions and see readiness deltas",
        "Roadmap: generate phased plan with resources and time-to-ready",
        "Execute: daily plan + outreach (jobs, email templates)",
    ]
    for i, step in enumerate(steps, 1):
        st.write(f"{i}. {step}")

    if st.button("Start with profile", type="primary"):
        st.session_state.page = "Profile"
        st.rerun()


def render_profile(skill_extractor):
    st.subheader("Create or refine your profile")
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name", value=st.session_state.user_profile.get("name", "") if st.session_state.user_profile else "")
            education = st.selectbox(
                "Education level",
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
                "Experience",
                ["Student", "Fresh Graduate", "0-2 Years", "2-5 Years", "5+ Years"],
            )
        with col2:
            major = st.text_input("Major/Field", value="")
            goal = st.text_input("Career goal", value="")
            interests = st.text_area("Interests", value="", height=80)

        skills_input = st.text_area(
            "Skills or experience (comma-separated or free text)",
            value="",
            height=120,
            help="Include tools, languages, platforms, and domain strengths",
        )
        submitted = st.form_submit_button("Save profile", type="primary")

        if submitted:
            if not skills_input:
                st.error("Add at least a few skills or experiences.")
            else:
                with st.spinner("Extracting skills"):
                    extracted = skill_extractor.extract_from_list(skills_input) if "," in skills_input else skill_extractor.extract_from_text(skills_input)
                if not extracted:
                    st.error("No skills detected. Try comma-separated keywords.")
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
                    st.success(f"Profile saved with {len(extracted)} skills. Move to Career Mentor.")

    if st.session_state.user_profile:
        st.markdown("---")
        st.markdown("**Snapshot**")
        p = st.session_state.user_profile
        col1, col2 = st.columns(2)
        col1.write(f"Name: {p['name']}")
        col1.write(f"Education: {p['education']}")
        col1.write(f"Experience: {p['experience_level']}")
        col2.write(f"Goal: {p.get('career_goal') or 'Not set'}")
        col2.write(f"Skills: {len(p['skills'])}")
        with st.expander("View categorized skills"):
            for cat, skills in p["skills_categorized"].items():
                st.write(f"**{cat}**: {', '.join(skills)}")


def render_career_mentor(career_matcher):
    if not st.session_state.user_profile:
        st.warning("Create a profile first.")
        return

    profile = st.session_state.user_profile
    if st.session_state.career_matches is None:
        with st.spinner("Matching you to roles"):
            st.session_state.career_matches = career_matcher.match_careers(
                profile["skills"], profile.get("interests", ""), top_n=5
            )

    matches = st.session_state.career_matches
    st.subheader("Career matches")
    st.caption("Scores blend skill overlap and semantic fit. Select one to analyze readiness.")

    for match in matches:
        with st.container():
            cols = st.columns([3, 1, 1, 1])
            cols[0].markdown(f"**{match['role_name']}** · {match['category']}")
            cols[0].write(match["description"])
            cols[1].metric("Match", f"{match['match_score']:.1f}%")
            cols[2].metric("Overlap", f"{match['skill_overlap_score']:.1f}%")
            cols[3].metric("Missing", len(match["missing_skills"]))
            if st.button("Analyze readiness", key=f"select_{match['role_id']}"):
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
        st.warning("Pick a career from Career Mentor first.")
        return

    career = st.session_state.selected_career
    profile = st.session_state.user_profile

    gap = skill_gap_analyzer.analyze_gap(profile["skills"], career)
    score = readiness_calculator.calculate_score(gap)
    if st.session_state.baseline is None or st.session_state.baseline.get("career") != career["role_name"]:
        st.session_state.baseline = simulator.create_baseline(profile["skills"], career)

    baseline = st.session_state.baseline

    st.subheader(f"Readiness for {career['role_name']}")
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
    if c1.button("Run what-if simulation", type="primary"):
        st.session_state.page = "What-If Simulator"
        st.rerun()
    if c2.button("Generate roadmap", type="secondary"):
        st.session_state.page = "Roadmap"
        st.rerun()


def render_simulator(simulator):
    baseline = st.session_state.baseline
    if not baseline:
        st.warning("Complete readiness & gap analysis first.")
        return

    career = st.session_state.selected_career
    st.subheader("What-if simulation engine")
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
        target = st.selectbox("New career", [c["role_name"] for c in choices])
        if st.button("Simulate switch", type="primary"):
            chosen = next(c for c in choices if c["role_name"] == target)
            result = simulator.simulate_switch_career(baseline, chosen)
    elif sim_type == "Skip certifications":
        certs = [s for s in baseline["gap_analysis"]["missing_skills"] if any(k in s for k in ["AWS", "Azure", "GCP", "Certified", "Certificate"])]
        selected = st.multiselect("Certifications to skip", certs, default=certs)
        if st.button("Simulate skip"):
            result = simulator.simulate_skip_certifications(baseline, selected)
    elif sim_type == "Project-first learning":
        partial = baseline["gap_analysis"]["partial_skills"]
        chosen = st.multiselect("Skills to master via projects", partial, default=partial[:3] if partial else [])
        if st.button("Simulate projects"):
            result = simulator.simulate_focus_projects(baseline, chosen)
    elif sim_type == "Pause learning":
        weeks = st.slider("Pause duration (weeks)", 1, 52, 6)
        if st.button("Simulate pause"):
            result = simulator.simulate_pause_learning(baseline, weeks)
    elif sim_type == "Add new skills":
        missing = baseline["gap_analysis"]["missing_skills"]
        chosen = st.multiselect("Skills to add", missing, default=missing[:3] if missing else [])
        if st.button("Simulate adding skills"):
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
        if st.button("Clear simulations"):
            st.session_state.simulations = []
            st.rerun()


def render_roadmap(resources_df, skills_df):
    baseline = st.session_state.baseline
    if not baseline:
        st.warning("Generate readiness first.")
        return

    gap = baseline["gap_analysis"]
    st.subheader(f"Adaptive roadmap for {baseline['career']}")
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
        st.warning("Select a career and run readiness first.")
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
    pace = col1.selectbox("Learning pace", ["slow", "moderate", "intensive"], index=1)
    hours = col2.slider("Hours per day", 1, 6, 2)

    if st.button("Generate today's plan", type="primary"):
        st.session_state.daily_plan = daily_learning.generate_daily_plan(skill_gaps, user_progress, pace, hours)

    if st.session_state.daily_plan:
        for idx, task in enumerate(st.session_state.daily_plan):
            with st.expander(f"Task {idx+1}: {task['activity']} ({task['skill']})", expanded=idx == 0):
                st.write(f"Duration: {task['duration']}")
                st.write(f"Milestone: {task['milestone']}")
                if task["resources"]:
                    st.caption("Resources")
                    for res in task["resources"]:
                        title = res.get("title") or res.get("name") or "Resource"
                        url = res.get("url", "")
                        st.markdown(f"- [{title}]({url})")
                current = user_progress.get(task["skill"], 0)
                new = st.slider("Progress", 0, 100, current, key=f"progress_{idx}")
                if st.button("Save", key=f"save_{idx}"):
                    user_progress[task["skill"]] = new
                    st.session_state.learning_progress = user_progress
                    user_auth.update_learning_progress(st.session_state.user_email, task["skill"], new)
                    st.success("Progress saved")

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
        st.warning("Pick a career first.")
        return

    career = st.session_state.selected_career["role_name"]
    st.subheader(f"Job discovery for {career}")
    col1, col2, col3 = st.columns(3)
    location = col1.selectbox("Location", ["Remote", "Hybrid", "On-site", "Any"], index=0)
    experience = col2.selectbox("Experience", ["entry", "mid", "senior"], index=0)
    top_n = col3.slider("Results", 5, 20, 10)

    if st.button("Search jobs", type="primary"):
        with st.spinner("Scanning boards"):
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
                if st.button("Generate application email", key=f"email_{idx}"):
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
        job_title = st.text_input("Job title", value=job.get("title") if job else "Software Engineer")
        company = st.text_input("Company", value=job.get("company") if job else "Tech Corp")
        exp = st.text_input("Your experience", value="recent graduate")
        if st.button("Generate application email"):
            email = email_templates.generate_application_email(job_title, company, user_name, skills, exp)
            st.text_area("Draft", email, height=320)
    elif template_type == "Networking":
        recipient = st.text_input("Recipient name", value="Alex")
        company = st.text_input("Company", value="Tech Corp")
        common = st.text_input("Common interest", value="cloud engineering")
        background = st.text_input("Your background", value="builder who loves shipping projects")
        if st.button("Generate networking email"):
            email = email_templates.generate_cold_email_networking(recipient, company, user_name, background, common)
            st.text_area("Draft", email, height=320)
    elif template_type == "Referral request":
        contact = st.text_input("Contact name", value="Friend")
        company = st.text_input("Company", value="Tech Corp")
        position = st.text_input("Position", value="Software Engineer")
        relationship = st.text_input("Relationship cue", value="We worked together at XYZ")
        if st.button("Generate referral email"):
            email = email_templates.generate_referral_request_email(contact, company, position, user_name, relationship)
            st.text_area("Draft", email, height=320)
    elif template_type == "Follow-up":
        interviewer = st.text_input("Interviewer name", value="Hiring Manager")
        company = st.text_input("Company", value="Tech Corp")
        position = st.text_input("Role", value="Software Engineer")
        date_str = st.date_input("Interview date")
        if st.button("Generate follow-up email"):
            email = email_templates.generate_follow_up_email(
                interviewer, company, position, user_name, date_str.strftime("%B %d, %Y")
            )
            st.text_area("Draft", email, height=320)


def render_settings():
    st.subheader("Settings")
    notif = st.checkbox("Enable daily email notifications", value=True)
    sender_email = st.text_input("Sender email (optional)")
    sender_password = st.text_input("Sender password", type="password") if sender_email else None

    if st.button("Save notification preferences"):
        preferences = {"email_notifications": notif, "notification_time": "09:00"}
        success, msg = user_auth.update_notification_preferences(st.session_state.user_email, preferences)
        if success:
            st.success("Preferences saved")
        else:
            st.error(msg)

    st.markdown("---")
    st.write("Account")
    st.write(f"Email: {st.session_state.user_email}")
    st.write(f"User type: {st.session_state.user_data.get('user_type', 'student').title()}")
    st.write(f"Created: {st.session_state.user_data.get('created_at', 'N/A')}")

    if sender_email and sender_password and st.button("Send test email"):
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
            st.success("Test email sent")
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
