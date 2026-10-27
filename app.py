"""Entry point for Digital Mess Cleanup."""

import streamlit as st

st.set_page_config(
    page_title="Digital Mess Cleanup",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="expanded",
)

from digital_mess_cleanup.ui import render_app

render_app()
