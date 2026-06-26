import streamlit as st
import re

from pages.live_call import get_live_call_url
from shared_session import read_shared_page, write_shared_page

PAGES = [
    ("Home", "⌂  Home"),
    ("Learning Mode", "▤  Learning"),
    ("Mock Exam", "☑  Mock Exam"),
    ("Review Mistakes", "☆  Review"),
    ("Progress", "▟  Progress"),
    ("__live_call__", "♡  Live Call"),
    ("IPTVSmartersPro", "IPTVSmartersPro"),
]


def _page_key(page):
    return re.sub(r"[^a-z0-9_]+", "_", page.lower()).strip("_")


def app_navigation():
    if "active_page" not in st.session_state:
        st.session_state.active_page = "Home"
    if "shared_page_seen_at" not in st.session_state:
        st.session_state.shared_page_seen_at = 0.0

    shared_page, shared_updated_at = read_shared_page(st.session_state.active_page)
    valid_pages = {page for page, _ in PAGES if page != "__live_call__"}
    if (
        shared_page in valid_pages
        and shared_updated_at > st.session_state.shared_page_seen_at
        and shared_page != st.session_state.active_page
    ):
        st.session_state.active_page = shared_page
        st.session_state.shared_page_seen_at = shared_updated_at

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
            padding: 0.62rem 1.65rem;
            border-radius: 999px;
            background: linear-gradient(135deg, #f4669c 0%, #db6dbd 52%, #a967e6 100%);
            color: white;
            font-size: 18px;
            font-weight: 900;
            box-shadow:
                inset 0 1px 0 rgba(255, 255, 255, 0.48),
                0 18px 34px rgba(189, 86, 174, 0.30);
        }}
        .st-key-nav_{active_key} button {{
            background: linear-gradient(135deg, #f4669c 0%, #db6dbd 52%, #a967e6 100%) !important;
            color: #ffffff !important;
            border: 1px solid rgba(255, 255, 255, 0.86) !important;
            font-weight: 900 !important;
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.55),
                0 18px 34px rgba(189, 86, 174, 0.34) !important;
            transform: translateY(-2px);
        }}
        .st-key-nav_{active_key} button:hover {{
            background: linear-gradient(135deg, #e85992 0%, #cb5fb0 52%, #9957d6 100%) !important;
            color: #ffffff !important;
        }}
        div.st-key-nav_{active_key} div[data-testid="stButton"] button,
        div.st-key-nav_{active_key} button {{
            min-height: 58px !important;
            border-radius: 15px !important;
            background: linear-gradient(135deg, #f4669c 0%, #db6dbd 52%, #a967e6 100%) !important;
            color: #ffffff !important;
            border: 1px solid rgba(255, 255, 255, 0.86) !important;
            font-family: Georgia, "Times New Roman", serif !important;
            font-size: clamp(16px, 1.55vw, 20px) !important;
            font-weight: 700 !important;
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.55),
                0 18px 34px rgba(189, 86, 174, 0.34) !important;
            transform: translateY(-2px);
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
                st.session_state.shared_page_seen_at = write_shared_page(page)
                st.rerun()

    return st.session_state.active_page
