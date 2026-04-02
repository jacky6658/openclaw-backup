#!/usr/bin/env python3
"""
列出你加入的所有 TG 群組和 ID
"""

import asyncio
from telethon import TelegramClient
from telethon.tl.types import Channel, Chat

API_ID = 36809032
API_HASH = "2b6a76191a426f7a03a1918702154628"
PHONE = "+886958616744"

async def main():
    async with TelegramClient('tg_session', API_ID, API_HASH,
                               device_model='iPhone 15',
                               system_version='iOS 17.0',
                               app_version='10.3.1') as client:
        await client.start(PHONE, password='Chen051285')
        print("✅ 登入成功\n")
        print(f"{'群組名稱':<30} {'群組 ID':<20} {'人數'}")
        print("-" * 65)

        async for dialog in client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                entity = dialog.entity
                members = getattr(entity, 'participants_count', '?')
                print(f"{dialog.name[:28]:<30} {dialog.id:<20} {members}")

asyncio.run(main())
