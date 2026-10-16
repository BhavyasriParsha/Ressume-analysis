from __future__ import annotations

import hashlib

import streamlit as st

from components import ui
from services.resume_analyzer import analyze_resume_document
from services.resume_parser import SECTION_NAMES
from services.scoring import SCORE_MAXIMA
from utils.config import get_groq_api_key, is_demo_mode

BREAKDOWN_NOTES = {
    "structure": "Five points for each non-empty summary, skills, experience and education section.",
    "clarity": "A word-count band; this is not a readability assessment.",
    "impact": "Counts numeric mentions up to 20 points; it does not verify that numbers show outcomes.",
    "evidence": "Points increase with experience-section length, or overall length if absent; claims are not verified.",
    "keywords": "Counts up to 20 distinct terms from the resume body, not job-specific matches.",
}


def render_resume_analyzer() -> None:
    ui.page_header("Resume review", "Upload your resume to get a score, what's working, and what to fix first.")

    with st.container(border=True):
        upload_col, job_col = st.columns(2, gap="large")
        with upload_col:
            uploaded = st.file_uploader("Resume PDF", type=["pdf"], help="Text-based PDFs up to 5 MB. Scanned images can't be read.")
        with job_col:
            job_description = st.text_area(
                "Job description (optional)",
                height=124,
                value=st.session_state.get("job_description_text", ""),
                placeholder="Paste a job posting to check which of its keywords your resume covers.",
            )

    if uploaded is not None:
        # Re-run when the resume, job description, or AI configuration changes.
        digest = hashlib.sha256(uploaded.getvalue())
        digest.update(b"\0")
        digest.update(job_description.encode("utf-8"))
        digest.update(b"\0")
        digest.update(get_groq_api_key().encode("utf-8"))
        digest.update(b"\0")
        digest.update(b"demo" if is_demo_mode() else b"live")
        cache_key = digest.hexdigest()

        if st.session_state.get("resume_analysis_key") != cache_key or "resume_analysis" not in st.session_state:
            try:
                with st.spinner("Reading your resume..."):
                    result = analyze_resume_document(uploaded, job_description)
            except ValueError as exc:
                st.error(f"{exc} Export the resume from your editor as a PDF and upload it again.", icon=":material/error:")
                return
            if not result["text"].strip():
                st.warning("No text could be read from this PDF. If it is a scanned image, export a text-based PDF instead.", icon=":material/warning:")
                return
            result["file_name"] = uploaded.name
            result["job_description"] = job_description
            st.session_state["resume_analysis"] = result
            st.session_state["resume_analysis_key"] = cache_key
            st.session_state["resume_text"] = result["text"]
            if job_description.strip():
                st.session_state["job_description_text"] = job_description

    result = st.session_state.get("resume_analysis")
    if result is None:
        ui.empty_state(
            "No resume uploaded yet",
            "Your score, a section-by-section breakdown and suggested fixes will appear here.",
        )
        return
    if uploaded is None:
        # The uploader forgets its file when you leave the page; the analysis is kept.
        st.html(ui.muted(f"Showing results for {result.get('file_name', 'your last upload')}. Upload a PDF to replace it."))
    job_description = result.get("job_description", job_description)
    anal = result["analysis"]

    score_col, breakdown_col = st.columns([5, 7], gap="large")
    with score_col:
        st.html(ui.gauge(anal.quality_score, "Resume score", "Scored out of 100"))
    with breakdown_col:
        st.html(ui.section_title("How the score adds up") + ui.breakdown(anal.score_breakdown, SCORE_MAXIMA, BREAKDOWN_NOTES))

    ui.render_html(ui.section_title("Summary"), ui.summary(anal.summary))
    ui.source_note(anal.ai_generated)

    found = [name.title() for name in SECTION_NAMES if anal.sections.get(name)]
    not_found = [name.title() for name in SECTION_NAMES if not anal.sections.get(name)]

    fix_tab, gaps_tab, strengths_tab, keywords_tab, sections_tab = st.tabs([
        f"Fix first ({len(anal.recommendations)})",
        f"Gaps ({len(anal.weaknesses)})",
        f"Strengths ({len(anal.strengths)})",
        "Keywords",
        f"Sections ({len(found)} of {len(SECTION_NAMES)})",
    ])
    with fix_tab:
        st.html(ui.item_list(anal.recommendations, "action"))
    with gaps_tab:
        st.html(ui.item_list(anal.weaknesses, "gap"))
    with strengths_tab:
        st.html(ui.item_list(anal.strengths, "good"))
    with keywords_tab:
        parts = [
            ui.section_title("Found in your resume", "The terms that appear most often."),
            ui.chips(anal.keywords, "neutral", "No keywords detected."),
        ]
        if job_description.strip():
            parts += [
                ui.section_title("In the job description but not your resume", "Add these only where they describe real experience."),
                ui.chips(anal.missing_keywords, "missing", "Your resume covers the job description's main terms."),
            ]
        else:
            parts.append(ui.muted("Paste a job description above to see which of its keywords are missing."))
        ui.render_html(*parts)
    with sections_tab:
        ui.render_html(
            ui.section_title("Found"),
            ui.chips(found, "match", "No standard section headings were found."),
            ui.section_title("Not found", "Recruiters and applicant tracking systems look for these headings."),
            ui.chips(not_found, "missing", "All standard sections are present."),
        )
