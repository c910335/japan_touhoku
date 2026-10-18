#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build interactive Tohoku 20-day web application v3 with deep fact-checked enrichment,
instant search, PWA support, one-click Japanese copy, luggage callout, and multi-stop day maps.
Outputs:
- itinerary_data.json
- itinerary.html
- index.html
"""

import re
import json
import os
import html
import textwrap
from pathlib import Path
from datetime import date, timedelta
import markdown
from bs4 import BeautifulSoup, NavigableString

BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / 'dist'
ITINERARY_MD_PATH = str(BASE_DIR / 'tohoku_20day_itinerary.md')
TEMPLATE_PATH = str(BASE_DIR / 'template.html')
OUTPUT_HTML_PATH = str(DIST_DIR / 'itinerary.html')
OUTPUT_INDEX_PATH = str(DIST_DIR / 'index.html')
OUTPUT_JSON_PATH = str(DIST_DIR / 'itinerary_data.json')

LUGGAGE_TRANSITIONS = {
    1: "🧳 啟程換宿：自桃園機場搭乘班機抵達青森機場，搭乘利木津巴士至青森站，大行李直接入住寄放至「ホテルマイステイズ青森駅前（東口步行3分）」，晚餐轉戰さくら野百貨店北海道展。",
    2: "🧳 連住不換宿：續住ホテルマイステイズ青森駅前，全日輕裝參加八甲田、十和田奧入瀨與十和田湖遊覽船一日遊，傍晚 18:20 專車返抵市區直達林檎家成吉思汗烤肉，晚間回飯店投幣洗衣。",
    3: "🧳 溫泉換宿：早晨退房後大行李寄放飯店櫃檯，十點多漫步至 AUGA 丸青食堂早午餐，11:20 取行李搭 11:26 市營公車 C11 直達海扇閣寄放，下午溫泉街散策並於 cafe apricot 享受手沖咖啡，15:00 準時 Check-in！",
    4: "🧳 淺虫同街換宿：海扇閣退房，大行李委託專車移送至隔壁「浅虫温泉 椿館」，傍晚漫步日落海灘後椿館專車接駁至飯店！",
    5: "🧳 換宿回青森市：椿館退房後專車送站，搭乘 10:00 青森市營巴士 U5 直達「市役所前」，下車步行 2 分鐘將大行李寄放「リッチモンドホテル青森」，11:00 開門首批搶先入座味の札幌大西味噌咖哩牛奶拉麵！",
    6: "🧳 連住不換宿：續住リッチモンドホテル青森，晨間 06:30～10:00 完整時段享用 5F 頂級朝食百匯吃好吃滿，下午決定留在飯店客房深層靜養放鬆不出門，13:00 起於 5F Premier Lounge 享受青森蘋果汁盲測品評、17:00 起免費酒精暢飲，晚間漫步 4 分鐘至隔壁津輕三味線居酒屋。",
    7: "🧳 換宿八戶：首選市役所前 07:30 搭乘市營巴士 T50 直達新青森站南口（07:46抵・低底盤推行李一車直達免轉車；公車備案 1：市役所前 07:50 搭乘 T50 於 08:05 抵新青森站旁「石江」站牌下車步行 200m 進南口；計程車備案 2：08:00 飯店排班計程車），2F 新幹線改札內ブナの森弁当売店挑選特色鐵路便當，搭乘 08:37 東北新幹線 はやぶさ 12 號（車上享用便當）直達八戶站（09:04抵），直達「コンフォートホテル八戸（東口步行2分）」迅速寄存大行李，銜接 09:33 電車前往三澤航空科學館！",
    8: "🧳 連住不換宿：續住コンフォートホテル八戸，全日輕裝持 Suica 搭乘 JR 八戶線巡禮種差海岸大草皮、大須賀鳴沙海岸、葦毛崎展望台與蕪嶋神社。",
    9: "🧳 連住不換宿：續住コンフォートホテル八戸，全日輕裝搭電車至陸奧湊みなと食堂（金賞平目漬丼）、八戶酒造見學、八食中心七厘村現烤海鮮。",
    10: "🧳 跨縣前進松島：退房攜大行李搭乘東北新幹線 Hayabusa 南下仙台，轉東北本線至松島站，致電松島一之坊專車接駁直達海景第一排！",
    11: "🧳 換宿仙台東口：松島一之坊退房專車送至松島海岸碼頭，仁王丸巡航與參拜瑞嚴寺，下午搭仙石線至仙台站東口，入住「スーパーホテル仙台駅東口天然温泉（步行3分）」。",
    12: "🧳 連住不換宿：續住スーパーホテル仙台駅東口天然温泉，客房充裕補眠放鬆至14:15出發，搭地下鐵南北線直達定禪寺通櫸木林蔭、媒體中心 smt 巡禮，晚間百年かとう壽喜燒、AER 31F 夜景！",
    13: "🧳 連住不換宿：續住スーパーホテル仙台駅東口天然温泉，全日輕裝搭乘 JR 仙山線跨縣出擊 Nikka 宮城峽威士忌蒸餾所、山形山寺（立石寺）千階登頂。",
    14: "🧳 連住不換宿：續住スーパーホテル仙台駅東口天然温泉，全日輕裝參觀瑞鳳殿、品嚐だし廊飛魚拉麵、享受飯店 4 小時 Welcome Bar 地酒暢飲與 Gusto 家庭餐廳晚宴！",
    15: "🧳 同城換宿仙台西口：Super Hotel 退房，行李推過仙台站直達西口「リッチモンドホテル プレミア仙台駅前（直通拱廊街）」提前寄存，搭乘市區公車直達參拜國寶大崎八幡宮，下午14:00提早入住享用免費下午茶霜淇淋與手作馬芬！",
    16: "🧳 連住不換宿：續住リッチモンドホテル プレミア仙台駅前，全日輕裝漫步仙台朝市、水族館、ちからや A5 仙台牛吃到飽，晚間享受飯店免費霜淇淋與鴨蕎麥麵宵夜！",
    17: "🧳 連住不換宿：續住リッチモンドホテル プレミア仙台駅前，早晨客房悠閒補眠消食重置胃袋，午後一番町卡拉OK包廂歡唱消食近6小時、晚間閣炙燒牛舌刺身。",
    18: "🧳 連住不換宿：續住リッチモンドホテル プレミア仙台駅前，全日輕裝鯛きち現烤薄皮鯛魚燒、牡丹低溫熟成炸豬排、八木山動物公園、16:05 長榮 BR117 開搶回程機位、斎太郎痛風鍋居酒屋美食全達成！",
    19: "🧳 壓軸名宿換宿：Richmond 退房寄存行李於御宿野乃，11:20 提前享用避開人潮之びっくりドンキー漢堡排，午後搭乘「るーぷる仙台」直攻仙台城跡（免爬70m大陡坡），下坡漫步至仙台市博物館，16:30 先至一番町大啖老舖「開盛庵」蒲燒鰻魚飯，18:00 順路入住御宿野乃享受 14F 天然溫泉桑拿與夜鳴拉麵！",
    20: "🧳 歸國返台：御宿野乃享用 3 小時生鮭魚卵厚切牛舌極上早餐後退房，攜行行李步行至仙台站，搭乘仙台機場 Access 線直達仙台機場返台！"
}

DAY_ROUTES = {
    1: "https://www.google.com/maps/dir/?api=1&origin=青森空港&destination=ホテルマイステイズ青森駅前&waypoints=さくら野百貨店+青森本店&travelmode=transit",
    2: "https://www.google.com/maps/dir/?api=1&origin=ホテルマイステイズ青森駅前&destination=ホテルマイステイズ青森駅前&waypoints=八甲田ロープウェー|奥入瀬渓流|十和田湖遊覧船|生ラムジンギスカン+林檎家+古川店&travelmode=transit",
    3: "https://www.google.com/maps/dir/?api=1&origin=ホテルマイステイズ青森駅前&destination=南部屋・海扇閣&waypoints=アウガ新鮮市場|青森駅|cafe+apricot|南部屋・海扇閣&travelmode=transit",
    4: "https://www.google.com/maps/dir/?api=1&origin=南部屋・海扇閣&destination=浅虫温泉+椿館&waypoints=浅虫水族館|正立食堂|サンセットビーチあさむし&travelmode=walking",
    5: "https://www.google.com/maps/dir/?api=1&origin=リッチモンドホテル青森&destination=リッチモンドホテル青森&waypoints=味の札幌+大西|ねぶたの家+ワ・ラッセ|A-FACTORY|八甲田丸|アスパム|馬肉料理+吉兆+青森店&travelmode=walking",
    6: "https://www.google.com/maps/dir/?api=1&origin=リッチモンドホテル青森&destination=リッチモンドホテル青森&waypoints=三内丸山遺跡|津軽じょっぱり漁屋酒場&travelmode=transit",
    7: "https://www.google.com/maps/dir/?api=1&origin=リッチモンドホテル青森&destination=コンフォートホテル八戸&waypoints=新青森駅|青森県立三沢航空科学館|八戸市美術館|みろく横丁&travelmode=transit",
    8: "https://www.google.com/maps/dir/?api=1&origin=八戸駅&destination=コンフォートホテル八戸&waypoints=種差海岸天然芝生地|種差海岸インフォメーションセンター|波光食堂|大須賀海岸|葦毛崎展望台|蕪嶋神社|食彩酒房+天草&travelmode=transit",
    9: "https://www.google.com/maps/dir/?api=1&origin=八戸駅&destination=コンフォートホテル八戸&waypoints=みなと食堂|八戸酒造|八食センター&travelmode=transit",
    10: "https://www.google.com/maps/dir/?api=1&origin=八戸駅&destination=松島一の坊&waypoints=仙台駅|松島駅&travelmode=transit",
    11: "https://www.google.com/maps/dir/?api=1&origin=松島一の坊&destination=スーパーホテル仙台駅東口天然温泉&waypoints=松島島巡り観光船|瑞巌寺|みちのく伊達政宗歴史館|焼肉+泰山+HANARE&travelmode=transit",
    12: "https://www.google.com/maps/dir/?api=1&origin=スーパーホテル仙台駅東口天然温泉&destination=スーパーホテル仙台駅東口天然温泉&waypoints=定禅寺通ケヤキ並木|せんだいメディアテーク|すき焼割烹+かとう|AER展望テラス&travelmode=transit",
    13: "https://www.google.com/maps/dir/?api=1&origin=仙台駅&destination=スーパーホテル仙台駅東口天然温泉&waypoints=作並駅|ニッカウヰスキー宮城峡蒸溜所|宝珠山立石寺|洋食+HACHI+仙台駅店&travelmode=transit",
    14: "https://www.google.com/maps/dir/?api=1&origin=スーパーホテル仙台駅東口天然温泉&destination=スーパーホテル仙台駅東口天然温泉&waypoints=瑞鳳殿|だし廊|ガスト+仙台名掛丁店&travelmode=transit",
    15: "https://www.google.com/maps/dir/?api=1&origin=リッチモンドホテル+プレミア仙台駅前&destination=リッチモンドホテル+プレミア仙台駅前&waypoints=大崎八幡宮|陽だまり食堂&travelmode=transit",
    16: "https://www.google.com/maps/dir/?api=1&origin=リッチモンドホテル+プレミア仙台駅前&destination=リッチモンドホテル+プレミア仙台駅前&waypoints=仙台朝市|仙台うみの杜水族館|焼肉ダイニング+ちからや+仙台駅前店&travelmode=transit",
    17: "https://www.google.com/maps/dir/?api=1&origin=リッチモンドホテル+プレミア仙台駅前&destination=リッチモンドホテル+プレミア仙台駅前&waypoints=カラオケ館+一番町本店|牛たん料理+閣+ブランドーム本店&travelmode=walking",
    18: "https://www.google.com/maps/dir/?api=1&origin=リッチモンドホテル+プレミア仙台駅前&destination=リッチモンドホテル+プレミア仙台駅前&waypoints=鯛きち+名掛丁本店|とんかつ牡丹|八木山動物公園+フジサキの杜|斎太郎&travelmode=transit",
    19: "https://www.google.com/maps/dir/?api=1&origin=リッチモンドホテル+プレミア仙台駅前&destination=天然温泉+杜都の湯+御宿+野乃+仙台&waypoints=びっくりドンキー+クリスロード店|仙台城跡|仙台市博物館|開盛庵&travelmode=transit",
    20: "https://www.google.com/maps/dir/?api=1&origin=天然温泉+杜都の湯+御宿+野乃+仙台&destination=仙台空港&waypoints=仙台駅&travelmode=transit"
}

def add_minutes(time_str, minutes=45):
    try:
        h, m = map(int, time_str.split(':'))
        total_m = h * 60 + m + minutes
        new_h = (total_m // 60) % 24
        new_m = total_m % 60
        return f"{new_h:02d}:{new_m:02d}"
    except Exception:
        return time_str

def clean_fact_markdown(s):
    if not s:
        return ""
    s = re.sub(r'\[([^\]]+)\]\((https?://[^\)]+)\)', r'<a href="\2" target="_blank" rel="noopener noreferrer" class="it-link">\1 ↗</a>', s)
    s = re.sub(r'\*\*\*([^*]+)\*\*\*', r'<strong><em>\g<1></em></strong>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\g<1></strong>', s)
    s = re.sub(r'\*([^*]+)\*', r'<em>\g<1></em>', s)
    s = s.replace('**', '').replace('*', '').strip()
    return s

def parse_appendix_tables(full_text):
    # 1. Parse Spot Table
    spot_dict = {}
    spot_start = full_text.find('## <a id="spot-summary-table"')
    spot_end = full_text.find('## <a id="transit-summary-table"')
    if spot_start != -1 and spot_end != -1:
        spot_section = full_text[spot_start:spot_end]
        spot_rows = [r.strip() for r in spot_section.split('\n') if r.strip().startswith('| **Day')]
        for row in spot_rows:
            cols = [c.strip() for c in row.split('|')[1:-1]]
            if len(cols) >= 6:
                m_day = re.search(r'Day\s*(\d+)', cols[0])
                day_num = int(m_day.group(1)) if m_day else 0
                name_cell = cols[2]
                m_jp = re.search(r'\*\(([^)]+)\)\*', name_cell)
                jp_name = m_jp.group(1).strip() if m_jp else ""
                m_title = re.search(r'\[([^\]]+)\]', name_cell)
                spot_title = m_title.group(1).strip() if m_title else name_cell
                badge_cell = cols[3].replace('<br>', ' ').strip('* ')
                rules_cell = cols[4]
                highlights_cell = cols[5]
                rules_clean = [clean_fact_markdown(r.strip('• *').strip()) for r in rules_cell.split('<br>') if r.strip()]
                key = spot_title.split('(')[0].split('（')[0].strip()
                spot_dict[key] = {
                    "day": day_num,
                    "title": spot_title,
                    "jp_name": jp_name or key,
                    "badge": clean_fact_markdown(badge_cell),
                    "rules": rules_clean,
                    "highlights": clean_fact_markdown(highlights_cell.strip())
                }

    # 2. Parse Dining Table
    dining_dict = {}
    dining_start = full_text.find('## <a id="dining-summary-table"')
    dining_end = full_text.find('## 🎯 需求檢核與亮點一覽表')
    if dining_start != -1 and dining_end != -1:
        dining_section = full_text[dining_start:dining_end]
        dining_rows = [r.strip() for r in dining_section.split('\n') if r.strip().startswith('| **')]
        for row in dining_rows:
            cols = [c.strip() for c in row.split('|')[1:-1]]
            if len(cols) >= 8:
                m_day = re.search(r'Day\s*(\d+)', cols[0])
                day_num = int(m_day.group(1)) if m_day else 0
                name_cell = cols[2]
                m_title = re.search(r'\[([^\]]+)\]', name_cell)
                rest_name = m_title.group(1).strip() if m_title else name_cell
                m_sub = re.search(r'\*\(([^)]+)\)\*', name_cell)
                cuisine = m_sub.group(1).strip() if m_sub else ""
                hours_cell = cols[3].replace('<br>', ' ｜ ')
                closed_cell = cols[4].replace('<br>', ' ｜ ')
                rating_cell = cols[5].replace('<br>', ' ').strip('* ')
                channel_cell = cols[6].replace('<br>', ' ｜ ')
                tips_cell = cols[7]
                clean_name = rest_name.split('(')[0].split('（')[0].strip()
                dining_dict[clean_name] = {
                    "day": day_num,
                    "name": rest_name,
                    "jp_name": clean_name,
                    "cuisine": clean_fact_markdown(cuisine),
                    "hours": clean_fact_markdown(hours_cell),
                    "closed": clean_fact_markdown(closed_cell),
                    "rating": clean_fact_markdown(rating_cell),
                    "channel": clean_fact_markdown(channel_cell),
                    "tips": clean_fact_markdown(tips_cell.strip())
                }

    # 3. Parse Hotel Table
    hotel_dict = {}
    hotel_start = full_text.find('## <a id="hotel-summary-table"')
    hotel_end = full_text.find('## <a id="dining-summary-table"')
    if hotel_start != -1 and hotel_end != -1:
        hotel_section = full_text[hotel_start:hotel_end]
        hotel_rows = [r.strip() for r in hotel_section.split('\n') if r.strip().startswith('| **[')]
        for row in hotel_rows:
            cols = [c.strip() for c in row.split('|')[1:-1]]
            if len(cols) >= 6:
                name_cell = cols[0]
                m_title = re.search(r'\[([^\]]+)\]', name_cell)
                hotel_name = m_title.group(1).strip() if m_title else name_cell
                clean_name = re.sub(r'^[①-⑨\s]+', '', hotel_name).strip()
                hotel_dict[clean_name] = {
                    "name": clean_name,
                    "jp_name": clean_name,
                    "checkin_out": clean_fact_markdown(cols[1].replace('<br>', ' ｜ ').strip()),
                    "lounge": clean_fact_markdown(cols[2].replace('<br>', ' ｜ ').strip()),
                    "bath_onsen": clean_fact_markdown(cols[3].replace('<br>', ' ｜ ').strip()),
                    "laundry": clean_fact_markdown(cols[4].replace('<br>', ' ｜ ').strip()),
                    "breakfast": clean_fact_markdown(cols[5].replace('<br>', ' ｜ ').strip()),
                }

    return spot_dict, dining_dict, hotel_dict

DAY_HOTEL_MAP = {
    1: 'ホテルマイステイズ青森駅前',
    2: 'ホテルマイステイズ青森駅前',
    3: '南部屋・海扇閣',
    4: '浅虫温泉 椿館',
    5: 'リッチモンドホテル青森',
    6: 'リッチモンドホテル青森',
    7: 'コンフォートホテル八戸',
    8: 'コンフォートホテル八戸',
    9: 'コンフォートホテル八戸',
    10: '松島一之坊',
    11: 'スーパーホテル仙台駅東口天然温泉',
    12: 'スーパーホテル仙台駅東口天然温泉',
    13: 'スーパーホテル仙台駅東口天然温泉',
    14: 'スーパーホテル仙台駅東口天然温泉',
    15: 'リッチモンドホテル プレミア仙台駅前',
    16: 'リッチモンドホテル プレミア仙台駅前',
    17: 'リッチモンドホテル プレミア仙台駅前',
    18: 'リッチモンドホテル プレミア仙台駅前',
    19: '天然溫泉 杜都之湯 御宿 野乃 仙台',
    20: '天然溫泉 杜都之湯 御宿 野乃 仙台',
}

GENERIC_STOPWORDS = {
    '天然溫泉', '國寶', '八戸市', '青森縣立', '公園', '美術館', '水族館', '動物園', 
    '市場', '展望台', '神社', '寺院', '城跡', '海岸', '溫泉', '食堂', '拉麵', '燒肉'
}

def match_hotel(item, hotel_dict):
    day_num = item['day']
    title = item['title']
    cat = item['category']
    raw = item.get('raw_text', '')
    
    # Priority 0: Check-out handling
    # Check-outs strictly anchor to the hotel stayed in the previous night (day_num - 1)
    if ('退房' in title or 'check-out' in title.lower()) and not any(kw in title for kw in ['準時 check-in', '正式 check-in', '辦理入住']):
        target_k = DAY_HOTEL_MAP.get(day_num - 1)
        if target_k and target_k in hotel_dict:
            return target_k, hotel_dict[target_k]

    # Priority 1: Direct distinct name match in title
    for k, v in hotel_dict.items():
        if k in title:
            return k, v
        if 'マイステイズ' in k and ('マイステイズ' in title or 'mystays' in title.lower()):
            return k, v
        if '海扇閣' in k and '海扇閣' in title and cat == 'hotel':
            return k, v
        if '椿館' in k and '椿館' in title and cat == 'hotel':
            return k, v
        if 'コンフォート' in k and ('コンフォート' in title or 'comfort' in title.lower()) and cat == 'hotel':
            return k, v
        if '一之坊' in k and ('一之坊' in title or '一の坊' in title or '太古天泉' in title or (day_num == 11 and any(w in title for w in ['太古天泉', '水上庭園', '客房海景陽台']))):
            return k, v
        if 'スーパーホテル' in k and ('スーパーホテル' in title or 'super hotel' in title.lower()):
            return k, v
        if '野乃' in k and ('野乃' in title or '御宿' in title):
            return k, v
        if 'プレミア仙台駅前' in k and ('プレミア仙台駅前' in title or ('プレミア' in title and '仙台' in title)):
            return k, v
        if 'リッチモンドホテル青森' in k and ('リッチモンド' in title and '青森' in title):
            return k, v

    # Priority 2: If item category is hotel, anchor to the appropriate hotel
    if cat == 'hotel' or any(kw in title for kw in ['住宿【', 'Check-in', '退房', '寄放行李', '寄存行李', '換宿']):
        if ('退房' in title or 'check-out' in title.lower()) and not any(kw in title for kw in ['新飯店', '換宿', '寄放', '寄存']):
            target_k = DAY_HOTEL_MAP.get(day_num - 1, DAY_HOTEL_MAP.get(day_num))
            if target_k and target_k in hotel_dict:
                return target_k, hotel_dict[target_k]
        if 'プレミア' in title or ('新飯店' in title and day_num == 15):
            target_k = 'リッチモンドホテル プレミア仙台駅前'
            return target_k, hotel_dict[target_k]
        if '野乃' in title or '御宿' in title:
            target_k = '天然溫泉 杜都之湯 御宿 野乃 仙台'
            return target_k, hotel_dict[target_k]
        
        target_k = DAY_HOTEL_MAP.get(day_num)
        if target_k and target_k in hotel_dict:
            return target_k, hotel_dict[target_k]
            
    return None, None

def match_dining(item, dining_dict):
    day_num = item['day']
    title = item['title']
    cat = item['category']
    if cat == 'transit':
        return None, None
        
    # Priority 1: Exact / Distinct name match in title
    for k, v in dining_dict.items():
        if k in title:
            return k, v
        if '大西' in k and '大西' in title:
            return k, v
        if ('さくら野' in k or '北海道展' in k) and ('さくら野' in title or '北海道展' in title):
            return k, v
        if '長尾中華そば' in k and '長尾中華' in title:
            return k, v
        if '神田川' in k and '神田川' in title:
            return k, v
        if '林檎家' in k and '林檎家' in title:
            return k, v
        if '丸青食堂' in k and '丸青' in title:
            return k, v
        if ('cafe apricot' in k.lower() or 'アプリコット' in k) and ('apricot' in title.lower() or 'アプリコット' in title or ('咖啡' in title and day_num == 3)):
            return k, v
        if '海つ路' in k:
            if '海つ路' in title or (day_num == 3 and any(w in title for w in ['晚餐', 'buffet', 'Buffet', '料理'])):
                return k, v
        if '正立食堂' in k and '正立食堂' in title:
            return k, v
        if '椿の宴' in k:
            if '椿の宴' in title or (day_num == 4 and any(w in title for w in ['晚餐', '會席'])):
                return k, v
        if 'のっけ丼' in k or '魚菜センター' in k:
            if any(w in title for w in ['のっけ丼', '魚菜センター']) or ('古川市場' in title and ('朝食' in title or '海鮮丼' in title)):
                return k, v
        if '吉兆' in k and '吉兆' in title:
            return k, v
        if 'Richmond Hotel 青森 5F 朝食' in k or 'Richmond Hotel 青森 5F 朝食百匯' in k:
            if day_num == 6 and ('朝食' in title or '早餐' in title or 'buffet' in title.lower()):
                return k, v
        if '大正浪漫喫茶室' in k and any(w in title for w in ['大正浪漫', '喫茶室']):
            return k, v
        if 'じょっぱり' in k and 'じょっぱり' in title:
            return k, v
        if 'ブナの森' in k and ('ブナの森' in title or 'ひとくちだらけ' in title or '便當' in title or '駅弁' in title or (day_num == 7 and '改札' in title)):
            return k, v
        if 'みろく横丁' in k and 'みろく横丁' in title and ('晚餐' in title or cat == 'dining'):
            return k, v
        if 'Comfort Hotel 八戶 1F 朝食' in k:
            if ('comfort' in title.lower() or '八戶' in title) and ('朝食' in title or '早餐' in title) and day_num in [8, 10]:
                return k, v
        if '波光食堂' in k and '波光食堂' in title:
            return k, v
        if '天草' in k and '天草' in title:
            return k, v
        if 'みなと食堂' in k and 'みなと食堂' in title:
            return k, v
        if '七厘村' in k and ('七厘村' in title or ('八食' in title and '烤' in title)):
            return k, v
        if '烹鱗' in k and ('烹鱗' in title or 'いかめしや' in title):
            return k, v
        if '青海波' in k and '青海波' in title:
            if ('朝食' in k or '早餐' in k or v.get('day') == 11) and (day_num == 11 or any(w in title for w in ['朝食', '早餐'])):
                return k, v
            if ('夕食' in k or '晚餐' in k or '料理長' in k or v.get('day') == 10) and (day_num == 10 or any(w in title for w in ['晚餐', '夕食', '晚宴'])):
                return k, v
        if '焼がきハウス' in k and any(w in title for w in ['焼がきハウス', '烤海鞘', '松島さかな市場', '牡蠣']):
            return k, v
        if '泰山' in k and '泰山' in title:
            return k, v
        if 'どん亭' in k and 'どん亭' in title:
            return k, v
        if 'かとう' in k and 'かとう' in title:
            return k, v
        if '美登屋' in k and ('美登屋' in title or '瀧不動' in title or ('山寺' in title and '蕎麥' in title and day_num == 13)):
            return k, v
        if '陽だまり食堂' in k and ('陽だまり' in title or ('蛋包飯' in title and (day_num == 13 or day_num == 15))):
            return k, v
        if 'だし廊' in k and ('だし廊' in title or 'dashiro' in title.lower()):
            return k, v
        if 'ガスト' in k and ('ガスト' in title or 'gusto' in title.lower()):
            return k, v
        if '洋食 HACHI' in k and ('ハチ' in title or re.search(r'\bhachi\b', title, re.I) or ('洋食' in title and '蛋包飯' not in title and '陽だまり' not in title)) and '八幡宮' not in title:
            return k, v
        if '仙台朝市 鮮魚攤' in k and (('鮮魚' in title or '齋藤' in title) or (day_num == 16 and '朝市' in title and ('朝食' in title or '早餐' in title))):
            return k, v
        if 'みそ壱' in k and 'みそ壱' in title:
            return k, v
        if 'ちからや' in k and ('ちからや' in title or 'ち力らや' in title):
            return k, v
        if '開盛庵' in k and '開盛庵' in title:
            return k, v
        if '牛たん料理 閣' in k and '閣' in title and ('牛たん' in title or '牛舌' in title):
            return k, v
        if ('鯛きち' in k or 'たい焼き' in k) and ('鯛きち' in title or 'たい焼き' in title or '鯛魚燒' in title):
            return k, v
        if 'さいち' in k and ('さいち' in title or 'saichi' in title.lower() or '萩餅' in title):
            return k, v
        if '牡丹' in k and ('牡丹' in title or 'とんかつ牡丹' in title):
            return k, v
        if '斎太郎' in k and ('斎太郎' in title or ('痛風鍋' in title and day_num == 18)):
            return k, v
        if 'すし哲' in k and ('すし哲' in title or ('壽司盛宴' in title and day_num == 19)):
            return k, v
        if '御宿野乃 仙台 2F 旅籠' in k and ('hatago' in title.lower() or '旅籠' in title or (day_num == 20 and ('早餐' in title or '朝食' in title))):
            return k, v

    return None, None

def match_spot(item, spot_dict):
    day_num = item['day']
    title = item['title']
    cat = item['category']
    raw = item.get('raw_text', '')
    
    # Strictly disallow transit items matching spots unless it's a scenic cruise or ropeway
    if cat == 'transit' and not any(kw in title for kw in ['觀光船', '仁王丸', '纜車', 'ロープウェー']):
        return None, None
        
    for k, v in spot_dict.items():
        if k in title:
            return k, v
        if '青い海公園' in k and '青い海公園' in title:
            return k, v
        if '八甲田空中纜車' in k and ('八甲田' in title and ('纜車' in title or 'ロープウェー' in title)):
            return k, v
        if '奧入瀨溪流' in k and '奧入瀨' in title:
            return k, v
        if '十和田湖' in k and ('十和田湖' in title or '遊覽船' in title or '遊覧船' in title):
            return k, v
        if 'アウガ新鮮市場' in k and ('アウガ' in title or 'auga' in title.lower()):
            return k, v
        if '淺蟲螢火蟲湖' in k and ('螢火蟲湖' in title or 'ホタル湖' in title or '浅虫ダム' in title):
            return k, v
        if '淺虫水族館' in k and ('淺虫水族館' in title or '浅虫水族館' in title):
            return k, v
        if '淺虫日落海灘' in k and ('日落海灘' in title or 'サンセットビーチ' in title):
            return k, v
        if '古川市場' in k and '古川市場' in title and cat != 'dining':
            return k, v
        if 'WARASSE' in k and ('warasse' in title.lower() or 'ワ・ラッセ' in title or '睡魔之家' in title):
            return k, v
        if 'A-FACTORY' in k and ('a-factory' in title.lower() and cat != 'dining'):
            return k, v
        if '冬景色歌謠碑' in k and '冬景色' in title:
            return k, v
        if '八甲田丸' in k and '八甲田丸' in title:
            return k, v
        if 'ASPAM' in k and ('aspam' in title.upper() or ('展望台' in title and day_num == 5)):
            return k, v
        if '三內丸山' in k and ('三內丸山' in title or '三内丸山' in title):
            return k, v
        if '弘前城' in k and ('弘前城' in title or '弘前公園' in title):
            return k, v
        if '藤田紀念庭園' in k and '藤田紀念庭園' in title and cat != 'dining':
            return k, v
        if '津輕藩佞武多村' in k and ('佞武多村' in title or 'ねぷた村' in title):
            return k, v
        if '星巴克 弘前公園前店' in k and '星巴克' in title and day_num == 6:
            return k, v
        if '三澤航空科學館' in k and ('航空科學館' in title or '航空科学館' in title):
            return k, v
        if '八戶市美術館' in k and '八戶市美術館' in title:
            return k, v
        if 'みろく横丁' in k and 'みろく横丁' in title and cat != 'dining':
            return k, v
        if '魚菜零售市場' in k and ('魚菜零售市場' in title or '陸奧湊朝市' in title):
            return k, v
        if '種差海岸天然大草皮' in k and ('天然大草皮' in title or '天然芝生地' in title or ('種差海岸' in title and '遊客中心' not in title and 'インフォメーション' not in title and '站' not in title)):
            return k, v
        if '種差海岸遊客中心' in k and ('遊客中心' in title or 'インフォメーション' in title or 'information' in title.lower()):
            return k, v
        if '葦毛崎展望台' in k and '葦毛崎' in title:
            return k, v
        if '大須賀海岸' in k and '大須賀' in title:
            return k, v
        if '蕪嶋神社' in k and ('蕪嶋' in title or '蕪島' in title) and cat != 'transit':
            return k, v
        if '八戶酒造' in k and ('八戶酒造' in title or '八仙' in title) and ('見學' in title or '酒藏' in title):
            return k, v
        if '八食中心' in k and '八食中心' in title and cat != 'dining':
            return k, v
        if '松島一之坊 水上庭園' in k and ('水上庭園' in title or ('一之坊' in title and '休息室' in title)):
            return k, v
        if '藤田喬平玻璃美術館' in k and ('藤田喬平' in title or '玻璃美術館' in title):
            return k, v
        if '松島繞島觀光船' in k and ('仁王丸' in title or ('觀光船' in title and day_num == 11)):
            return k, v
        if '國寶 瑞嚴寺' in k and ('瑞嚴寺' in title or '瑞巌寺' in title or ('五大堂' in title and day_num == 11)):
            return k, v
        if '陸奧伊達政宗歷史館' in k and ('伊達政宗歷史館' in title or '伊達歷史館' in title):
            return k, v
        if '仙台市博物館' in k and '仙台市博物館' in title:
            return k, v
        if '仙台城跡' in k and ('仙台城跡' in title or '青葉城跡' in title or '騎馬像' in title) and '下山' not in title:
            return k, v
        if '定禪寺通' in k and ('定禪寺通' in title or '定禅寺通' in title) and cat not in ['transit', 'dining']:
            return k, v
        if '仙台媒體中心' in k and ('仙台媒體中心' in title or 'メディアテーク' in title or 'smt' in title.lower()):
            return k, v
        if 'AER 展望テラス' in k and ('aer' in title.lower() and ('展望台' in title or '展望テラス' in title)):
            return k, v
        if '宮城峽蒸餾所' in k and ('宮城峽' in title or '宮城峡' in title or 'nikka' in title.lower()) and '專車' not in title:
            return k, v
        if '山寺' in k and ('山寺' in title or '立石寺' in title) and ('石階' in title or '名剎' in title or '登山' in title or cat == 'spot') and '下山' not in title:
            return k, v
        if '瑞鳳殿' in k and '瑞鳳殿' in title and ('長眠' in title or '靈廟' in title or cat == 'spot') and '前往' not in title:
            return k, v
        if '大崎八幡宮' in k and '大崎八幡宮' in title:
            return k, v
        if '仙台朝市' in k and '仙台朝市' in title and cat != 'dining':
            return k, v
        if '仙台海洋森林水族館' in k and ('仙台海洋森林水族館' in title or 'うみの杜' in title) and '直奔' not in title:
            return k, v
        if '卡拉OK館 一番町本店' in k and ('卡拉ok' in title.lower() or 'カラオケ' in title) and cat in ['activity', 'spot']:
            return k, v
        if '八木山動物公園' in k and ('八木山動物公園' in title or 'フジサキの杜' in title) and '直達' not in title:
            return k, v
        if '天然溫泉 杜都之湯 御宿 野乃 仙台' in k and day_num == 19 and ('杜都之湯' in title or ('野乃' in title and '溫泉' in title)):
            return k, v

    return None, None

def match_entity(item, spot_dict, dining_dict, hotel_dict):
    cat = item['category']
    
    # 1. Category-aware primary matching
    if cat == 'hotel':
        hk, hval = match_hotel(item, hotel_dict)
        if hval:
            return 'hotel', hk, hval
    elif cat == 'dining':
        dk, dval = match_dining(item, dining_dict)
        if dval:
            return 'dining', dk, dval
        sk, sval = match_spot(item, spot_dict)
        if sval:
            return 'spot', sk, sval
    elif cat == 'spot':
        sk, sval = match_spot(item, spot_dict)
        if sval:
            return 'spot', sk, sval
        dk, dval = match_dining(item, dining_dict)
        if dval:
            return 'dining', dk, dval
    elif cat == 'activity':
        sk, sval = match_spot(item, spot_dict)
        if sval:
            return 'spot', sk, sval
        dk, dval = match_dining(item, dining_dict)
        if dval:
            return 'dining', dk, dval
        hk, hval = match_hotel(item, hotel_dict)
        if hval:
            return 'hotel', hk, hval
    elif cat == 'transit':
        # Only scenic cruise or ropeway allowed
        sk, sval = match_spot(item, spot_dict)
        if sval:
            return 'spot', sk, sval
        return None, None, None
            
    # Fallback for general items:
    sk, sval = match_spot(item, spot_dict)
    if sval:
        return 'spot', sk, sval
    dk, dval = match_dining(item, dining_dict)
    if dval:
        return 'dining', dk, dval
    hk, hval = match_hotel(item, hotel_dict)
    if hval:
        return 'hotel', hk, hval
        
    return None, None, None

def parse_markdown():
    with open(ITINERARY_MD_PATH, 'r', encoding='utf-8') as f:
        full_text = f.read()

    spot_dict, dining_dict, hotel_dict = parse_appendix_tables(full_text)
    print(f"Loaded {len(spot_dict)} spots, {len(dining_dict)} dining, {len(hotel_dict)} hotels from appendix tables.")

    d20_end = full_text.find('## 📝 全方位行前準備與預訂 TODO List')
    if d20_end != -1:
        itinerary_text = full_text[:d20_end]
    else:
        itinerary_text = full_text

    day_pattern = r'#### 🗓️ Day (\d+)（([^）]+)）[：:]([^\n]+)'
    matches = list(re.finditer(day_pattern, itinerary_text))

    time_pattern = r'(\d{1,2}:\d{2})(?:\s*[-～~—]\s*(\d{1,2}:\d{2}))?'

    days = []

    day_tags = {
        1: ("青森市", "航班抵達・拉麵"),
        2: ("八甲田・十和田", "奧入瀨溪流・成吉思汗烤肉"),
        3: ("淺虫溫泉", "AUGA市場・海扇閣Buffet"),
        4: ("淺虫溫泉", "水族館・日落海灘・椿館"),
        5: ("青森市", "味の札幌大西・WARASSE・A-Factory"),
        6: ("青森市", "頂級朝食百匯・三內丸山遺跡・じょっぱり"),
        7: ("三澤・八戶", "航空科學館・みろく橫丁"),
        8: ("種差海岸", "天然大草皮・蕪嶋神社・天草馬刺"),
        9: ("八戶市", "八戶酒造・八食中心七厘村"),
        10: ("松島町", "新幹線南下・松島一之坊"),
        11: ("松島町", "仁王丸・瑞嚴寺・伊達歷史館"),
        12: ("仙台市", "定禪寺通・媒體中心smt・壽喜燒かとう"),
        13: ("山寺・作並", "宮城峽威士忌・山寺・洋食HACHI漢堡排"),
        14: ("仙台市", "瑞鳳殿・だし廊・Welcome Bar"),
        15: ("仙台市", "國寶大崎八幡宮・Richmond午茶・陽だまり食堂蛋包飯"),
        16: ("仙台市", "仙台朝市・水族館・ちからや仙台牛"),
        17: ("仙台市", "客房休息消食・卡拉OK暢唱・閣牛舌刺身"),
        18: ("仙台市", "鯛きち鯛魚燒・牡丹炸豬排・八木山動物公園・斎太郎"),
        19: ("仙台市", "漢堡排・青葉城・仙台博物館・開盛庵鰻魚"),
        20: ("仙台機場", "豪華早餐・返抵台灣"),
    }

    start_base_date = date(2026, 9, 28)

    for i, m in enumerate(matches):
        day_num = int(m.group(1))
        date_raw = m.group(2).strip()
        day_title = m.group(3).strip()

        start_pos = m.end()
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(itinerary_text)
        day_block = itinerary_text[start_pos:end_pos].strip()

        iso_date = (start_base_date + timedelta(days=day_num - 1)).strftime('%Y-%m-%d')
        region, subtitle = day_tags.get(day_num, ("東北", ""))

        clean_day_title = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', day_title)

        wakeup_match = re.search(r'- [⏰\s]*\*\*預計起床時間\*\*[：:]\s*\*\*(\d{1,2}:\d{2})\*\*(?:（([^）\n]+)）)?', day_block)
        wake_up_time = wakeup_match.group(1).strip() if wakeup_match else None
        wake_up_note = wakeup_match.group(2).strip() if (wakeup_match and wakeup_match.group(2)) else ""

        raw_items = [it.strip() for it in re.split(r'\n(?=- \*\*)', '\n' + day_block) if it.strip()]
        
        parsed_items = []
        intro_text = ""

        item_idx = 1
        for it in raw_items:
            if not it.startswith('- **'):
                intro_text += it + "\n"
                continue

            lines = it.split('\n')
            first_line = lines[0]
            body_lines = lines[1:]

            clean_first = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', first_line)
            clean_first = re.sub(r'^- \*\*', '', clean_first)
            clean_first = re.sub(r'\*\*[：:]?.*$', '', clean_first).strip()

            tm = re.match(r'^\s*' + time_pattern, clean_first)
            if tm:
                time_display = tm.group(0).strip()
                t_start = tm.group(1)
                t_end = tm.group(2)
                item_title = clean_first[tm.end():].strip()
            else:
                if '住宿' in clean_first or '宿：' in clean_first:
                    time_display = "今晚宿泊"
                    t_start = "21:00"
                    t_end = "23:59"
                    item_title = clean_first
                else:
                    tm_sub = re.search(time_pattern, it)
                    if tm_sub:
                        time_display = tm_sub.group(0).strip()
                        t_start = tm_sub.group(1)
                        t_end = tm_sub.group(2)
                        item_title = clean_first
                    else:
                        time_display = "全日"
                        t_start = "12:00"
                        t_end = "13:00"
                        item_title = clean_first

            item_title = re.sub(r'^[【\[\s]+', '', item_title)
            item_title = re.sub(r'[】\]\s]+$', '', item_title)
            if not item_title or item_title == clean_first:
                after_col = first_line.split('**：')
                if len(after_col) > 1 and after_col[1].strip():
                    item_title = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', after_col[1].strip())
                else:
                    item_title = clean_first

            item_title = item_title.replace('**', '').strip()
            item_title = item_title.strip('【】[]*:： ')

            fl_lower = first_line.lower()
            category = "general"
            category_label = "📌 行程"
            badge = ""

            if any(k in fl_lower for k in ['apricot', '喫茶']) and not any(k in fl_lower for k in ['🏨', 'check-in', '退房', '寄放行李', '寄存行李']):
                category = "dining"
                category_label = "🥩 極上美食"
            elif any(k in fl_lower for k in ['🥩', '🍜', '🍣', '🍱', '午餐', '晚餐', '早餐', '朝食', '夕食', '美食', '拉麵', 'ラーメン', '壽喜燒', 'すき焼き', '燒肉', '焼肉', '居酒屋', '牛舌', '牛たん', '鰻魚', 'う那ぎ', 'う那ぎ', 'うなぎ', '豬排', 'とんかつ', '吃到飽', '下午茶', '食堂', '咖啡']) and not any(k in fl_lower for k in ['步行前往', '散步前往', '住宿【', 'check-in', 'checkin', '退房', '入住', '寄放行李', '寄存行李', '換宿', '迎賓微醺', 'welcome bar', 'lounge', '客房', '陽台', '小憩']):
                category = "dining"
                category_label = "🥩 極上美食"
            elif any(k in fl_lower for k in ['🏨', '住宿', 'check-in', 'checkin', '退房', '入住', '寄放行李', '寄存行李', '換宿', '迎賓', '風呂', 'lounge', 'welcome bar', '大浴場', '天然溫泉', '泡湯']):
                category = "hotel"
                category_label = "🏨 頂級名宿"
            elif any(k in fl_lower for k in ['🎤', '🧺', '洗衣服', '洗衣', '見學', '體驗', '採買', '購物', '卡拉ok', 'カラオケ']):
                category = "activity"
                category_label = "🎯 特色體驗"
            elif any(k in fl_lower for k in ['うみねこ號', 'うみねこ号', 'みずうみ号', 'みずうみ號', '市營公車', '市營巴士', '町民バス', '接駁專車']):
                category = "transit"
                category_label = "🚌 交通銜接"
            elif any(k in fl_lower for k in ['水族館', '動物園', '博物館', '美術館', '三內丸山', '三内丸山', '立石寺', '瑞嚴寺', '瑞巌寺', '輪王寺', '瑞鳳殿', '青葉城', '弘前城', '八幡宮', '神宮', '靈廟', '蕪嶋神社', '蕪島', '日落海灘', '大須賀海岸', '種差海岸', '展望台', '展望テラス', '八甲田丸', '三澤航空', '八戶酒造', '奧入瀨', '十和田湖', '媒體中心', 'メディアテーク', '自然名勝', '大草皮', '天然芝生地', '遊客中心', '定禪寺通', '定禅寺通', '必去景點']) and not any(k in fl_lower for k in ['公車', '巴士', '電車', '新幹線', '鐵道', 'jr', '搭乘', '車程', '接駁', '送迎', '候車', '直達', '返回', '返抵', '前往', '直奔', '下車', '出發']):
                category = "spot"
                if '必去景點' in fl_lower or any(f'必去景點 {c}' in fl_lower for c in '①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳㉑㉒㉓㉔㉕㉖㉗'):
                    category_label = "🌟 必去景點"
                else:
                    category_label = "🏛️ 景點名勝"
            elif any(k in fl_lower for k in ['🚌', '🚅', '🚄', '✈️', '🚢', '🚕', '公車', '巴士', '新幹線', '電車', '鐵道', 'jr', '車程', '接駁', '送迎', '利木津', '航線', '航班', '搭乘', '出發', '抵達', '步行', '漫步', '散步', '前往', '直達', '下山']):
                if any(k in fl_lower for k in ['觀光船', '仁王丸', '纜車', 'ロープウェー']):
                    category = "spot"
                    category_label = "🌟 必去景點"
                else:
                    category = "transit"
                    category_label = "🚌 交通銜接"
            else:
                combined_text = it.lower()
                if any(k in combined_text for k in ['必去景點']):
                    category = "spot"
                    category_label = "🌟 必去景點"
                elif any(k in combined_text for k in ['拉麵', 'ラーメン', '午餐', '晚餐', '夕食', '壽喜燒', '居酒屋']):
                    category = "dining"
                    category_label = "🥩 極上美食"

            if '必去景點' in fl_lower:
                m_spot = re.search(r'必去景點\s*([①-㊿\d]+)', it)
                if m_spot:
                    badge = f"🌟 必去景點 {m_spot.group(1)}"
                else:
                    badge = "🌟 必去景點"
            elif '已預約妥當' in it or '已訂妥' in it or '已完成預約' in it:
                badge = "🌟 已確定訂妥"
            elif '免費接駁' in it or '送迎專車' in it:
                badge = "🚐 免費接駁"
            elif '免預約' in it:
                badge = "🟢 免預約自由搭乘"
            elif '必預約' in it or '🔴' in it:
                badge = "🔴 必預約名店"
            elif '自費加購' in it or '自選' in it:
                badge = "💡 彈性自選"

            map_links = []
            seen_urls = set()
            link_pattern = r'\[([^\]]+)\]\((https://www\.google\.com/maps/[^\)]+)\)'
            for l_text, l_url in re.findall(link_pattern, it):
                if l_url not in seen_urls:
                    seen_urls.add(l_url)
                    is_dir = ("dir/?api=1" in l_url or "travelmode=" in l_url)
                    clean_l_name = l_text.strip('🚶🚗🚌📍 ')
                    map_links.append({
                        "name": clean_l_name,
                        "url": l_url.strip(),
                        "is_dir": is_dir
                    })

            cautions = []
            for line in body_lines:
                sline = line.strip()
                if any(p in sline for p in ['🚨', '⚠️', '💡', '🚫', '避坑', '防雷', '加購機制', '搶位秘訣', '不吃芹菜', '重要註記', '定休日', '連假']):
                    clean_c = re.sub(r'^(\s*[-*+>]+\s+)+', '', sline)
                    clean_c = convert_markdown_inline(clean_c)
                    clean_c = re.sub(r'^\*+|\*+$', '', clean_c).strip()
                    if len(clean_c) > 8 and clean_c not in cautions:
                        cautions.append(clean_c)

            body_html = format_markdown_body(body_lines)

            custom_links = []
            if any(k in it for k in ['うみねこ號', 'うみねこ号']):
                custom_links.append({
                    "name": "うみねこ號 官方時刻表",
                    "url": "https://www.city.hachinohe.aomori.jp/section/bus/onecoin_uminekogou.html",
                    "icon": "🚌"
                })
                custom_links.append({
                    "name": "時刻表 PDF (令和8年度)",
                    "url": "https://www.city.hachinohe.aomori.jp/section/bus/image/side_button/tanesashi/2026timetablefull_tanesashi.pdf",
                    "icon": "📄"
                })
            if '蕪島町' in it or ('蕪島' in it and any(b in it for b in ['市營巴士', '市営バス', '市營公車'])):
                custom_links.append({
                    "name": "蕪島町公車時刻表 PDF (001)",
                    "url": "https://www.city.hachinohe.aomori.jp/section/bus/image/jikokuhyou/jikoku/0115_001.pdf",
                    "icon": "🚌"
                })
            if any(k in it for k in ['八食 150', '八食150', '八食センター 150', '150円巴士', '150 円巴士']):
                custom_links.append({
                    "name": "八食150円巴士 時刻表 PDF",
                    "url": "https://www.849net.com/access/bus150_202604.pdf",
                    "icon": "🚌"
                })

            temp_item = {
                "id": f"d{day_num}-item-{item_idx}",
                "day": day_num,
                "time_display": time_display,
                "start_time": t_start,
                "end_time": t_end,
                "title": item_title,
                "category": category,
                "category_label": category_label,
                "badge": badge,
                "cautions": cautions[:6],
                "map_links": map_links,
                "custom_links": custom_links,
                "body_html": body_html,
                "raw_text": it,
                "japanese_name": "",
                "fact_data": None
            }

            etype, ek, evalue = match_entity(temp_item, spot_dict, dining_dict, hotel_dict)
            if evalue:
                temp_item['japanese_name'] = evalue.get('jp_name', '')
                if etype == 'spot':
                    temp_item['fact_data'] = {
                        "type": "spot",
                        "title": evalue['title'],
                        "jp_name": evalue['jp_name'],
                        "badge": evalue['badge'],
                        "rules": evalue['rules'],
                        "highlights": evalue['highlights']
                    }
                    raw_b = evalue.get('badge', '')
                    if '指定必去景點' in raw_b or '世界文化遺產' in raw_b or any(c in raw_b for c in '①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳㉑㉒㉓㉔㉕㉖㉗'):
                        temp_item['category_label'] = "🌟 必去景點"
                        m_num = re.search(r'([①-㊿\d]+)', raw_b)
                        if m_num:
                            temp_item['badge'] = f"🌟 必去景點 {m_num.group(1)}"
                        elif '世界文化遺產' in raw_b:
                            temp_item['badge'] = "🌟 世界文化遺產"
                        else:
                            temp_item['badge'] = "🌟 指定必去景點"
                    elif '需求檢核表' in raw_b:
                        temp_item['category_label'] = "🎯 需求景點"
                        m_cat = re.search(r'【([^】]+)】', raw_b)
                        temp_item['badge'] = f"🎯 需求：{m_cat.group(1)}" if m_cat else "🎯 需求檢核"
                    elif '國寶' in raw_b:
                        temp_item['category_label'] = "🏛️ 國寶古蹟"
                        temp_item['badge'] = "💡 國寶古蹟（非檢核表）"
                    elif '助理推薦' in raw_b:
                        temp_item['category_label'] = "✨ 助理推薦"
                        temp_item['badge'] = "✨ 助理推薦（非檢核表）"
                    elif any(w in raw_b for w in ['名剎', '靈廟', '歷史']):
                        temp_item['category_label'] = "🏛️ 文化名勝"
                        temp_item['badge'] = "💡 歷史名勝（非檢核表）"
                    elif any(w in raw_b for w in ['自然名勝', '大草皮', '遊客中心']):
                        temp_item['category_label'] = "🌲 自然名勝"
                        temp_item['badge'] = "💡 自然名勝（非檢核表）"
                    else:
                        temp_item['category_label'] = "🏛️ 景點名勝"
                        temp_item['badge'] = "💡 行程景點"
                elif etype == 'dining':
                    temp_item['fact_data'] = {
                        "type": "dining",
                        "name": evalue['name'],
                        "jp_name": evalue['jp_name'],
                        "cuisine": evalue['cuisine'],
                        "hours": evalue['hours'],
                        "closed": evalue['closed'],
                        "rating": evalue['rating'],
                        "channel": evalue['channel'],
                        "tips": evalue['tips']
                    }
                elif etype == 'hotel':
                    temp_item['fact_data'] = {
                        "type": "hotel",
                        "name": evalue['name'],
                        "jp_name": evalue['jp_name'],
                        "checkin_out": evalue['checkin_out'],
                        "lounge": evalue['lounge'],
                        "bath_onsen": evalue['bath_onsen'],
                        "laundry": evalue['laundry'],
                        "breakfast": evalue['breakfast']
                    }

            parsed_items.append(temp_item)
            item_idx += 1

        if wake_up_time:
            next_start = None
            for itm in parsed_items:
                if itm.get('start_time') and itm['start_time'] > wake_up_time:
                    next_start = itm['start_time']
                    break
            
            end_time = next_start if next_start else add_minutes(wake_up_time, 45)
            clean_note = wake_up_note.rstrip('。')
            wakeup_title = f"預計起床時間（{clean_note}）" if clean_note else "預計起床時間"
            
            wakeup_item = {
                "id": f"d{day_num}-item-0",
                "day": day_num,
                "time_display": wake_up_time,
                "start_time": wake_up_time,
                "end_time": end_time,
                "title": wakeup_title,
                "category": "wakeup",
                "category_label": "⏰ 起床整備",
                "badge": "⏰ 晨起整備",
                "cautions": [],
                "map_links": [],
                "custom_links": [],
                "body_html": f"<p>⏰ 晨間整備重點：{clean_note}。</p>" if clean_note else "",
                "raw_text": f"- ⏰ **預計起床時間**：**{wake_up_time}**（{clean_note}）。",
                "japanese_name": "",
                "fact_data": None
            }
            parsed_items.insert(0, wakeup_item)

        days.append({
            "day": day_num,
            "date_info": date_raw,
            "iso_date": iso_date,
            "title": clean_day_title,
            "region": region,
            "subtitle": subtitle,
            "wake_up_time": wake_up_time,
            "wake_up_note": wake_up_note,
            "intro_text": intro_text.strip(),
            "luggage_note": LUGGAGE_TRANSITIONS.get(day_num, ""),
            "route_url": DAY_ROUTES.get(day_num, ""),
            "items": parsed_items
        })

    return days

def normalize_list_indents(lines):
    bullet_indents = []
    for l in lines:
        m = re.match(r'^(\s*)[-*+]\s+', l)
        if m:
            bullet_indents.append(len(m.group(1)))
    
    if not bullet_indents:
        return '\n'.join(lines).strip()
    
    min_indent = min(bullet_indents)
    new_lines = []
    for l in lines:
        m = re.match(r'^(\s*)([-*+]\s+.*)$', l)
        if m:
            curr_indent = len(m.group(1))
            adjusted_indent = max(0, curr_indent - min_indent)
            new_lines.append(' ' * adjusted_indent + m.group(2))
        else:
            if l.startswith(' ' * min_indent):
                new_lines.append(l[min_indent:])
            else:
                new_lines.append(l.lstrip())
    return '\n'.join(new_lines).strip()

def format_markdown_body(lines):
    if not lines:
        return ""
    
    raw_text = normalize_list_indents(lines)
    if not raw_text:
        return ""

    html_content = markdown.markdown(raw_text, extensions=['extra'], tab_length=2)
    soup = BeautifulSoup(html_content, 'html.parser')

    def process_list(list_elem, depth=1):
        list_type = "ol" if list_elem.name == "ol" else "ul"
        list_elem['class'] = list_elem.get('class', []) + ['it-sublist', f'it-sublist-level-{depth}', f'it-sublist-{list_type}']
        for li in list_elem.find_all('li', recursive=False):
            li_classes = li.get('class', []) + ['it-sublist-item', f'it-sublist-item-level-{depth}']
            child_lists = li.find_all(['ul', 'ol'], recursive=False)
            if child_lists:
                li_classes.append('it-has-children')
                header_nodes = []
                for child in list(li.contents):
                    if child in child_lists:
                        break
                    header_nodes.append(child)
                if header_nodes:
                    div = soup.new_tag('div', attrs={'class': f'it-item-title it-item-title-level-{depth}'})
                    child_lists[0].insert_before(div)
                    for n in header_nodes:
                        div.append(n)
                    while div.contents:
                        last_c = div.contents[-1]
                        if isinstance(last_c, NavigableString):
                            s = str(last_c).rstrip()
                            s_clean = re.sub(r'[：:\s]+$', '', s)
                            if not s_clean:
                                last_c.extract()
                                continue
                            else:
                                last_c.replace_with(s_clean)
                                break
                        else:
                            break
                for child_list in child_lists:
                    process_list(child_list, depth + 1)
            li['class'] = li_classes

    for top_list in soup.find_all(['ul', 'ol'], recursive=False):
        process_list(top_list, 1)

    for p in soup.find_all('p'):
        p['class'] = p.get('class', []) + ['it-para']
    for bq in soup.find_all('blockquote'):
        bq['class'] = bq.get('class', []) + ['it-quote']
    for a in soup.find_all('a'):
        a['class'] = a.get('class', []) + ['it-link']
        a['target'] = '_blank'
        a['rel'] = 'noopener noreferrer'
        if not a.get_text().strip().endswith('↗'):
            a.append(' ↗')
    for code in soup.find_all('code'):
        code['class'] = code.get('class', []) + ['it-code']

    return str(soup)

def convert_markdown_inline(text):
    if not text:
        return ""
    text = re.sub(r'\[([^\]]+)\]\((https?://[^\)]+)\)', r'<a href="\2" target="_blank" rel="noopener noreferrer" class="it-link">\1 ↗</a>', text)
    text = re.sub(r'\*\*\*([^*]+)\*\*\*', r'<strong><em>\g<1></em></strong>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\g<1></strong>', text)
    text = re.sub(r'__([^_]+)__', r'<strong>\g<1></strong>', text)
    text = re.sub(r'\*([^*]+)\*', r'<em>\g<1></em>', text)
    text = re.sub(r'`([^`]+)`', r'<code class="it-code">\1</code>', text)
    return text

def build_web_app(days):
    json_data_str = json.dumps(days, ensure_ascii=False, indent=2)

    with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
        f.write(json_data_str)
    print(f"Written JSON to {OUTPUT_JSON_PATH}")

    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        html_template = f.read()

    final_html = html_template.replace('__JSON_DATA__', json_data_str)

    with open(OUTPUT_HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(final_html)
    print(f"Written HTML to {OUTPUT_HTML_PATH}")

    with open(OUTPUT_INDEX_PATH, 'w', encoding='utf-8') as f:
        f.write(final_html)
    print(f"Written HTML to {OUTPUT_INDEX_PATH}")

if __name__ == '__main__':
    days = parse_markdown()
    print(f"Parsed {len(days)} days.")
    build_web_app(days)
    print("Build complete!")
