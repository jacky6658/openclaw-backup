#!/usr/bin/env python3
"""
取得 Telegram 群組成員名單 v3
使用 iter_participants，無需管理員權限
"""

import asyncio
import csv
import os
from telethon import TelegramClient
from telethon.tl.types import InputPeerChannel

API_ID = 36809032
API_HASH = "2b6a76191a426f7a03a1918702154628"
PHONE = "+886958616744"

async def main():
    print("=" * 40)
    print("TG 群組成員抓取工具 v3")
    print("=" * 40)
    group_input = input("請輸入群組 ID 或 username：").strip()

    try:
        group = int(group_input)
    except ValueError:
        group = group_input

    output_file = os.path.expanduser(f"~/Downloads/tg_members_{str(group_input).replace('-','')}.csv")

    async with TelegramClient('tg_session', API_ID, API_HASH,
                               device_model='iPhone 15',
                               system_version='iOS 17.0',
                               app_version='10.3.1') as client:
        await client.start(PHONE, password='Chen051285')
        print("✅ 登入成功")
        print(f"開始抓取群組：{group}")

        members = []
        count = 0

        async for user in client.iter_participants(group):
            if user.bot:
                continue
            members.append(user)
            count += 1
            if count % 200 == 0:
                print(f"已取得 {count} 人...")
            await asyncio.sleep(0.3)

        print(f"\n總計 {len(members)} 位成員")

        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['user_id', 'username', '名字', '電話'])
            for m in members:
                name = f"{m.first_name or ''} {m.last_name or ''}".strip()
                writer.writerow([
                    m.id,
                    m.username or '',
                    name,
                    m.phone or ''
                ])

        print(f"✅ 已儲存到 {output_file}")

asyncio.run(main())
