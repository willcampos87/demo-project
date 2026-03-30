"""
Summarize ingested JSONL into a metrics CSV (views, engagement proxy).

  python tools/compute_metrics.py --in .tmp/ingest_xxx.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd


def load_videos_jsonl(path: Path) -> pd.DataFrame:
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            if "_meta" in obj:
                continue
            rows.append(obj)
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


def run_compute(in_path: Path, out_path: Path) -> Path:
    df = load_videos_jsonl(in_path)
    if df.empty:
        raise RuntimeError("No video rows in JSONL")
    views = df["view_count"].clip(lower=0)
    engagement = (df["like_count"].fillna(0) + df["comment_count"].fillna(0)) / views.replace(0, float("nan"))
    engagement = engagement.fillna(0) * 1000.0
    df = df.assign(engagement_per_1k_views=engagement.round(4))
    df = df.sort_values("view_count", ascending=False)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    return out_path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--in", "-i", dest="in_path", type=Path, required=True)
    p.add_argument("--out", "-o", type=Path, default=None)
    args = p.parse_args()
    stem = args.in_path.stem
    out = args.out or (args.in_path.parent / f"{stem}_metrics.csv")
    try:
        path = run_compute(args.in_path, out)
    except Exception as e:
        print(e, file=sys.stderr)
        return 1
    print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
