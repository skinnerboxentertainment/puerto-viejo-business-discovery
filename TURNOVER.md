# Paradisio — Complete Project Turnover

## 1. Project Identity

**Name:** Paradisio (codename)
**Repository:** `skinnerboxentertainment/mekatelyu` (GitHub)
**Live URL:** https://skinnerboxentertainment.github.io/mekatelyu/paradisio_app/
**Original source data repo:** `skinnerboxentertainment/puerto-viejo-business-discovery` (unchanged upstream)
**Purpose:** A persistent web application that is the commercial and cultural operating system for Puerto Viejo de Talamanca, Costa Rica. Every business is listed by default (opt-out, not opt-in). The platform includes a business directory, classifieds board, QR code generator, interactive maps, Instagram-based enrichment, trust signals, and a print-ready magazine concept.

---

## 2. Data Foundation

### Master Dataset
- **File:** `pv_master_unified.csv` — 750 records, 34 columns
- **Sources:** PV Satellite crawl (450), SQLite cache (139), OSM additions (31), grid scan (134)
- **Enrichment pipeline:** Instagram verification (Playwright), Maps CID crawl (Playwright), website crawl (httpx), stealth Maps search (Playwright + real Chrome)

### Coverage (current)

| Field | Count | % |
|-------|------:|--:|
| Business name | 750 | 100% |
| Google Maps CID | 699 | 93% |
| WhatsApp | 614 | 82% |
| Phone | 611 | 81% |
| Coordinates | 606 | 81% |
| Instagram | 452 | 60% |
| Instagram (verified) | 223 | 30% |
| Facebook | 361 | 48% |
| Website | 191 | 25% |
| Booking.com | 171 | 23% |
| Email | 75 | 10% |
| Star Rating (Maps enrich) | 640 | 85% |
| Amenities (Maps enrich) | 215 | 29% |
| Check-in/out (Maps enrich) | 203 | 27% |
| Street Address (Maps enrich) | 105 | 14% |

### Maps CID Enrichment (v1 pass)
- **Script:** `paradisio_app/maps_enrich.py`
- **Method:** Playwright opens `https://www.google.com/maps?cid={CID}`, extracts visible text via DOM TreeWalker
- **Captured:** rating, phone, website, plus code, check-in/out, amenities, prices, nearby competitors
- **NOT captured (available but missed):** street address (descriptive, not Plus Code), hours of operation (restaurants/shops), open/closed status
- **NOT saved:** full visible text was discarded after parsing (only 300-char sample retained)
- **Results file:** `docs/paradisio_app/data/maps_enrich.json` (674 successful records)

### v2 CID Re-Scan (planned, not executed)
- **Methodology:** `docs/cid_v2_extraction_methodology.md`
- **Key change:** save full visible text, category-aware parsing, no data loss
- **Sample analysis:** `docs/paradisio_app/data/cid_v2_samples/analysis_report.txt` — 11 businesses across 6 categories
- **Estimated time:** 4-6 hours at moderate pace with pacing
- **Requires:** Authenticated Chrome profile for full page rendering (some businesses return only 48 lines without login)

---

## 3. Application Architecture

### Stack
- **Generator:** Pure Python stdlib (`build.py`) — reads CSV + JSON, outputs static HTML/JSON
- **Frontend:** Vanilla HTML/CSS/JS — no frameworks, no build step
- **Maps:** Leaflet.js + OpenStreetMap tiles
- **QR codes:** qrcode Python library (Pillow for PNG output)
- **Analytics:** GoatCounter (privacy-first, open source)
- **Hosting:** GitHub Pages via `docs/` directory
- **AI bridge:** CODEX_ENDPOINT v2 (OpenCode ↔ OpenAI Codex CLI)

### Directory Structure

