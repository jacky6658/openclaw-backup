#!/usr/bin/env python3
"""Simple Google Drive file downloader.

Usage:
  python drive_download.py FILE_ID [OUTPUT_PATH]
  python drive_download.py https://drive.google.com/file/d/FILE_ID/view

First run will open a browser window to authorize access.
Reuses credentials afterwards.
"""

import os
import re
import sys
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Scopes: read-only Drive access is enough for downloads
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

ROOT = Path.home() / "Library" / "Application Support" / "gogcli"
CLIENT_SECRET_PATH = ROOT / "credentials.json"  # reuse the same client_secret as gog
TOKEN_PATH = ROOT / "drive_downloader_token.json"


def extract_file_id(arg: str) -> str:
    """Accept either a bare file ID or a Drive URL and return the file ID."""
    # If it looks like a URL, try to extract /d/<id>
    if arg.startswith("http://") or arg.startswith("https://"):
        m = re.search(r"/d/([a-zA-Z0-9_-]+)/", arg)
        if not m:
            # Some links use id=<ID>
            m = re.search(r"id=([a-zA-Z0-9_-]+)", arg)
        if not m:
            raise SystemExit("無法從網址裡抓到 file ID，請直接給我 ID。")
        return m.group(1)
    return arg


def get_creds() -> Credentials:
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    else:
        creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CLIENT_SECRET_PATH.exists():
                raise SystemExit(
                    f"找不到 client_secret 檔案：{CLIENT_SECRET_PATH}\n"
                    "請確認 gog 的 credentials.json 存在。"
                )
            import json

            with CLIENT_SECRET_PATH.open("r", encoding="utf-8") as f:
                data = json.load(f)

            # gog 的 credentials.json 是扁平格式，手動包成 InstalledAppFlow 需要的結構
            client_config = {
                "installed": {
                    "client_id": data["client_id"],
                    "client_secret": data["client_secret"],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            }

            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        with TOKEN_PATH.open("w", encoding="utf-8") as f:
            f.write(creds.to_json())

    return creds


def main(argv: list[str]) -> None:
    if len(argv) < 2:
        print("用法：python drive_download.py FILE_ID [OUTPUT_PATH]")
        raise SystemExit(1)

    raw = argv[1]
    file_id = extract_file_id(raw)

    output_path: Path
    if len(argv) >= 3:
        output_path = Path(argv[2]).expanduser()
    else:
        # default: save into ./downloads/<file_id>
        out_dir = Path.cwd() / "downloads"
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = out_dir / file_id

    creds = get_creds()
    service = build("drive", "v3", credentials=creds)

    # Get metadata (to pick filename + mimeType)
    meta = (
        service.files()
        .get(fileId=file_id, fields="id, name, mimeType")
        .execute()
    )

    # If user didn't specify a filename, use Drive name
    if len(argv) < 3:
        safe_name = meta["name"].replace("/", "_")
        output_path = output_path.with_name(safe_name)

    mime = meta["mimeType"]

    # For Google Docs/Sheets/Slides types, use export; for binary files, use files().get_media
    from googleapiclient.http import MediaIoBaseDownload
    import io

    if mime.startswith("application/vnd.google-apps."):
        # Map Docs/Sheets to a reasonable export format
        export_mime = "application/pdf"
        if mime == "application/vnd.google-apps.document":
            export_mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif mime == "application/vnd.google-apps.spreadsheet":
            export_mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        request = service.files().export_media(fileId=file_id, mimeType=export_mime)
    else:
        request = service.files().get_media(fileId=file_id)

    fh = io.FileIO(output_path, "wb")
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        if status:
            print(f"下載中… {int(status.progress() * 100)}%", end="\r")

    fh.close()
    print(f"\n已下載：{output_path}")


if __name__ == "__main__":  # pragma: no cover
    main(sys.argv)
