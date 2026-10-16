from __future__ import annotations

import streamlit as st

from components import ui
from services.job_matcher import perform_job_match


def render_job_matcher() -> None:
    ui.page_header("Job match", "Compare your resume with a job posting to see which terms overlap and which are missing.")

    with st.form("job_match_form", border=True):
        resume_col, job_col = st.columns(2, gap="large")
        with resume_col:
            resume_text = st.text_area(
                "Your resume",
                height=240,
                value=st.session_state.get("resume_text", ""),
                placeholder="Paste your resume text, or upload a PDF on the Resume page to fill this in.",
            )
        with job_col:
            job_description = st.text_area(
                "Job description",
                height=240,
                value=st.session_state.get("job_description_text", ""),
                placeholder="Paste the full job posting, including requirements.",
            )
        submitted = st.form_submit_button("Compare", type="primary")

    if submitted:
        if not resume_text.strip() or not job_description.strip():
            st.session_state.pop("job_match", None)
            missing = "your resume" if not resume_text.strip() else "the job description"
            st.warning(f"Add {missing} to compare.", icon=":material/warning:")
        else:
            with st.spinner("Comparing..."):
                st.session_state["job_match"] = perform_job_match(resume_text, job_description)
            st.session_state["resume_text"] = resume_text
            st.session_state["job_description_text"] = job_description

    result = st.session_state.get("job_match")
    if result is None:
        ui.empty_state("No comparison yet", "Paste both texts and select Compare. Your match score and skill gaps will appear here.")
        return

    score_col, summary_col = st.columns([5, 7], gap="large")
    with score_col:
        st.html(ui.gauge(result.match_score, "Job match", "Overlap among up to 30 frequent terms; not a semantic fit score"))
    with summary_col:
        ui.render_html(ui.section_title("Summary"), ui.summary(result.summary))
        ui.source_note(result.ai_generated)

    skills_col, gaps_col = st.columns(2, gap="large")
    with skills_col:
        ui.render_html(
            ui.section_title(f"On your resume ({len(result.matched_skills)})"),
            ui.chips(result.matched_skills, "match", "None of the job's key terms were found."),
        )
    with gaps_col:
        ui.render_html(
            ui.section_title(f"Missing from your resume ({len(result.missing_skills)})", "Add these only where they describe real experience."),
            ui.chips(result.missing_skills, "missing", "No selected job-description terms are missing."),
        )

    experience_tab, actions_tab, requirements_tab = st.tabs([
        "Relevant experience",
        f"What to change ({len(result.recommendations)})",
        f"Requirements not shown ({len(result.requirements_not_demonstrated)})",
    ])
    with experience_tab:
        st.html(ui.quote_list(result.relevant_experience, "No resume lines clearly relate to the job's key terms yet."))
    with actions_tab:
        st.html(ui.item_list(result.recommendations, "action"))
    with requirements_tab:
        st.html(ui.item_list(result.requirements_not_demonstrated, "gap", "No unshown requirements were returned; keyword overlap is not proof of requirement evidence."))
