"""
Channel discovery via YouTube Data API search.list (type=channel).

Quota: each request costs 100 units (see Google quota docs). Use sparingly;
prefer known channel IDs + playlist ingest for routine runs.

Run from repo root:
  python tools/discover_channels.py
  python tools/discover_channels.py --query "AI agents" --max-results 5
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser(description="Discover YouTube channels by search query.")
    parser.add_argument(
        "--query",
        "-q",
        default="AI automation",
        help="Search query (default: AI automation)",
    )
    parser.add_argument(
        "--max-results",
        "-n",
        type=int,
        default=5,
        help="Max channels to return (1-50, default: 5)",
    )
    args = parser.parse_args()
    n = max(1, min(50, args.max_results))

    load_dotenv(ROOT / ".env")
    key = (os.environ.get("YOUTUBE_API_KEY") or "").strip()
    if not key:
        print("Missing YOUTUBE_API_KEY in .env", file=sys.stderr)
        return 1

    print("Note: search.list uses 100 quota units per request.", file=sys.stderr)

    try:
        youtube = build("youtube", "v3", developerKey=key, cache_discovery=False)
        resp = (
            youtube.search()
            .list(part="snippet", type="channel", q=args.query, maxResults=n)
            .execute()
        )
    except HttpError as e:
        print(f"YouTube API error: {e}", file=sys.stderr)
        return 1

    items = resp.get("items") or []
    if not items:
        print("No channels returned (try a different query).")
        return 0

    print(f"Query: {args.query!r}\n")
    for i, it in enumerate(items, 1):
        sn = it.get("snippet") or {}
        rid = it.get("id") or {}
        cid = rid.get("channelId") or sn.get("channelId") or "?"
        title = sn.get("title", "(no title)")
        desc = (sn.get("description") or "").replace("\n", " ")[:120]
        print(f"{i}. {title}")
        print(f"   channel_id: {cid}")
        if desc:
            print(f"   {desc}...")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
