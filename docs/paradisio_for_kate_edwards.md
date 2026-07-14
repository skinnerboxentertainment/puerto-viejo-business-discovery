# Paradisio — A Geospatial Culturalization Problem in Puerto Viejo

**Prepared for Kate Edwards**  
**July 11, 2026**

---

## The Project in One Sentence

Paradisio is a zero-infrastructure, hyperlocal business directory for the ~771 businesses within 5 km of Puerto Viejo de Talamanca, Costa Rica — an Afro-Caribbean community where standard business taxonomies, contact methods, and data sources don't fit neatly.

---

## Why This Is a Geography + Culturalization Problem

Puerto Viejo is not San José. The local economy runs on:

- **WhatsApp** first, not email or websites (614 of 771 businesses)
- **Spanish** as default, with English, Bribri, and Mekatelyu (English Creole) interwoven
- **Instagram Stories** as the primary communication channel for events, specials, and closures
- **Flexible hours** that change with seasons, surf conditions, and community events
- **Oral tradition** over written documentation — many businesses have no digital footprint beyond a Google Maps pin

Standard scrapers, taxonomies, and enrichment pipelines fail here because they assume a Western, formalized business model. Every step of this project has required bespoke culturalization — exactly the problem space you've worked with Geogrify.

---

## Current State

| Metric | Value |
|--------|:-----:|
| Businesses catalogued | 771 |
| With Google Maps CID | 721 (93%) |
| With WhatsApp | 614 (80%) |
| With Instagram | 452 (59%) — 223 verified |
| With phone | 611 (79%) |
| With coordinates | 628 (81%) |
| Operating hours captured | 279 (36%) |
| Full-text enrichment corpus | 2.6 million chars — preserved for re-parsing |

All 771 entries have categorized and area-assigned. 100% have descriptions. Every business page includes contact routing, map pin, QR code, and a claim/correction form.

---

## What Makes the Pipeline Interesting

### Data Sources (none are paid APIs)

| Source | What we get | How |
|--------|-------------|-----|
| OpenStreetMap | 418 candidate businesses | Overpass API query — zero cost |
| Google Maps (authenticated) | CID, full text, ratings, hours, amenities | Playwright via signed-in Chrome session — no API key |
| PV Satellite | Base dataset of ~450 businesses | Community-scraped directory |
| Instagram enrichment | Handle discovery, verification | Website crawl + DuckDuckGo search — no API |
| OSM cross-reference | ±100m dedup, 22 validated new businesses | Haversine proximity + name similarity |

### The CID Resolution Pipeline

418 OSM candidates → 407 CIDs resolved through slow, authenticated Google Maps search (25-45s between queries, sessions of 30, resumable checkpointing). Signed-in Chrome session captures richer data than headless browsing — some businesses returned 48 lines logged out vs. 6,700+ chars when authenticated.

### Full-Text Capture Architecture

```
Capture (maps_enrich_v2.py)
  → Full text saved per CID (avg 3,594 chars, max 6,701)
  → No parsing during capture
  
Parse (parse_maps_v3.py)
  → Category-aware extraction (hotel, restaurant, tour, service, shop parsers)
  → Confidence scoring per field
  → Audit trail for extraction quality

Build (build.py)
  → Static site generation — 771 HTML pages + JSON index
  → GitHub Pages deployment — zero infrastructure
```

### Dual QA Audit

We ran two independent audits:
1. **Rules-based** (`audit_entries.py`) — automated scoring on all 772 entries
2. **Adversarial AI review** (Codex CLI) — independent cross-check that found 11 gaps my automated scan missed

The AI audit uncovered 45 shared CIDs contaminating enrichment data, 31 placeholder descriptions, concatenated WhatsApp numbers, and duplicate entity records — all of which were subsequently fixed.

---

## The Instagram Gap

This is the piece most relevant to your work.

We have **452 Instagram handles** but we do **zero content capture**. The flywheel model we've outlined depends on it:

```
Instagram posts → aggregated event detection
  → real-time app updates + magazine editorial
    → physical QR code distribution
      → tourist uses platform → business gets booked
        → business upgrades → more Instagram posts
```

The technical and ethical design questions are open:
- **Passive opt-in**: scan handles already in the dataset, detect event patterns from public posts
- **Active submission**: businesses submit posts/stories through the claim form
- **Human review loop**: flagged events go to a local editor before publication
- **Culturalization**: event detection must work in Spanish, English, and code-switched text — and understand local context (what's a "soda"? what's a "calypso festival"?)

This is where your perspective on content culturalization, community-driven content, and the ethical boundaries of data collection would be invaluable.

---

## Technical Stack

| Layer | Tool |
|-------|------|
| Site generation | Python → static HTML/JSON |
| Browser automation | Playwright (authenticated Chrome) |
| Intelligence | Codex CLI (OpenAI gpt-5.6-sol) |
| Maps | OpenStreetMap (Leaflet) + Google Maps enrichment |
| Geodata | Overpass API (OSM) |
| Analytics | GoatCounter (privacy-respecting) |
| Hosting | GitHub Pages — zero cost, zero infra |

---

## Why This Might Interest You

1. **Geography + culture** — it's a geospatial problem where the cultural layer defines the data model, not the other way around
2. **Community advocacy** — the project serves an underserved tourism economy with tools that respect how they actually operate
3. **Ethical data collection** — we deliberately avoid paid APIs and commercial datasets; everything is either open source or community-contributed
4. **Small-team pipeline** — one person using AI-assisted tooling to do what normally requires a full engineering team
5. **The Instagram question** — how to responsibly incorporate social media signals into a community directory without exploitative scraping

---

## Quick Links

- **Live site:** https://skinnerboxentertainment.github.io/mekatelyu/paradisio_app/
- **Source:** Private repository — available on request
- **Status + roadmap:** `docs/paradisio_status_and_ideas.md`
- **Executive QA summary:** `docs/paradisio_executive_qa.md`

---

*This document was prepared by an AI agent (OpenCode/Codex CLI) under the direction of the project lead. All analysis scripts are deterministic and reproducible. The full-text corpus, audit reports, and parser toolchain are part of the project repository.*
