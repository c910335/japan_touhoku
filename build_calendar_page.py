#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate calendar_export.html: An interactive Google Calendar & iCalendar export center.
Provides:
1. One-click download for Full .ics, Essential .ics, and Google CSV
2. Visual step-by-step guides for Google Calendar (Web/Android) and Apple Calendar (iOS)
3. Interactive timeline preview with search, day filtering, and "Add to Google Calendar" web links.
"""

import os
import json
import urllib.parse
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / 'dist'
DATA_JSON_PATH = str(DIST_DIR / 'itinerary_data.json')
OUTPUT_HTML = str(DIST_DIR / 'calendar_export.html')

def build_page():
    with open(DATA_JSON_PATH, 'r', encoding='utf-8') as f:
        days = json.load(f)

    # Flatten events for interactive table/cards
    events = []
    for d in days:
        day_num = d['day']
        iso_date = d['iso_date']
        region = d.get('region', '東北')

        for idx, it in enumerate(d.get('items', [])):
            st = it.get('start_time')
            et = it.get('end_time')
            if not st:
                continue

            # Format time
            time_display = f"{st} - {et}" if et else st
            title = it.get('title', '')
            cat = it.get('category', 'general')
            cat_label = it.get('category_label', '行程活動')
            raw_text = it.get('raw_text', '')

            # Location
            location = ""
            fact = it.get('fact_data')
            if fact:
                location = fact.get('jp_name') or fact.get('name') or ""
            if not location:
                for ml in it.get('map_links', []):
                    if not ml.get('is_dir') and ml.get('name'):
                        location = ml.get('name')
                        break
            if not location:
                location = region

            # Make Google Calendar Web Intent link
            # dates format: YYYYMMDDTHHMMSSZ/YYYYMMDDTHHMMSSZ (using UTC or local)
            # For simplicity: local with TZID or formatted
            try:
                # Calculate approx UTC for web intent
                # Japan is UTC+9, Taiwan is UTC+8
                is_tw = (day_num == 1 and int(st.split(':')[0]) < 10) or (day_num == 20 and int(st.split(':')[0]) >= 19)
                tz_offset = 8 if is_tw else 9

                dt_start_local = datetime.strptime(f"{iso_date} {st}", "%Y-%m-%d %H:%M")
                dt_start_utc = dt_start_local - timedelta(hours=tz_offset)
                dtstart_param = dt_start_utc.strftime("%Y%m%dT%H%M%SZ")

                if et:
                    dt_end_local = datetime.strptime(f"{iso_date} {et}", "%Y-%m-%d %H:%M")
                    dt_end_utc = dt_end_local - timedelta(hours=tz_offset)
                else:
                    dt_end_utc = dt_start_utc + timedelta(minutes=30)
                dtend_param = dt_end_utc.strftime("%Y%m%dT%H%M%SZ")

                details_clean = raw_text.replace('**', '').replace('`', '')[:500]
                if fact and fact.get('hours'):
                    details_clean += f"\n營業時間：{fact['hours']}"

                gcal_url = (
                    "https://calendar.google.com/calendar/render?action=TEMPLATE"
                    f"&text={urllib.parse.quote(title)}"
                    f"&dates={dtstart_param}/{dtend_param}"
                    f"&details={urllib.parse.quote(details_clean)}"
                    f"&location={urllib.parse.quote(location)}"
                )
            except Exception:
                gcal_url = "https://calendar.google.com/calendar/"

            events.append({
                'day': day_num,
                'iso_date': iso_date,
                'time_display': time_display,
                'title': title,
                'category': cat,
                'category_label': cat_label,
                'location': location,
                'gcal_url': gcal_url
            })

    events_json = json.dumps(events, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, viewport-fit=cover">
  <title>📅 Google Calendar 日曆匯出與即時同步中心 ｜ 2026 東北20天秋楓美饌之旅</title>
  <meta name="description" content="2026 日本東北 20 天 19 夜秋楓美饌之旅 Google Calendar / iCalendar (.ics) 日曆匯出中心。支援 Google 日曆 30 秒一鍵匯入、雙時區精確校準、手機行事曆自動雲端同步與重要預約提醒。">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Noto+Sans+TC:wght@400;500;600;700&family=Noto+Serif+JP:wght@600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --primary: #c2410c;
      --primary-light: #fff7ed;
      --primary-dark: #9a3412;
      --accent: #0284c7;
      --accent-light: #f0f9ff;
      --emerald: #059669;
      --emerald-light: #ecfdf5;
      --amber: #d97706;
      --amber-light: #fffbeb;
      --purple: #7c3aed;
      --purple-light: #f5f3ff;
      --text-main: #1e293b;
      --text-muted: #64748b;
      --text-light: #94a3b8;
      --bg-page: #f8fafc;
      --bg-card: #ffffff;
      --border-color: #e2e8f0;
      --border-focus: #cbd5e1;
      --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
      --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
      --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
      --radius-sm: 8px;
      --radius-md: 12px;
      --radius-lg: 16px;
      --radius-full: 9999px;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      -webkit-tap-highlight-color: transparent;
    }}

    body {{
      font-family: 'Plus Jakarta Sans', 'Noto Sans TC', sans-serif;
      background-color: var(--bg-page);
      color: var(--text-main);
      line-height: 1.6;
      padding-bottom: 80px;
    }}

    .navbar {{
      position: sticky;
      top: 0;
      z-index: 100;
      background: rgba(255, 255, 255, 0.95);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border-color);
      padding: 12px 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      max-width: 1200px;
      margin: 0 auto;
    }}

    .nav-brand {{
      display: flex;
      align-items: center;
      gap: 10px;
      font-weight: 800;
      font-size: 1.15rem;
      color: var(--primary-dark);
      text-decoration: none;
    }}

    .nav-links {{
      display: flex;
      gap: 10px;
      align-items: center;
    }}

    .nav-btn {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 8px 14px;
      border-radius: var(--radius-full);
      font-size: 0.88rem;
      font-weight: 600;
      text-decoration: none;
      transition: all 0.2s ease;
      border: 1px solid var(--border-color);
      background: #fff;
      color: var(--text-main);
    }}

    .nav-btn:hover {{
      background: var(--bg-page);
      border-color: var(--text-light);
    }}

    .nav-btn.active {{
      background: var(--primary);
      color: #fff;
      border-color: var(--primary);
    }}

    .container {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 24px 20px;
    }}

    .hero-banner {{
      background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
      color: #ffffff;
      border-radius: var(--radius-lg);
      padding: 36px 32px;
      margin-bottom: 32px;
      box-shadow: var(--shadow-lg);
      position: relative;
      overflow: hidden;
    }}

    .hero-banner::after {{
      content: '📅';
      position: absolute;
      right: 20px;
      bottom: -20px;
      font-size: 130px;
      opacity: 0.12;
      pointer-events: none;
    }}

    .hero-badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: rgba(194, 65, 12, 0.35);
      border: 1px solid rgba(251, 146, 60, 0.4);
      color: #fdba74;
      padding: 4px 12px;
      border-radius: var(--radius-full);
      font-size: 0.82rem;
      font-weight: 700;
      letter-spacing: 0.5px;
      margin-bottom: 12px;
    }}

    .hero-title {{
      font-size: 2rem;
      font-weight: 800;
      line-height: 1.25;
      margin-bottom: 12px;
      letter-spacing: -0.5px;
    }}

    .hero-desc {{
      color: #94a3b8;
      font-size: 1.05rem;
      max-width: 800px;
      line-height: 1.6;
    }}

    /* Export Cards Grid */
    .download-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 20px;
      margin-bottom: 36px;
    }}

    .dl-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      padding: 24px;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      position: relative;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}

    .dl-card:hover {{
      transform: translateY(-3px);
      box-shadow: var(--shadow-md);
    }}

    .dl-card.highlight {{
      border-color: #fb923c;
      background: linear-gradient(180deg, #fffaf5 0%, #ffffff 100%);
    }}

    .dl-card-tag {{
      display: inline-block;
      padding: 4px 10px;
      border-radius: var(--radius-full);
      font-size: 0.75rem;
      font-weight: 700;
      margin-bottom: 14px;
    }}

    .tag-orange {{ background: var(--primary-light); color: var(--primary); }}
    .tag-blue {{ background: var(--accent-light); color: var(--accent); }}
    .tag-emerald {{ background: var(--emerald-light); color: var(--emerald); }}

    .dl-card-title {{
      font-size: 1.25rem;
      font-weight: 700;
      color: var(--text-main);
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .dl-card-desc {{
      color: var(--text-muted);
      font-size: 0.92rem;
      margin-bottom: 20px;
      line-height: 1.5;
    }}

    .dl-stats {{
      display: flex;
      gap: 16px;
      margin-bottom: 20px;
      padding: 12px 14px;
      background: var(--bg-page);
      border-radius: var(--radius-md);
      font-size: 0.85rem;
    }}

    .dl-stat-item b {{
      color: var(--primary-dark);
      font-weight: 800;
    }}

    .dl-btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      width: 100%;
      padding: 12px 16px;
      border-radius: var(--radius-md);
      font-weight: 700;
      font-size: 0.95rem;
      text-decoration: none;
      transition: all 0.2s ease;
      cursor: pointer;
    }}

    .btn-primary {{
      background: var(--primary);
      color: #fff;
      border: 1px solid var(--primary-dark);
      box-shadow: 0 2px 4px rgba(194, 65, 12, 0.2);
    }}

    .btn-primary:hover {{
      background: var(--primary-dark);
    }}

    .btn-secondary {{
      background: #fff;
      color: var(--text-main);
      border: 1px solid var(--border-color);
    }}

    .btn-secondary:hover {{
      background: var(--bg-page);
      border-color: var(--text-light);
    }}

    .url-box {{
      display: flex;
      align-items: center;
      background: var(--bg-page);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      padding: 6px 10px;
      margin-bottom: 12px;
      gap: 8px;
    }}

    .url-box code {{
      font-family: monospace;
      font-size: 0.76rem;
      color: var(--text-muted);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      flex: 1;
      user-select: all;
    }}

    .btn-row {{
      display: flex;
      gap: 8px;
      margin-top: 8px;
    }}

    .btn-sub {{
      flex: 1;
      padding: 8px 10px;
      font-size: 0.82rem;
      font-weight: 600;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border-color);
      background: #fff;
      color: var(--text-main);
      text-decoration: none;
      text-align: center;
      transition: all 0.2s ease;
      cursor: pointer;
    }}

    .btn-sub:hover {{
      background: var(--bg-page);
      border-color: var(--text-light);
    }}

    /* Tutorial Section */
    .section-title {{
      font-size: 1.4rem;
      font-weight: 800;
      color: var(--text-main);
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .guide-box {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      padding: 28px;
      margin-bottom: 36px;
      box-shadow: var(--shadow-sm);
    }}

    .pro-tip {{
      background: var(--amber-light);
      border-left: 4px solid var(--amber);
      padding: 16px 20px;
      border-radius: 0 var(--radius-md) var(--radius-md) 0;
      margin-bottom: 24px;
      font-size: 0.95rem;
      color: #92400e;
    }}

    .pro-tip b {{
      color: #78350f;
    }}

    .steps-container {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 20px;
    }}

    .step-card {{
      background: var(--bg-page);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: 20px;
      position: relative;
    }}

    .step-num {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 28px;
      height: 28px;
      background: var(--primary);
      color: #fff;
      border-radius: 50%;
      font-weight: 800;
      font-size: 0.85rem;
      margin-bottom: 12px;
    }}

    .step-title {{
      font-weight: 700;
      font-size: 1.05rem;
      color: var(--text-main);
      margin-bottom: 8px;
    }}

    .step-desc {{
      font-size: 0.9rem;
      color: var(--text-muted);
      line-height: 1.55;
    }}

    /* Interactive Event Preview */
    .filter-bar {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-bottom: 20px;
      align-items: center;
      justify-content: space-between;
    }}

    .search-input {{
      padding: 10px 16px;
      border-radius: var(--radius-full);
      border: 1px solid var(--border-color);
      font-size: 0.92rem;
      width: 100%;
      max-width: 320px;
      background: #fff;
      outline: none;
    }}

    .search-input:focus {{
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(194, 65, 12, 0.15);
    }}

    .filter-pills {{
      display: flex;
      gap: 8px;
      overflow-x: auto;
      padding-bottom: 4px;
    }}

    .pill-btn {{
      padding: 6px 14px;
      border-radius: var(--radius-full);
      border: 1px solid var(--border-color);
      background: #fff;
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--text-muted);
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.2s;
    }}

    .pill-btn.active {{
      background: var(--primary);
      color: #fff;
      border-color: var(--primary);
    }}

    .events-list {{
      display: flex;
      flex-direction: column;
      gap: 10px;
      max-height: 700px;
      overflow-y: auto;
      padding-right: 4px;
    }}

    .event-row {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: 14px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      transition: all 0.2s;
    }}

    .event-row:hover {{
      border-color: var(--border-focus);
      box-shadow: var(--shadow-sm);
    }}

    .event-left {{
      display: flex;
      align-items: center;
      gap: 14px;
      flex: 1;
      min-width: 0;
    }}

    .event-day-badge {{
      display: inline-flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-width: 54px;
      padding: 4px 6px;
      background: var(--bg-page);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      font-weight: 800;
      font-size: 0.78rem;
      color: var(--primary-dark);
    }}

    .event-day-badge span {{
      font-size: 0.7rem;
      font-weight: 600;
      color: var(--text-light);
    }}

    .event-info {{
      min-width: 0;
    }}

    .event-time {{
      font-size: 0.8rem;
      font-weight: 700;
      color: var(--accent);
      margin-bottom: 2px;
    }}

    .event-title {{
      font-weight: 700;
      font-size: 0.95rem;
      color: var(--text-main);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .event-loc {{
      font-size: 0.8rem;
      color: var(--text-muted);
    }}

    .add-gcal-btn {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 6px 12px;
      border-radius: var(--radius-md);
      font-size: 0.82rem;
      font-weight: 700;
      color: var(--primary);
      background: var(--primary-light);
      border: 1px solid #fed7aa;
      text-decoration: none;
      white-space: nowrap;
      transition: all 0.2s;
    }}

    .add-gcal-btn:hover {{
      background: #ffedd5;
      border-color: #fdba74;
    }}

    @media (max-width: 768px) {{
      .hero-title {{ font-size: 1.55rem; }}
      .hero-banner {{ padding: 24px 20px; }}
      .download-grid {{ grid-template-columns: 1fr; }}
      .steps-container {{ grid-template-columns: 1fr; }}
      .event-row {{ flex-direction: column; align-items: flex-start; }}
      .add-gcal-btn {{ width: 100%; justify-content: center; }}
    }}
  </style>
</head>
<body>

  <!-- Sticky Navbar -->
  <header class="navbar">
    <a href="index.html" class="nav-brand">
      <span>🍁 東北秋楓 2026</span>
    </a>
    <nav class="nav-links">
      <a href="itinerary.html" class="nav-btn">📋 完整行程</a>
      <a href="maps_places.html" class="nav-btn">🗺️ 地圖清單</a>
      <a href="calendar_export.html" class="nav-btn active">📅 日曆匯出</a>
    </nav>
  </header>

  <main class="container">
    
    <!-- Hero Header -->
    <section class="hero-banner">
      <div class="hero-badge">RFC 5545 iCalendar & Google Calendar Ready</div>
      <h1 class="hero-title">Google Calendar 日曆網址訂閱與即時同步中心</h1>
      <p class="hero-desc">
        將 20 天 19 夜（青森・奧入瀨・八戶・松島・仙台・山寺）所有景點、排隊美食、新幹線班次、飯店 Check-in 與重要預約席一鍵訂閱至 Google 日曆與手機行事曆。支援 URL 動態自動同步、台日雙時區自動校準與 30 分鐘前推播提醒！
      </p>
    </section>

    <!-- Calendar Subscription Cards -->
    <section class="download-grid">
      <!-- Full ICS Subscription -->
      <article class="dl-card highlight">
        <div>
          <span class="dl-card-tag tag-orange">🌟 最強推薦・動態自動同步</span>
          <h2 class="dl-card-title">📡 完整分秒全覽版（日曆網址）</h2>
          <p class="dl-card-desc">
            收錄全行程 336 個活動節點（含所有市區公車/電車班次、步行銜接、景點參拜、美食營業與每日全天行程概覽 Banner）。貼入 Google 日曆後，行程微調將自動同步！
          </p>
          <div class="dl-stats">
            <div class="dl-stat-item">總事件數：<b>336 筆</b></div>
            <div class="dl-stat-item">全天總覽：<b>20 日</b></div>
            <div class="dl-stat-item">同步模式：<b>URL 動態同步</b></div>
          </div>
          <div class="url-box">
            <code id="code-full-ics">./tohoku_itinerary_full.ics</code>
          </div>
        </div>
        <div>
          <button class="dl-btn btn-primary" onclick="copyIcsUrl('tohoku_itinerary_full.ics', this)">
            📋 複製日曆訂閱網址
          </button>
          <div class="btn-row">
            <a href="tohoku_itinerary_full.ics" download="tohoku_itinerary_full.ics" class="btn-sub">
              📥 下載 .ics
            </a>
            <a id="link-webcal-full" href="tohoku_itinerary_full.ics" class="btn-sub">
              🍎 iOS 一鍵訂閱
            </a>
          </div>
        </div>
      </article>

      <!-- Essential ICS Subscription -->
      <article class="dl-card">
        <div>
          <span class="dl-card-tag tag-blue">🎯 俐落焦點・清爽好讀</span>
          <h2 class="dl-card-title">📡 精選里程碑版（日曆網址）</h2>
          <p class="dl-card-desc">
            過濾掉細微的步行與起床整備，專注收錄 44 處景點、40 家老饕美食、9 家飯店 Check-in/退房、新幹線與航班，適合喜歡簡潔日曆的旅人。
          </p>
          <div class="dl-stats">
            <div class="dl-stat-item">核心里程碑：<b>170 筆</b></div>
            <div class="dl-stat-item">版面密度：<b>清爽聚焦</b></div>
            <div class="dl-stat-item">同步模式：<b>URL 動態同步</b></div>
          </div>
          <div class="url-box">
            <code id="code-essential-ics">./tohoku_itinerary_essential.ics</code>
          </div>
        </div>
        <div>
          <button class="dl-btn btn-secondary" onclick="copyIcsUrl('tohoku_itinerary_essential.ics', this)">
            📋 複製日曆訂閱網址
          </button>
          <div class="btn-row">
            <a href="tohoku_itinerary_essential.ics" download="tohoku_itinerary_essential.ics" class="btn-sub">
              📥 下載 .ics
            </a>
            <a id="link-webcal-essential" href="tohoku_itinerary_essential.ics" class="btn-sub">
              🍎 iOS 一鍵訂閱
            </a>
          </div>
        </div>
      </article>

      <!-- Google CSV -->
      <article class="dl-card">
        <div>
          <span class="dl-card-tag tag-emerald">📊 試算表彈性編修</span>
          <h2 class="dl-card-title">📊 Google 日曆專用 CSV</h2>
          <p class="dl-card-desc">
            標準 Google Calendar CSV 試算表格式，適合習慣在 Excel 或 Google 試算表中先行檢視、增修個人自訂備註後再行匯入。
          </p>
          <div class="dl-stats">
            <div class="dl-stat-item">試算表格式：<b>CSV (UTF-8)</b></div>
            <div class="dl-stat-item">相容性：<b>Google Calendar</b></div>
          </div>
        </div>
        <a href="tohoku_calendar_google.csv" download="tohoku_calendar_google.csv" class="dl-btn btn-secondary">
          📊 下載 Google 專用 CSV
        </a>
      </article>
    </section>

    <!-- Visual Tutorial -->
    <section class="guide-box">
      <h2 class="section-title">💡 透過網址訂閱 Google 日曆教學（一次設定，自動永續同步！）</h2>

      <div class="pro-tip">
        <b>⭐ 為什麼強烈推薦「網址訂閱」而非手動匯入？</b><br>
        ① <b>自動動態同步</b>：日後任何景點營業時間、公車班次或用餐調整發布後，Google 日曆會在背景定時自動抓取最新版同步至您的手機，<b>您完全不用手動重複下載匯入！</b><br>
        ② <b>獨立次日曆好管理</b>：訂閱的日曆會作為獨立日曆存在，可自由設定專屬顏色（如楓葉橙紅），回國後或平日可隨時一鍵勾選顯示/隱藏，絕不弄亂您個人的工作與日常生活行程。
      </div>

      <div class="steps-container">
        <div class="step-card">
          <div class="step-num">1</div>
          <h3 class="step-title">複製上方日曆訂閱網址</h3>
          <p class="step-desc">
            在上方卡片點擊 <b>「📋 複製日曆訂閱網址」</b>（首選推薦「完整分秒全覽版」），日曆訂閱網址將自動複製到您的剪貼簿。
          </p>
        </div>

        <div class="step-card">
          <div class="step-num">2</div>
          <h3 class="step-title">開啟 Google 日曆「透過網址訂閱」</h3>
          <p class="step-desc">
            開啟電腦版 <a href="https://calendar.google.com" target="_blank" style="color:var(--accent);font-weight:700;">Google 日曆</a>（或手機瀏覽器開啟並切換至「電腦版網站」），在左側欄「其他日曆」旁邊點擊 <b>「＋」➔ 選擇「透過網址訂閱 (From URL)」</b>。
          </p>
        </div>

        <div class="step-card">
          <div class="step-num">3</div>
          <h3 class="step-title">貼上網址並點擊新增</h3>
          <p class="step-desc">
            將剛才複製的網址貼入「日曆網址」欄位，點擊 <b>「新增日曆」</b>！Google 日曆與您所有登入同帳號的手機 App（iPhone / Android）將自動連動最新行程！
          </p>
        </div>
      </div>

      <div style="margin-top: 18px; padding: 12px 16px; background: var(--bg-page); border-radius: var(--radius-sm); font-size: 0.88rem; color: var(--text-muted); border: 1px dashed var(--border-color);">
        🍎 <b>iPhone / iPad / Mac 用戶捷徑</b>：若習慣使用蘋果原生「行事曆」App，只要點擊上方卡片的 <b>「🍎 iOS 一鍵訂閱」</b>，系統便會自動彈出訂閱視窗，點擊「加入」即可秒級同步！
      </div>
    </section>

    <!-- Interactive Event Preview & Single Add -->
    <section>
      <h2 class="section-title">🔍 行程日曆即時預覽 ＆ 單筆快速加入</h2>
      
      <div class="filter-bar">
        <input type="text" id="searchInput" class="search-input" placeholder="搜尋景點、餐廳、新幹線或行程...">
        <div class="filter-pills">
          <button class="pill-btn active" data-filter="all">全部行程</button>
          <button class="pill-btn" data-filter="spot">🏛️ 景點</button>
          <button class="pill-btn" data-filter="dining">🍴 美食</button>
          <button class="pill-btn" data-filter="transit">🚌 交通</button>
          <button class="pill-btn" data-filter="hotel">🏨 住宿</button>
        </div>
      </div>

      <div id="eventsList" class="events-list">
        <!-- Rendered by JS -->
      </div>
    </section>

  </main>

  <script>
    const eventsData = {events_json};
    let currentFilter = 'all';
    let searchQuery = '';

    const eventsListEl = document.getElementById('eventsList');
    const searchInput = document.getElementById('searchInput');
    const pillBtns = document.querySelectorAll('.pill-btn');

    function renderEvents() {{
      const filtered = eventsData.filter(ev => {{
        const matchFilter = currentFilter === 'all' || ev.category === currentFilter;
        const matchSearch = !searchQuery || 
          ev.title.toLowerCase().includes(searchQuery) || 
          ev.location.toLowerCase().includes(searchQuery) ||
          ('day ' + ev.day).includes(searchQuery);
        return matchFilter && matchSearch;
      }});

      if (filtered.length === 0) {{
        eventsListEl.innerHTML = '<div style="text-align:center;padding:40px;color:var(--text-muted);">查無相符行程項目</div>';
        return;
      }}

      eventsListEl.innerHTML = filtered.map(ev => `
        <div class="event-row">
          <div class="event-left">
            <div class="event-day-badge">
              Day ${{String(ev.day).padStart(2, '0')}}
              <span>${{ev.iso_date.slice(5)}}</span>
            </div>
            <div class="event-info">
              <div class="event-time">${{ev.time_display}} · ${{ev.category_label}}</div>
              <div class="event-title">${{ev.title}}</div>
              <div class="event-loc">📍 ${{ev.location}}</div>
            </div>
          </div>
          <a href="${{ev.gcal_url}}" target="_blank" rel="noopener noreferrer" class="add-gcal-btn">
            ➕ 加到 Google 日曆
          </a>
        </div>
      `).join('');
    }}

    searchInput.addEventListener('input', e => {{
      searchQuery = e.target.value.toLowerCase().trim();
      renderEvents();
    }});

    pillBtns.forEach(btn => {{
      btn.addEventListener('click', () => {{
        pillBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentFilter = btn.dataset.filter;
        renderEvents();
      }});
    }});

    function getAbsoluteUrl(rel) {{
      try {{
        return new URL(rel, window.location.href).href;
      }} catch (e) {{
        return rel;
      }}
    }}

    function getWebcalUrl(rel) {{
      return getAbsoluteUrl(rel).replace(/^https?:\\/\\//i, 'webcal://');
    }}

    function copyIcsUrl(rel, btnEl) {{
      const fullUrl = getAbsoluteUrl(rel);
      copyToClipboard(fullUrl, btnEl);
    }}

    function copyToClipboard(text, btnEl) {{
      navigator.clipboard.writeText(text).then(() => {{
        const originalText = btnEl.innerHTML;
        btnEl.innerHTML = '✅ 已複製訂閱網址！';
        btnEl.style.background = '#059669';
        btnEl.style.borderColor = '#047857';
        btnEl.style.color = '#fff';
        setTimeout(() => {{
          btnEl.innerHTML = originalText;
          btnEl.style.background = '';
          btnEl.style.borderColor = '';
          btnEl.style.color = '';
        }}, 2500);
      }}).catch(() => {{
        prompt('請手動複製此日曆訂閱網址：', text);
      }});
    }}

    try {{
      const fullCode = document.getElementById('code-full-ics');
      const essCode = document.getElementById('code-essential-ics');
      const webcalFull = document.getElementById('link-webcal-full');
      const webcalEss = document.getElementById('link-webcal-essential');
      if (fullCode) fullCode.textContent = getAbsoluteUrl('tohoku_itinerary_full.ics');
      if (essCode) essCode.textContent = getAbsoluteUrl('tohoku_itinerary_essential.ics');
      if (webcalFull) webcalFull.href = getWebcalUrl('tohoku_itinerary_full.ics');
      if (webcalEss) webcalEss.href = getWebcalUrl('tohoku_itinerary_essential.ics');
    }} catch (e) {{
      console.warn('URL resolution fallback', e);
    }}

    renderEvents();
  </script>
</body>
</html>
"""

    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Generated Calendar Hub: {OUTPUT_HTML}")

if __name__ == '__main__':
    build_page()
