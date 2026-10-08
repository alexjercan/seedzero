#!/usr/bin/env python3
"""Upload a finished short to the Seed Zero channel as private.

usage: yt-upload.py NAME

Reads projects/NAME/metadata.json and uploads media/NAME/final.mp4 with
one multipart videos.insert request (1,600 quota units). Verifies first
that the token sees exactly the Seed Zero channel, then prints the new
video id. After a failed insert it lists the uploads playlist, because a
failed response does not prove that no video was created.
"""

from __future__ import annotations

import datetime as dt
import json
import sys
import time
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_httplib2 import AuthorizedHttp
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

REPO = Path(__file__).resolve().parent.parent
SEED_ZERO_ID = "UCWXsZTvrh_OHkzt6v1xkTsw"
UPLOADS_PLAYLIST = "UUWXsZTvrh_OHkzt6v1xkTsw"
TRANSIENT = {401, 410, 500, 502, 503, 504}


def execute(request, tries: int = 4, delay_seconds: int = 10):
    """Run a cheap read; retry transient answers (2026-10-08: 401s for a
    token that worked seconds before and after)."""
    for attempt in range(1, tries + 1):
        try:
            return request.execute()
        except HttpError as error:
            if attempt == tries or error.resp.status not in TRANSIENT:
                raise
            print(f"transient HTTP {error.resp.status}; retry {attempt} of {tries - 1} in {delay_seconds} s", file=sys.stderr)
            time.sleep(delay_seconds)


def find_recent_upload(youtube, title: str, since: dt.datetime) -> str | None:
    """Return the id of a video with this title created since `since`.

    2026-10-08: the media PUT answered 410 Gone although the insert had
    created the video, so a failed next_chunk() does not prove that no
    video exists. Check before counting the attempt as empty (1 unit).
    """
    items = execute(youtube.playlistItems().list(
        playlistId=UPLOADS_PLAYLIST, part="snippet", maxResults=5
    )).get("items", [])
    for item in items:
        snippet = item["snippet"]
        created = dt.datetime.fromisoformat(snippet["publishedAt"].replace("Z", "+00:00"))
        if snippet["title"] == title and created >= since:
            return snippet["resourceId"]["videoId"]
    return None


def client():
    creds = Credentials.from_authorized_user_file(str(REPO / "secrets/token.json"))
    if not creds.valid:
        creds.refresh(Request())
    # No silent refresh-and-resend on 401: every insert request this
    # script sends must be one recorded attempt (2026-10-08: the library's
    # hidden resend after a 401 blip turned into a 410 on a dead session).
    http = AuthorizedHttp(creds, refresh_status_codes=())
    return build("youtube", "v3", http=http)


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

    if len(meta["title"]) > 100:
        print(f"error: title is {len(meta['title'])} characters; YouTube allows 100", file=sys.stderr)
        return 1
    if len(meta["description"]) > 5000:
        print(f"error: description is {len(meta['description'])} characters; YouTube allows 5,000", file=sys.stderr)
        return 1
    for field in ("title", "description"):
        if "<" in meta[field] or ">" in meta[field]:
            # videos.insert rejects the whole request with invalidTitle or
            # invalidDescription before any media is sent (2026-09-24: the
            # "->" arrows in a description cost an insert attempt).
            print(f"error: {field} contains < or >, which YouTube rejects", file=sys.stderr)
            return 1

    youtube = client()
    channels = execute(youtube.channels().list(part="id", mine=True))["items"]
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
    # One multipart request (metadata plus the whole file) instead of a
    # resumable session: a 3 MB short needs no chunking, and one request
    # is half the exposure to the 401 blips seen on 2026-10-08. The
    # request is sent exactly once; a failure here is one spent attempt.
    media = MediaFileUpload(str(video), mimetype="video/mp4", resumable=False)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    started = dt.datetime.now(dt.timezone.utc) - dt.timedelta(seconds=30)
    try:
        response = request.execute()
    except HttpError as error:
        print(f"insert failed: HTTP {error.resp.status} {error.reason}", file=sys.stderr)
        time.sleep(10)
        found = find_recent_upload(youtube, meta["title"], started)
        if found:
            print(f"but the uploads playlist holds a new video with this title: {found} https://youtu.be/{found}", file=sys.stderr)
            print("check it with scripts/yt-qa.py before any replacement upload", file=sys.stderr)
        else:
            print("the uploads playlist holds no new video with this title", file=sys.stderr)
        return 1
    print(f"uploaded: {response['id']} https://youtu.be/{response['id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
