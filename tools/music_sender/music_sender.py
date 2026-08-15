#!/usr/bin/env python3
"""
music_sender.py - Capture now-playing info from Windows and expose via HTTP.

Detection chain:
1. WinRT Global Media Session API (real metadata: artist, title, elapsed, duration)
2. Browser extension POST (Deezer, Spotify Web, YouTube, etc.)
3. pycaw fallback (detects active audio)
"""

import sys
import os
import time
import json
import threading
import re
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- WinRT: Windows Global Media Session ---
try:
    from winrt.windows.media.control import (
        GlobalSystemMediaTransportControlsSessionManager,
        GlobalSystemMediaTransportControlsSession,
    )
    HAS_WINRT = True
except ImportError:
    HAS_WINRT = False

# --- pycaw: audio session detection ---
try:
    from pycaw.pycaw import AudioUtilities
    HAS_PYCAW = True
except ImportError:
    HAS_PYCAW = False

# --- pygetwindow: window title parsing ---
try:
    import pygetwindow as gw
    HAS_GETWINDOW = True
except ImportError:
    HAS_GETWINDOW = False

# Global state
current_track = {
    "artist": "",
    "title": "",
    "elapsed": 0,
    "duration": 0,
    "source": "none",
    "playing": False
}

# Web extension data has priority for TTL seconds
last_web_update = 0
WEB_UPDATE_TTL = 30


class NowPlayingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/nowplaying":
            global current_track, last_web_update
            now = time.time()
            if current_track["source"] == "web" and (now - last_web_update) < WEB_UPDATE_TTL:
                response = {
                    "artist": current_track["artist"],
                    "title": current_track["title"],
                    "elapsed": current_track["elapsed"],
                    "duration": current_track["duration"],
                    "source": "web",
                    "playing": True
                }
            elif current_track.get("playing"):
                response = {
                    "artist": current_track["artist"],
                    "title": current_track["title"],
                    "elapsed": current_track["elapsed"],
                    "duration": current_track["duration"],
                    "source": current_track["source"],
                    "playing": True
                }
            else:
                response = {"playing": False}
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        elif self.path == "/health":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/nowplaying":
            global current_track, last_web_update
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                title = data.get("title", "").strip()
                if not title:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "skipped", "reason": "empty title"}).encode())
                    return
                current_track = {
                    "artist": data.get("artist", ""),
                    "title": title,
                    "elapsed": int(data.get("elapsed", 0)),
                    "duration": int(data.get("duration", 0)),
                    "source": "web",
                    "playing": True
                }
                last_web_update = time.time()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok"}).encode())
            except Exception as e:
                print(f"POST error: {e}")
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok"}).encode())
            except Exception as e:
                print(f"POST error: {e}")
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress default logging
        pass


# =============================================================================
# DETECTION: WinRT Global Media Session
# =============================================================================

def _winrt_get_session():
    """Get the current media session via WinRT."""
    if not HAS_WINRT:
        return None
    try:
        manager = GlobalSystemMediaTransportControlsSessionManager()
        session = manager.get_current_session()
        return session
    except Exception:
        return None


def _winrt_get_properties(session):
    """Get media properties from a session."""
    try:
        props = session.try_get_media_properties()
        return props
    except Exception:
        return None


def _winrt_to_track(props):
    """Convert WinRT media properties to our track dict."""
    try:
        title = props.title or ""
        artist_list = props.artists or []
        artist = ", ".join(artist_list) if artist_list else ""
        album = props.album_title or ""

        # Try to get playback position
        elapsed = 0
        duration = 0
        try:
            position = props.position
            if position:
                elapsed = int(position.total_seconds())
        except (AttributeError, Exception):
            pass
        try:
            dur = props.duration
            if dur:
                duration = int(dur.total_seconds())
        except (AttributeError, Exception):
            pass

        if title or artist:
            return {
                "artist": artist,
                "title": title,
                "elapsed": elapsed,
                "duration": duration,
                "source": "winrt",
                "playing": True
            }
    except Exception:
        pass
    return None


def detect_winrt():
    """Try WinRT Global Media Session API."""
    session = _winrt_get_session()
    if session is None:
        return None
    props = _winrt_get_properties(session)
    if props is None:
        return None
    return _winrt_to_track(props)


# =============================================================================
# DETECTION: Window title parsing (VLC, Spotify Desktop, etc.)
# =============================================================================

_PLAYER_NAMES = ["vlc", "spotify", "foobar", "musicbee", "itunes", "groove", "mediaplayer"]
_PLAYER_SUFFIX_RE = re.compile(
    r'\s*[-—|•]\s*.*(?:' + '|'.join(re.escape(p) for p in _PLAYER_NAMES) + r')\b.*$',
    re.IGNORECASE
)
_EXT_RE = re.compile(
    r'\.(mp3|mp4|flac|wav|ogg|aac|m4a|wma|opus|m4v|webm)\s*$',
    re.IGNORECASE
)
_SEPARATORS = [" - ", " | ", " • ", " – "]
_TIME_RE = re.compile(r'(\d{1,2}):(\d{2})(?::(\d{2}))?')


