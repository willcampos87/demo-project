"""
YouTube niche pipeline running in Modal's cloud (Monday 06:00 UTC cron).

Setup (one-time):
  1. pip install modal
  2. python -m modal setup                    (browser auth)
  3. Create Modal Secret named 'youtube-niche-secrets' at modal.com/secrets with:
       YOUTUBE_API_KEY   - from your .env
       REPORT_TO_EMAIL   - from your .env
       GOOGLE_TOKEN_JSON - full contents of your local token.json
  4. python -m modal deploy tools/modal_pipeline.py

Manual test:
  python -m modal run tools/modal_pipeline.py::run_weekly

Remove cron:
  modal app stop youtube-niche-weekly
"""
from __future__ import annotations

import sys
from pathlib import Path

import modal

# ---------------------------------------------------------------------------
# Image — debian slim + all Python dependencies + local tools/ folder mounted
# ---------------------------------------------------------------------------
_THIS_DIR = Path(__file__).resolve().parent

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install(
        "python-dotenv>=1.0.0",
        "google-api-python-client>=2.0.0",
        "google-auth-httplib2>=0.2.0",
        "google-auth-oauthlib>=1.0.0",
        "pandas>=2.0.0",
        "matplotlib>=3.8.0",
        "Pillow>=10.0.0",
    )
    .add_local_dir(str(_THIS_DIR), remote_path="/app/tools")
)

app = modal.App("youtube-niche-weekly")

yt_secrets = modal.Secret.from_name("youtube-niche-secrets")
vol = modal.Volume.from_name("youtube-niche-tmp", create_if_missing=True)

# ---------------------------------------------------------------------------
# Scheduled function
# ---------------------------------------------------------------------------

@app.function(
    image=image,
    secrets=[yt_secrets],
    volumes={"/tmp/yt": vol},  # nosec B108 — container-local path, not shared OS temp
    schedule=modal.Cron("0 6 * * 1"),  # every Monday 06:00 UTC
    timeout=600,
)
def run_weekly() -> None:
    """Ingest -> metrics -> charts -> Slides -> Gmail."""
    import os
    from datetime import datetime, timezone

    # Add tools to Python path (Modal mounts them at /app/tools)
    sys.path.insert(0, "/app/tools")

    import google_creds as _gc
    from build_yt_slides import run_build
    from compute_metrics import run_compute
    from export_charts import run_export_charts
    from ingest_uploads import DEFAULT_SEED_CHANNELS, run_ingest
    from send_gmail_report import run_send

    # ------------------------------------------------------------------
    # Write OAuth token from Modal Secret to a temp file so that
    # load_credentials() (file-based) can find it.  google_creds.TOKEN_PATH
    # is a module-level variable, so patching it here affects all callers.
    # ------------------------------------------------------------------
    token_json = os.environ.get("GOOGLE_TOKEN_JSON", "")
    if not token_json.strip():
        raise RuntimeError(
            "GOOGLE_TOKEN_JSON is missing from Modal Secret 'youtube-niche-secrets'. "
            "Paste the contents of your local token.json there."
        )
    token_path = Path("/tmp/token.json")  # nosec B108 — Modal container filesystem
    token_path.write_text(token_json, encoding="utf-8")
    _gc.TOKEN_PATH = token_path  # redirect load_credentials() to this temp file

    # ------------------------------------------------------------------
    # Run directory inside the Modal Volume mount
    # ------------------------------------------------------------------
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = Path("/tmp/yt") / f"pipeline_{ts}"  # nosec B108 — Modal Volume mount point
    run_dir.mkdir(parents=True, exist_ok=True)

    jsonl = run_dir / f"ingest_{ts}.jsonl"
    csv_path = run_dir / f"ingest_{ts}_metrics.csv"
    charts_dir = run_dir / "charts"

    # Step 1: ingest
    chans = [c.strip() for c in DEFAULT_SEED_CHANNELS.split(",") if c.strip()]
    print("Step 1/4: ingest uploads...")
    run_ingest(chans, 10, jsonl)
    print(f"  {jsonl}")

    # Step 2: metrics
    print("Step 2/4: compute metrics...")
    run_compute(jsonl, csv_path)
    print(f"  {csv_path}")

    # Step 3: charts
    print("Step 3/4: export charts...")
    chart_paths = run_export_charts(csv_path, charts_dir)
    for p in chart_paths:
        print(f"  {p}")
    vol.commit()  # persist charts to Modal Volume

    # Step 4: Slides + Gmail
    print("Step 4/4: build Slides deck...")
    url = run_build(csv_path, "YouTube niche report")
    print(f"  Slides: {url}")

    to_addr = (os.environ.get("REPORT_TO_EMAIL") or "").strip()
    if to_addr:
        run_send(url, subject="YouTube niche report - deck link")
        print("  Email sent.")
    else:
        print("  REPORT_TO_EMAIL not set - skipping email.")

    print("\nDone.")
