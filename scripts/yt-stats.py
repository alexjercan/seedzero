#!/usr/bin/env python3
"""Refresh web/data/status.json and web/data/slate.json from the channel.

usage: yt-stats.py [--dry-run]

Reads the Seed Zero uploads playlist and every video's statistics
(channels.list 1 unit, playlistItems.list 1 unit per 50 videos,
videos.list 1 unit per 50 videos). Updates views and likes on every slate
entry that carries a video URL, appends entries for videos the slate does
not list yet (ordered by publish time), keeps non-video entries such as
the backlog line at the end, and writes the per-video view total, the
subscriber count and the video count to status.json. With --dry-run it
prints the result and writes nothing.
"""

from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

REPO = Path(__file__).resolve().parents[1]
SEED_ZERO_ID = "UCWXsZTvrh_OHkzt6v1xkTsw"


def client():
    creds = Credentials.from_authorized_user_file(str(REPO / "secrets/token.json"))
    if not creds.valid:
        creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)


def video_id(url: str) -> str:
    return url.rsplit("/", 1)[-1]


def main() -> int:
    dry = "--dry-run" in sys.argv
    youtube = client()
    quota = 0
    channel = youtube.channels().list(part="id,contentDetails,statistics", mine=True).execute()["items"]
    quota += 1
    if [c["id"] for c in channel] != [SEED_ZERO_ID]:
        print("error: token does not see exactly the Seed Zero channel", file=sys.stderr)
        return 1
    uploads = channel[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    subscribers = int(channel[0]["statistics"]["subscriberCount"])

    ids: list[str] = []
    page = None
    while True:
        res = youtube.playlistItems().list(
            playlistId=uploads, part="contentDetails", maxResults=50, pageToken=page
        ).execute()
        quota += 1
        ids += [it["contentDetails"]["videoId"] for it in res.get("items", [])]
        page = res.get("nextPageToken")
        if not page:
            break

    videos: dict[str, dict] = {}
    for i in range(0, len(ids), 50):
        res = youtube.videos().list(id=",".join(ids[i:i + 50]), part="snippet,status,statistics").execute()
        quota += 1
        for v in res.get("items", []):
            videos[v["id"]] = v

    slate_path = REPO / "web/data/slate.json"
    status_path = REPO / "web/data/status.json"
    slate = json.loads(slate_path.read_text())
    status = json.loads(status_path.read_text())

    listed = [e for e in slate if "url" in e]
    others = [e for e in slate if "url" not in e]
    seen = set()
    for entry in listed:
        vid = video_id(entry["url"])
        seen.add(vid)
        v = videos.get(vid)
        if v is None:
            print(f"warning: {vid} is in the slate but not on the channel", file=sys.stderr)
            continue
        entry["views"] = int(v["statistics"].get("viewCount", 0))
        entry["likes"] = int(v["statistics"].get("likeCount", 0))
        entry["status"] = v["status"]["privacyStatus"]
    new = [v for vid, v in videos.items() if vid not in seen]
    new.sort(key=lambda v: v["snippet"]["publishedAt"])
    for v in new:
        published = dt.datetime.fromisoformat(v["snippet"]["publishedAt"].replace("Z", "+00:00")).astimezone()
        listed.append({
            "title": v["snippet"]["title"],
            "status": v["status"]["privacyStatus"],
            "date": published.strftime("%Y-%m-%d"),
            "url": f"https://youtu.be/{v['id']}",
            "views": int(v["statistics"].get("viewCount", 0)),
            "likes": int(v["statistics"].get("likeCount", 0)),
        })
    slate = listed + others

    total_views = sum(int(v["statistics"].get("viewCount", 0)) for v in videos.values())
    status["updated_at"] = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    status["stats"]["subscribers"] = subscribers
    status["stats"]["views"] = total_views
    status["stats"]["videos"] = len(videos)

    summary = (f"channel: {len(videos)} videos, {total_views} views (per-video sum), {subscribers} subscribers; "
               f"slate: {len(listed)} video entries ({len(new)} added); quota {quota} units")
    if dry:
        print(json.dumps(status, indent=2))
        print(json.dumps(slate[-4:], indent=2))
        print(summary)
        return 0
    slate_path.write_text(json.dumps(slate, indent=2) + "\n")
    status_path.write_text(json.dumps(status, indent=2) + "\n")
    print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
