"""
DMD Marquee image cache with on-demand downloading from Pixelcade.
First request for a game shows text, downloads DMD marquee in background, then swaps.
Subsequent requests are instant from cache.
"""
import os
import re
import logging
import threading
import urllib.request
import urllib.error
from PIL import Image

# Pixelcade system name mapping
# Recalbox SystemId -> Pixelcade repository folder
SYSTEM_MAP = {
    "mame": "mame",
    "fbneo": "mame",
    "neogeo": "neogeo",
    "nes": "nes",
    "snes": "snes",
    "n64": "n64",
    "gb": "gb",
    "gba": "gba",
    "gbc": "gbc",
    "megadrive": "genesis",
    "genesis": "genesis",
    "mastersystem": "mastersystem",
    "gamegear": "gamegear",
    "psx": "psx",
    "dreamcast": "dreamcast",
    "pcengine": "pcengine",
    "atari2600": "atari2600",
}

def sanitize_filename(name):
    """Sanitize a game name for Pixelcade filename format."""
    # Pixelcade uses the rom base name exactly, no special escaping needed
    # (e.g. tmnt.zip -> tmnt.png)
    return name


class DMDCache:
    def __init__(self, cache_dir=None):
        if cache_dir is None:
            cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache", "dmds")
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        self._current_request_id = 0
        self._lock = threading.Lock()
        self._negative_cache = set()  # Games we know don't have wheels

    def _cache_path(self, system, game_name):
        """Get the local cache file path for a game."""
        safe_sys = system.replace("/", "_")
        safe_name = sanitize_filename(game_name)
        sys_dir = os.path.join(self.cache_dir, safe_sys)
        os.makedirs(sys_dir, exist_ok=True)
        return os.path.join(sys_dir, f"{safe_name}.png")

    def get_cached(self, system, game_name):
        """Check if a DMD marquee image is already cached. Returns PIL Image or None."""
        path = self._cache_path(system, game_name)
        if os.path.exists(path):
            try:
                return Image.open(path).convert("RGBA")
            except Exception:
                os.remove(path)
        return None

    def _download_wheel(self, system, game_name):
        """Try to download a DMD marquee from Pixelcade GitHub."""
        pixelcade_system = SYSTEM_MAP.get(system, system)
        
        # We will try the exact name first, and if it fails, try a cleaned name (without tags)
        clean_name = re.sub(r'\s*\(.*?\)', '', game_name)
        clean_name = re.sub(r'\s*\[.*?\]', '', clean_name).strip()
        
        names_to_try = [game_name]
        if clean_name and clean_name != game_name:
            names_to_try.append(clean_name)
            
        for name_variant in names_to_try:
            safe_name = sanitize_filename(name_variant)
            
            for ext in [".png", ".gif"]:
                url = f"https://raw.githubusercontent.com/alinke/pixelcade/master/{pixelcade_system}/{urllib.request.quote(safe_name)}{ext}"
                
                try:
                    logging.info(f"DMDCache: Downloading DMD Marquee for '{name_variant}' [{system}]")
                    req = urllib.request.Request(url, headers={'User-Agent': 'ArcadeMatrix'})
                    with urllib.request.urlopen(req, timeout=5) as response:
                        data = response.read()
                        cache_path = self._cache_path(system, game_name) # Always save under original name
                        temp_path = f"{cache_path}.tmp.{threading.get_ident()}"
                        with open(temp_path, "wb") as f:
                            f.write(data)
                        os.rename(temp_path, cache_path)
                        logging.info(f"DMDCache: Cached '{game_name}' -> {cache_path}")
                        return Image.open(cache_path).convert("RGBA")
                except urllib.error.HTTPError as e:
                    if e.code == 404:
                        continue  # Try next extension/variant
                    logging.warning(f"DMDCache: HTTP Error {e.code} for {url}")
                except Exception as e:
                    logging.warning(f"DMDCache: Download failed: {e}")
                    
        return None

    def fetch_async(self, system, game_name, callback):
        """
        Fetch a DMD marquee image asynchronously.
        - If cached: calls callback immediately with the image
        - If not: downloads in background, calls callback when ready
        - Returns a request_id that can be used to cancel stale callbacks
        """
        with self._lock:
            self._current_request_id += 1
            request_id = self._current_request_id

        # Check cache first (instant)
        cached = self.get_cached(system, game_name)
        if cached:
            callback(cached, request_id)
            return request_id

        # Check negative cache (don't re-download known missing)
        cache_key = f"{system}/{game_name}"
        if cache_key in self._negative_cache:
            return request_id

        # Download in background
        def _worker():
            img = self._download_wheel(system, game_name)
            if img is None:
                self._negative_cache.add(cache_key)
                return
            callback(img, request_id)

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
        return request_id

    def is_current(self, request_id):
        """Check if a request_id is still the most recent one."""
        with self._lock:
            return request_id == self._current_request_id
