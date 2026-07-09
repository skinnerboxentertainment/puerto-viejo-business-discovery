# Paradisio Board — Build Spec

## Product Definition

A persistent bilingual web directory for Puerto Viejo de Talamanca, Costa Rica, that routes visitors from intent to local contact. Every business gets a stable page with WhatsApp/phone/IG/map/website links, a prefilled Spanish WhatsApp message, and a "claim this page" CTA. Generated as static HTML from the master CSV. No backend, no auth, no payments in v1.

---

## Tech Stack

- **Build:** Python standard library (csv, json, html, hashlib, re, urllib.parse, pathlib)
- **Output:** Static files under `paradisio_app/`
- **Frontend:** Vanilla HTML/CSS/JS — no frameworks
- **Search:** Client-side JSON index — no backend
- **Analytics:** localStorage event logger stub
- **Hosting:** GitHub Pages via `docs/` directory

---

## File List

### Build tooling
- `paradisio_app/build.py` — reads `pv_master_unified.csv`, normalizes, generates static app

### Templates
- `paradisio_app/templates/index.html` — search UI shell
- `paradisio_app/templates/business.html` — business detail page template

### Static assets
- `paradisio_app/static/app.js` — client-side search/filter, intent buttons, event tracking, WhatsApp message generation
- `paradisio_app/static/styles.css` — responsive, text-first, fast-loading design

### Generated output (`docs/paradisio_app/`)
- `index.html` — app entry point with search + filters
- `businesses/<slug>.html` — one page per business (~750)
- `data/businesses.json` — search index for client-side filtering
- `data/metrics.json` — build stats (counts, coverage, freshness)

---

## Data Model (derived JSON per business)

```json
{
  "id": "stable_hash_or_cid",
  "slug": "business-name-area",
  "name": "Business Name",
  "category": "restaurant",
  "area": "Cocles",
  "lat": 9.65,
  "lng": -82.75,
  "distance_km": 1.8,
  "channels": {
    "phone": "+506...",
    "whatsapp": "+506...",
    "instagram": "handle",
    "facebook_url": "https://...",
    "website": "https://...",
    "booking_url": "https://...",
    "tripadvisor_url": "https://...",
    "google_maps_cid": "..."
  },
  "links": {
    "whatsapp": "https://wa.me/...?...",
    "call": "tel:+506...",
    "instagram": "https://instagram.com/...",
    "map": "https://www.google.com/maps?cid=..."
  },
  "scores": {
    "contactability": 0-100,
    "visibility": 0-100,
    "data_completeness": 0-100
  },
  "badges": ["WhatsApp", "Instagram", "Booking", "Map verified"],
  "intents": ["eat", "stay", "tour", "shop", "service", "rainy_day_candidate", "low_friction_contact"],
  "claim": {
    "status": "unclaimed",
    "claim_url": "mailto:...?..."
  }
}
```

---

## UX Surface

### Homepage
- Search box: "What do you need in Puerto Viejo?"
- Filters: Eat, Stay, Tours, Shops, Services, Nightlife, WhatsApp, Instagram, Booking
- Area filters: Puerto Viejo, Cocles, Playa Chiquita, Punta Uva, Manzanillo, other
- Result cards: name, category, area, contact badges, primary CTA button
- Top stats bar: total businesses, WhatsApp/phone/IG counts, last generated date
- Empty state: friendly message when no results match

### Business Page
- Business name, category, area label
- Primary contact action: WhatsApp > phone > Instagram > website > map
- Secondary links: all other available channels
- Prefilled Spanish WhatsApp message with business name
- Google Maps link from CID
- "Is this your business? Claim or correct this page." CTA
- "Put this QR on your door" prompt (no payment yet)
- Back to directory link

---

## Build Steps

### Step 1: Normalize
- Read `pv_master_unified.csv`
- Parse all 34 columns
- Compute slug from business name + area
- Determine primary contact channel (priority: WhatsApp > phone > IG > website > map)
- Compute scores (contactability, visibility, data_completeness)
- Assign badges and intents

