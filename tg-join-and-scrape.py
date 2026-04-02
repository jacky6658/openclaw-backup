#!/usr/bin/env python3
"""
TG 批量加入群組 + 抓成員名單
自動加入清單內所有群組，並抓取成員存成 CSV
"""

import asyncio
import csv
import os
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest

API_ID = 36809032
API_HASH = "2b6a76191a426f7a03a1918702154628"
PHONE = "+886958616744"

# ===== 要加入並抓取的群組清單 =====
GROUPS = [
    "taiwanjob",           # Job & career of Taiwan
    "TW_IT_Job",           # TW-IT Job
    "tech_TW",             # 科技閒聊群組
    "it_normal_life_new",  # IT人的生活日常
    "devopstw",            # DevOps 台灣
    "dotnet_tw",           # TW .NET Developer
    "ISDATW",              # ISDA 公開群
    "HWDTaiwan",           # 公園 Web Developer
]
# ====================================

OUTPUT_DIR = os.path.expanduser("~/Downloads/tg_scrape")

async def join_group(client, group):
    try:
        await client(JoinChannelRequest(group))
        print(f"✅ 加入成功：{group}")
        await asyncio.sleep(3)
    except Exception as e:
        print(f"⚠️ 加入失敗 {group}：{e}")

async def scrape_members(client, group):
    try:
        members = []
        count = 0
        async for user in client.iter_participants(group):
            if user.bot:
                continue
            members.append(user)
            count += 1
            if count % 100 == 0:
                print(f"  已取得 {count} 人...")
            await asyncio.sleep(0.2)
        return members
    except Exception as e:
        print(f"⚠️ 抓取失敗 {group}：{e}")
        return []

async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 45)
    print("TG 批量加入 + 抓成員工具")
    print("=" * 45)
    print(f"目標群組數：{len(GROUPS)} 個")
    print(f"輸出目錄：{OUTPUT_DIR}")
    print()

    mode = input("選擇模式：\n1. 只加入群組（不抓成員）\n2. 只抓成員（已加入的群組）\n3. 加入 + 抓成員\n請輸入(1/2/3)：").strip()

    async with TelegramClient('tg_session', API_ID, API_HASH,
                               device_model='iPhone 15',
                               system_version='iOS 17.0',
                               app_version='10.3.1') as client:
        await client.start(PHONE, password='Chen051285')
        print("\n✅ 登入成功\n")

        all_members = []

        for group in GROUPS:
            print(f"\n處理群組：{group}")

            # 加入群組
            if mode in ['1', '3']:
                await join_group(client, group)

            # 抓成員
            if mode in ['2', '3']:
                print(f"  開始抓取 {group} 的成員...")
                members = await scrape_members(client, group)
                print(f"  取得 {len(members)} 位成員")

                # 存個別 CSV
                output_file = os.path.join(OUTPUT_DIR, f"tg_{group}.csv")
                with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(['user_id', 'username', '名字', '電話', '來源群組'])
                    for m in members:
                        name = f"{m.first_name or ''} {m.last_name or ''}".strip()
                        writer.writerow([m.id, m.username or '', name, m.phone or '', group])

                all_members.extend([(m, group) for m in members])
                await asyncio.sleep(5)  # 每個群組間隔 5 秒

        # 合併所有成員去重後存一個大 CSV
        if mode in ['2', '3'] and all_members:
            seen_ids = set()
            unique_members = []
            for m, grp in all_members:
                if m.id not in seen_ids:
                    seen_ids.add(m.id)
                    unique_members.append((m, grp))

            merged_file = os.path.join(OUTPUT_DIR, "tg_all_members_merged.csv")
            with open(merged_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['user_id', 'username', '名字', '電話', '來源群組'])
                for m, grp in unique_members:
                    name = f"{m.first_name or ''} {m.last_name or ''}".strip()
                    writer.writerow([m.id, m.username or '', name, m.phone or '', grp])

            print(f"\n{'='*45}")
            print(f"✅ 完成！")
            print(f"總計抓取：{len(all_members)} 筆")
            print(f"去重後：{len(unique_members)} 位唯一用戶")
            print(f"合併檔案：{merged_file}")
            print(f"各群組個別檔案：{OUTPUT_DIR}/")

asyncio.run(main())
