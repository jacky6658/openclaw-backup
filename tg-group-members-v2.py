#!/usr/bin/env python3
"""
取得 Telegram 群組成員名單
輸出：user_id, username, 名字, 電話（有的話）
"""

import asyncio
import csv
from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

# === 固定設定 ===
API_ID = 36809032
API_HASH = "2b6a76191a426f7a03a1918702154628"
PHONE = "+886958616744"
# ================

async def get_members(client, group):
    entity = await client.get_entity(group)
    members = []
    offset = 0
    limit = 200

    while True:
        participants = await client(GetParticipantsRequest(
            channel=entity,
            filter=ChannelParticipantsSearch(''),
            offset=offset,
            limit=limit,
            hash=0
        ))
        if not participants.users:
            break
        members.extend(participants.users)
        offset += len(participants.users)
        print(f"已取得 {len(members)} 人...")
        await asyncio.sleep(1)

    return members

async def main():
    # 讓使用者輸入群組
    print("=" * 40)
    print("TG 群組成員抓取工具")
    print("=" * 40)
    group_input = input("請輸入群組 ID 或 username（例如：-1002997693797 或 some_group）：").strip()

    # 自動轉換為數字（如果是群組 ID）
    try:
        group = int(group_input)
    except ValueError:
        group = group_input

    import os
    output_file = os.path.expanduser(f"~/Downloads/tg_members_{group_input.replace('-','')}.csv")

    async with TelegramClient('tg_session', API_ID, API_HASH,
                               device_model='iPhone 15',
                               system_version='iOS 17.0',
                               app_version='10.3.1') as client:
        await client.start(PHONE, password='Chen051285')
        print("✅ 登入成功")

        print(f"開始抓取群組：{group}")
        members = await get_members(client, group)
        print(f"\n總計 {len(members)} 位成員")

        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['user_id', 'username', '名字', '電話'])
            for m in members:
                if m.bot:
                    continue
                name = f"{m.first_name or ''} {m.last_name or ''}".strip()
                writer.writerow([
                    m.id,
                    m.username or '',
                    name,
                    m.phone or ''
                ])

        print(f"✅ 已儲存到 {output_file}")

asyncio.run(main())