```
paradisio_app/
├── build.py                        ← Main generator (870 lines)
├── generate_qr.py                  ← QR code generator
├── capture_mobile.py               ← Playwright screenshot capture
├── maps_enrich.py                  ← Maps CID enrichment crawler
├── maps_enrich_report.py           ← Enrichment summary reporter
├── data/
│   ├── classifieds.json            ← Seed classifieds data (15 listings)
│   └── (generated at build time)
├── static/
│   ├── tokens.css                  ← Design system tokens (colors, type, spacing)
│   ├── styles.css                  ← All component styles (uses token variables)
│   ├── app.js                      ← Directory + map + search JS
│   └── classifieds.js              ← Classifieds search JS
├── templates/                      ← (reserved)

docs/paradisio_app/                 ← Generated output (committed to Git)
├── index.html                      ← App entry point (homepage)
├── businesses/                     ← 750 individual business pages
│   └── {slug}.html
├── classifieds/                    ← Classifieds board
│   ├── index.html
│   └── {slug}.html
├── qr/                             ← QR codes (750 PNGs + redirect pages)
│   ├── index.html                  ← Print gallery
│   ├── {slug}.png
│   └── {slug}.html
├── data/
│   ├── businesses.json             ← Search index (750 records)
│   ├── metrics.json                ← Build metrics
│   ├── maps_enrich.json            ← CID enrichment results
│   └── maps_checkpoint.json        ← Crawl resume checkpoint
├── static/                         ← Copied assets
│   ├── tokens.css
│   ├── styles.css
│   ├── app.js
│   └── classifieds.js
└── screenshots/                    ← Playwright captures

docs/                               ← GitHub Pages root
├── .nojekyll                       ← Disables Jekyll processing
├── index.html                      ← Landing page (with QR code, OG tags)
├── directory.html                  ← Classic interactive directory
├── gapmap.html                     ← Grid-based gap scanner
├── report.html                     ← Analytical report
├── audit.html                      ← Data audit dashboard
├── paradisio_app/                  ← ← THIS IS THE MAIN APP
```

### Build Pipeline

```
python paradisio_app/build.py       → docs/paradisio_app/
python paradisio_app/generate_qr.py → docs/paradisio_app/qr/
python paradisio_app/maps_enrich.py → docs/paradisio_app/data/maps_enrich.json
python paradisio_app/capture_mobile.py → docs/paradisio_app/screenshots/mobile/
```

To rebuild and deploy:
```powershell
python paradisio_app/build.py
git add -A
git commit -m "rebuild"
git push mekatelyu master
```

---

## 4. Features — Current Status

### Built & Live
| Feature | Description | Key file |
|---------|-------------|----------|
| 750 business pages | Full detail pages with contact routing, maps, ratings, badges | `build.py` |
| Search + filters | Category, area, text, contact-channel filters with pagination | `app.js` |
| Interactive maps | Leaflet.js on each business page, cluster map on homepage toggle | `app.js`, `build.py` |
| Mobile-first CSS | 4 viewport breakpoints, sticky CTA bar, safe-area padding | `styles.css` |
| Design token system | CSS custom properties for colors, type, spacing, radii, shadows | `tokens.css` |
| Display name cleanup | 380+ location suffixes stripped from business names | `build.py:clean_display_name` |
| Star ratings | From Maps enrich, displayed as HTML entities | `build.py` |
| Amenities chips | Filtered, deduplicated from Maps enrich | `build.py` |
| Check-in/out hours | From Maps enrich, displayed on business pages | `build.py` |
| Trust signals | Source badges, claimed/unclaimed status on business pages | `build.py` |
| Contact labels | Human-readable (Verified/Strong/Partial/Limited) replacing numeric scores | `app.js` |
| Subcategory/cuisine | Extracted from Maps and business names | `_add_cuisine.py` |
| QR codes | 750 print-ready PNGs, redirect pages, print gallery | `generate_qr.py` |
| QR on business pages | Preview + download link per business | `build.py` |
| Classifieds board | 15 seed listings, 8 categories, search, categories nav | `build.py`, `classifieds.js`, `classifieds.json` |
| Cluster map | Homepage toggle, Leaflet.markercluster, filter-aware | `app.js` |
| Analytics | GoatCounter on all pages | `build.py` template |
| Bilingual nav | English primary, Spanish labels ready | `build.py:nav_html` |
| GitHub Pages | Auto-deploys from `docs/` on push | — |

