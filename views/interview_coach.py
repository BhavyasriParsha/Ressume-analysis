from __future__ import annotations

import streamlit as st

from components import ui
from services.ai_service import AIService

ROLES = ["Software Engineer", "Product Manager", "Data Analyst", "UX Designer", "Marketing Analyst"]
TYPES = {"technical": "Technical", "behavioral": "Behavioral", "hr": "HR", "role-specific": "Role-specific"}
LEVELS = {"beginner": "Beginner", "intermediate": "Intermediate", "advanced": "Advanced"}


def _new_question() -> None:
    st.session_state["question"] = AIService().generate_interview_question(
        st.session_state["iv_role"], st.session_state["iv_type"], st.session_state["iv_level"]
    )
    # Start each question with a blank answer and no stale feedback.
    st.session_state["interview_answer"] = ""
    st.session_state.pop("current_feedback", None)


def render_interview_coach() -> None:
    ui.page_header("Interview practice", "Answer one question at a time and get feedback on structure, reasoning and impact.")
    st.caption("Question generation and answer feedback use built-in rules; they do not send answers to Groq.")

    with st.container(border=True):
        role_col, type_col, level_col = st.columns(3)
        with role_col:
            st.selectbox("Role", ROLES, key="iv_role")
        with type_col:
            st.selectbox("Question type", list(TYPES), format_func=TYPES.get, key="iv_type")
        with level_col:
            st.selectbox("Difficulty", list(LEVELS), format_func=LEVELS.get, key="iv_level")
        label = "New question" if "question" in st.session_state else "Get a question"
        st.button(label, type="primary", on_click=_new_question)

    question = st.session_state.get("question")
    if question is None:
        ui.empty_state("No question yet", "Choose a role and question type, then select Get a question.")
        return

    expectations = ui.item_list(question.answer_expectations, "neutral")
    st.html(
        '<section class="cp-briefing" aria-label="Interview question">'
        f'<p class="cp-briefing-meta"><span class="cp-pill">{ui.escape(TYPES.get(question.category, question.category))}</span>'
        f'<span class="cp-pill">{ui.escape(LEVELS.get(question.difficulty, question.difficulty))}</span></p>'
        f'<p class="cp-briefing-question">{ui.escape(question.question)}</p>'
        f'{ui.section_title("A strong answer")}{expectations}</section>'
    )

    answer = st.text_area(
        "Your answer",
        height=220,
        key="interview_answer",
        placeholder="Describe the situation, what you did, and what happened as a result.",
    )
    words = len(answer.split())
    st.caption(f"{words} words. Most strong answers run 120 to 250 words.")

    if st.button("Get feedback", type="primary"):
        if not answer.strip():
            st.session_state.pop("current_feedback", None)
            st.warning("Write an answer first, then select Get feedback.", icon=":material/warning:")
        else:
            role = st.session_state.get("iv_role", ROLES[0])
            feedback = AIService().evaluate_interview_answer(answer, role, question.category)
            st.session_state["interview_feedback"] = feedback
            st.session_state["current_feedback"] = feedback

    feedback = st.session_state.get("current_feedback")
    if feedback is None:
        return

    score_col, detail_col = st.columns([5, 7], gap="large")
    with score_col:
        st.html(ui.gauge(feedback.score, "Answer score", "Rule-based checklist; not an AI evaluation"))
    with detail_col:
        ui.render_html(
            ui.section_title("What worked"),
            ui.item_list(feedback.strengths, "good"),
            ui.section_title("What to add"),
            ui.item_list(feedback.gaps, "gap"),
        )

    coaching_col, follow_col = st.columns(2, gap="large")
    with coaching_col:
        ui.render_html(ui.section_title("Coaching"), ui.item_list(feedback.coaching, "action"))
    with follow_col:
        ui.render_html(
            ui.section_title("Likely follow-up questions", "Interviewers often dig in with questions like these."),
            ui.item_list(feedback.follow_up_questions, "neutral"),
        )
