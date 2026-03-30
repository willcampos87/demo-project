"""
Ingest recent uploads for seed channels (playlist-based, quota-friendly).

Writes JSONL to .tmp/ — one JSON object per line per video.

  python tools/ingest_uploads.py --channels UCxxx,UCyyy --max-per-channel 10
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from googleapiclient.errors import HttpError

from yt_common import ROOT, get_youtube

# Default: three AI-automation channels (override with --channels)
DEFAULT_SEED_CHANNELS = (
    "UCjWpQlNWtRo_3zZtvyBsmdg,UC2ojq-nuP8ceeHqiroeKhBA,UCuU3oDzMkwAD8gCLjgnF-Xw"
)


def _uploads_playlist_id(youtube, channel_id: str) -> str | None:
    r = youtube.channels().list(part="contentDetails", id=channel_id).execute()
    items = r.get("items") or []
    if not items:
        return None
    return (items[0].get("contentDetails") or {}).get("relatedPlaylists", {}).get("uploads")


def _collect_video_ids(youtube, playlist_id: str, max_n: int) -> list[str]:
    ids: list[str] = []
    page = None
    while len(ids) < max_n:
        req = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=min(50, max_n - len(ids)),
            pageToken=page,
        )
        resp = req.execute()
        for it in resp.get("items") or []:
            vid = (it.get("contentDetails") or {}).get("videoId")
            if vid:
                ids.append(vid)
            if len(ids) >= max_n:
                break
        page = resp.get("nextPageToken")
        if not page:
            break
    return ids[:max_n]


def _normalize_video(item: dict) -> dict:
    sn = item.get("snippet") or {}
    st = item.get("statistics") or {}
    cd = item.get("contentDetails") or {}
    vc = st.get("viewCount")
    lc = st.get("likeCount")
    cc = st.get("commentCount")
    return {
        "video_id": item.get("id"),
        "channel_id": sn.get("channelId"),
        "channel_title": sn.get("channelTitle"),
        "title": sn.get("title"),
        "published_at": sn.get("publishedAt"),
        "description": (sn.get("description") or "")[:800],
        "view_count": int(vc) if vc is not None else 0,
        "like_count": int(lc) if lc is not None else 0,
        "comment_count": int(cc) if cc is not None else 0,
        "duration": cd.get("duration"),
    }


def _fetch_videos(youtube, video_ids: list[str]) -> list[dict]:
    rows: list[dict] = []
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i : i + 50]
        r = (
            youtube.videos()
            .list(part="snippet,statistics,contentDetails", id=",".join(chunk))
            .execute()
        )
        for it in r.get("items") or []:
            rows.append(_normalize_video(it))
    return rows


def run_ingest(
    channel_ids: list[str],
    max_per_channel: int,
    out_path: Path,
) -> Path:
    youtube = get_youtube()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    all_rows: list[dict] = []
    for cid in channel_ids:
        cid = cid.strip()
        if not cid:
            continue
        upl = _uploads_playlist_id(youtube, cid)
        if not upl:
            print(f"Skip unknown channel: {cid}", file=sys.stderr)
            continue
        vids = _collect_video_ids(youtube, upl, max_per_channel)
        if not vids:
            print(f"No videos for channel {cid}", file=sys.stderr)
            continue
        all_rows.extend(_fetch_videos(youtube, vids))

    meta = {
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "channel_count": len(channel_ids),
        "max_per_channel": max_per_channel,
        "video_count": len(all_rows),
    }
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(json.dumps({"_meta": meta}, ensure_ascii=False) + "\n")
        for row in all_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return out_path


def main() -> int:
    p = argparse.ArgumentParser(description="Ingest recent uploads for channels.")
    p.add_argument(
        "--channels",
        "-c",
        default=DEFAULT_SEED_CHANNELS,
        help="Comma-separated channel IDs",
    )
    p.add_argument("--max-per-channel", "-n", type=int, default=10)
    p.add_argument(
        "--out",
        "-o",
        type=Path,
        default=None,
        help="Output JSONL path (default: .tmp/ingest_<timestamp>.jsonl)",
    )
    args = p.parse_args()
    chans = [x.strip() for x in args.channels.split(",") if x.strip()]
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out = args.out or (ROOT / ".tmp" / f"ingest_{ts}.jsonl")

    try:
        path = run_ingest(chans, args.max_per_channel, out)
    except HttpError as e:
        print(f"YouTube API error: {e}", file=sys.stderr)
        return 1
    except RuntimeError as e:
        print(e, file=sys.stderr)
        return 1

    print(f"Wrote {path} ({path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