### Remaining Ideas (not built)
| # | Idea | What's needed |
|---|------|--------------|
| 1 | Premium listings ($100/$200) | Payments (SINPE), analytics, featured placement |
| 2 | QR affiliate network | Affiliate tracking, commission payouts |
| 3 | AI service upsells | OpenAI integration per service |
| 4 | Middleman fees (10-20%) | Concierge ops, dispute handling |
| 5 | Instagram capture engine | Scraping pipeline + analytics |
| 6 | Quarterly print magazine | Layout, print vendor, distribution |
| 7 | Creative layer (artists, musicians) | Profile type expansion, curation |
| 8 | Community layer (Reddit, Discord) | Seeding, moderation, content ops |
| 9 | Town API | Query wrapper around existing JSON |
| 10 | WhatsApp concierge | WhatsApp Business API or web launcher |
| 11 | Refreshable scanner (port to other towns) | Run method on a second town |
| 12 | Puerto Viejo Economic Tarot | Static microsite with archetype cards |
| 13 | v2 CID re-scan | Overnight job with category-aware parsing |

---

## 5. Design Direction

Resolved between OpenCode and Codex. Documented in `docs/paradisio_direction_unified.md`.

**Direction:** "Polished Local Warmth" — warm minimalism as mood, polished local board as product.
**Tagline:** "Find Puerto Viejo businesses with confidence."
**Palette:** Sand backgrounds, jungle green identity, coral CTAs, reef accent for interactive elements.
**Typography:** System font stack (no Google Fonts dependency).
**Map:** List/search default, map as prominent toggle (not default view).
**Photography:** Category-specific CSS placeholders. No Instagram scraping. Owner-submitted after claim flow.
**Spanish:** Design for bilingual now, ship full translation later.

---

## 6. CODEX_ENDPOINT System

### Purpose
File-based IPC hub enabling OpenCode (orchestrator) to delegate tasks to OpenAI Codex CLI (worker). Two protocols:

**v1 — One-Shot:**
```powershell
python codex_bridge.py "task description" --json
```
Best for simple, focused tasks. Output is JSON on stdout.

**v2 — Session Bidirectional:**
```powershell
python CODEX_ENDPOINT\session_orchestrator.py create --title "Task" --description "Desc"
python CODEX_ENDPOINT\session_orchestrator.py next --session-id <id> --message "instruction"
```
Best for multi-turn iterative tasks. Uses state machine with atomic writes and lock protocol.

### Known Issues
- `session_orchestrator.py` crashes on `print(json.dumps(output))` when Codex output contains unicode characters (→, emoji, etc.) on Windows cp1252 terminal. The session IS updated by the bridge before the crash, but the JSON dump fails. **Workaround:** Use one-shot calls (`codex_bridge.py --json`) for tasks that don't need iteration, or read the .bak file after a session crash.
- Codex sometimes writes plain strings to `artifacts[]` instead of `{"path": "..."}` objects, causing Pydantic validation errors. **Fix:** Use `replaceAll` or add `"response"` to `EntryType` enum.

---

## 7. Key Scripts Reference

| Script | Purpose | When to run |
|--------|---------|-------------|
| `paradisio_app/build.py` | Generate all HTML/JSON from CSV + data files | After any data change |
| `paradisio_app/generate_qr.py` | Generate QR code PNGs + redirect pages | After build, or when BASE_URL changes |
| `paradisio_app/maps_enrich.py` | CID enrichment crawl (Playwright) | Overnight, resumable |
| `paradisio_app/capture_mobile.py` | Playwright screenshots at mobile viewports | After design changes |
| `codex_bridge.py` | One-shot Codex task delegation | Ad-hoc tasks |
| `maps_enrich_report.py` | Print enrichment coverage summary | After enrichment run |

