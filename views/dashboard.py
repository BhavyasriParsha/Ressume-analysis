from __future__ import annotations

import streamlit as st

from components import navigation, ui


def render_dashboard() -> None:
    ui.page_header("Overview", "Where your application stands. Work through the four steps in order, or jump to any of them.")

    analysis = st.session_state.get("resume_analysis")
    match = st.session_state.get("job_match")
    interview = st.session_state.get("interview_feedback")
    roadmap = st.session_state.get("roadmap")

    resume_score = analysis["analysis"].quality_score if analysis else None
    match_score = match.match_score if match else None
    interview_score = interview.score if interview else None
    roadmap_fit = roadmap.progress if roadmap else None

    ui.gauge_row([
        (resume_score, "Resume", "Upload a resume to measure"),
        (match_score, "Job match", "Compare against a job to measure"),
        (interview_score, "Interview", "Answer a question to measure"),
        (roadmap_fit, "Roadmap fit", "Add a job to your roadmap to measure" if roadmap else "Build a roadmap to measure"),
    ])

    ui.render_section_title("Steps")
    steps = [
        ("resume", "Review your resume", "Get a score and the fixes that matter most.", analysis is not None, "Review resume"),
        ("job-match", "Match it to a job", "See which job-description terms your resume already contains.", match is not None, "Match a job"),
        ("interview", "Practice an answer", "Answer one question and get feedback on structure and impact.", interview is not None, "Practice"),
        ("roadmap", "Plan what to learn", "Turn your skill gaps into a week-by-week plan.", roadmap is not None, "Build roadmap"),
    ]
    for number, (key, title, detail, done, action) in enumerate(steps, start=1):
        with st.container(border=True):
            text_col, link_col = st.columns([4, 1.3], vertical_alignment="center")
            with text_col:
                st.html(ui.checklist_step(number, title, detail, done))
            with link_col:
                st.page_link(navigation.page(key), label="Open again" if done else action, width="stretch")

    if analysis:
        ui.render_html(ui.section_title("Latest resume summary"), ui.summary(analysis["analysis"].summary))
