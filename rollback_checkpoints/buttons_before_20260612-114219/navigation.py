import streamlit as st
import re

from pages.live_call import get_live_call_url

PAGES = [
    ("Home", "Home"),
    ("Learning Mode", "Learning"),
    ("Mock Exam", "Mock Exam"),
    ("Review Mistakes", "Review"),
    ("Progress", "Progress"),
    ("__live_call__", "Live Call"),
    ("Study Music", "Music"),
]


def _page_key(page):
    return re.sub(r"[^a-z0-9_]+", "_", page.lower()).strip("_")


def app_navigation():
    if "active_page" not in st.session_state:
        st.session_state.active_page = "Home"

    active_page = st.session_state.active_page
    active_label = next((label for page, label in PAGES if page == active_page), active_page)
    active_key = _page_key(active_page)

    st.markdown(
        f"""
        <style>
        .top-nav-title {{
            text-align: center;
            font-size: 24px;
            font-weight: 900;
            color: #0f172a;
            margin: 1rem 0 0.65rem;
            letter-spacing: 0.01em;
        }}
        .active-section-banner {{
            width: fit-content;
            margin: 0 auto 1.5rem;
            padding: 0.55rem 1.2rem;
            border-radius: 999px;
            background: linear-gradient(135deg, #2563eb, #7c3aed);
            color: white;
            font-size: 18px;
            font-weight: 900;
            box-shadow: 0 12px 26px rgba(37, 99, 235, 0.28);
        }}
        .st-key-nav_{active_key} button {{
            background: linear-gradient(135deg, #2563eb, #7c3aed) !important;
            color: #ffffff !important;
            border: 2px solid #1d4ed8 !important;
            font-weight: 900 !important;
            box-shadow: 0 12px 24px rgba(37, 99, 235, 0.24) !important;
            transform: translateY(-2px);
        }}
        .st-key-nav_{active_key} button:hover {{
            background: linear-gradient(135deg, #1d4ed8, #6d28d9) !important;
            color: #ffffff !important;
        }}
        </style>
        <div class="top-nav-title">Choose a section</div>
        <div class="active-section-banner">Selected: {active_label}</div>
        """,
        unsafe_allow_html=True,
    )
    cols = st.columns(len(PAGES))

    for col, (page, label) in zip(cols, PAGES):
        with col:
            if page == "__live_call__":
                st.link_button(label, get_live_call_url(), use_container_width=True)
                continue

            if st.button(label, key=f"nav_{_page_key(page)}", use_container_width=True):
                st.session_state.active_page = page
                st.rerun()

    return st.session_state.active_page
