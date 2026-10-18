#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate maps_places.html: An interactive Google Maps places directory & export hub.
Supports dual-mode: 83 unique physical locations and 94 itinerary activity stops.
"""

import json
import csv
import html
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / 'dist'
DEDUP_CSV_PATH = str(DIST_DIR / 'tohoku_google_maps_places.csv')
ALL_STOPS_CSV_PATH = str(DIST_DIR / 'tohoku_google_maps_all_stops.csv')
OUTPUT_HTML = str(DIST_DIR / 'maps_places.html')

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

def load_csv(path):
    rows = []
    with open(path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            for k in row:
                if k != 'Google地圖即時連結':
                    row[k] = clean_markdown_text(row[k])
            rows.append(row)
    return rows

def build_page():
    unique_places = load_csv(DEDUP_CSV_PATH)
    all_stops = load_csv(ALL_STOPS_CSV_PATH)

    unique_json = json.dumps(unique_places, ensure_ascii=False)
    stops_json = json.dumps(all_stops, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, viewport-fit=cover">
  <title>🗺️ Google Maps 地點清單與導航匯出中心 ｜ 2026 東北20天秋楓美饌之旅</title>
  <meta name="description" content="2026 日本東北 20 天 83 處獨立實體地標與 94 個行程活動節點 Google Maps 地點清單，支援 Google 我的地圖 30 秒一鍵匯入與手機 Google Maps App 即時同步導航。">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Noto+Sans+TC:wght@400;500;600;700&family=Noto+Serif+JP:wght@600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-dark: #07090e;
      --bg-card: rgba(18, 24, 38, 0.7);
      --bg-card-hover: rgba(26, 35, 56, 0.85);
      --border-color: rgba(255, 255, 255, 0.08);
      --border-accent: rgba(249, 115, 22, 0.3);
      --text-main: #f1f5f9;
      --text-sub: #94a3b8;
      --text-muted: #64748b;
      --accent-orange: #f97316;
      --accent-emerald: #10b981;
      --accent-blue: #38bdf8;
      --accent-purple: #a855f7;
      --accent-gold: #eab308;
      --font-base: 'Plus Jakarta Sans', 'Noto Sans TC', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji', sans-serif;
      --font-jp: 'Noto Serif JP', serif;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: var(--bg-dark);
      background-image: 
        radial-gradient(ellipse 80% 50% at 50% -20%, rgba(249, 115, 22, 0.15), transparent 70%),
        radial-gradient(circle at 10% 20%, rgba(56, 189, 248, 0.08), transparent 40%),
        radial-gradient(circle at 90% 80%, rgba(16, 185, 129, 0.06), transparent 50%);
      background-attachment: fixed;
      color: var(--text-main);
      font-family: var(--font-base);
      line-height: 1.6;
      padding-bottom: max(60px, calc(30px + env(safe-area-inset-bottom, 0px)));
      -webkit-font-smoothing: antialiased;
      overflow-x: hidden;
    }}

    .container {{
      width: 100%;
      max-width: 1200px;
      margin: 0 auto;
      min-width: 0;
      padding-left: max(16px, env(safe-area-inset-left, 0px));
      padding-right: max(16px, env(safe-area-inset-right, 0px));
    }}

    /* Top Nav */
    .top-nav {{
      position: sticky;
      top: 0;
      z-index: 50;
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      background: rgba(7, 9, 14, 0.88);
      border-bottom: 1px solid var(--border-color);
      padding-top: max(12px, env(safe-area-inset-top, 0px));
      padding-bottom: 12px;
      margin-bottom: 24px;
    }}
    .nav-inner {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
    }}
    .brand {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      text-decoration: none;
      color: var(--text-main);
      font-weight: 700;
      font-size: 1.05rem;
      white-space: nowrap;
      flex-shrink: 1;
      min-width: 0;
    }}
    .brand-title {{
      white-space: nowrap;
    }}
    .brand-badge {{
      background: linear-gradient(135deg, var(--accent-orange), #ea580c);
      color: white;
      font-size: 0.72rem;
      padding: 3px 8px;
      border-radius: 9999px;
      font-weight: 700;
      white-space: nowrap;
      flex-shrink: 0;
    }}
    .nav-actions {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      flex-shrink: 0;
    }}
    .btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      padding: 8px 14px;
      border-radius: 9999px;
      font-size: 0.82rem;
      font-weight: 600;
      text-decoration: none;
      cursor: pointer;
      transition: all 0.2s ease;
      border: 1px solid transparent;
      white-space: nowrap;
      flex-shrink: 0;
    }}
    .btn-primary {{
      background: linear-gradient(135deg, #f97316, #ea580c);
      color: white;
      box-shadow: 0 4px 14px rgba(249, 115, 22, 0.3);
    }}
    .btn-primary:hover {{
      transform: translateY(-1px);
      box-shadow: 0 6px 20px rgba(249, 115, 22, 0.45);
    }}
    .btn-secondary {{
      background: rgba(255, 255, 255, 0.08);
      color: var(--text-main);
      border-color: rgba(255, 255, 255, 0.15);
    }}
    .btn-secondary:hover {{
      background: rgba(255, 255, 255, 0.15);
    }}

    /* Hero Section */
    .hero {{
      text-align: center;
      padding: 20px 0 32px 0;
    }}
    .hero-tag {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: rgba(249, 115, 22, 0.12);
      border: 1px solid rgba(249, 115, 22, 0.3);
      color: #fb923c;
      font-size: 0.8rem;
      padding: 4px 14px;
      border-radius: 9999px;
      font-weight: 600;
      margin-bottom: 14px;
    }}
    .hero h1 {{
      font-size: 2.1rem;
      font-weight: 800;
      letter-spacing: -0.02em;
      margin-bottom: 12px;
      background: linear-gradient(135deg, #ffffff 40%, #cbd5e1 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      line-height: 1.25;
    }}
    .hero p {{
      color: var(--text-sub);
      font-size: 0.95rem;
      max-width: 820px;
      margin: 0 auto 20px auto;
      line-height: 1.6;
    }}
    .hero-stats {{
      display: flex;
      justify-content: center;
      gap: 12px;
      flex-wrap: wrap;
    }}
    .stat-pill {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 14px;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border-color);
      border-radius: 9999px;
      font-size: 0.82rem;
      color: var(--text-sub);
    }}
    .stat-num {{
      color: #ffffff;
      font-weight: 700;
    }}

    /* Tutorial Box */
    .tutorial-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      padding: 20px;
      margin-bottom: 24px;
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
    }}
    .tutorial-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      cursor: pointer;
      user-select: none;
    }}
    .tutorial-title {{
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 1.02rem;
      font-weight: 700;
      color: #ffffff;
    }}
    .tut-icon {{
      font-size: 1.25rem;
    }}
    #tutToggleIcon {{
      color: var(--accent-orange);
      font-size: 0.8rem;
      font-weight: 600;
      padding: 4px 10px;
      border-radius: 6px;
      background: rgba(249, 115, 22, 0.1);
      border: 1px solid rgba(249, 115, 22, 0.2);
    }}
    .steps-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
      margin-top: 16px;
    }}
    .step-item {{
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 12px;
      padding: 14px 16px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
    .step-badge {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: var(--accent-orange);
      color: white;
      font-weight: 800;
      font-size: 0.75rem;
      flex-shrink: 0;
    }}
    .step-text {{
      font-size: 0.84rem;
      color: #e2e8f0;
      line-height: 1.5;
    }}
    .step-sub {{
      font-size: 0.75rem;
      color: var(--text-muted);
    }}

    /* Controls */
    .controls-wrapper {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      padding: 16px;
      margin-bottom: 24px;
      display: flex;
      flex-direction: column;
      gap: 14px;
      min-width: 0;
      max-width: 100%;
    }}
    .mode-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 10px;
      min-width: 0;
      max-width: 100%;
    }}
    .view-mode-toggle {{
      display: inline-flex;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border-color);
      padding: 3px;
      border-radius: 9999px;
      gap: 4px;
      flex-shrink: 0;
    }}
    .mode-btn {{
      background: transparent;
      border: none;
      color: var(--text-sub);
      font-size: 0.8rem;
      font-weight: 600;
      padding: 5px 12px;
      border-radius: 9999px;
      cursor: pointer;
      transition: all 0.2s ease;
      font-family: inherit;
    }}
    .mode-btn.active {{
      background: var(--accent-orange);
      color: white;
      box-shadow: 0 2px 8px rgba(249, 115, 22, 0.4);
    }}
    .search-input-box {{
      position: relative;
      width: 100%;
      min-width: 0;
      max-width: 100%;
    }}
    .search-icon {{
      position: absolute;
      left: 14px;
      top: 50%;
      transform: translateY(-50%);
      font-size: 1rem;
      color: var(--text-muted);
      pointer-events: none;
    }}
    .search-input {{
      width: 100%;
      min-width: 0;
      max-width: 100%;
      padding: 11px 16px 11px 42px;
      background: rgba(7, 9, 14, 0.7);
      border: 1px solid var(--border-color);
      border-radius: 10px;
      color: var(--text-main);
      font-size: 0.9rem;
      font-family: inherit;
      outline: none;
      transition: all 0.2s ease;
    }}
    .search-input:focus {{
      border-color: var(--accent-orange);
      box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.15);
    }}

    .filter-tabs {{
      display: flex;
      gap: 8px;
      overflow-x: auto;
      padding-bottom: 2px;
      -webkit-overflow-scrolling: touch;
      scrollbar-width: none;
      min-width: 0;
      max-width: 100%;
      width: 100%;
    }}
    .filter-tabs::-webkit-scrollbar {{ display: none; }}
    .tab-btn {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 7px 15px;
      border-radius: 9999px;
      font-size: 0.84rem;
      font-weight: 600;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border-color);
      color: var(--text-sub);
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.2s ease;
      font-family: inherit;
    }}
    .tab-btn:hover {{
      color: var(--text-main);
      background: rgba(255, 255, 255, 0.1);
    }}
    .tab-btn.active {{
      background: rgba(249, 115, 22, 0.15);
      border-color: var(--accent-orange);
      color: #fb923c;
    }}

    .day-chips {{
      display: flex;
      gap: 6px;
      overflow-x: auto;
      padding-bottom: 4px;
      -webkit-overflow-scrolling: touch;
      scrollbar-width: none;
      min-width: 0;
      max-width: 100%;
      width: 100%;
    }}
    .day-chips::-webkit-scrollbar {{ display: none; }}
    .day-chip {{
      padding: 4px 10px;
      border-radius: 8px;
      font-size: 0.76rem;
      font-weight: 600;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border-color);
      color: var(--text-muted);
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.2s ease;
      font-family: inherit;
    }}
    .day-chip:hover {{
      color: var(--text-main);
      background: rgba(255, 255, 255, 0.08);
    }}
    .day-chip.active {{
      background: rgba(56, 189, 248, 0.15);
      border-color: var(--accent-blue);
      color: var(--accent-blue);
    }}

    /* Results Bar */
    .results-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      font-size: 0.85rem;
      color: var(--text-sub);
    }}
    .results-tip {{
      color: var(--text-muted);
      font-size: 0.78rem;
    }}

    /* Places Grid */
    .places-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(min(100%, 360px), 1fr));
      gap: 16px;
    }}
    .place-card {{
      min-width: 0;
      word-wrap: break-word;
      overflow-wrap: break-word;
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 14px;
      padding: 18px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      transition: all 0.2s ease;
      position: relative;
    }}
    .place-card:hover {{
      border-color: rgba(255, 255, 255, 0.2);
      background: var(--bg-card-hover);
      transform: translateY(-2px);
    }}
    .card-meta {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 8px;
    }}
    .meta-badges {{
      display: flex;
      align-items: center;
      gap: 6px;
      flex-wrap: wrap;
    }}
    .badge-category {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 0.72rem;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 6px;
      white-space: nowrap;
    }}
    .badge-spot {{
      background: rgba(56, 189, 248, 0.12);
      color: #38bdf8;
      border: 1px solid rgba(56, 189, 248, 0.3);
    }}
    .badge-dining {{
      background: rgba(249, 115, 22, 0.12);
      color: #fb923c;
      border: 1px solid rgba(249, 115, 22, 0.3);
    }}
    .badge-hotel {{
      background: rgba(16, 185, 129, 0.12);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.3);
    }}
    .badge-multi {{
      background: rgba(168, 85, 247, 0.15);
      color: #c084fc;
      border: 1px solid rgba(168, 85, 247, 0.35);
    }}
    .badge-role-tag {{
      display: inline-flex;
      align-items: center;
      gap: 3px;
      font-size: 0.7rem;
      padding: 2px 7px;
      border-radius: 9999px;
      background: rgba(234, 179, 8, 0.15);
      color: #facc15;
      border: 1px solid rgba(234, 179, 8, 0.3);
      font-weight: 600;
    }}
    .badge-day {{
      font-size: 0.72rem;
      font-weight: 700;
      color: #cbd5e1;
      background: rgba(255, 255, 255, 0.06);
      padding: 3px 8px;
      border-radius: 6px;
      white-space: nowrap;
    }}

    .place-title {{
      font-size: 1.05rem;
      font-weight: 700;
      color: #ffffff;
      line-height: 1.4;
    }}
    .place-jp {{
      display: flex;
      align-items: center;
      gap: 8px;
      font-family: var(--font-jp);
      font-size: 0.85rem;
      color: var(--text-muted);
      margin-top: 2px;
    }}
    .copy-btn {{
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid var(--border-color);
      color: var(--text-sub);
      font-size: 0.7rem;
      padding: 2px 6px;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.2s ease;
    }}
    .copy-btn:hover {{
      background: rgba(255, 255, 255, 0.15);
      color: #ffffff;
    }}

    .place-info-block {{
      background: rgba(0, 0, 0, 0.28);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 8px;
      padding: 10px 12px;
      font-size: 0.8rem;
      display: flex;
      flex-direction: column;
      gap: 7px;
    }}
    .info-row {{
      display: flex;
      align-items: baseline;
      gap: 8px;
    }}
    .info-label {{
      color: var(--text-muted);
      font-weight: 600;
      font-size: 0.75rem;
      white-space: nowrap;
      min-width: 62px;
      flex-shrink: 0;
    }}
    .info-val {{
      color: #e2e8f0;
      line-height: 1.45;
      word-break: break-word;
      overflow-wrap: anywhere;
      min-width: 0;
      font-size: 0.8rem;
    }}
    .pay-chips-container {{
      display: flex;
      flex-direction: column;
      gap: 5px;
      width: 100%;
      min-width: 0;
    }}
    .pay-line {{
      display: flex;
      flex-wrap: wrap;
      gap: 5px;
      align-items: center;
      line-height: 1.4;
      min-width: 0;
    }}
    .pay-chip {{
      display: inline-flex;
      align-items: center;
      padding: 1.5px 7px;
      border-radius: 4px;
      font-size: 0.72rem;
      font-weight: 600;
      white-space: nowrap;
      line-height: 1.35;
      max-width: 100%;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .pay-chip.chip-ok {{
      background: rgba(16, 185, 129, 0.15);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.35);
    }}
    .pay-chip.chip-no {{
      background: rgba(239, 68, 68, 0.12);
      color: #f87171;
      border: 1px solid rgba(239, 68, 68, 0.25);
    }}
    .pay-chip.chip-warn {{
      background: rgba(234, 179, 8, 0.15);
      color: #facc15;
      border: 1px solid rgba(234, 179, 8, 0.35);
    }}
    .pay-chip.chip-free {{
      background: rgba(56, 189, 248, 0.15);
      color: #38bdf8;
      border: 1px solid rgba(56, 189, 248, 0.35);
    }}
    .pay-chip.chip-info {{
      background: rgba(148, 163, 184, 0.12);
      color: #cbd5e1;
      border: 1px solid rgba(148, 163, 184, 0.25);
    }}
    .pay-role-tag {{
      font-size: 0.7rem;
      font-weight: 700;
      color: #a5b4fc;
      background: rgba(99, 102, 241, 0.15);
      padding: 1px 5px;
      border-radius: 3px;
      margin-right: 3px;
    }}
    .pay-note {{
      font-size: 0.73rem;
      color: #94a3b8;
      font-style: normal;
    }}

    .place-tips {{
      font-size: 0.82rem;
      color: var(--text-sub);
      line-height: 1.5;
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
      overflow: hidden;
      flex-grow: 1;
      word-break: break-word;
      overflow-wrap: anywhere;
      min-width: 0;
    }}

    .card-footer {{
      display: flex;
      gap: 8px;
      margin-top: 4px;
    }}
    .btn-maps {{
      flex: 2;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      padding: 8px 12px;
      background: rgba(56, 189, 248, 0.12);
      border: 1px solid rgba(56, 189, 248, 0.3);
      color: #38bdf8;
      border-radius: 8px;
      font-size: 0.82rem;
      font-weight: 600;
      text-decoration: none;
      transition: all 0.2s ease;
    }}
    .btn-maps:hover {{
      background: rgba(56, 189, 248, 0.22);
      border-color: #38bdf8;
    }}
    .btn-nav {{
      flex: 1;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 4px;
      padding: 8px 10px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border-color);
      color: var(--text-sub);
      border-radius: 8px;
      font-size: 0.82rem;
      font-weight: 600;
      text-decoration: none;
      transition: all 0.2s ease;
    }}
    .btn-nav:hover {{
      background: rgba(255, 255, 255, 0.12);
      color: var(--text-main);
    }}

    /* Toast */
    .toast {{
      position: fixed;
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%) translateY(100px);
      background: #1e293b;
      border: 1px solid var(--accent-emerald);
      color: #ffffff;
      padding: 10px 20px;
      border-radius: 9999px;
      font-size: 0.85rem;
      font-weight: 600;
      box-shadow: 0 10px 25px rgba(0,0,0,0.5);
      z-index: 100;
      opacity: 0;
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      pointer-events: none;
    }}
    .toast.show {{
      transform: translateX(-50%) translateY(0);
      opacity: 1;
    }}

    /* Mobile Responsive Optimizations */
    @media (max-width: 768px) {{
      .top-nav {{
        margin-bottom: 16px;
      }}
      .brand {{
        font-size: 0.95rem;
      }}
      .nav-actions {{
        gap: 6px;
      }}
      .btn {{
        padding: 6px 10px;
        font-size: 0.76rem;
      }}
      .hero {{
        padding: 12px 0 24px 0;
      }}
      .hero h1 {{
        font-size: 1.55rem;
        line-height: 1.3;
        margin-bottom: 10px;
      }}
      .hero p {{
        font-size: 0.86rem;
        margin-bottom: 16px;
      }}
      .hero-stats {{
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 8px;
        max-width: 440px;
        margin: 0 auto;
      }}
      .stat-pill {{
        padding: 8px 6px;
        font-size: 0.75rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 3px;
        text-align: center;
        border-radius: 10px;
      }}
      .stat-num {{
        font-size: 0.92rem;
        margin-left: 0;
      }}
      .tutorial-card {{
        padding: 16px;
        margin-bottom: 20px;
      }}
      .tutorial-title {{
        font-size: 0.92rem;
        line-height: 1.4;
      }}
      #tutToggleIcon {{
        font-size: 0.72rem;
        padding: 3px 8px;
      }}
      .steps-grid {{
        grid-template-columns: 1fr;
        gap: 12px;
      }}
      .step-item {{
        padding: 12px 14px;
      }}
      .controls-wrapper {{
        padding: 12px;
        margin-bottom: 20px;
        border-radius: 14px;
        gap: 10px;
      }}
      .search-input {{
        padding: 10px 14px 10px 38px;
      }}
      .search-icon {{
        left: 12px;
      }}
      .tab-btn {{
        font-size: 0.78rem;
        padding: 5px 11px;
      }}
      .day-chip {{
        font-size: 0.72rem;
        padding: 3px 8px;
      }}
      .results-bar {{
        flex-direction: column;
        align-items: flex-start;
        gap: 4px;
        margin-bottom: 14px;
      }}
      .results-tip {{
        font-size: 0.74rem;
        color: var(--text-muted);
      }}
      .places-grid {{
        grid-template-columns: minmax(0, 1fr);
        gap: 14px;
      }}
      .place-card {{
        min-width: 0;
        padding: 14px;
        border-radius: 12px;
      }}
    }}

    @media (max-width: 600px) {{
      .nav-btn-text {{
        display: none;
      }}
      .brand-title {{
        font-size: 0.95rem;
      }}
      .brand-badge {{
        display: none;
      }}
      .btn {{
        padding: 6px 9px;
        font-size: 0.75rem;
      }}
      .nav-actions {{
        gap: 5px;
      }}
    }}

    @media (max-width: 520px) {{
      .badge-desktop-only {{
        display: none;
      }}
    }}

    @media (max-width: 380px) {{
      .brand-title {{
        font-size: 0.88rem;
      }}
      .btn {{
        padding: 5px 7px;
        font-size: 0.70rem;
      }}
    }}
  </style>
</head>
<body>

  <!-- Top Nav -->
  <header class="top-nav">
    <div class="container nav-inner">
      <a href="index.html" class="brand">
        <span class="brand-title">🍁 東北 20 天</span>
        <span class="brand-badge"><span class="badge-desktop-only">Google Maps </span>清單</span>
      </a>
      <div class="nav-actions">
        <a href="tohoku_google_maps_places.csv" download="tohoku_google_maps_places.csv" class="btn btn-primary" title="下載 82 處獨立實體地標 CSV（Google My Maps 匯入無重複圖釘）">
          <span>📥 <span class="nav-btn-text">獨立地標 </span>CSV</span>
        </a>
        <a href="tohoku_google_maps_all_stops.csv" download="tohoku_google_maps_all_stops.csv" class="btn btn-secondary" title="下載 93 站全行程活動節點 CSV">
          <span>📋 <span class="nav-btn-text">全行程 </span>93站</span>
        </a>
        <a href="calendar_export.html" class="btn btn-secondary" title="前往 Google Calendar 日曆匯出與同步中心">
          <span>📅 <span class="nav-btn-text">日曆 </span>匯出</span>
        </a>
        <a href="index.html" class="btn btn-secondary" title="前往 20 天全景互動行程 App">
          <span>📱 <span class="nav-btn-text">行程 </span>App</span>
        </a>
      </div>
    </div>
  </header>

  <main class="container">
    <!-- Hero -->
    <section class="hero">
      <div class="hero-tag">📍 Google Maps Travel Hub</div>
      <h1>東北全景 82 處獨立地點與 93 站行程導航中心</h1>
      <p>嚴謹收錄全行程 <strong>82 處獨立實體地標</strong>（涵蓋 44 處觀光名勝文化設施、29 家獨立美饌與 9 家奢華名宿）。在 20 天行程中精準構成 <strong>93 個行程活動節點</strong>（其中古川市場、八食中心、藤田庭園、飯店一泊二食等 11 處多功能場域已完整統合，去重不灌水，真實可考）。支援 Google 我的地圖 30 秒一鍵匯入！</p>
      
      <div class="hero-stats">
        <div class="stat-pill">🏛️ 景點文化體驗 <span class="stat-num">44 處</span></div>
        <div class="stat-pill">🍱 必吃老饕美饌 <span class="stat-num">40 餐</span></div>
        <div class="stat-pill">🏨 頂級預訂飯店 <span class="stat-num">9 家</span></div>
        <div class="stat-pill">📍 獨立實體地標 <span class="stat-num">82 處（共93站）</span></div>
      </div>
    </section>

    <!-- Tutorial Box -->
    <section class="tutorial-card">
      <div class="tutorial-header" onclick="toggleTutorial()">
        <div class="tutorial-title">
          <span class="tut-icon">💡</span>
          <span>如何在 30 秒內將這份清單匯入您的手機 Google Maps？</span>
        </div>
        <span id="tutToggleIcon">▲ 點擊收合</span>
      </div>
      <div class="steps-grid" id="tutSteps">
        <div class="step-item">
          <div style="display:flex; align-items:center; gap:8px;">
            <span class="step-badge">1</span>
            <strong style="color:#ffffff; font-size:0.95rem;">下載專用 CSV 檔案</strong>
          </div>
          <p class="step-text">點擊上方「📥 獨立地標 CSV」按鈕取得 <code style="color:#fb923c;">tohoku_google_maps_places.csv</code>（83 處獨立地標無重複，最推薦用於 Google My Maps 建立圖釘）；或點擊「📋 全行程 94 站 CSV」取得依時序排定之完整行程節點。</p>
          <span class="step-sub">已預先配置好精準搜尋字串與雙語欄位。</span>
        </div>
        <div class="step-item">
          <div style="display:flex; align-items:center; gap:8px;">
            <span class="step-badge">2</span>
            <strong style="color:#ffffff; font-size:0.95rem;">電腦開啟 Google 我的地圖</strong>
          </div>
          <p class="step-text">打開電腦瀏覽器前往 <a href="https://mymaps.google.com/" target="_blank" rel="noopener" style="color:#38bdf8; text-decoration:underline;">mymaps.google.com</a> ➔ 點擊左上角「<strong>+ 建立新地圖</strong>」➔ 點擊圖層下的「<strong>匯入</strong>」上傳 CSV。</p>
          <span class="step-sub">標記欄位選「Google地圖搜尋關鍵字」，標題選「地點名稱」。</span>
        </div>
        <div class="step-item">
          <div style="display:flex; align-items:center; gap:8px;">
            <span class="step-badge">3</span>
            <strong style="color:#ffffff; font-size:0.95rem;">手機 Google Maps 開啟同步</strong>
          </div>
          <p class="step-text">在 iPhone 或 Android 打開 <strong>Google Maps App</strong> ➔ 點底部「<strong>已儲存</strong>」➔ 滑到最下方點「<strong>地圖</strong>」➔ 點開該地圖！</p>
          <span class="step-sub">全 83 處獨立地標或 94 個行程節點彩色圖釘常駐在手機地圖上，邊走邊點即時導航！</span>
        </div>
      </div>
    </section>

    <!-- Controls -->
    <div class="controls-wrapper">
      <div class="mode-row">
        <div class="view-mode-toggle">
          <button class="mode-btn active" id="btnModeStops" onclick="setViewMode('stops')">🚩 行程節點 (94站)</button>
          <button class="mode-btn" id="btnModePlaces" onclick="setViewMode('places')">📍 獨立地標 (83處)</button>
        </div>
        <div style="font-size:0.8rem; color:var(--text-muted);">
          <span id="modeDescription">依 20 天每日行程先後時序呈現所有參觀、用餐與住宿節點</span>
        </div>
      </div>

      <div class="search-input-box">
        <span class="search-icon">🔍</span>
        <input type="text" id="searchInput" class="search-input" placeholder="搜尋地點名稱、日文、城市、料理或特色（如：大西、牛舌、十和田、A5、馬肉...）">
      </div>
      
      <div class="filter-tabs">
        <button class="tab-btn active" data-cat="all">全部 (<span id="tabCountAll">94</span>)</button>
        <button class="tab-btn" data-cat="🏛️ 景點・文化・體驗">🏛️ 景點文化 (<span id="tabCountSpots">45</span>)</button>
        <button class="tab-btn" data-cat="🍱 必吃美饌">🍱 必吃美饌 (<span id="tabCountDining">40</span>)</button>
        <button class="tab-btn" data-cat="🏨 入住飯店">🏨 預訂飯店 (<span id="tabCountHotels">9</span>)</button>
      </div>

      <div class="day-chips" id="dayChips">
        <button class="day-chip active" data-day="all">所有天數</button>
        <!-- Days 1 to 20 -->
      </div>
    </div>

    <!-- Results Count -->
    <div class="results-bar">
      <span>顯示 <strong id="visibleCount" style="color: var(--accent-orange);">94</strong> 個地點</span>
      <span class="results-tip">點擊「開啟 / 儲存」直接載入官方 Google 地點卡片</span>
    </div>

    <!-- Grid -->
    <div class="places-grid" id="placesGrid">
      <!-- Injected by JS -->
    </div>
  </main>

  <div class="toast" id="toast">✅ 已複製日文名稱！</div>

  <script>
    const uniquePlacesData = {unique_json};
    const allStopsData = {stops_json};

    let viewMode = 'stops'; // 'stops' or 'places'
    let rawPlaces = allStopsData;
    let currentCat = 'all';
    let currentDay = 'all';
    let currentSearch = '';

    function updateTabCounts() {{
      const source = viewMode === 'stops' ? allStopsData : uniquePlacesData;
      document.getElementById('tabCountAll').textContent = source.length;
      document.getElementById('tabCountSpots').textContent = source.filter(p => p['分類'].includes('景點')).length;
      document.getElementById('tabCountDining').textContent = source.filter(p => p['分類'].includes('美饌') || p['分類'].includes('美食')).length;
      document.getElementById('tabCountHotels').textContent = source.filter(p => p['分類'].includes('飯店')).length;
    }}

    function setViewMode(mode) {{
      viewMode = mode;
      document.getElementById('btnModeStops').classList.toggle('active', mode === 'stops');
      document.getElementById('btnModePlaces').classList.toggle('active', mode === 'places');
      
      const desc = document.getElementById('modeDescription');
      if (mode === 'stops') {{
        rawPlaces = allStopsData;
        desc.textContent = '依 20 天每日行程先後時序呈現所有參觀、用餐與住宿節點（共 94 站）';
      }} else {{
        rawPlaces = uniquePlacesData;
        desc.textContent = '合併多功能場域，呈現全行程 83 處純粹獨立之實體建築地標（無重疊圖釘）';
      }}
      updateTabCounts();
      render();
    }}

    // Init day chips
    const dayChipsContainer = document.getElementById('dayChips');
    for (let d = 1; d <= 20; d++) {{
      const btn = document.createElement('button');
      btn.className = 'day-chip';
      btn.textContent = `Day ${{d}}`;
      btn.dataset.day = `Day ${{d}}`;
      btn.addEventListener('click', () => {{
        document.querySelectorAll('.day-chip').forEach(c => c.classList.remove('active'));
        btn.classList.add('active');
        currentDay = `Day ${{d}}`;
        render();
      }});
      dayChipsContainer.appendChild(btn);
    }}

    document.querySelector('.day-chip[data-day="all"]').addEventListener('click', function() {{
      document.querySelectorAll('.day-chip').forEach(c => c.classList.remove('active'));
      this.classList.add('active');
      currentDay = 'all';
      render();
    }});

    // Tab buttons
    document.querySelectorAll('.tab-btn').forEach(tab => {{
      tab.addEventListener('click', () => {{
        document.querySelectorAll('.tab-btn').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        currentCat = tab.dataset.cat;
        render();
      }});
    }});

    // Search input
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', (e) => {{
      currentSearch = e.target.value.trim().toLowerCase();
      render();
    }});

    function copyText(txt) {{
      navigator.clipboard.writeText(txt).then(() => {{
        const toast = document.getElementById('toast');
        toast.textContent = `✅ 已複製：${{txt}}`;
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 2000);
      }});
    }}

    function cleanText(txt) {{
      if (!txt) return '';
      return txt.replaceAll('**', '').replaceAll('`', '').replaceAll('*', '');
    }}

    function escapeHtml(str) {{
      if (!str) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    }}

    function renderPaymentChips(payStr) {{
      if (!payStr) return '<span class="text-muted" style="font-size:0.75rem;">依現場公告</span>';
      
      const parts = payStr.split(/(?=(?:景點|美饌|飯店):)/g);
      const outLines = [];
      
      parts.forEach(part => {{
        let trimmed = part.trim().replace(/^｜\\s*/, '').replace(/｜\\s*$/, '').trim();
        if (!trimmed) return;
        
        let roleLabel = '';
        let content = trimmed;
        const mRole = content.match(/^((?:景點|美饌|飯店):)\\s*(.*)/);
        if (mRole) {{
          roleLabel = mRole[1];
          content = mRole[2].trim();
        }}
        
        let bracketTag = '';
        const mBracket = content.match(/^(【[^】]+】)\\s*(.*)/);
        if (mBracket) {{
          bracketTag = mBracket[1].trim();
          content = mBracket[2].trim();
        }}
        
        let mainPart = content;
        let notePart = '';
        const mNote = content.match(/^(.*?)\\s*（(.*)）\\s*$/);
        if (mNote) {{
          mainPart = mNote[1].trim();
          notePart = mNote[2].trim();
        }}
        
        const chunks = mainPart.split('｜').map(c => c.trim()).filter(Boolean);
        let chipsHtml = '';
        
        if (bracketTag) {{
          chipsHtml += `<span class="pay-chip chip-free">${{escapeHtml(bracketTag)}}</span> `;
        }}
        
        chunks.forEach(c => {{
          let cls = 'chip-info';
          if (c.includes('⭕')) cls = 'chip-ok';
          else if (c.includes('❌')) cls = 'chip-no';
          else if (c.includes('🔺')) cls = 'chip-warn';
          else if (c.includes('0 円') || c.includes('0円') || c.includes('免費') || c.includes('全包') || c.includes('住客免費')) cls = 'chip-free';
          
          chipsHtml += `<span class="pay-chip ${{cls}}">${{escapeHtml(c)}}</span> `;
        }});
        
        let lineHtml = '<div class="pay-line">';
        if (roleLabel) {{
          lineHtml += `<span class="pay-role-tag">${{escapeHtml(roleLabel)}}</span> `;
        }}
        lineHtml += chipsHtml;
        if (notePart) {{
          lineHtml += `<span class="pay-note">（${{escapeHtml(notePart)}}）</span>`;
        }}
        lineHtml += '</div>';
        outLines.push(lineHtml);
      }});
      
      return outLines.join('');
    }}

    function toggleTutorial() {{
      const steps = document.getElementById('tutSteps');
      const icon = document.getElementById('tutToggleIcon');
      if (steps.style.display === 'none') {{
        steps.style.display = 'grid';
        icon.textContent = '▲ 點擊收合';
      }} else {{
        steps.style.display = 'none';
        icon.textContent = '▼ 展開 30秒教學';
      }}
    }}

    function render() {{
      const grid = document.getElementById('placesGrid');
      grid.innerHTML = '';

      const filtered = rawPlaces.filter(p => {{
        // Category filter: match substring to handle multi-role venues
        if (currentCat !== 'all') {{
          const targetKey = currentCat.includes('景點') ? '景點' : (currentCat.includes('美饌') ? '美饌' : '飯店');
          if (!p['分類'].includes(targetKey)) return false;
        }}
        // Day filter
        if (currentDay !== 'all') {{
          const pDay = p['造訪天數'] || '';
          if (!pDay.includes(currentDay)) return false;
        }}
        // Search filter
        if (currentSearch) {{
          const haystack = (
            (p['地點名稱'] || '') + ' ' +
            (p['中文名稱'] || '') + ' ' +
            (p['日文名稱'] || '') + ' ' +
            (p['Google地圖搜尋關鍵字'] || '') + ' ' +
            (p['用餐時段或景點屬性'] || '') + ' ' +
            (p['預計時間'] || '') + ' ' +
            (p['營業時間'] || '') + ' ' +
            (p['公休日'] || '') + ' ' +
            (p['門票或預約'] || '') + ' ' +
            (p['支付方式'] || '') + ' ' +
            (p['特色亮點與老饕推薦'] || '') + ' ' +
            (p['最新營業與營運規範'] || '')
          ).toLowerCase();
          if (!haystack.includes(currentSearch)) return false;
        }}
        return true;
      }});

      document.getElementById('visibleCount').textContent = filtered.length;

      if (filtered.length === 0) {{
        grid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 60px 20px; color: var(--text-muted);">
          <div style="font-size: 2.5rem; margin-bottom: 12px;">🔍</div>
          <div style="font-size: 1.1rem; font-weight: 600; color: #cbd5e1;">找不到符合條件的地點</div>
          <div style="font-size: 0.85rem; margin-top: 6px;">請嘗試更換關鍵字或重設篩選條件</div>
        </div>`;
        return;
      }}

      filtered.forEach(p => {{
        const card = document.createElement('div');
        card.className = 'place-card';

        let badgeClass = 'badge-spot';
        if (p['分類'].includes('美饌') || p['分類'].includes('美食')) badgeClass = 'badge-dining';
        if (p['分類'].includes('飯店')) badgeClass = 'badge-hotel';
        if (p['分類'].includes('＆')) badgeClass = 'badge-multi';

        const isMulti = p['分類'].includes('＆');
        const gmapQuery = encodeURIComponent(p['Google地圖搜尋關鍵字'] || p['地點名稱']);
        const dirUrl = `https://www.google.com/maps/dir/?api=1&destination=${{gmapQuery}}`;

        card.innerHTML = `
          <div class="card-meta">
            <div class="meta-badges">
              <span class="badge-category ${{badgeClass}}">${{p['分類']}}</span>
              ${{isMulti ? '<span class="badge-role-tag">⭐ 複合地標</span>' : ''}}
            </div>
            <span class="badge-day">${{p['造訪天數']}}</span>
          </div>

          <div>
            <h3 class="place-title">${{p['中文名稱'] || p['地點名稱']}}</h3>
            <div class="place-jp">
              <span>${{p['日文名稱']}}</span>
              <button class="copy-btn" onclick="copyText('${{p['日文名稱'].replace(/'/g, "\\\\\\'")}}')" title="複製日文名稱">📋 複製</button>
            </div>
          </div>

          <div class="place-info-block">
            <div class="info-row">
              <span class="info-label">時段屬性</span>
              <span class="info-val">${{cleanText(p['用餐時段或景點屬性'] || '參觀體驗')}}</span>
            </div>
            ${{p['預計時間'] ? `<div class="info-row"><span class="info-label">行程時序</span><span class="info-val">${{cleanText(p['預計時間'])}}</span></div>` : ''}}
            ${{p['營業時間'] ? `<div class="info-row"><span class="info-label">營業時間</span><span class="info-val">${{cleanText(p['營業時間'])}}</span></div>` : ''}}
            ${{p['公休日'] ? `<div class="info-row"><span class="info-label">公休規則</span><span class="info-val">${{cleanText(p['公休日'])}}</span></div>` : ''}}
            ${{p['門票或預約'] ? `<div class="info-row"><span class="info-label">門票/預約</span><span class="info-val">${{cleanText(p['門票或預約'])}}</span></div>` : ''}}
            ${{p['支付方式'] ? `<div class="info-row"><span class="info-label">支付方式</span><div class="info-val pay-chips-container">${{renderPaymentChips(p['支付方式'])}}</div></div>` : ''}}
          </div>

          <p class="place-tips" title="${{cleanText(p['特色亮點與老饕推薦']).replace(/"/g, '&quot;')}}">${{cleanText(p['特色亮點與老饕推薦'])}}</p>

          <div class="card-footer">
            <a href="${{p['Google地圖即時連結']}}" target="_blank" rel="noopener noreferrer" class="btn-maps">
              <span>📍 開啟 / 儲存</span>
            </a>
            <a href="${{dirUrl}}" target="_blank" rel="noopener noreferrer" class="btn-nav" title="開啟 Google Maps 路線導航">
              <span>🧭 導航</span>
            </a>
          </div>
        `;
        grid.appendChild(card);
      }});
    }}

    // Initial render
    updateTabCounts();
    render();
  </script>
</body>
</html>
"""

    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Generated {OUTPUT_HTML} successfully!")

if __name__ == '__main__':
    build_page()
