from pathlib import Path
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen
import json
import re

import streamlit as st


CONFIG_PATH = Path(__file__).resolve().parents[1] / "data" / "iptv_login.json"


def _load_saved_login():
    if not CONFIG_PATH.exists():
        return {}
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _save_login(server_url, username, password):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        json.dumps(
            {
                "server_url": server_url,
                "username": username,
                "password": password,
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def _forget_saved_login():
    try:
        CONFIG_PATH.unlink(missing_ok=True)
    except OSError:
        pass


def _apply_saved_login_defaults():
    saved = _load_saved_login()
    defaults = {
        "iptv_server_url": saved.get("server_url", ""),
        "iptv_username": saved.get("username", ""),
        "iptv_password": saved.get("password", ""),
    }
    for key, value in defaults.items():
        if value and not st.session_state.get(key):
            st.session_state[key] = value


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


def _movie_url(server_url, username, password, stream_id, ext):
    return urljoin(server_url, f"movie/{username}/{password}/{stream_id}.{ext}")


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
    st.caption("If it does not play, the provider may block browser playback or require its own app.")


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
    st.subheader("Xtream Codes IPTV / imediaTELLY Login")
    _apply_saved_login_defaults()
    st.write("Enter legal IPTV provider details. The saved login is used for both Live TV and Movies.")

    server_url = _normalize_server(
        st.text_input("Server URL", key="iptv_server_url", placeholder="http://provider-server.com:8080")
    )
    username = st.text_input("Username", key="iptv_username")
    password = st.text_input("Password", key="iptv_password", type="password")
    content_type = st.radio("What do you want to watch?", ["Live TV", "Movies"], horizontal=True)
    ext = st.selectbox("Stream format", ["m3u8", "ts", "mp4", "mkv"], index=0)

    col1, col2 = st.columns(2)
    with col1:
        load_categories = st.button("Load Categories", use_container_width=True)
    with col2:
        clear_login = st.button("Clear IPTV Login", use_container_width=True)

    remember_login = st.checkbox("Remember login in this app", value=CONFIG_PATH.exists())
    if remember_login and server_url and username and password:
        _save_login(server_url, username, password)

    if clear_login:
        _forget_saved_login()
        for key in [
            "iptv_server_url",
            "iptv_username",
            "iptv_password",
            "iptv_categories",
            "iptv_streams",
            "iptv_movies",
        ]:
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
                    action = "get_live_categories" if content_type == "Live TV" else "get_vod_categories"
                    categories = _fetch_json(_xtream_url(server_url, username, password, action=action))
                    st.session_state.iptv_categories = categories if isinstance(categories, list) else []
                    st.session_state.iptv_streams = []
                    st.session_state.iptv_movies = []
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
        load_label = "Load Channels" if content_type == "Live TV" else "Load Movies"
        if st.button(load_label, use_container_width=True):
            try:
                action = "get_live_streams" if content_type == "Live TV" else "get_vod_streams"
                streams = _fetch_json(
                    _xtream_url(
                        server_url,
                        username,
                        password,
                        action=action,
                        category_id=category.get("category_id"),
                    )
                )
                if content_type == "Live TV":
                    st.session_state.iptv_streams = streams if isinstance(streams, list) else []
                    st.session_state.iptv_movies = []
                    st.success(f"Loaded {len(st.session_state.iptv_streams)} channels.")
                else:
                    st.session_state.iptv_movies = streams if isinstance(streams, list) else []
                    st.session_state.iptv_streams = []
                    st.success(f"Loaded {len(st.session_state.iptv_movies)} movies.")
            except Exception as exc:
                st.error(f"Could not load items: {exc}")

    streams = st.session_state.get("iptv_streams", [])
    if streams:
        search = st.text_input("Search IPTV channels", key="iptv_stream_search")
        filtered = [stream for stream in streams if not search or search.lower() in stream.get("name", "").lower()]
        selected = st.selectbox("Choose channel", filtered, format_func=lambda stream: stream.get("name", "Channel"))
        if selected:
            _play_stream(_stream_url(server_url, username, password, selected.get("stream_id"), ext))

    movies = st.session_state.get("iptv_movies", [])
    if movies:
        search = st.text_input("Search movies", key="iptv_movie_search")
        filtered = [movie for movie in movies if not search or search.lower() in movie.get("name", "").lower()]
        selected = st.selectbox("Choose movie", filtered, format_func=lambda movie: movie.get("name", "Movie"))
        if selected:
            movie_ext = selected.get("container_extension") or ext
            _play_stream(_movie_url(server_url, username, password, selected.get("stream_id"), movie_ext))


def show_iptv_smarters():
    st.title("IPTVSmartersPro / imediaTELLY")
    st.info(
        "This slide plays legal IPTV live channels and movies inside the program when the provider supports browser playback. "
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
