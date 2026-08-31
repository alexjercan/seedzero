#!/usr/bin/env python3
"""One-time OAuth authorization for the Seed Zero channel.

Opens a browser login. Pick the Seed Zero brand-channel identity in the
account chooser, never the main-account identity. Stores the refresh token
at secrets/token.json, then verifies the token sees exactly one channel.
"""

from __future__ import annotations

import sys
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

REPO = Path(__file__).resolve().parent.parent
CLIENT_SECRET = REPO / "secrets" / "client_secret.json"
TOKEN = REPO / "secrets" / "token.json"
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]


def main() -> int:
    if not CLIENT_SECRET.exists():
        print(f"error: {CLIENT_SECRET} not found", file=sys.stderr)
        return 1

    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
    creds = flow.run_local_server(
        port=0,
        access_type="offline",
        prompt="consent",
        authorization_prompt_message=(
            "Open this URL and pick the SEED ZERO channel identity:\n{url}"
        ),
    )
    TOKEN.write_text(creds.to_json())
    print(f"token stored at {TOKEN}")

    youtube = build("youtube", "v3", credentials=creds)
    response = youtube.channels().list(part="snippet", mine=True).execute()
    channels = response.get("items", [])
    for channel in channels:
        print(f"channel: {channel['snippet']['title']} ({channel['id']})")

    if len(channels) != 1:
        print("error: expected exactly one channel", file=sys.stderr)
        return 1
    title = channels[0]["snippet"]["title"]
    if title != "Seed Zero":
        print(
            f"error: token sees '{title}', not Seed Zero. Delete "
            f"{TOKEN} and rerun, picking the Seed Zero identity.",
            file=sys.stderr,
        )
        return 1
    print("ok: token is scoped to the Seed Zero channel only")
    return 0


if __name__ == "__main__":
    sys.exit(main())
