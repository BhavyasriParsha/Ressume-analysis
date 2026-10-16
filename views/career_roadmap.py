from __future__ import annotations

import streamlit as st

from components import ui
from services.career_service import generate_roadmap

LEVELS = {"entry": "Entry level", "mid": "Mid level", "senior": "Senior"}


def render_career_roadmap() -> None:
    ui.page_header("Career roadmap", "Turn the gap between your resume and a target role into a week-by-week plan.")
    st.caption("Roadmap steps are generated from built-in templates and keyword matching; resume text is not sent to Groq from this page.")

    with st.form("roadmap_form", border=True):
        role_col, level_col = st.columns([2, 1])
        with role_col:
            target_role = st.text_input("Target role", value=st.session_state.get("roadmap_role", "Senior Product Analyst"))
        with level_col:
            experience_level = st.selectbox("Your level", list(LEVELS), index=1, format_func=LEVELS.get)
        resume_col, job_col = st.columns(2, gap="large")
        with resume_col:
            resume_text = st.text_area(
                "Your resume",
                height=180,
                value=st.session_state.get("resume_text", ""),
                placeholder="Paste your resume text, or upload a PDF on the Resume page.",
            )
        with job_col:
            job_description = st.text_area(
                "Job description (optional)",
                height=180,
                value=st.session_state.get("job_description_text", ""),
                placeholder="Add a job posting to base the plan on its exact skill gaps.",
            )
        submitted = st.form_submit_button("Build roadmap", type="primary")

    if submitted:
        if not resume_text.strip() and not job_description.strip():
            st.session_state.pop("roadmap", None)
            st.warning("Add your resume or a job description to build a roadmap.", icon=":material/warning:")
        elif not target_role.strip():
            st.session_state.pop("roadmap", None)
            st.warning("Add the role you're aiming for.", icon=":material/warning:")
        else:
            st.session_state["roadmap"] = generate_roadmap(resume_text, target_role.strip(), experience_level, job_description)
            st.session_state["roadmap_role"] = target_role.strip()
            for key in [k for k in st.session_state if str(k).startswith("milestone_")]:
                del st.session_state[key]

    roadmap = st.session_state.get("roadmap")
    if roadmap is None:
        ui.empty_state("No roadmap yet", "Fill in your target role and resume, then select Build roadmap.")
        return

    fit_col, summary_col = st.columns([5, 7], gap="large")
    with fit_col:
        st.html(ui.gauge(roadmap.progress, "Current fit", "Add a job description to measure fit" if roadmap.progress is None else "Against the job description"))
    with summary_col:
        ui.render_html(
            ui.section_title("Summary"),
            ui.summary(roadmap.summary),
            ui.section_title("Already on your resume"),
            ui.chips(roadmap.strengths, "match"),
            ui.section_title("Skills to build"),
            ui.chips(roadmap.skill_gaps, "missing"),
        )

    route_col, milestones_col = st.columns([7, 5], gap="large")
    with route_col:
        steps = [step.model_dump() for step in roadmap.learning_sequence]
        destination = st.session_state.get("roadmap_role", "your target")
        ui.render_html(ui.section_title("Your plan"), ui.route(steps, destination))
    with milestones_col:
        with st.container(border=True):
            ui.render_section_title("Every week", "Tick these off as you go.")
            for index, milestone in enumerate(roadmap.weekly_milestones):
                st.checkbox(milestone, key=f"milestone_{index}")
