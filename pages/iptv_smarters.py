from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen
import json
import re

import streamlit as st


def _normalize_server(server_url):
    server_url = (server_url or "").strip()
    if not server_url:
        return ""
    if not server_url.startswith(("http://", "https://")):
        server_url = "http://" + server_url
    return server_url.rstrip("/") + "/"


def _fetch_json(url, timeout=15):
    request = Request(url, headers={"User-Agent": "LeilaESTPrep/1.0"})
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


def _fetch_text(url, timeout=15):
    request = Request(url, headers={"User-Agent": "LeilaESTPrep/1.0"})
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def _xtream_url(server_url, username, password, **params):
    query = {"username": username, "password": password}
    query.update(params)
    return urljoin(server_url, "player_api.php") + "?" + urlencode(query)


def _stream_url(server_url, username, password, stream_id, ext):
    return urljoin(server_url, f"live/{username}/{password}/{stream_id}.{ext}")


def _parse_m3u(text):
    channels = []
    title = ""
    logo = ""
    group = ""

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        if line.startswith("#EXTINF"):
            name_match = re.search(r",(.+)$", line)
            logo_match = re.search(r'tvg-logo="([^"]*)"', line)
            group_match = re.search(r'group-title="([^"]*)"', line)
            title = name_match.group(1).strip() if name_match else "Channel"
            logo = logo_match.group(1).strip() if logo_match else ""
            group = group_match.group(1).strip() if group_match else ""
            continue

        if not line.startswith("#") and line.startswith(("http://", "https://")):
            channels.append({"name": title or line, "url": line, "logo": logo, "group": group})
            title = ""
            logo = ""
            group = ""

    return channels


def _play_stream(stream_url):
    st.video(stream_url)
    st.caption("If a channel does not play, the provider may block browser playback or require its own app.")


def _show_direct_player():
    st.subheader("Direct IPTV Player")
    st.write("Use a legal direct `.m3u8` channel link or a legal M3U playlist URL.")

    direct_url = st.text_input(
        "M3U playlist URL or direct HLS/M3U8 stream URL",
        key="iptv_direct_url",
        placeholder="https://example.com/playlist.m3u or https://example.com/channel.m3u8",
    )

    col1, col2 = st.columns(2)
    with col1:
        load_playlist = st.button("Load Playlist", use_container_width=True)
    with col2:
        play_direct = st.button("Play Direct Link", use_container_width=True)

    if play_direct and direct_url:
        _play_stream(direct_url)

    if load_playlist and direct_url:
        try:
            channels = _parse_m3u(_fetch_text(direct_url))
            st.session_state.iptv_m3u_channels = channels
            st.success(f"Loaded {len(channels)} channels.")
        except Exception as exc:
            st.error(f"Could not load playlist: {exc}")

    channels = st.session_state.get("iptv_m3u_channels", [])
    if channels:
        search = st.text_input("Search playlist channels", key="iptv_m3u_search")
        filtered = [
            channel
            for channel in channels
            if not search
            or search.lower() in channel["name"].lower()
            or search.lower() in channel.get("group", "").lower()
        ]
        selected = st.selectbox(
            "Choose channel",
            filtered,
            format_func=lambda channel: f"{channel.get('group', '')} - {channel['name']}".strip(" -"),
        )
        if selected:
            _play_stream(selected["url"])


def _show_xtream_player():
    st.subheader("Xtream Codes IPTV Login")
    st.write("Enter legal IPTV provider details. They are kept only in the current running app session.")

    server_url = _normalize_server(
        st.text_input("Server URL", key="iptv_server_url", placeholder="http://provider-server.com:8080")
    )
    username = st.text_input("Username", key="iptv_username")
    password = st.text_input("Password", key="iptv_password", type="password")
    ext = st.selectbox("Stream format", ["m3u8", "ts"], index=0)

    col1, col2 = st.columns(2)
    with col1:
        load_categories = st.button("Load IPTV Categories", use_container_width=True)
    with col2:
        clear_login = st.button("Clear IPTV Login", use_container_width=True)

    if clear_login:
        for key in ["iptv_server_url", "iptv_username", "iptv_password", "iptv_categories", "iptv_streams"]:
            st.session_state.pop(key, None)
        st.rerun()

    if load_categories:
        if not server_url or not username or not password:
            st.warning("Enter server URL, username, and password first.")
        else:
            try:
                auth = _fetch_json(_xtream_url(server_url, username, password))
                user_info = auth.get("user_info", {}) if isinstance(auth, dict) else {}
                if str(user_info.get("auth", "1")) == "0":
                    st.error("The provider rejected this login.")
                else:
                    categories = _fetch_json(_xtream_url(server_url, username, password, action="get_live_categories"))
                    st.session_state.iptv_categories = categories if isinstance(categories, list) else []
                    st.success(f"Loaded {len(st.session_state.iptv_categories)} categories.")
            except Exception as exc:
                st.error(f"Could not connect to IPTV provider: {exc}")

    categories = st.session_state.get("iptv_categories", [])
    if categories:
        category = st.selectbox(
            "Choose category",
            categories,
            format_func=lambda item: item.get("category_name", "Category"),
        )
        if st.button("Load Channels", use_container_width=True):
            try:
                streams = _fetch_json(
                    _xtream_url(
                        server_url,
                        username,
                        password,
                        action="get_live_streams",
                        category_id=category.get("category_id"),
                    )
                )
                st.session_state.iptv_streams = streams if isinstance(streams, list) else []
                st.success(f"Loaded {len(st.session_state.iptv_streams)} channels.")
            except Exception as exc:
                st.error(f"Could not load channels: {exc}")

    streams = st.session_state.get("iptv_streams", [])
    if streams:
        search = st.text_input("Search IPTV channels", key="iptv_stream_search")
        filtered = [stream for stream in streams if not search or search.lower() in stream.get("name", "").lower()]
        selected = st.selectbox("Choose channel", filtered, format_func=lambda stream: stream.get("name", "Channel"))
        if selected:
            _play_stream(_stream_url(server_url, username, password, selected.get("stream_id"), ext))


def show_iptv_smarters():
    st.title("IPTVSmartersPro")
    st.info(
        "This slide plays legal IPTV streams inside the program when the provider supports browser playback. "
        "Use only an IPTV subscription you are allowed to use."
    )

    mode = st.radio(
        "Choose IPTV connection type",
        ["Xtream Codes Login", "Direct M3U / HLS Link"],
        horizontal=True,
    )

    if mode == "Xtream Codes Login":
        _show_xtream_player()
    else:
        _show_direct_player()
