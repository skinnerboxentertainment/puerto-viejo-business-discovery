# Paradisio — Status & Idea Landscape

## Built

| Feature | Status | Detail |
|---------|--------|--------|
| Static app generator | Done | `build.py` — pure Python, reads CSV, outputs HTML/JSON |
| 750 business pages | Done | Full detail pages with contact routing |
| Search + filters | Done | Category, area, text, contact-channel filters |
| Pagination | Done | 50 at a time, load more, resets on filter change |
| Cluster map (homepage) | Done | Leaflet + markercluster toggle, filter-aware |
| Maps (Leaflet/OSM) per page | Done | Interactive pins on 606 business pages |
| Mobile-first CSS | Done | 4 viewports, sticky CTA bar, safe-area padding |
| Design token system | Done | CSS custom properties (tokens.css) |
| Display name cleanup | Done | 380+ location suffixes stripped |
| Contact labels | Done | Human-readable: Verified/Strong/Partial/Limited |
| Trust signals | Done | Source badges, claimed/unclaimed status |
| Subcategory/cuisine | Done | Extracted from Maps + business names |
| QR generator | Done | 750 print-ready PNGs + redirect pages + gallery |
| QR on business pages | Done | Preview image + download link per business |
| Maps enrichment v2 (authenticated) | Done | 715 CIDs — full text capture, 689 ratings |
| Ratings on biz pages | Done | Star ratings on 689 pages |
| Amenities on biz pages | Done | Filtered chips on 200+ pages |
| Addresses on biz pages | Done | Maps address on ~100 pages |
| Hours on biz pages | Done | Check-in/out + open_status field added |
| OSM candidates merged | Done | 418 scanned → 22 validated new businesses added |
| Classifieds board | Done | 15 seed listings, 8 categories, search, detail pages |
| Multi-language | Done | EN/ES/DE with client-side switcher, locale JSON files |
| GitHub Discussions | Done | Forum + issue templates (bugs, ideas, classifieds) |
| OSM cross-ref (v2) | Done | 418 candidates found |
| OSM CID resolution (authenticated) | Done | 418 searched, 407 CIDs found, 244 phones, 168 websites |
| GoatCounter analytics | Live | Pageview tracking on all pages |
| GitHub Pages | Live | https://skinnerboxentertainment.github.io/mekatelyu/paradisio_app/ |

## Coverage (from the data)

*772 master records (750 original + 22 validated OSM additions)*

| Channel | Count | % of 772 |
|---------|:-----:|:--------:|
| Google Maps CID | 721 | 93% |
| WhatsApp | 614 | 80% |
| Phone | 611 | 79% |
| Instagram | 452 | 59% |
| Instagram (verified) | 223 | 29% |
| Facebook | 361 | 47% |
| Website | 191 | 25% |
| Booking.com | 171 | 22% |
| Email | 75 | 10% |
| Coordinates | 628 | 81% |
| **Rating (v2 enrich)** | **689** | **89%** |
| **Address (v2 enrich)** | **TBD** | **—** |
| **Hours/Open status** | **New** | **v2 field** |
| WhatsApp | 614 | — |
| Phone | 611 | ~855 |
| Instagram | 452 | — |
| Instagram (verified) | 223 | — |
| Facebook | 361 | — |
| Website | 191 | ~359 |
| Booking.com | 171 | — |
| Email | 75 | — |
| Coordinates | 606 | — |
| **Rating (Maps enrich)** | **640** | **85%** |
| **Amenities (Maps enrich)** | **215** | **29%** |
| **Check-in/out (Maps enrich)** | **203** | **27%** |
| **Address (Maps enrich)** | **105** | **14%** |

## Remaining Ideas

| # | Idea | What's needed |
|---|------|--------------|
| 1 | Frontend: surface open_status/hours on biz pages | New v2 fields captured but not yet displayed in HTML |
| 2 | Classifieds posting flow | Web3Forms + WhatsApp-first submission form |
| 3 | Premium listings ($100/$200) | Payments (SINPE), analytics, featured placement logic |
| 4 | QR affiliate network | Affiliate tracking, commission payouts, sales materials |
| 5 | AI service upsells (WhatsApp auto-reply, IG content pack, menu translation) | OpenAI integration per service |
| 6 | Middleman fees (10-20% on transport, tours, dining) | Concierge ops, dispute handling |
| 7 | Instagram capture engine (event detection, dashboards) | Scraping pipeline + analytics backend |
| 8 | Quarterly print magazine | Layout, print vendor, distribution |
| 9 | Creative layer (artists, musicians, photographers) | Profile type expansion, curation |
| 10 | Community layer (Reddit, Discord, blog) | Seeding, moderation, content ops |
| 11 | Town API (intent router for Puerto Viejo) | Query wrapper around existing JSON data |
| 12 | WhatsApp concierge (traveler-facing assistant) | WhatsApp Business API or web launcher |
| 13 | Refreshable scanner (port to other towns) | Run proven method on a second town |
| 14 | Puerto Viejo Economic Tarot (data-art oracle) | Static microsite with archetype cards |

## The Flywheel

```
Instagram posts → aggregated analytics & event detection
  → magazine editorial + real-time web app updates
    → physical distribution + QR code scans
      → tourist uses platform
        → business gets booked
          → business upgrades to premium
            → more Instagram posts
```

---

*Generated 2026-07-09*
