"""Shared YouTube API client for tools (API key from .env)."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from googleapiclient.discovery import build

ROOT = Path(__file__).resolve().parent.parent


def get_youtube():
    load_dotenv(ROOT / ".env")
    key = (os.environ.get("YOUTUBE_API_KEY") or "").strip()
    if not key:
        raise RuntimeError("Missing YOUTUBE_API_KEY in .env")
    return build("youtube", "v3", developerKey=key, cache_discovery=False)
