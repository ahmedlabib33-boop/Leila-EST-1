from urllib.parse import quote

import streamlit as st


DEFAULT_ROOM = "LeilaESTPrepLiveClass"


def _clean_room_name(value):
    cleaned = "".join(ch for ch in value.strip() if ch.isalnum() or ch in "-_")
    return cleaned or DEFAULT_ROOM


def get_live_call_url():
    room_name = _clean_room_name(st.session_state.get("live_call_room", DEFAULT_ROOM))
    st.session_state.live_call_room = room_name
    return f"https://meet.jit.si/{quote(room_name)}#config.prejoinPageEnabled=true"


def show_call_launcher():
    meet_url = get_live_call_url()
    st.link_button("Live Call", meet_url, use_container_width=True)
