from __future__ import annotations

import streamlit as st

from components import navigation
from components.ui import LOGO_PATH, inject_styles


st.set_page_config(
    page_title="CareerPilot",
    page_icon=":material/flight_takeoff:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_styles()
if LOGO_PATH.exists():
    st.logo(str(LOGO_PATH), size="large")

st.navigation(navigation.all_pages(), position="top").run()
