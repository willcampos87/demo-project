"""
End-to-end: latest pipeline CSV -> Google Slides -> Gmail (if REPORT_TO_EMAIL set).

  1. Run tools/run_pipeline.py first (or pass --csv).
  2. Run tools/google_oauth_auth.py once (credentials.json + token.json).
  3. Set REPORT_TO_EMAIL in .env.

  python tools/complete_youtube_report.py
  python tools/complete_youtube_report.py --csv path/to/metrics.csv
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from yt_common import ROOT

from build_yt_slides import run_build
from send_gmail_report import run_send


def _latest_metrics_csv() -> Path:
    tmp = ROOT / ".tmp"
    dirs = sorted(
        [p for p in tmp.glob("pipeline_*") if p.is_dir()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not dirs:
        raise RuntimeError("No .tmp/pipeline_* folder found. Run: python tools/run_pipeline.py")
    run_dir = dirs[0]
    candidates = list(run_dir.glob("ingest_*_metrics.csv"))
    if not candidates:
        raise RuntimeError(f"No ingest_*_metrics.csv under {run_dir}")
    return candidates[0]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--csv", type=Path, default=None)
    p.add_argument("--title", default="YouTube niche report")
    p.add_argument("--skip-email", action="store_true")
    args = p.parse_args()

    csv_path = args.csv or _latest_metrics_csv()
    if not csv_path.is_file():
        print(f"CSV not found: {csv_path}", file=sys.stderr)
        return 1

    try:
        url = run_build(csv_path, args.title)
    except Exception as e:
        print(e, file=sys.stderr)
        return 1

    print(f"Slides: {url}")

    if args.skip_email:
        return 0

    try:
        run_send(
            url,
            subject=f"{args.title} — deck link",
        )
    except Exception as e:
        print(f"Email skipped or failed: {e}", file=sys.stderr)
        print("Fix REPORT_TO_EMAIL in .env or run: python tools/send_gmail_report.py --slides-url ...")
        return 0

    print("Done — deck created and email sent (if Gmail succeeded).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
