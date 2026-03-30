"""
Build chart PNGs from metrics CSV (non-interactive backend).

  python tools/export_charts.py --in .tmp/ingest_x_metrics.csv --out-dir .tmp/charts_run
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402


def run_export_charts(csv_path: Path, out_dir: Path, top_n: int = 15) -> list[Path]:
    df = pd.read_csv(csv_path)
    if df.empty:
        raise RuntimeError("Empty CSV")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_paths: list[Path] = []

    def short_labels(series: pd.Series) -> pd.Series:
        return series.astype(str).str[:40] + series.astype(str).apply(lambda s: "..." if len(s) > 40 else "")

    top_views = df.sort_values("view_count", ascending=False).head(top_n).copy()
    top_views["label"] = short_labels(top_views["title"])

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(top_views["label"][::-1], top_views["view_count"][::-1], color="#2563eb")
    ax.set_xlabel("View count")
    ax.set_title("Top videos by views (sample)")
    fig.tight_layout()
    p1 = out_dir / "top_views.png"
    fig.savefig(p1, dpi=150)
    plt.close(fig)
    out_paths.append(p1)

    if "engagement_per_1k_views" in df.columns:
        t2 = df.sort_values("engagement_per_1k_views", ascending=False).head(top_n).copy()
        t2["label"] = short_labels(t2["title"])
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        ax2.barh(t2["label"][::-1], t2["engagement_per_1k_views"][::-1], color="#059669")
        ax2.set_xlabel("Likes + comments per 1k views (approx)")
        ax2.set_title("Top videos by engagement proxy")
        fig2.tight_layout()
        p2 = out_dir / "top_engagement.png"
        fig2.savefig(p2, dpi=150)
        plt.close(fig2)
        out_paths.append(p2)

    return out_paths


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--in", "-i", dest="in_path", type=Path, required=True)
    p.add_argument("--out-dir", "-d", type=Path, required=True)
    p.add_argument("--top", type=int, default=15)
    args = p.parse_args()
    try:
        paths = run_export_charts(args.in_path, args.out_dir, top_n=args.top)
    except Exception as e:
        print(e, file=sys.stderr)
        return 1
    for x in paths:
        print(f"Wrote {x}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
