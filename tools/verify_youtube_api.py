"""
Read-only check: one videos.list call using YOUTUBE_API_KEY from project .env.
Run from repo root:  python tools/verify_youtube_api.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    load_dotenv(ROOT / ".env")
    key = (os.environ.get("YOUTUBE_API_KEY") or "").strip()
    if not key:
        print("Missing YOUTUBE_API_KEY in .env", file=sys.stderr)
        return 1

    # Public video ID — minimal quota (videos.list = 1 unit per request)
    test_id = "dQw4w9WgXcQ"

    try:
        youtube = build("youtube", "v3", developerKey=key, cache_discovery=False)
        resp = (
            youtube.videos()
            .list(part="snippet,statistics", id=test_id, maxResults=1)
            .execute()
        )
    except HttpError as e:
        print(f"YouTube API error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    items = resp.get("items") or []
    if not items:
        print("Unexpected: empty items (check API key restrictions)", file=sys.stderr)
        return 1

    snip = items[0]["snippet"]
    stats = items[0].get("statistics") or {}
    title = snip.get("title", "(no title)")
    views = stats.get("viewCount", "?")
    print("OK - YouTube Data API v3 accepted your API key.")
    print(f"Sample video title: {title}")
    print(f"View count (public): {views}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
