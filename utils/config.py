from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"

# utf-8-sig tolerates the BOM that Windows editors and PowerShell often write.
load_dotenv(ENV_PATH, encoding="utf-8-sig", override=False)


def _get_streamlit_secret(name: str) -> str:
    import streamlit as st
    from streamlit.errors import StreamlitSecretNotFoundError

    try:
        value = st.secrets.get(name)
    except StreamlitSecretNotFoundError:
        return ""
    return str(value).strip() if value is not None else ""


def get_groq_api_key() -> str:
    if "GROQ_API_KEY" in os.environ:
        return os.environ["GROQ_API_KEY"].strip()
    return _get_streamlit_secret("GROQ_API_KEY")


def is_groq_key_from_streamlit_secrets() -> bool:
    return "GROQ_API_KEY" not in os.environ and bool(_get_streamlit_secret("GROQ_API_KEY"))


def is_demo_mode() -> bool:
    value = os.environ.get("DEMO_MODE")
    if value is None:
        value = _get_streamlit_secret("DEMO_MODE")
    value = (value or "true").strip().lower()
    return value in {"1", "true", "yes", "on"}


def initialize_session_state() -> None:
    import streamlit as st

    st.session_state.setdefault("selected_page", "Dashboard")
