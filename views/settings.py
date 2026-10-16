from __future__ import annotations

import os

import streamlit as st

from components import ui
from utils.config import ENV_PATH, get_groq_api_key, is_groq_key_from_streamlit_secrets


def _save_env(api_key: str | None) -> None:
    content = ENV_PATH.read_text(encoding="utf-8-sig") if ENV_PATH.exists() else ""
    lines = [
        line for line in content.splitlines()
        if not line.strip().startswith(("GROQ_API_KEY=", "DEMO_MODE="))
    ]
    if api_key:
        os.environ["GROQ_API_KEY"] = api_key
        os.environ["DEMO_MODE"] = "false"
        lines += [f"GROQ_API_KEY={api_key}", "DEMO_MODE=false"]
    else:
        os.environ.pop("GROQ_API_KEY", None)
        os.environ["DEMO_MODE"] = "true"
        lines.append("DEMO_MODE=true")
    ENV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _clear_session() -> None:
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state["settings_notice"] = "Session cleared. Your resume, results and answers have been removed."


def render_settings() -> None:
    ui.page_header("Settings", "Connect AI feedback and manage the data this session holds.")

    notice = st.session_state.pop("settings_notice", None)
    if notice:
        st.success(notice, icon=":material/check_circle:")

    ai_col, data_col = st.columns(2, gap="large")

    with ai_col:
        with st.container(border=True):
            ui.render_section_title(
                "AI feedback",
                "With a Groq API key, summaries and suggestions are written for resume reviews and job matches. "
                "Scores always come from the same fixed rules.",
            )
            has_key = bool(get_groq_api_key())
            deployment_key = is_groq_key_from_streamlit_secrets()
            # The saved key is never sent back to the browser; only whether one exists.
            if ui.ai_configured():
                st.html('<p class="cp-muted">Status: a key is configured. Provider access is checked when you request feedback.</p>')
            elif has_key:
                source = "deployment secret" if deployment_key else "saved key"
                st.html(f'<p class="cp-muted">Status: a {source} is present, but demo mode is on.</p>')
            else:
                st.html('<p class="cp-muted">Status: demo mode. Feedback comes from built-in rules.</p>')

            if deployment_key:
                st.caption("This key comes from Streamlit deployment secrets. Manage it in the hosting settings; it cannot be changed here.")
            else:
                with st.form("api_key_form", border=False, clear_on_submit=True):
                    provided_key = st.text_input(
                        "Groq API key",
                        type="password",
                        placeholder="gsk_...",
                        help="Get a free key at console.groq.com. It is saved to the .env file in this project.",
                    )
                    saved = st.form_submit_button("Save key", type="primary")
                if saved:
                    cleaned = provided_key.strip()
                    if cleaned:
                        _save_env(cleaned)
                        st.session_state["settings_notice"] = (
                            "Key saved. Resume and job-match requests will try Groq; verify provider access after a request."
                        )
                        st.rerun()
                    else:
                        st.warning("Paste a key to save.", icon=":material/warning:")
                if has_key and st.button("Remove key"):
                    _save_env(None)
                    st.session_state["settings_notice"] = "Key removed. Demo mode is on."
                    st.rerun()

    with data_col:
        with st.container(border=True):
            ui.render_section_title("Your data")
            st.html(ui.item_list([
                "Resumes and answers stay in this browser session's memory and are never written to disk.",
                "With Groq configured, resume-review text (up to 6,000 resume and 4,000 job-description characters) and job-match text (up to 6,000 characters each) are sent to the provider. Interview and roadmap inputs stay local.",
                "Scores are guidance, not an official applicant tracking system result.",
            ], "neutral"))
            st.button("Clear this session", on_click=_clear_session, help="Removes your uploaded resume, results and answers.")
