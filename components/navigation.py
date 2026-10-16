from __future__ import annotations

import importlib
from typing import Callable, Dict, List, Tuple

import streamlit as st

# key: (title, icon, module, render function). Views are imported lazily so a view
# can link to another page without a circular import.
PAGE_SPECS: Dict[str, Tuple[str, str, str, str]] = {
    "overview": ("Overview", ":material/flight_takeoff:", "views.dashboard", "render_dashboard"),
    "resume": ("Resume", ":material/description:", "views.resume_analyzer", "render_resume_analyzer"),
    "job-match": ("Job match", ":material/compare_arrows:", "views.job_matcher", "render_job_matcher"),
    "interview": ("Interview", ":material/record_voice_over:", "views.interview_coach", "render_interview_coach"),
    "roadmap": ("Roadmap", ":material/route:", "views.career_roadmap", "render_career_roadmap"),
    "settings": ("Settings", ":material/settings:", "views.settings", "render_settings"),
}


def _runner(module: str, function: str) -> Callable[[], None]:
    def run() -> None:
        getattr(importlib.import_module(module), function)()

    run.__name__ = function
    return run


def page(key: str) -> st.Page:
    title, icon, module, function = PAGE_SPECS[key]
    return st.Page(_runner(module, function), title=title, icon=icon, url_path=key, default=key == "overview")


def all_pages() -> List[st.Page]:
    return [page(key) for key in PAGE_SPECS]
