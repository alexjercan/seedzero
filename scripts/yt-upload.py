#!/usr/bin/env python3
"""Upload a finished short to the Seed Zero channel as private.

usage: yt-upload.py NAME

Reads projects/NAME/metadata.json and uploads media/NAME/final.mp4 with
videos.insert (1,600 quota units). Verifies first that the token sees
exactly the Seed Zero channel, then prints the new video id.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

REPO = Path(__file__).resolve().parent.parent
SEED_ZERO_ID = "UCWXsZTvrh_OHkzt6v1xkTsw"


def client():
    creds = Credentials.from_authorized_user_file(str(REPO / "secrets/token.json"))
    if not creds.valid:
        creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: yt-upload.py NAME", file=sys.stderr)
        return 2
    name = sys.argv[1]
    meta = json.loads((REPO / f"projects/{name}/metadata.json").read_text())
    video = REPO / f"media/{name}/final.mp4"
    if not video.exists():
        print(f"error: missing {video}", file=sys.stderr)
        return 1

    youtube = client()
    channels = youtube.channels().list(part="id", mine=True).execute()["items"]
    if [c["id"] for c in channels] != [SEED_ZERO_ID]:
        print("error: token does not see exactly the Seed Zero channel", file=sys.stderr)
        return 1

    body = {
        "snippet": {
            "title": meta["title"],
            "description": meta["description"],
            "tags": meta["tags"],
            "categoryId": meta["categoryId"],
        },
        "status": {
            "privacyStatus": meta["privacyStatus"],
            "selfDeclaredMadeForKids": meta["selfDeclaredMadeForKids"],
            "containsSyntheticMedia": meta["containsSyntheticMedia"],
        },
    }
    media = MediaFileUpload(str(video), mimetype="video/mp4", resumable=True)
    request = youtube.videos().insert(
        part="snippet,status", body=body, media_body=media
    )
    response = None
    while response is None:
        _, response = request.next_chunk()
    print(f"uploaded: {response['id']} https://youtu.be/{response['id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
