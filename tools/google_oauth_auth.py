"""
One-time (or occasional) OAuth login for Google Slides + Gmail send.

Prerequisites:
  1. Google Cloud project with these APIs enabled:
     - Google Slides API
     - Gmail API
  2. OAuth consent screen configured (External is fine for testing; add yourself as test user).
  3. OAuth 2.0 Client ID of type "Desktop app" — download JSON and save as:
       <project_root>/credentials.json

Run from project root:
  python tools/google_oauth_auth.py

Opens a browser to sign in and approve scopes, then writes token.json (gitignored).
"""
from __future__ import annotations

import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from google_creds import CREDENTIALS_PATH, SCOPES, TOKEN_PATH


def main() -> int:
    if not CREDENTIALS_PATH.is_file():
        print(
            "Missing credentials.json in project root.\n"
            f"Expected: {CREDENTIALS_PATH}\n\n"
            "You need the FULL downloaded JSON from Google Cloud (not only the Client ID string):\n"
            "  APIs & Services → Credentials → your OAuth 2.0 Client ID → Download (arrow icon)\n"
            "  Rename the file to credentials.json and put it here.",
            file=sys.stderr,
        )
        return 1

    creds: Credentials | None = None
    if TOKEN_PATH.is_file():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
            creds = flow.run_local_server(port=0, prompt="consent")

    TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
    print(f"OK — saved OAuth token to {TOKEN_PATH}")
    print("You can run Slides/Gmail tools that use this token.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