### Temp/Analysis Scripts (prefixed with `_`)
These are one-off analysis scripts created during development. Not part of the build pipeline:
- `_add_cuisine.py`, `_extract_cuisine.py` — Subcategory extraction from Maps text
- `_cid_postmortem.py`, `_cid_v2_batch_sample.py` — Deep CID analysis
- `_analyze_sample.py` — Cross-category field pattern analysis
- `_best_restaurant.py`, `_check_cuisine.py` — Data quality checks
- `_inspect_db.py`, `_check_reviews.py`, `_check_desc.py` — PVS SQLite exploration
- `_maps_inspect.py`, `_httpx_test.py` — CID page investigation tools
- `_check_pages.py`, `_check_pages2.py` — GitHub Pages status checks
- `_check_session.py`, `_check_bak.py`, `_get_debate.py` — CODEX session debugging
- `_analyze.py`, `_check_enrich.py`, `_check_qr.py` — Various data inspections

---

## 8. Agent Onboarding Instructions

When a new agent (OpenCode or Codex) needs to work on this project, provide this context:

### Initial Context for Any Agent

> This is Paradisio — a static web app for Puerto Viejo, Costa Rica business discovery. 750 businesses, 34 data columns, generated from a CSV by a Python build script. The app lives on GitHub Pages at `skinnerboxentertainment.github.io/mekatelyu/paradisio_app/`.
>
> **Key files to read first:**
> - `TURNOVER.md` — this document
> - `AGENTS.md` — operation protocols
> - `docs/paradisio_direction_unified.md` — design direction
> - `docs/paradisio_status_and_ideas.md` — feature inventory
>
> **Build pipeline:** `python paradisio_app/build.py` reads `pv_master_unified.csv` and generates `docs/paradisio_app/`. All HTML/CSS/JS is vanilla. No frameworks.
>
> **Data enrichment:** Maps CID data is in `docs/paradisio_app/data/maps_enrich.json`. The enrichment crawler is `paradisio_app/maps_enrich.py`.
>
> **CODEX_ENDPOINT:** The `CODEX_ENDPOINT/` directory contains an IPC hub for delegating tasks to Codex CLI. One-shot: `python codex_bridge.py "task"`. Session: `python CODEX_ENDPOINT/session_orchestrator.py create/next/status`.
>
> **Git remotes:** `origin` = the original `puerto-viejo-business-discovery` repo (read-only, do not push). `mekatelyu` = the active working repo.
>
> **Current priorities (from latest discussion):**
> 1. Classifieds posting flow — implement Web3Forms + WhatsApp-first submission form
> 2. v2 CID re-scan — overnight job with full text capture + category-aware parsing
> 3. Presentation layer Phase 2 — two-column desktop layout, trust signals, photography strategy

---

## 9. Environment Setup

### Prerequisites
- Python 3.13+
- Playwright: `pip install playwright && playwright install chromium`
- QR code: `pip install qrcode[pil]`
- Validated with `codex exec` (Codex CLI v0.142.5, gpt-5.5)

### Required Environment Variables
- `CODEX_PATH` — Path to codex.exe (default: `~/.codex/.sandbox-bin/codex.exe`)
- `PARADISIO_BASE_URL` — Production URL for absolute QR codes (defaults to GitHub Pages URL in `generate_qr.py`)
- `CODEX_COOLDOWN` — Seconds between Codex invocations (default: 2.0)

### First-Time Setup
```powershell
git clone https://github.com/skinnerboxentertainment/mekatelyu.git
cd mekatelyu
pip install qrcode[pil] playwright httpx
playwright install chromium
python paradisio_app/build.py
python paradisio_app/generate_qr.py
```