def _clean_window_title(raw, player_names=None):
    """Remove player suffix and file extension from window title."""
    text = _PLAYER_SUFFIX_RE.sub('', raw)
    text = _EXT_RE.sub('', text)
    return text.strip()


def _parse_time_from_title(title):
    """Extract elapsed time from window title like '1:23 / 3:45'."""
    elapsed = 0
    duration = 0
    match = _TIME_RE.search(title)
    if match:
        m, s = int(match.group(1)), int(match.group(2))
        ms = int(match.group(3)) if match.group(3) else 0
        elapsed = m * 60 + s
        # Look for duration after a separator
        rest = title[match.end():]
        m2 = _TIME_RE.search(rest)
        if m2:
            mm, ss = int(m2.group(1)), int(m2.group(2))
            duration = mm * 60 + ss
    return elapsed, duration


def detect_window_titles():
    """Parse window titles of media players."""
    if not HAS_GETWINDOW:
        return None
    try:
        best_win = None
        for win in gw.getAllWindows():
            title = win.title.strip()
            if not title or win.isMinimized:
                continue
            for player in _PLAYER_NAMES:
                if player.lower() in title.lower():
                    # Prefer windows with separators (more info)
                    if best_win is None or any(s in title for s in _SEPARATORS):
                        best_win = win
                    break

        if best_win is None:
            return None

        raw_title = best_win.title.strip()
        cleaned = _clean_window_title(raw_title)

        # Extract time info from raw title before cleaning
        elapsed, duration = _parse_time_from_title(raw_title)

        # Parse "Artist - Title" from cleaned
        for sep in _SEPARATORS:
            if sep in cleaned:
                parts = cleaned.split(sep, 1)
                artist = parts[0].strip()
                track_title = parts[1].strip()
                if artist and track_title:
                    return {
                        "artist": artist,
                        "title": track_title,
                        "elapsed": elapsed,
                        "duration": duration,
                        "source": "window",
                        "playing": True
                    }

        # No separator: cleaned is the filename or title
        if cleaned:
            return {
                "artist": "Media Player",
                "title": cleaned,
                "elapsed": elapsed,
                "duration": duration,
                "source": "window",
                "playing": True
            }

        return None
    except Exception as e:
        print(f"Window detection error: {e}")
        return None


# =============================================================================
# DETECTION: pycaw fallback
# =============================================================================

def detect_pycaw():
    """Detect active audio sessions via pycaw (skip browsers - they use extension instead)."""
    if not HAS_PYCAW:
        return None
    _BROWSER_EXES = {"brave.exe", "chrome.exe", "msedge.exe", "firefox.exe", "opera.exe", "vivaldi.exe"}
    try:
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.State == 0:
                pname = ""
                if session.Process:
                    pname = session.Process.name() if callable(session.Process.name) else session.Process.name
                if pname and pname.lower() not in _BROWSER_EXES:
                    return {
                        "artist": "Native Player",
                        "title": pname,
                        "elapsed": 0,
                        "duration": 0,
                        "source": "pycaw",
                        "playing": True
                    }
        return None
    except Exception as e:
        print(f"pycaw error: {e}")
        return None


# =============================================================================
# MAIN UPDATE LOOP
# =============================================================================

def update_current_track():
    """Periodically update track info using detection chain."""
    global current_track, last_web_update

    try:
        # Web extension data has priority during TTL
        now = time.time()
        if current_track["source"] == "web" and (now - last_web_update) < WEB_UPDATE_TTL:
            return  # Keep web data, don't overwrite

        # 1. WinRT (real metadata from Windows Media Session)
        track = detect_winrt()

        # 2. Window title parsing
        if track is None:
            track = detect_window_titles()

        # 3. pycaw fallback (skips browser processes - handled by extension)
        if track is None:
            track = detect_pycaw()

        if track and track["playing"]:
            current_track = track
        elif track is None and current_track.get("playing"):
            current_track["playing"] = False
            current_track["artist"] = ""
            current_track["title"] = ""
    except Exception as e:
        print(f"Update error: {e}")


# =============================================================================
# SERVER
# =============================================================================

def run_server(port=8085):
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, NowPlayingHandler)
    print(f"Server listening on port {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Music sender for ArcadeMatrix_RPI')
    parser.add_argument('--port', '-p', type=int, default=8085)
    args = parser.parse_args()

    # Start server in background thread
    server_thread = threading.Thread(target=run_server, args=(args.port,), daemon=True)
    server_thread.start()

    print(f"music_sender running on port {args.port}")
    print("Detection: WinRT -> Window titles -> pycaw | Web extension: POST /nowplaying")

    try:
        while True:
            update_current_track()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped.")
