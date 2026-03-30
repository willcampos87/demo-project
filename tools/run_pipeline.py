"""
Run ingest → metrics → charts (Phases 1–3). Slides + Gmail need OAuth; not included.

  python tools/run_pipeline.py
  python tools/run_pipeline.py --max-per-channel 5
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from yt_common import ROOT

# Import step runners (same directory)
from compute_metrics import run_compute
from export_charts import run_export_charts
from ingest_uploads import DEFAULT_SEED_CHANNELS, run_ingest


def main() -> int:
    p = argparse.ArgumentParser(description="YouTube niche pipeline: ingest → metrics → charts")
    p.add_argument("--channels", "-c", default=DEFAULT_SEED_CHANNELS, help="Comma-separated channel IDs")
    p.add_argument("--max-per-channel", "-n", type=int, default=10)
    p.add_argument(
        "--run-dir",
        type=Path,
        default=None,
        help="Output folder under .tmp (default: .tmp/pipeline_<utc timestamp>)",
    )
    args = p.parse_args()
    chans = [x.strip() for x in args.channels.split(",") if x.strip()]
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = args.run_dir or (ROOT / ".tmp" / f"pipeline_{ts}")
    run_dir.mkdir(parents=True, exist_ok=True)

    jsonl = run_dir / f"ingest_{ts}.jsonl"
    csv_path = run_dir / f"ingest_{ts}_metrics.csv"
    charts_dir = run_dir / "charts"

    print("Step 1/3: ingest uploads...", file=sys.stderr)
    try:
        run_ingest(chans, args.max_per_channel, jsonl)
    except Exception as e:
        print(f"Ingest failed: {e}", file=sys.stderr)
        return 1

    print("Step 2/3: compute metrics...", file=sys.stderr)
    try:
        run_compute(jsonl, csv_path)
    except Exception as e:
        print(f"Metrics failed: {e}", file=sys.stderr)
        return 1
    print(f"  {csv_path}", file=sys.stderr)

    print("Step 3/3: export charts...", file=sys.stderr)
    try:
        paths = run_export_charts(csv_path, charts_dir)
    except Exception as e:
        print(f"Charts failed: {e}", file=sys.stderr)
        return 1
    for x in paths:
        print(f"  {x}", file=sys.stderr)

    print("\nDone.")
    print(f"Run directory: {run_dir}")
    print(f"JSONL: {jsonl}")
    print(f"CSV:   {csv_path}")
    print(f"Charts: {charts_dir}")
    print("\nSlides + Gmail are not in this pipeline (require OAuth). See plans/youtube-niche-intelligence.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