### Deployment
Any push to `master` triggers GitHub Pages auto-deploy from `docs/`. Alternatively:
```powershell
python -m http.server 8080 --directory docs/paradisio_app
```

---

## 10. Key Decisions & Rationale

| Decision | Rationale |
|----------|-----------|
| Static site (no backend) | Zero infrastructure cost, GitHub Pages hosting, Git-based deployment |
| Vanilla JS (no framework) | Keeps bundle <50KB, no build step, maximum compatibility |
| CSV as source of truth | Portable, diffable, version-controlled, editable in any tool |
| Opt-out listing model | Every business is on the board by default — flips standard directory economics |
| Warm minimalism design | Approaches users as utility, not as luxury travel aspirants |
| GoatCounter over Plausible | Zero signup friction, open source, free |
| Leaflet over Google Maps API | No API key, no billing, no usage limits |
| WhatsApp routing as primary CTA | Matches how Costa Rica actually does business |
| QR codes for physical distribution | Connects digital platform to physical town — stickers on doors |
| Category shortcuts (not hero carousel) | Utility over inspiration — users arrive with intent, not wanderlust |

---

## 11. Troubleshooting

### GitHub Pages builds stuck in "queued"
Delete and recreate GitHub Pages:
```powershell
gh api repos/skinnerboxentertainment/mekatelyu/pages -X DELETE
# Wait 30 seconds
Set-Content -Path "$env:TEMP\pages.json" -Value '{"source":{"branch":"master","path":"/docs"}}'
gh api repos/skinnerboxentertainment/mekatelyu/pages -X POST --input "$env:TEMP\pages.json"
```

### Unicode encoding errors in session_orchestrator.py
The Windows cp1252 terminal cannot print certain unicode characters. Workaround: read the bridge log file directly instead of using `session_orchestrator.py next`:
```powershell
# After a session times out on print:
python -c "import json; d=json.load(open('CODEX_ENDPOINT/sessions/<id>.bak')); print(d['conversation'][-1]['message'])"
```

### Maps enrichment page too sparse (<50 lines)
Some businesses return limited data without a logged-in Google account. Solution: use authenticated Chrome profile via CDP (pattern in `stealth_search.py`).

---

## 12. File Manifest (Key Files Only)

| File | Lines | Purpose |
|------|-------|---------|
| `paradisio_app/build.py` | 870 | Main app generator |
| `paradisio_app/generate_qr.py` | 205 | QR code generator |
| `paradisio_app/maps_enrich.py` | 300 | CID enrichment crawler |
| `paradisio_app/capture_mobile.py` | 100 | Mobile screenshot capture |
| `paradisio_app/static/tokens.css` | 100 | Design tokens |
| `paradisio_app/static/styles.css` | 530 | All component styles |
| `paradisio_app/static/app.js` | 370 | Directory + map JS |
| `paradisio_app/static/classifieds.js` | 100 | Classifieds JS |
| `codex_bridge.py` | 490 | Codex CLI bridge |
| `pv_master_unified.csv` | 750 rows | Master dataset |
| `docs/paradisio_direction_unified.md` | — | Design direction (resolved) |
| `docs/paradisio_status_and_ideas.md` | — | Feature inventory + idea list |
| `docs/paradisio_roadmap.md` | — | Feasibility/ROI analysis |
| `docs/cid_enrichment_strategy_report.md` | — | CID enrichment strategy |
| `docs/cid_v2_extraction_methodology.md` | — | v2 CID methodology |
| `docs/request_classifieds_posting.md` | — | Classifieds posting research |
| `docs/paradisio_presentation_considerations.md` | — | Design considerations |
| `docs/paradisio_build_spec.md` | — | Original build spec |
| `docs/paradisio_vision.md` | — | Original vision doc |
| `AGENTS.md` | 70 | Agent operation protocols |
| `TURNOVER.md` | — | This document |

---

*Generated 2026-07-09. For questions, refer to the git log or the original brainstorming session in CODEX_ENDPOINT/sessions/.*
