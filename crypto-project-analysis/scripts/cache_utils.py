#!/usr/bin/env python3
"""
cache_utils.py — Simple file-based caching for crypto-project-analysis skill
Enables offline fallback when APIs are unreachable or rate-limited.

Usage in other scripts:
    from cache_utils import cached_fetch, save_to_cache, load_from_cache

Cache location: ../cache/ (relative to scripts/)
"""

import os
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Callable

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "cache")
DEFAULT_MAX_AGE_HOURS = 24


def _ensure_cache_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)


def _get_cache_path(key: str) -> str:
    """Create a safe filename from the key."""
    safe_key = hashlib.md5(key.encode("utf-8")).hexdigest()[:16]
    return os.path.join(CACHE_DIR, f"{safe_key}.json")


def save_to_cache(key: str, data: Dict[str, Any], source: str = "live"):
    """Save data to cache with timestamp and source info."""
    _ensure_cache_dir()
    cache_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": source,
        "key": key,
        "data": data
    }
    path = _get_cache_path(key)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cache_entry, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[CACHE WARN] Failed to write cache for {key}: {e}", file=sys.stderr)


def load_from_cache(key: str, max_age_hours: int = DEFAULT_MAX_AGE_HOURS) -> Optional[Dict[str, Any]]:
    """Load from cache if it exists and is not too old. Returns the inner 'data' or None."""
    path = _get_cache_path(key)
    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            entry = json.load(f)

        ts_str = entry.get("timestamp", "")
        if ts_str.endswith("Z"):
            ts_str = ts_str[:-1]
        cached_time = datetime.fromisoformat(ts_str)
        age = datetime.utcnow() - cached_time

        if age > timedelta(hours=max_age_hours):
            print(f"[CACHE] Cached data for '{key}' is {age.total_seconds()/3600:.1f}h old (older than {max_age_hours}h) — ignoring.", file=sys.stderr)
            return None

        data = entry.get("data")
        if data:
            print(f"[CACHE] Using cached data for '{key}' (age: {age.total_seconds()/3600:.1f}h, source: {entry.get('source', 'unknown')})", file=sys.stderr)
            return data
    except Exception as e:
        print(f"[CACHE WARN] Failed to read cache for {key}: {e}", file=sys.stderr)
    return None


def cached_fetch(
    key: str,
    fetch_func: Callable[[], Optional[Dict[str, Any]]],
    max_age_hours: int = DEFAULT_MAX_AGE_HOURS,
    force_refresh: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Try live fetch first. On failure (or if force_refresh=False and cache exists), fall back to cache.
    Always updates cache on successful live fetch.
    """
    if not force_refresh:
        cached = load_from_cache(key, max_age_hours=max_age_hours)
        if cached:
            return cached

    # Try live
    result = fetch_func()
    if result:
        save_to_cache(key, result, source="live")
        return result

    # Live failed — try cache as last resort (even if slightly stale)
    cached = load_from_cache(key, max_age_hours=72)  # more lenient on fallback
    if cached:
        print(f"[CACHE] Live fetch failed for '{key}'. Falling back to cached data.", file=sys.stderr)
        return cached

    return None


# For standalone testing
if __name__ == "__main__":
    import sys
    print("cache_utils.py — Simple caching helper for crypto-project-analysis skill")
    print(f"Cache directory: {os.path.abspath(CACHE_DIR)}")
    if len(sys.argv) > 1 and sys.argv[1] == "clear":
        for f in os.listdir(CACHE_DIR):
            if f.endswith(".json"):
                os.remove(os.path.join(CACHE_DIR, f))
        print("Cache cleared.")
    else:
        print("Usage: python cache_utils.py clear  # to wipe cache")