### Step 2: Generate JSON index
- Write `docs/paradisio_app/data/businesses.json` — full search index
- Write `docs/paradisio_app/data/metrics.json` — build stats
- Metric fields: total businesses, by category, by area, contact channel coverage, unclaimed count, generation timestamp

### Step 3: Generate business pages
- For each business: render `templates/business.html` with data
- Output to `docs/paradisio_app/businesses/<slug>.html`

### Step 4: Generate app entry
- Render `templates/index.html` with aggregate data
- Output to `docs/paradisio_app/index.html`

### Step 5: Copy static assets
- Copy `static/app.js` and `static/styles.css` to `docs/paradisio_app/static/`

---

## Contact Priority Logic

```
if business has WhatsApp number (normalized_phone or whatsapp field):
    primary = WhatsApp (wa.me link with prefilled message)
elif business has phone number:
    primary = Call (tel: link)
elif business has instagram_handle:
    primary = Instagram DM
elif business has website:
    primary = Website
elif business has google_maps_cid:
    primary = Open in Maps
else:
    primary = View on Map (no direct contact)
```

Prefilled WhatsApp message in Spanish:
```
Hola [Business Name], vi su página en Paradisio. ¿Están abiertos hoy? Me gustaría saber más sobre sus servicios. Gracias.
```

---

## Scoring Logic

### Contactability (0-100)
- Has WhatsApp: +40
- Has phone: +30
- Has Instagram: +15
- Has website: +10
- Has Facebook: +5

### Visibility (0-100)
- Has Google Maps CID: +35
- Has coordinates: +25
- Has Booking.com: +15
- Has TripAdvisor: +10
- Has email: +5
- Has verified Instagram (confidence = verified): +10

### Data Completeness (0-100)
- Name: +10
- Category: +10
- Area: +10
- Coordinates: +15
- Any phone: +10
- Any website: +10
- Any social: +10
- Description: +10
- Operating status: +5
- Verified date: +10

---

## Badge Generation

- "WhatsApp" — has valid WhatsApp number
- "Instagram" — has verified Instagram handle
- "Booking.com" — has Booking.com URL
- "Map Verified" — has Google Maps CID
- "Has Website" — has real website URL
- "Phone" — has phone number
- "Fully Online" — contactability + visibility > 140

---

## Claim / QR CTA (static v1)

Every business page includes a "Claim this page" link:
```
mailto:paradisio@example.com?subject=Claim%20[SLUG]&body=I%20own%20this%20business...
```

No auth. No payments. No database. The claim intent is captured by email. v2 adds a real claims system.

QR-ready URL pattern:
```
https://[domain]/paradisio_app/qr/<slug>.html
```
(v1: same as the business page URL, aliased)

---

## Definition of Done

- [ ] `python paradisio_app/build.py` succeeds with no errors
- [ ] `docs/paradisio_app/index.html` exists — loads and shows search/filter UI
- [ ] `docs/paradisio_app/data/businesses.json` contains ~750 records
- [ ] `docs/paradisio_app/data/metrics.json` has valid build stats
- [ ] `docs/paradisio_app/businesses/` contains one HTML file per business
- [ ] Client-side search works by category, area, text, and channel filter
- [ ] Every listing has at least one contact action based on available data
- [ ] WhatsApp prefilled message is generated per business in Spanish
- [ ] Claim page CTA exists on every business page
- [ ] Primary contact ranking logic is implemented correctly
- [ ] Generated pages open in browser and render without JS errors

---

## Post-MVP Roadmap (not building now)

- Claim flow (auth + database)
- QR code generation + tracking
- Analytics dashboard (Plausible or self-hosted)
- Affiliate sales portal
- Premium payment processing (SINPE/BTC)
- AI add-ons (WhatsApp auto-reply, IG content pack)
- Instagram capture engine
- Middleman booking concierge
- Print magazine generator
- Artist/creator profiles layer
- Discord/Reddit/blog community layer
