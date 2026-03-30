"""
Create a Google Slides deck from a pipeline metrics CSV (text summary).

Requires token.json from tools/google_oauth_auth.py.

  python tools/build_yt_slides.py --csv .tmp/pipeline_xxx/ingest_*_metrics.csv
"""
from __future__ import annotations

import argparse
import csv
import sys
import uuid
from pathlib import Path

from googleapiclient.discovery import build

from google_creds import load_credentials
from yt_common import ROOT


def _text_from_csv(csv_path: Path, max_rows: int = 12) -> str:
    lines = ["YouTube niche snapshot — top videos by views\n\n"]
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= max_rows:
                break
            title = (row.get("title") or "")[:90]
            views = row.get("view_count", "")
            ch = (row.get("channel_title") or "")[:45]
            eng = row.get("engagement_per_1k_views", "")
            lines.append(f"• {title}\n  {views} views · engagement/1k ≈ {eng} · {ch}\n\n")
    return "".join(lines)


def run_build(csv_path: Path, deck_title: str) -> str:
    creds = load_credentials()
    slides = build("slides", "v1", credentials=creds, cache_discovery=False)

    pres = slides.presentations().create(body={"title": deck_title}).execute()
    presentation_id = pres["presentationId"]

    pres_full = slides.presentations().get(presentationId=presentation_id).execute()
    slide_list = pres_full.get("slides") or []
    if not slide_list:
        raise RuntimeError("New presentation has no slides")
    slide_id = slide_list[0]["objectId"]

    body_text = _text_from_csv(csv_path)
    box_id = f"textbox_{uuid.uuid4().hex[:12]}"

    emu = "EMU"
    requests = [
        {
            "createShape": {
                "objectId": box_id,
                "shapeType": "TEXT_BOX",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {
                        "height": {"magnitude": 4500000, "unit": emu},
                        "width": {"magnitude": 8500000, "unit": emu},
                    },
                    "transform": {
                        "scaleX": 1,
                        "scaleY": 1,
                        "translateX": 400000,
                        "translateY": 400000,
                        "unit": emu,
                    },
                },
            }
        },
        {"insertText": {"objectId": box_id, "insertionIndex": 0, "text": body_text}},
    ]
    slides.presentations().batchUpdate(
        presentationId=presentation_id, body={"requests": requests}
    ).execute()

    url = f"https://docs.google.com/presentation/d/{presentation_id}/edit"
    return url


def main() -> int:
    p = argparse.ArgumentParser(description="Build Slides deck from metrics CSV")
    p.add_argument("--csv", "-c", type=Path, required=True)
    p.add_argument("--title", "-t", default="YouTube niche report")
    args = p.parse_args()
    if not args.csv.is_file():
        print(f"Not found: {args.csv}", file=sys.stderr)
        return 1
    try:
        url = run_build(args.csv, args.title)
    except Exception as e:
        print(e, file=sys.stderr)
        return 1
    print(url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
