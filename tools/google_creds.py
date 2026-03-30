"""Load OAuth2 user credentials for Google Slides / Gmail (token.json)."""
from __future__ import annotations

import json
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

ROOT = Path(__file__).resolve().parent.parent
CREDENTIALS_PATH = ROOT / "credentials.json"
TOKEN_PATH = ROOT / "token.json"

SCOPES = [
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/gmail.send",
]


def load_credentials() -> Credentials:
    if not TOKEN_PATH.is_file():
        raise RuntimeError(
            f"Missing OAuth token. Place credentials.json in the project root, then run:\n"
            f"  python tools/google_oauth_auth.py\n"
            f"Expected token at: {TOKEN_PATH}"
        )
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    refreshed = False
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            refreshed = True
        else:
            raise RuntimeError("Token invalid; run: python tools/google_oauth_auth.py")
    if refreshed:
        TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
    return creds


def load_credentials_from_json(token_json: str) -> Credentials:
    """Load credentials from a raw token JSON string (e.g. from a Modal Secret env var).

    In-memory only — refreshes if expired but does not persist the updated token.
    Suitable for cloud execution where token.json is not on disk.
    """
    creds = Credentials.from_authorized_user_info(json.loads(token_json), SCOPES)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise RuntimeError(
                "Google OAuth token is invalid. Re-paste a fresh token.json into the "
                "Modal Secret 'youtube-niche-secrets' as GOOGLE_TOKEN_JSON."
            )
    return creds
