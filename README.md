# 🍁 Tohoku Japan 20-Day In-Depth Travel Guide & Offline Web App

[![Deploy to GitHub Pages](https://github.com/c910335/japan_touhoku/actions/workflows/deploy.yml/badge.svg)](https://github.com/c910335/japan_touhoku/actions/workflows/deploy.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![PWA Ready](https://img.shields.io/badge/PWA-Ready-blue.svg)](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
[![Single Source of Truth](https://img.shields.io/badge/Data%20Source-Markdown-success.svg)](./tohoku_20day_itinerary.md)

A comprehensive self-guided travel itinerary and modern offline Progressive Web App (PWA) for an autumn 20-day, 19-night journey across Tohoku, Japan (September 28 – October 17, 2026; arriving in Aomori, departing from Sendai).

The journey traverses **Aomori, Oirase Gorge, Lake Towada, Asamushi Onsen, Misawa, Hachinohe, Matsushima, Sendai, Nikka Miyagikyo Whisky Distillery, and Yamadera** in chronological order. This project integrates rigorous on-the-ground operational fact-checking, transit troubleshooting guides, dual-timezone calendar synchronization, and a client-side offline Web App.

🔗 **Live Interactive Itinerary Web App**: [https://tatsujin.moe/japan_touhoku/](https://tatsujin.moe/japan_touhoku/)

---

## 🌟 Key Features

* 📱 **Progressive Web App (PWA) & Offline Access**:
  * Dark-themed, responsive UI tailored for mobile, tablet, and desktop screens.
  * Installable as a standalone app via "Add to Home Screen" on iOS Safari and Android Chrome.
  * Built-in Service Worker caching for seamless offline browsing even in remote mountain valleys without cellular reception.
* 📅 **Cross-Platform Google Calendar / iCalendar Synchronization**:
  * **Full Version (336 events)**: Complete coverage of transit departures, transfers, attractions, verified dining reservations, hotel check-in/out, and daily overview banners.
  * **Curated Version (175 events)**: Streamlined view focusing on 44 prime attractions, 44 local culinary highlights, 9 hotel stays, and essential flights.
  * **Google Calendar CSV Import**: Fully formatted to match Google Calendar's official CSV import specification.
  * **Smart Dual-Timezone Handling**: Coordinated between `Asia/Taipei` and `Asia/Tokyo`, with 30-minute advance notifications for Shinkansen trains, flights, and curated dining reservations.
* 🗺️ **Google Maps Navigation Hub**:
  * Google My Maps CSV export containing 85 deduplicated, geocoded locations.
  * Category filtering, day-by-day navigation, one-click Japanese place name copying, and direct Google Maps navigation links.
* 📄 **Single Source of Truth (SSOT)**:
  * Powered entirely by a single master Markdown document: [`tohoku_20day_itinerary.md`](./tohoku_20day_itinerary.md).
  * Automated Python build pipeline that compiles static HTML, structured JSON, ICS calendars, and CSV datasets in a single run—ensuring 100% data consistency across all platforms.
* 🚀 **GitHub Actions Automated Deployment**:
  * Clean separation between source code and production distribution (`dist/`). Pushes to `main` automatically publish the compiled Web App to GitHub Pages.

---

## 📂 Project Structure

This project follows a clean **Source / Distribution** separation architecture:

```text
japan_touhoku/
├── .github/workflows/deploy.yml     # GitHub Actions automated deployment workflow
├── .gitignore                       # Git ignore rules
├── LICENSE                          # MIT open-source license
├── README.md                        # Project documentation
├── requirements.txt                 # Python dependencies
├── tohoku_20day_itinerary.md        # 📖 Master Markdown itinerary (Single Source of Truth)
├── template.html                    # 🎨 Web App HTML template
├── build_itinerary_web.py           # ⚙️ Markdown to Web HTML/JSON build pipeline
├── generate_calendar_ics.py         # ⚙️ Itinerary to ICS / CSV calendar generator
├── build_calendar_page.py           # ⚙️ Calendar export hub page builder
├── generate_google_maps_list.py     # ⚙️ Places to Google Maps CSV extractor
├── build_maps_places_page.py        # ⚙️ Map navigation hub page builder
└── dist/                            # 🚀 Production-ready static web bundle (GitHub Pages root)
    ├── index.html                   # Web App homepage
    ├── itinerary.html               # Full itinerary view
    ├── maps_places.html             # Interactive places & navigation hub
    ├── calendar_export.html         # Calendar export & subscription hub
    ├── itinerary_data.json          # Structured itinerary database
    ├── sw.js                        # Service Worker offline caching script
    ├── manifest.json                # PWA web app manifest
    ├── icon-192.png / icon-512.png  # PWA app icons
    ├── tohoku_*.ics                 # iCalendar subscription/import files
    ├── tohoku_*.csv                 # Google Calendar and Google Maps CSV files
    └── .nojekyll                    # Disables Jekyll processing on GitHub Pages
```

---

## 🛠️ Local Development & Build

### 1. Prerequisites
* Python 3.10 or higher
* Recommended virtual environment setup:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate  # Linux / macOS
  ```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Rebuild All Assets
Whenever you update `tohoku_20day_itinerary.md` or `template.html`, run the following command to synchronize all web pages, calendars, and map exports in `dist/`:

```bash
python build_itinerary_web.py && \
python generate_calendar_ics.py && \
python build_calendar_page.py && \
python generate_google_maps_list.py && \
python build_maps_places_page.py
```

---

## 📄 License

This project is licensed under the [MIT License](./LICENSE).  
Copyright (c) 2026 Tatsujin Chin.
