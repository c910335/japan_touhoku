#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate comprehensive iCalendar (.ics) and Google Calendar CSV files for the Tohoku 20-Day Itinerary.
1. tohoku_itinerary_full.ics (All 317+ detailed transit, dining, spots, and hotel steps + 20 day banners)
2. tohoku_itinerary_essential.ics (Core milestones: 44 spots, 40 dining, 9 hotels, Shinkansen, flights)
3. tohoku_calendar_google.csv (Google Calendar compatible CSV format)
"""

import os
import re
import json
import csv
from pathlib import Path
from datetime import datetime, timedelta, timezone

BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / 'dist'
DATA_JSON_PATH = str(DIST_DIR / 'itinerary_data.json')
OUTPUT_ICS_FULL = str(DIST_DIR / 'tohoku_itinerary_full.ics')
OUTPUT_ICS_CALENDAR = str(DIST_DIR / 'tohoku_calendar.ics')
OUTPUT_ICS_ESSENTIAL = str(DIST_DIR / 'tohoku_itinerary_essential.ics')
OUTPUT_CSV_GOOGLE = str(DIST_DIR / 'tohoku_calendar_google.csv')

def clean_text_for_calendar(text: str) -> str:
    if not text:
        return ""
    text = text.replace(r'\n', '\n')
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('**', '').replace('`', '').replace('*', '')
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def escape_ics_text(text: str) -> str:
    if not text:
        return ""
    # Normalize any literal '\n' string to actual newline character
    text = text.replace(r'\n', '\n')
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # RFC 5545 escaping order:
    # 1. Backslashes must be escaped first as '\\'
    text = text.replace('\\', '\\\\')
    # 2. Semicolons and commas
    text = text.replace(';', r'\;')
    text = text.replace(',', r'\,')
    # 3. Newlines in iCalendar text format must be escaped as '\n' (single backslash + n)
    text = text.replace('\n', r'\n')
    return text

def parse_time_str(time_str: str):
    if not time_str:
        return None
    m = re.search(r'(\d{1,2}):(\d{2})', time_str)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None

def format_iso_time(base_date_str: str, hour: int, minute: int):
    d = datetime.strptime(base_date_str, '%Y-%m-%d')
    dt = d.replace(hour=hour, minute=minute, second=0)
    return dt.strftime('%Y%m%dT%H%M%S')

def is_essential_item(item: dict) -> bool:
    cat = item.get('category', '')
    title = item.get('title', '')
    
    # Spots, Dining, Hotel checkin/checkout/stays
    if cat in ['spot', 'dining', 'activity']:
        return True
    if cat == 'hotel' and any(k in title for k in ['Check-in', '入住', '退房', '寄放行李', '宿：', '住宿', '天泉', '溫泉']):
        return True
    if cat == 'transit' and any(k in title for k in ['新幹線', 'はやぶさ', 'BR122', 'BR117', '直飛', '專車啟程', '拼車', '觀光船', '仁王丸', '抵達青森']):
        return True
    return False

def generate():
    with open(DATA_JSON_PATH, 'r', encoding='utf-8') as f:
        days_data = json.load(f)

    full_events = []
    essential_events = []
    csv_rows = []

    dtstamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')

    for day in days_data:
        day_num = day['day']
        iso_date = day['iso_date']
        date_obj = datetime.strptime(iso_date, '%Y-%m-%d')
        next_date_obj = date_obj + timedelta(days=1)
        next_iso_date = next_date_obj.strftime('%Y%m%d')
        curr_iso_date = date_obj.strftime('%Y%m%d')

        day_title = clean_text_for_calendar(day.get('title', ''))
        day_subtitle = clean_text_for_calendar(day.get('subtitle', ''))
        luggage_note = clean_text_for_calendar(day.get('luggage_note', ''))
        region = day.get('region', '東北')

        # 1. Day Banner (All-day event)
        banner_summary = f"🍁【Day {day_num:02d}・{region}】{day_subtitle or day_title[:30]}"
        banner_desc = f"行程：{day_title}\n\n行李與換宿：{luggage_note}\n\n完整行程：./itinerary.html#day-{day_num}"
        
        banner_event = {
            'uid': f"tohoku2026-day-{day_num}-banner@antigravity",
            'dtstamp': dtstamp,
            'is_allday': True,
            'dtstart': curr_iso_date,
            'dtend': next_iso_date,
            'summary': banner_summary,
            'description': banner_desc,
            'location': region,
            'categories': '全天行程概覽,2026東北行',
            'has_alarm': False
        }
        full_events.append(banner_event)
        essential_events.append(banner_event)

        # CSV row for banner
        csv_rows.append({
            'Subject': banner_summary,
            'Start Date': date_obj.strftime('%m/%d/%Y'),
            'Start Time': '',
            'End Date': date_obj.strftime('%m/%d/%Y'),
            'End Time': '',
            'All Day Event': 'True',
            'Description': clean_text_for_calendar(banner_desc),
            'Location': region,
            'Private': 'False'
        })

        items = day.get('items', [])
        for idx, it in enumerate(items):
            st_raw = it.get('start_time')
            et_raw = it.get('end_time')
            if not st_raw:
                continue

            st_tuple = parse_time_str(st_raw)
            if not st_tuple:
                continue

            # Determine end time
            if et_raw:
                et_tuple = parse_time_str(et_raw)
            else:
                # Lookahead to next item
                et_tuple = None
                if idx + 1 < len(items) and items[idx + 1].get('start_time'):
                    nst = parse_time_str(items[idx + 1]['start_time'])
                    if nst:
                        st_mins = st_tuple[0] * 60 + st_tuple[1]
                        nst_mins = nst[0] * 60 + nst[1]
                        diff = nst_mins - st_mins
                        if 5 <= diff <= 120:
                            et_tuple = nst

                if not et_tuple:
                    # Default duration 30 min
                    dt_temp = datetime.strptime(f"{iso_date} {st_tuple[0]:02d}:{st_tuple[1]:02d}", "%Y-%m-%d %H:%M") + timedelta(minutes=30)
                    et_tuple = (dt_temp.hour, dt_temp.minute)

            cat = it.get('category', 'general')
            cat_label = it.get('category_label', '')
            raw_title = clean_text_for_calendar(it.get('title', ''))

            # Prefix icon based on category
            cat_icons = {
                'spot': '🏛️',
                'dining': '🍴',
                'hotel': '🏨',
                'transit': '🚌',
                'activity': '🎯',
                'wakeup': '⏰',
                'general': '📌'
            }
            icon = cat_icons.get(cat, '📌')
            if '新幹線' in raw_title: icon = '🚄'
            elif '飛機' in raw_title or '航空' in raw_title or 'BR1' in raw_title: icon = '✈️'
            elif '船' in raw_title: icon = '⛴️'
            elif '拉麵' in raw_title or 'そば' in raw_title or '蕎麥' in raw_title: icon = '🍜'
            elif '牛' in raw_title or '燒肉' in raw_title or '肉' in raw_title: icon = '🥩'
            elif '咖啡' in raw_title or '喫茶' in raw_title: icon = '☕'
            elif '朝市' in raw_title or '市場' in raw_title: icon = '🐟'
            elif '卡拉OK' in raw_title: icon = '🎤'

            # Clean summary
            summary = f"{icon} {raw_title}"

            # Location determination
            location = ""
            fact = it.get('fact_data')
            if fact:
                location = fact.get('jp_name') or fact.get('name') or ""
            if not location:
                # check map links
                for ml in it.get('map_links', []):
                    if not ml.get('is_dir') and ml.get('name'):
                        location = ml.get('name')
                        break
            if not location:
                location = region

            # Timezone logic: Day 1 Taiwan events before flight arrival, Day 20 flight departure
            tzid = "Asia/Tokyo"
            if day_num == 1:
                # Up to 09:55 is Taiwan
                if st_tuple[0] < 9 or (st_tuple[0] == 9 and st_tuple[1] < 55):
                    tzid = "Asia/Taipei"
                elif st_tuple[0] == 9 and st_tuple[1] == 55:
                    # Flight BR122
                    tzid = "Asia/Taipei" # Departure in Taipei time
            elif day_num == 20:
                if st_tuple[0] >= 19:
                    tzid = "Asia/Taipei" # Arrival in Taipei

            dtstart_str = format_iso_time(iso_date, st_tuple[0], st_tuple[1])
            dtend_str = format_iso_time(iso_date, et_tuple[0], et_tuple[1])

            # Description compilation
            desc_lines = []
            desc_lines.append(f"【Day {day_num}・{cat_label or cat}】")
            
            raw_text = it.get('raw_text', '')
            clean_raw = clean_text_for_calendar(raw_text)
            if clean_raw:
                # Truncate if very long
                lines = [line.strip('- *') for line in clean_raw.split('\n') if line.strip()]
                desc_lines.extend(lines[:8])

            if fact:
                desc_lines.append("")
                if fact.get('hours'):
                    desc_lines.append(f"⏰ 營業時間：{clean_text_for_calendar(fact['hours'])}")
                if fact.get('closed'):
                    desc_lines.append(f"🚫 公休日：{clean_text_for_calendar(fact['closed'])}")
                if fact.get('tips'):
                    desc_lines.append(f"💡 備註：{clean_text_for_calendar(fact['tips'])}")

            map_links = it.get('map_links', [])
            if map_links:
                desc_lines.append("")
                for ml in map_links[:2]:
                    desc_lines.append(f"🗺️ {ml.get('name')}: {ml.get('url')}")

            cautions = it.get('cautions', [])
            if cautions:
                desc_lines.append("")
                for c in cautions[:2]:
                    desc_lines.append(f"⚠️ {clean_text_for_calendar(c)}")

            final_desc = "\n".join(desc_lines)

            # Check if alarm needed (Shinkansen, flights, JCB bookings, tours)
            has_alarm = False
            alarm_msg = ""
            if any(k in raw_title for k in ['はやぶさ', '新幹線', 'BR122', 'BR117']):
                has_alarm = True
                alarm_msg = f"提醒：{raw_title[:30]} 即將發車/起飛，請預先抵達月台/候機室！"
            elif any(k in raw_title for k in ['已預約', 'JCB', '吉兆', 'じょっぱり', '泰山', '閣', '斎太郎', '八戶酒造', '宮城峽']):
                has_alarm = True
                alarm_msg = f"預約提醒：{raw_title[:30]} 席位即將開始，請準時抵達！"

            event_obj = {
                'uid': f"tohoku2026-d{day_num}-it{idx}@antigravity",
                'dtstamp': dtstamp,
                'is_allday': False,
                'tzid': tzid,
                'dtstart': dtstart_str,
                'dtend': dtend_str,
                'summary': summary,
                'description': final_desc,
                'location': location,
                'categories': f"{cat_label or cat},2026東北行",
                'has_alarm': has_alarm,
                'alarm_msg': alarm_msg
            }

            full_events.append(event_obj)
            if is_essential_item(it):
                essential_events.append(event_obj)

            # CSV row
            csv_rows.append({
                'Subject': summary,
                'Start Date': date_obj.strftime('%m/%d/%Y'),
                'Start Time': f"{st_tuple[0]:02d}:{st_tuple[1]:02d}",
                'End Date': date_obj.strftime('%m/%d/%Y'),
                'End Time': f"{et_tuple[0]:02d}:{et_tuple[1]:02d}",
                'All Day Event': 'False',
                'Description': clean_text_for_calendar(final_desc),
                'Location': location,
                'Private': 'False'
            })

    # Render ICS Full
    write_ics_file(OUTPUT_ICS_FULL, full_events, "🍁 2026 東北20天秋楓全行程（分秒必爭全覽版）")
    write_ics_file(OUTPUT_ICS_CALENDAR, full_events, "🍁 2026 東北20天秋楓全行程（分秒必爭全覽版）")
    # Render ICS Essential
    write_ics_file(OUTPUT_ICS_ESSENTIAL, essential_events, "🍁 2026 東北20天秋楓精選（核心里程碑版）")

    # Render CSV Google
    with open(OUTPUT_CSV_GOOGLE, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = ['Subject', 'Start Date', 'Start Time', 'End Date', 'End Time', 'All Day Event', 'Description', 'Location', 'Private']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)

    print(f"Generated Full ICS: {len(full_events)} events -> {OUTPUT_ICS_FULL}")
    print(f"Generated Essential ICS: {len(essential_events)} events -> {OUTPUT_ICS_ESSENTIAL}")
    print(f"Generated Google CSV: {len(csv_rows)} rows -> {OUTPUT_CSV_GOOGLE}")

def write_ics_file(file_path: str, events: list, cal_name: str):
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Antigravity Travel Studio//Tohoku Itinerary 2026//ZH-TW",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{cal_name}",
        "X-WR-TIMEZONE:Asia/Tokyo",
        "X-WR-CALDESC:2026 日本東北 20 天 19 夜（青森・奧入瀨・八戶・松島・仙台・山寺）秋楓美饌全行程日曆",
        "BEGIN:VTIMEZONE",
        "TZID:Asia/Tokyo",
        "X-LIC-LOCATION:Asia/Tokyo",
        "BEGIN:STANDARD",
        "TZOFFSETFROM:+0900",
        "TZOFFSETTO:+0900",
        "TZNAME:JST",
        "DTSTART:19700101T000000",
        "END:STANDARD",
        "END:VTIMEZONE",
        "BEGIN:VTIMEZONE",
        "TZID:Asia/Taipei",
        "X-LIC-LOCATION:Asia/Taipei",
        "BEGIN:STANDARD",
        "TZOFFSETFROM:+0800",
        "TZOFFSETTO:+0800",
        "TZNAME:CST",
        "DTSTART:19700101T000000",
        "END:STANDARD",
        "END:VTIMEZONE"
    ]

    for ev in events:
        lines.append("BEGIN:VEVENT")
        lines.append(f"UID:{ev['uid']}")
        lines.append(f"DTSTAMP:{ev['dtstamp']}")

        if ev.get('is_allday'):
            lines.append(f"DTSTART;VALUE=DATE:{ev['dtstart']}")
            lines.append(f"DTEND;VALUE=DATE:{ev['dtend']}")
            lines.append("TRANSP:TRANSPARENT")
        else:
            tzid = ev.get('tzid', 'Asia/Tokyo')
            lines.append(f"DTSTART;TZID={tzid}:{ev['dtstart']}")
            lines.append(f"DTEND;TZID={tzid}:{ev['dtend']}")
            lines.append("TRANSP:OPAQUE")

        lines.append(f"SUMMARY:{escape_ics_text(ev['summary'])}")
        if ev.get('description'):
            lines.append(f"DESCRIPTION:{escape_ics_text(ev['description'])}")
        if ev.get('location'):
            lines.append(f"LOCATION:{escape_ics_text(ev['location'])}")
        if ev.get('categories'):
            lines.append(f"CATEGORIES:{escape_ics_text(ev['categories'])}")

        if ev.get('has_alarm'):
            lines.append("BEGIN:VALARM")
            lines.append("ACTION:DISPLAY")
            lines.append(f"DESCRIPTION:{escape_ics_text(ev.get('alarm_msg', '行程提醒'))}")
            lines.append("TRIGGER:-PT30M")
            lines.append("END:VALARM")

        lines.append("END:VEVENT")

    lines.append("END:VCALENDAR")

    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        f.write("\r\n".join(lines) + "\r\n")

if __name__ == '__main__':
    generate()
