#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate comprehensive Google Maps place lists for Tohoku 20-day itinerary:
1. tohoku_google_maps_places.csv (83 deduplicated unique physical venues with consolidated multi-function metadata)
2. tohoku_google_maps_all_stops.csv (94 full itinerary activity stops)
3. Embeds into web app / provides direct download and interactive list
Structured fields: 營業時間, 公休日, 門票或預約, 支付方式
"""

import os
import re
import csv
import urllib.parse
from pathlib import Path
from build_itinerary_web import ITINERARY_MD_PATH

BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / 'dist'

def clean_markdown_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'\*\(([^\)]*)\)\*?', r'（\1）', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = text.replace('`', '')
    text = text.replace('**', '')
    text = text.replace('*', '')
    text = re.sub(r'<br\s*/?>', ' ｜ ', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = text.replace(' （', '（').replace('） ', '）')
    text = re.sub(r'(｜\s*)+', '｜ ', text)
    return text.strip(' ｜')

def generate_lists():
    with open(ITINERARY_MD_PATH, 'r', encoding='utf-8') as f:
        text = f.read()

    # 1. Parse Spots (45 genuine attractions, culture & activity venues)
    spot_start = text.find('## <a id="spot-summary-table"')
    spot_end = text.find('## <a id="transit-summary-table"')
    spot_section = text[spot_start:spot_end]
    spot_rows = [r.strip() for r in spot_section.split('\n') if r.strip().startswith('| **Day')]

    spots_data = []
    for r in spot_rows:
        cols = [c.strip() for c in r.split('|')[1:-1]]
        day_m = re.search(r'Day\s*(\d+)', cols[0])
        day = int(day_m.group(1)) if day_m else 0
        time_str = cols[1].replace('<br>', ' ').strip('* ')
        m_link = re.search(r'\[([^\]]+)\]\((https://www\.google\.com/maps/search/\?[^\)]+)\)', cols[2])
        name = m_link.group(1) if m_link else ''
        url = m_link.group(2) if m_link else ''
        query = urllib.parse.unquote(url.split('query=')[-1]) if 'query=' in url else ''
        m_jp = re.search(r'\*\(([^)]+)\)\*', cols[2])
        jp = m_jp.group(1) if m_jp else ''
        attr = cols[3].replace('<br>', ' ').strip('* ')
        rules = cols[4]
        highlights = cols[5].replace('<br>', ' ').strip('* ')
        
        # Extract structured fields
        m_h = re.search(r'•\s*\*\*(?:營業|時間|開放)\*\*[：:]\s*(.*?)(?=\s*<br>\s*•|\s*$)', rules)
        m_c = re.search(r'•\s*\*\*(?:定休|休館|公休)\*\*[：:]\s*(.*?)(?=\s*<br>\s*•|\s*$)', rules)
        m_t = re.search(r'•\s*\*\*(?:門票|包廂費|費用|入館|票價)\*\*[：:]\s*(.*?)(?=\s*<br>\s*•|\s*$)', rules)
        m_p = re.search(r'•\s*\*\*(?:支付|付款)\*\*[：:]\s*(.*?)(?=\s*<br>\s*•|\s*$)', rules)

        hours = clean_markdown_text(m_h.group(1)) if m_h else clean_markdown_text(rules)
        closed = clean_markdown_text(m_c.group(1)) if m_c else '全年無休'
        ticket = clean_markdown_text(m_t.group(1)) if m_t else '免費入場'
        pay = clean_markdown_text(m_p.group(1)) if m_p else '現場支付'

        # Determine clean display name
        if jp and jp not in name:
            if '(' in name or '（' in name:
                place_name = name
            else:
                place_name = f'{name} ({jp})'
        else:
            place_name = name

        summary_rules = f"營業：{hours} ｜ 定休：{closed} ｜ 門票：{ticket} ｜ 支付：{pay}"

        spots_data.append({
            '分類': '🏛️ 景點・文化・體驗',
            '造訪天數': f'Day {day}',
            '地點名稱': place_name,
            '中文名稱': name,
            '日文名稱': jp or name,
            '用餐時段或景點屬性': attr,
            '預計時間': time_str,
            '營業時間': hours,
            '公休日': closed,
            '門票或預約': ticket,
            '支付方式': pay,
            'Google地圖搜尋關鍵字': query,
            '最新營業與營運規範': summary_rules,
            '特色亮點與老饕推薦': highlights,
            'Google地圖即時連結': url
        })

    # 2. Parse Dining (40 meals)
    dining_start = text.find('## <a id="dining-summary-table"')
    dining_end = text.find('## 🎯 需求檢核與亮點一覽表')
    dining_section = text[dining_start:dining_end]
    dining_rows = [r.strip() for r in dining_section.split('\n') if r.strip().startswith('| **')]

    dining_data = []
    for r in dining_rows:
        cols = [c.strip() for c in r.split('|')[1:-1]]
        day_m = re.search(r'Day\s*(\d+)', cols[0])
        day = int(day_m.group(1)) if day_m else 0
        meal_m = re.search(r'(早餐|午餐|晚餐|上午|散策|宵夜|午茶)', cols[0])
        meal = meal_m.group(1) if meal_m else '用餐'
        time_str = cols[1].replace('<br>', ' ').strip('* ')
        m_link = re.search(r'\[([^\]]+)\]\((https://www\.google\.com/maps/search/\?[^\)]+)\)', cols[2])
        name = m_link.group(1) if m_link else ''
        url = m_link.group(2) if m_link else ''
        query = urllib.parse.unquote(url.split('query=')[-1]) if 'query=' in url else ''
        m_sub = re.search(r'\*\(([^)]+)\)\*', cols[2])
        cuisine = m_sub.group(1) if m_sub else ''
        
        hours_raw = clean_markdown_text(cols[3])
        hours_clean = re.sub(r'^[•\-\s]+', '', hours_raw)
        hours_clean = re.sub(r'\|\s*•\s*', '｜ ', hours_clean)
        
        closed = clean_markdown_text(cols[4])
        status = clean_markdown_text(cols[5])
        raw_channel = clean_markdown_text(cols[6]) if len(cols) > 6 else ''
        
        if raw_channel and raw_channel not in ['無', '—']:
            if raw_channel.startswith('無（') and raw_channel.endswith('）'):
                detail = raw_channel[2:-1].strip()
                ticket_booking = f'{status}（{detail}）'
            elif raw_channel.startswith('無 ('):
                detail = raw_channel[3:-1].strip()
                ticket_booking = f'{status}（{detail}）'
            else:
                ticket_booking = f'{status}（{raw_channel}）'
        else:
            ticket_booking = status

        m_p = re.search(r'•\s*(?:💳\s*)?\*\*(?:支付|付款)\*\*[：:]\s*(.*)', cols[2])
        pay = clean_markdown_text(m_p.group(1)) if m_p else '現場支付'
        tips = cols[7].replace('<br>', ' ').strip('* ') if len(cols) > 7 else ''

        clean_jp = name.split('(')[0].split('（')[0].strip()
        if cuisine:
            if '(' in name or '（' in name:
                dining_place_name = f'{name} ｜ {cuisine}'
            else:
                dining_place_name = f'{name} ({cuisine})'
        else:
            dining_place_name = name

        summary_rules = f"營業：{hours_clean} ｜ 公休：{closed} ｜ 預約：{ticket_booking} ｜ 支付：{pay}"

        dining_data.append({
            '分類': '🍱 必吃美饌',
            '造訪天數': f'Day {day}',
            '地點名稱': dining_place_name,
            '中文名稱': name,
            '日文名稱': clean_jp,
            '用餐時段或景點屬性': f'{meal}・{cuisine}',
            '預計時間': time_str,
            '營業時間': hours_clean,
            '公休日': closed,
            '門票或預約': ticket_booking,
            '支付方式': pay,
            'Google地圖搜尋關鍵字': query,
            '最新營業與營運規範': summary_rules,
            '特色亮點與老饕推薦': tips,
            'Google地圖即時連結': url
        })

    # 3. Parse Hotels (9 hotels)
    hotel_start = text.find('## <a id="hotel-summary-table"')
    hotel_end = text.find('## <a id="dining-summary-table"')
    hotel_section = text[hotel_start:hotel_end]
    hotel_rows = [r.strip() for r in hotel_section.split('\n') if r.strip().startswith('| **[')]

    hotel_data = []
    for r in hotel_rows:
        cols = [c.strip() for c in r.split('|')[1:-1]]
        m_link = re.search(r'\[([^\]]+)\]\((https://www\.google\.com/maps/search/\?[^\)]+)\)', cols[0])
        name = m_link.group(1) if m_link else ''
        url = m_link.group(2) if m_link else ''
        query = urllib.parse.unquote(url.split('query=')[-1]) if 'query=' in url else ''
        m_day = re.search(r'\*\((Day[^\)]+)\)\*', cols[0])
        day_str = m_day.group(1) if m_day else ''
        clean_name = re.sub(r'^[①-⑨\s]+', '', name).strip()

        in_out_m = re.search(r'In:\s*(.*?)\s*/\s*Out:\s*(.*?)(?=\s*<br>|\s*$)', cols[1])
        if in_out_m:
            check_in = clean_markdown_text(in_out_m.group(1))
            check_out = clean_markdown_text(in_out_m.group(2))
            hours = f'Check-in {check_in} / Check-out {check_out}'
        else:
            hours = clean_markdown_text(cols[1].split('<br>')[0])

        curfew = '門禁 23:00' if '門禁 23:00' in cols[1] else '24h 櫃檯'
        closed = f'年中無休（{curfew}）'

        is_package = any(k in clean_name for k in ['海扇閣', '椿館', '一之坊'])
        ticket = '🌟 已訂妥（一泊二食・全包式服務）' if is_package else '🌟 已預約確認（訂房完成）'
        pay = '線上已付款/預約確認 ｜ 現場退房支援 JCB ⭕｜ 台新Pay+(PayPay) ⭕｜ 現金 ⭕'

        lounge = cols[2].replace('<br>', ' ｜ ').strip('* ')
        onsen = cols[3].replace('<br>', ' ｜ ').strip('* ')

        summary_rules = f"入住退房：{hours} ｜ 溫泉桑拿：{clean_markdown_text(onsen)} ｜ 支付：{pay}"

        hotel_data.append({
            '分類': '🏨 入住飯店',
            '造訪天數': day_str,
            '地點名稱': clean_name,
            '中文名稱': clean_name,
            '日文名稱': clean_name,
            '用餐時段或景點屬性': '頂級溫泉名宿 / 商務飯店',
            '預計時間': check_in if in_out_m else hours,
            '營業時間': hours,
            '公休日': closed,
            '門票或預約': ticket,
            '支付方式': pay,
            'Google地圖搜尋關鍵字': query,
            '最新營業與營運規範': summary_rules,
            '特色亮點與老饕推薦': f'{clean_markdown_text(lounge)}；早餐亮點：{clean_markdown_text(cols[5]) if len(cols) > 5 else ""}',
            'Google地圖即時連結': url
        })

    all_stops = spots_data + dining_data + hotel_data
    for p in all_stops:
        for k in p:
            if k != 'Google地圖即時連結':
                p[k] = clean_markdown_text(p[k])

    fieldnames = [
        '地點名稱',
        '中文名稱',
        '日文名稱',
        '分類',
        '造訪天數',
        '用餐時段或景點屬性',
        '預計時間',
        '營業時間',
        '公休日',
        '門票或預約',
        '支付方式',
        'Google地圖搜尋關鍵字',
        '最新營業與營運規範',
        '特色亮點與老饕推薦',
        'Google地圖即時連結'
    ]

    # 1. Output All 94 Stops CSV
    all_stops_csv = str(DIST_DIR / 'tohoku_google_maps_all_stops.csv')
    with open(all_stops_csv, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in all_stops:
            writer.writerow({k: p.get(k, '') for k in fieldnames})

    # 2. Output Deduplicated 83 Unique Physical Places CSV
    def get_canonical_key(p):
        q = p['Google地圖搜尋關鍵字']
        name = p['地點名稱']
        if '古川市場' in name or '青森魚菜センター' in q:
            return '青森魚菜センター'
        elif '八食センター' in q or '八食中心' in name:
            return '八食センター'
        elif ('藤田' in q or '藤田' in name) and ('庭園' in q or '喫茶' in q or '庭園' in name):
            return '藤田記念庭園'
        elif 'A-FACTORY' in q or 'A-FACTORY' in name:
            return 'A-FACTORY'
        elif 'みろく横丁' in q or 'みろく横丁' in name:
            return 'みろく横丁'
        elif '仙台朝市' in q or '仙台朝市' in name:
            return '仙台朝市'
        elif '海扇閣' in q or '海扇閣' in name:
            return '南部屋・海扇閣'
        elif '椿館' in q or '椿館' in name:
            return '浅虫温泉 椿館'
        elif 'コンフォートホテル八戸' in q or 'Comfort Hotel 八戶' in name:
            return 'コンフォートホテル八戸'
        elif '松島一の坊' in q or '松島一之坊' in name:
            return '松島一の坊'
        elif '御宿' in q or '野乃' in q or '野乃' in name:
            return '御宿野乃 仙台'
        return q or name

    grouped = {}
    for p in all_stops:
        k = get_canonical_key(p)
        grouped.setdefault(k, []).append(p)

    def merge_field(group, field_name):
        items = []
        for item in group:
            val = item.get(field_name, '').strip()
            if val:
                cat_short = item['分類'][:2]
                items.append((cat_short, val))
        if not items:
            return ''
        unique_vals = list(dict.fromkeys([v for c, v in items]))
        if len(unique_vals) == 1:
            return unique_vals[0]
        # Multi distinct values: label by role
        return ' ｜ '.join([f"{c}: {v}" for c, v in items])

    def merge_payment(group):
        pays = [item.get('支付方式', '').strip() for item in group if item.get('支付方式', '').strip()]
        unique_pays = list(dict.fromkeys(pays))
        if len(unique_pays) == 1:
            return unique_pays[0]
        return ' ｜ '.join([f"{item['分類'][:2]}: {item.get('支付方式', '')}" for item in group if item.get('支付方式')])

    dedup_places = []
    for k, group in grouped.items():
        if len(group) == 1:
            dedup_places.append(group[0])
        else:
            cats = list(dict.fromkeys([item['分類'] for item in group]))
            combined_cat = " ＆ ".join(cats)
            days = list(dict.fromkeys([item['造訪天數'] for item in group]))
            combined_days = " / ".join(days)
            hotel_item = next((item for item in group if '飯店' in item['分類']), None)
            spot_item = next((item for item in group if '景點' in item['分類']), None)
            dining_item = next((item for item in group if '美饌' in item['分類']), None)
            
            primary = hotel_item or spot_item or group[0]
            combined_name = primary['地點名稱']
            if dining_item and dining_item != primary:
                meal_info = dining_item['用餐時段或景點屬性']
                if 'のっけ丼' in meal_info or '七厘村' in meal_info or '蘋果派' in meal_info or 'Live Kitchen' in meal_info or '海鮮丼' in meal_info:
                    combined_name = f"{primary['中文名稱']} ｜ {meal_info}"

            combined_attrs = " ＆ ".join([item['用餐時段或景點屬性'] for item in group])
            combined_times = " ｜ ".join([f"{item['分類'][:2]}: {item['預計時間']}" for item in group])
            combined_hours = merge_field(group, '營業時間')
            combined_closed = merge_field(group, '公休日')
            combined_ticket = merge_field(group, '門票或預約')
            combined_pay = merge_payment(group)
            combined_rules = " ｜ ".join(list(dict.fromkeys([item['最新營業與營運規範'] for item in group if item['最新營業與營運規範']])))
            combined_highlights = " ｜ ".join(list(dict.fromkeys([item['特色亮點與老饕推薦'] for item in group if item['特色亮點與老饕推薦']])))

            dedup_places.append({
                '分類': combined_cat,
                '造訪天數': combined_days,
                '地點名稱': combined_name,
                '中文名稱': primary['中文名稱'],
                '日文名稱': primary['日文名稱'],
                '用餐時段或景點屬性': combined_attrs,
                '預計時間': combined_times,
                '營業時間': combined_hours,
                '公休日': combined_closed,
                '門票或預約': combined_ticket,
                '支付方式': combined_pay,
                'Google地圖搜尋關鍵字': primary['Google地圖搜尋關鍵字'],
                '最新營業與營運規範': combined_rules,
                '特色亮點與老饕推薦': combined_highlights,
                'Google地圖即時連結': primary['Google地圖即時連結']
            })

    dedup_csv = str(DIST_DIR / 'tohoku_google_maps_places.csv')
    with open(dedup_csv, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in dedup_places:
            writer.writerow({k: p.get(k, '') for k in fieldnames})

    print(f"Generated Deduplicated CSV with {len(dedup_places)} unique places at: {dedup_csv}")
    print(f"Generated All-Stops CSV with {len(all_stops)} activity stops at: {all_stops_csv}")
    print(f" - Spots: {len(spots_data)}")
    print(f" - Dining: {len(dining_data)}")
    print(f" - Hotels: {len(hotel_data)}")
    print(f" - Multi-role consolidated venues: {len(all_stops) - len(dedup_places)}")

if __name__ == '__main__':
    generate_lists()
