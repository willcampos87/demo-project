"""
Send a short HTML email with a link (e.g. to your Slides deck).

Requires token.json from tools/google_oauth_auth.py and REPORT_TO_EMAIL in .env.

  python tools/send_gmail_report.py --slides-url "https://docs.google.com/presentation/d/..."
"""
from __future__ import annotations

import argparse
import base64
import html
import os
import sys
from email.mime.text import MIMEText

from dotenv import load_dotenv
from googleapiclient.discovery import build

from google_creds import load_credentials
from yt_common import ROOT


def run_send(slides_url: str, subject: str, body_text: str | None = None) -> None:
    load_dotenv(ROOT / ".env")
    to_addr = (os.environ.get("REPORT_TO_EMAIL") or "").strip()
    if not to_addr:
        raise RuntimeError("Set REPORT_TO_EMAIL in .env (recipient address).")

    creds = load_credentials()
    gmail = build("gmail", "v1", credentials=creds, cache_discovery=False)

    safe_url = html.escape(slides_url, quote=True)
    html_body = body_text or (
        "<p>Your YouTube niche report deck is ready.</p>"
        f'<p><a href="{safe_url}">Open Google Slides</a></p>'
    )
    msg = MIMEText(html_body, "html")
    msg["to"] = to_addr
    msg["subject"] = subject
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    gmail.users().messages().send(userId="me", body={"raw": raw}).execute()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--slides-url", "-u", required=True)
    p.add_argument("--subject", "-s", default="YouTube niche report (Slides)")
    p.add_argument("--body", "-b", default=None, help="Optional plain override; default is HTML with link")
    args = p.parse_args()
    try:
        run_send(args.slides_url, args.subject, args.body)
    except Exception as e:
        print(e, file=sys.stderr)
        return 1
    print("OK — email sent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
