#!/usr/bin/env python3
"""QA gate for a private Seed Zero upload, then optional publish.

usage: yt-qa.py NAME VIDEO_ID [--publish]

Reads projects/NAME/metadata.json and manifest.json (scene_duration sets
the accepted PT..S values), fetches the video with videos.list (1 quota
unit) and runs the 15-point gate. With --publish and a clean
gate it sets privacyStatus public with videos.update (50 units) and
re-reads the status 15 s later (1 unit). Appends to media/NAME/publish.log.
"""

from __future__ import annotations

import datetime as dt
import json
import sys
import time
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


def now() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def fetch(youtube, vid: str) -> dict:
    items = youtube.videos().list(
        id=vid, part="snippet,status,contentDetails,fileDetails,processingDetails,statistics"
    ).execute().get("items", [])
    if len(items) != 1:
        raise SystemExit(f"error: videos.list returned {len(items)} items for {vid}")
    return items[0]


def gate(v: dict, meta: dict, seconds: int) -> tuple[list[tuple[str, bool, str]], dict]:
    sn, st, cd = v["snippet"], v["status"], v["contentDetails"]
    durations = (f"PT{seconds}S", f"PT{seconds + 1}S")
    fd, pd = v.get("fileDetails", {}), v.get("processingDetails", {})
    streams = fd.get("videoStreams", [])
    src = f"{streams[0].get('widthPixels')}x{streams[0].get('heightPixels')}" if streams else "none"
    checks = [
        ("channel is Seed Zero", sn.get("channelId") == SEED_ZERO_ID, ""),
        ("uploadStatus processed", st.get("uploadStatus") == "processed", st.get("uploadStatus", "")),
        ("processingStatus succeeded", pd.get("processingStatus") == "succeeded", pd.get("processingStatus", "")),
        ("no rejection or failure", not st.get("rejectionReason") and not st.get("failureReason")
         and not pd.get("processingFailureReason"), ""),
        ("definition hd", cd.get("definition") == "hd", cd.get("definition", "")),
        ("embeddable", st.get("embeddable") is True, ""),
        ("source 1080x1920", src == "1080x1920", src if src != "1080x1920" else ""),
        ("title matches", sn.get("title") == meta["title"], sn.get("title", "")),
        ("description matches", sn.get("description") == meta["description"], ""),
        ("tags match (as a set)", set(sn.get("tags", [])) == set(meta["tags"]), str(sorted(sn.get("tags", [])))),
        ("categoryId 27", sn.get("categoryId") == "27", sn.get("categoryId", "")),
        ("madeForKids false", st.get("madeForKids") is False, str(st.get("madeForKids"))),
        ("selfDeclaredMadeForKids false", st.get("selfDeclaredMadeForKids") is False, str(st.get("selfDeclaredMadeForKids"))),
        (f"duration {durations[0]} or {durations[1]}", cd.get("duration") in durations, cd.get("duration", "")),
        ("private before publish", st.get("privacyStatus") == "private", st.get("privacyStatus", "")),
    ]
    extra = {
        "processingHints": pd.get("processingHints"),
        "containsSyntheticMedia": st.get("containsSyntheticMedia"),
        "publicStatsViewable": st.get("publicStatsViewable"),
        "license": st.get("license"),
        "publishedAt": sn.get("publishedAt"),
    }
    return checks, extra


def main() -> int:
    if len(sys.argv) not in (3, 4):
        print(__doc__, file=sys.stderr)
        return 2
    name, vid = sys.argv[1], sys.argv[2]
    publish = len(sys.argv) == 4 and sys.argv[3] == "--publish"
    meta = json.loads((REPO / f"projects/{name}/metadata.json").read_text())
    seconds = int(round(json.loads((REPO / f"projects/{name}/manifest.json").read_text())["scene_duration"]))
    log = REPO / f"media/{name}/publish.log"
    lines = [f"[{now()}] qa {name} {vid} publish={publish}"]
    quota = 0
    youtube = client()
    v = fetch(youtube, vid)
    quota += 1
    checks, extra = gate(v, meta, seconds)
    for label, ok, detail in checks:
        lines.append(f"  [{'ok' if ok else 'FAIL'}] {label}: {detail}")
    passed = sum(1 for _, ok, _ in checks if ok)
    lines.append(f"gate: {passed} of {len(checks)} pass; " + "; ".join(f"{k}={v_}" for k, v_ in extra.items()))
    if publish:
        if passed != len(checks):
            lines.append("publish refused: gate not clean")
        else:
            body = {
                "id": vid,
                "status": {
                    "privacyStatus": "public",
                    "selfDeclaredMadeForKids": False,
                    "containsSyntheticMedia": True,
                    "embeddable": True,
                },
            }
            youtube.videos().update(part="status", body=body).execute()
            quota += 50
            t_pub = now()
            time.sleep(15)
            st = youtube.videos().list(id=vid, part="status").execute()["items"][0]["status"]
            quota += 1
            lines.append(
                f"published: https://youtu.be/{vid} at {t_pub} ({dt.datetime.now(dt.timezone.utc).strftime('%H:%M:%SZ')} now); "
                f"re-read privacyStatus={st.get('privacyStatus')} madeForKids={st.get('madeForKids')} "
                f"selfDeclaredMadeForKids={st.get('selfDeclaredMadeForKids')} embeddable={st.get('embeddable')} "
                f"containsSyntheticMedia={st.get('containsSyntheticMedia')}"
            )
    lines.append(f"quota this run: {quota} units")
    text = "\n".join(lines) + "\n"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a") as f:
        f.write(text)
    print(text, end="")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
