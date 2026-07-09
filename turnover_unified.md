# Paradisio — Unified Turnover Document

## 1. Project Identity

**Name:** Paradisio
**Repository:** `skinnerboxentertainment/mekatelyu`
**Live URL:** https://skinnerboxentertainment.github.io/mekatelyu/paradisio_app/
**Original source data repo:** `skinnerboxentertainment/puerto-viejo-business-discovery`
**Current master dataset:** `pv_master_unified.csv`
**Purpose:** A static, mobile-friendly business directory and community board for Puerto Viejo de Talamanca, Costa Rica and nearby areas. It aggregates local businesses within roughly 5 km of Puerto Viejo, enriches them with contact, social, and map data, and publishes a GitHub Pages app under `docs/paradisio_app/`.

Primary users:
- Visitors and residents looking for hotels, rentals, restaurants, shops, tours, services, and classifieds.
- Project maintainers and agents enriching a local business dataset without paid APIs or Google API keys.
- Business owners who may eventually claim, correct, or improve listings.

Current state:
- `pv_master_unified.csv` has **750 records and 34 columns**.
- The generated app has **750 business detail pages**, **15 classifieds listings**, a directory/map UI, and QR assets.
- Older docs and `AGENTS.md` may still reference `pv_within_5km_enriched_b.csv`, 450 records, or 615 records. Those references are stale for the current app unless the user explicitly asks about historical data.

**Reconciliation decisions**
- Difference: `TURNOVER.md` presents Paradisio as a broader “commercial and cultural operating system”; `turnoverCodex.md` frames it as a static directory/community board.
Decision: **COMPROMISE.** The current implementation is a static directory/community board, while the operating-system framing is the product vision.
- Difference: `AGENTS.md` says canonical file is `pv_within_5km_enriched_b.csv`; both turnover files identify `pv_master_unified.csv` as current.
Decision: **AGREE with both turnover files over AGENTS.md.** The current generated app and metrics are based on `pv_master_unified.csv`.
- Difference: `TURNOVER.md` says GitHub Pages auto-deploys from `docs/`; `turnoverCodex.md` says no automated rebuild/deploy pipeline is evident.
Decision: **COMPROMISE.** GitHub Pages serves/deploys committed `docs/` output, but rebuilding that output is local script-driven.

## 2. Data

### Master Dataset

Primary dataset:
- File: `pv_master_unified.csv`
- Records: 750
- Columns: 34

Columns:
`business_name`, `category`, `area`, `latitude`, `longitude`, `distance_km`, `geofilter`, `geofilter_reason`, `coordinate_source`, `phone`, `normalized_phone`, `website`, `instagram_handle`, `instagram_url`, `facebook_url`, `google_maps_cid`, `verified_date`, `operating_status`, `url`, `instagram_enrich_source`, `instagram_enrich_date`, `instagram_enrich_confidence`, `instagram_confidence`, `ig_verified`, `ig_verify_date`, `whatsapp`, `email`, `tiktok_url`, `youtube_url`, `twitter_url`, `other_social_urls`, `description_full`, `booking_url`, `tripadvisor_url`.

### Data Lineage

Current app data combines:
- Puerto Viejo Satellite crawl core records.
- SQLite cache mining.
- OSM cross-reference additions.
- Grid scan / screenshot / vision workflow additions.
- Google Maps CID discovery and enrichment.
- Website crawling for contact/social links.
- Instagram verification/enrichment.

Approximate source counts from `TURNOVER.md`:
- PV Satellite crawl: 450
- SQLite cache: 139
- OSM additions: 31
- Grid scan: 134

These overlap and are reconciled into the 750-row master.

### Generated Runtime Data

Generated under `docs/paradisio_app/data/`:
- `businesses.json`: 750 generated business records used by the frontend.
- `metrics.json`: homepage and app counts.
- `maps_enrich.json`: 674 successful Maps enrichment records.
- `maps_checkpoint.json`: Maps enrichment checkpoint state.

Current generated metrics:
- Total: 750
- Google Maps CID: 699
- WhatsApp: 614
- Phone: 611
- Coordinates: 606
- Instagram: 452
- Instagram verified: 223
- Facebook: 361
- Website: 191
- Booking.com: 171
- Email: 75

Maps enrichment coverage from `TURNOVER.md`:
- Star rating: 640
- Amenities: 215
- Check-in/out: 203
- Street address: 105

Categories:
- hotel: 169
- vacation_rental: 145
- Uncategorized: 131
- restaurant: 118
- services: 77
- shopping: 52
- tour_company: 31
- hostel: 22
- real_estate: 5

Areas:
- Puerto Viejo: 218
- Unknown: 131
- Cahuita: 94
- Cocles: 94
- Playa Negra: 70
- Playa Chiquita: 55
- Manzanillo: 24
- Punta Uva: 24
- Hone Creek: 20
- Bribri: 7
- Sixaola: 7
- Gandoca: 6

### Classifieds

Source:
- `paradisio_app/data/classifieds.json`

Current state:
- 15 active listings.
- Categories: `events`, `for-sale`, `gigs`, `jobs`, `lost-found`, `rideshare`, `rooms-for-rent`, `services`.
- Generated output: `docs/paradisio_app/classifieds/`
- 16 generated HTML pages including index.

### QR Assets

Output:
- `docs/paradisio_app/qr/`

Current state:
- `TURNOVER.md` says 750 PNGs plus redirect pages.
- `turnoverCodex.md` says 751 PNG files.

Decision: **AGREE with turnoverCodex.md for the observed file count, but describe intent as business QR assets plus index/redirect output.** The exact count should be verified with the filesystem when QR work matters.

Business pages conditionally show QR sections if `docs/paradisio_app/qr/{slug}.png` exists.

### Maps Enrichment

Script:
- `paradisio_app/maps_enrich.py`

Input:
- `docs/paradisio_app/data/businesses.json`

Output:
- `docs/paradisio_app/data/maps_enrich.json`

Checkpoint:
- `docs/paradisio_app/data/maps_checkpoint.json`

Current file:
- 674 records, all marked successful.

Method:
- Playwright opens `https://www.google.com/maps?cid={CID}`.
- Extracts visible text via DOM TreeWalker.
- Uses pacing, checkpointing, retries, and batch pauses.

Extracted fields include:
- Rating
- Phone
- Website
- Address / plus code
- Check-in
- Check-out
- Amenities
- Prices
- Nearby competitors
- Subcategory
- Raw text sample
- Text length

Known limitation:
- v1 retained only a text sample, not full visible text.
- Some useful details, especially descriptive street address and hours/open status, were missed or inconsistently parsed.
- Success means page extraction succeeded, not that every field is correct.

Planned v2 CID re-scan:
- Methodology: `docs/cid_v2_extraction_methodology.md`
- Sample analysis: `docs/paradisio_app/data/cid_v2_samples/analysis_report.txt`
- Goal: full visible text capture, category-aware parsing, less data loss.
- Estimated runtime: 4-6 hours with pacing.
- Some pages may require authenticated Chrome rendering; this conflicts with “no Google login” unless explicitly approved.

**Reconciliation decisions**
- Difference: `TURNOVER.md` says CID enrichment captured plus code but not street address; `turnoverCodex.md` says extracted fields include address.
Decision: **COMPROMISE.** The schema/output includes address-like fields, but descriptive street address coverage is poor and was missed in many cases.
- Difference: `TURNOVER.md` recommends authenticated Chrome profile for v2; `AGENTS.md` says no Google login.
Decision: **COMPROMISE.** Direct CID scraping without login remains the default. Authenticated Chrome should only be used if the user explicitly overrides the no-login constraint.
- Difference: QR count 750 vs 751.
Decision: **AGREE with turnoverCodex.md as likely observed, but treat count as needing verification.**

## 3. Architecture

Paradisio is a static site generator plus generated static app. There is no backend server, runtime database, or frontend framework.

### Stack

- Generator: pure Python stdlib in `paradisio_app/build.py`
- Frontend: vanilla HTML/CSS/JS
- Maps: Leaflet.js + OpenStreetMap tiles + markercluster CDN
- QR codes: Python `qrcode` library with Pillow PNG output
- Analytics: GoatCounter
- Hosting: GitHub Pages via committed `docs/`
- Agent bridge: `codex_bridge.py` and `CODEX_ENDPOINT/`

### Source App

- `paradisio_app/build.py`: main static generator.
- `paradisio_app/static/app.js`: directory, search, filters, map behavior.
- `paradisio_app/static/classifieds.js`: classifieds search behavior.
- `paradisio_app/static/tokens.css`: design tokens.
- `paradisio_app/static/styles.css`: app styles.
- `paradisio_app/data/classifieds.json`: source classifieds listings.
- `paradisio_app/maps_enrich.py`: Maps enrichment crawler.
- `paradisio_app/generate_qr.py`: QR generation.
- `paradisio_app/capture_mobile.py`: screenshot/QA helper.

### Generated Output

- `docs/paradisio_app/index.html`: main directory app.
- `docs/paradisio_app/businesses/*.html`: one business page per record.
- `docs/paradisio_app/classifieds/*.html`: classifieds board and detail pages.
- `docs/paradisio_app/static/*`: copied JS/CSS.
- `docs/paradisio_app/data/*.json`: generated app data and enrichment files.
- `docs/paradisio_app/qr/*.png`: QR assets.
- `docs/paradisio_app/screenshots/`: Playwright captures.

GitHub Pages root:
- `docs/.nojekyll`
- `docs/index.html`
- `docs/directory.html`
- `docs/gapmap.html`
- `docs/report.html`
- `docs/audit.html`
- `docs/paradisio_app/`

### Generator Flow

`paradisio_app/build.py`:
1. Reads `pv_master_unified.csv`.
2. Reads `docs/paradisio_app/data/maps_enrich.json` if present.
3. Reads `paradisio_app/data/classifieds.json`.
4. Builds normalized business objects:
- cleaned display name
- slug
- deterministic ID
- contact channels
- primary contact
- secondary links
- scores
- badges
- intents
- Maps enrichment fields
5. Writes `businesses.json` and `metrics.json`.
6. Generates 750 business detail pages.
7. Generates directory index.
8. Generates classifieds pages.
9. Copies static JS/CSS into generated docs output.

### Frontend Behavior

`app.js`:
- Uses embedded/generated business, category, and area data.
- Provides text search across name, category, area, description, and badges.
- Filters by category, area, and contact channel.
- Sorts by name, contactability, or completeness.
- Renders paginated list cards, 50 per page.
- Supports “load more.”
- Supports category shortcut tiles.
- Supports list/map toggle.
- Uses Leaflet plus markercluster from CDN.
- Filters map markers based on current filters.

### Build Commands

```powershell
python paradisio_app/build.py
python paradisio_app/generate_qr.py
python paradisio_app/maps_enrich.py
python paradisio_app/capture_mobile.py
```

Deploy flow:
```powershell
python paradisio_app/build.py
git add -A
git commit -m "rebuild"
git push mekatelyu master
```

Local preview:
```powershell
python -m http.server 8080 --directory docs/paradisio_app
```

### CODEX_ENDPOINT / Agent Bridge

Purpose:
- File-based IPC hub enabling OpenCode or another orchestrator to delegate bounded tasks to Codex CLI.

v1 one-shot:
```powershell
python codex_bridge.py "task description" --json
```

v2 session:
```powershell
python CODEX_ENDPOINT\session_orchestrator.py create --title "Task" --description "Desc"
python CODEX_ENDPOINT\session_orchestrator.py next --session-id <id> --message "instruction"
python CODEX_ENDPOINT\session_orchestrator.py status --session-id <id>
python CODEX_ENDPOINT\session_orchestrator.py retry --session-id <id>
```

Session details:
- Sessions live in `CODEX_ENDPOINT/sessions/`.
- Artifacts live under `CODEX_ENDPOINT/tasks/<session_id>/artifacts/`.
- Responses/audit logs live under `CODEX_ENDPOINT/responses/bridge_*.json`.
- Session files are schema-validated, append-only, atomically written, lock-protected, and state-machine controlled.

**Reconciliation decisions**
- Difference: `TURNOVER.md` organizes CODEX_ENDPOINT as its own major section; requested unified structure does not.
Decision: **COMPROMISE.** Include CODEX_ENDPOINT under Architecture, Agent Onboarding, and Troubleshooting.
- Difference: `TURNOVER.md` lists line counts for files; `turnoverCodex.md` avoids relying on exact line counts.
Decision: **AGREE with turnoverCodex.md.** Line counts drift quickly and belong in a manifest only as rough hints if used.

## 4. Features (Built)

Built and currently represented in the app/codebase:

- Static GitHub Pages-ready app under `docs/paradisio_app/`.
- 750 generated business pages.
- Business detail pages with:
- contact links
- badges
- map block when coordinates exist
- QR block when QR asset exists
- ratings where Maps enrichment exists
- amenities/prices/check-in/check-out where available
- claim/correction mailto link
- mobile sticky CTA
- Search/filter/sort/paginated directory.
- Category and area filters.
- Contact-channel filters.
- Text search.
- “Load more” pagination.
- Category shortcut tiles.
- Leaflet map with marker clustering and filtered markers.
- List/map toggle on homepage.
- Mobile-first responsive CSS.
- Sticky mobile CTA bar.
- Design token system via CSS custom properties.
- Display name cleanup that strips many location suffixes.
- Contact labels using human-readable states such as Verified, Strong, Partial, Limited.
- Scores for contactability, visibility, and completeness.
- Primary contact routing priority:
- WhatsApp
- phone
- Instagram
- website
- Google Maps
- coordinates
- Secondary links for:
- call
- Instagram
- Facebook
- website
- Booking.com
- TripAdvisor
- Google Maps
- Subcategory/cuisine extraction from Maps/business names via helper scripts.
- QR code PNGs, redirect pages, and print gallery.
- QR preview/download link on business pages.
- Classifieds board:
- 15 seed listings
- 8 categories
- search
- category navigation/grouping
- detail pages
- post-by-email CTA
- GoatCounter analytics script.
- Maps CID enrichment pipeline with checkpointing.
- Codex delegation bridge with v1 one-shot and v2 sessions.
- Supporting enrichment scripts for OSM, geofiltering, Instagram, websites, stealth Maps search, reports, and audits.
- Bilingual navigation labels are partially prepared in code, though English is what currently renders.

**Reconciliation decisions**
- Difference: `TURNOVER.md` says “Bilingual nav” built; `turnoverCodex.md` says Spanish labels exist but only English outputs.
Decision: **AGREE with turnoverCodex.md.** Bilingual readiness exists, but full bilingual UI is not shipped.
- Difference: `TURNOVER.md` says contact labels replaced numeric scores; `turnoverCodex.md` says scores still exist.
Decision: **COMPROMISE.** Human-readable labels are displayed in parts of the UI, while underlying/generated scores still exist.
- Difference: `TURNOVER.md` presents trust signals as built; `turnoverCodex.md` flags that some trust badges may render unconditionally.
Decision: **COMPROMISE.** Trust signal UI exists, but conditional correctness needs review.

## 5. Features (Planned)

Planned, partial, or not production-ready:

- Classifieds posting flow:
- Web3Forms + WhatsApp-first submission form was a current priority in `TURNOVER.md`.
- Current implementation is only a mailto-style posting CTA.
- Real business claim workflow:
- Current claim/correction flow uses placeholder email.
- Owner verification is not implemented.
- Data correction workflow:
- No backend persistence or moderation queue.
- Premium listings:
- Potential $100/$200 tiers.
- Needs payment method such as SINPE, analytics, featured placement, and fulfillment rules.
- QR affiliate network:
- Needs tracking, attribution, and payout/commission operations.
- AI service upsells:
- Would require OpenAI/API integration and productized service flows.
- Middleman/concierge fees:
- Needs operational handling, disputes, and clear terms.
- Instagram capture engine:
- Needs scraping/enrichment pipeline and analytics.
- Must avoid scraping private or prohibited content.
- Quarterly print magazine:
- Needs layout, print vendor, ad sales, and distribution.
- Creative layer:
- Artists, musicians, creators, cultural profiles.
- Community layer:
- Reddit, Discord, or other moderated community channels.
- Town API:
- Query wrapper around existing generated JSON.
- WhatsApp concierge:
- Could use WhatsApp Business API or a web launcher.
- Refreshable scanner for other towns:
- Port the acquisition/enrichment workflow to a second location.
- Puerto Viejo Economic Tarot:
- Static microsite with archetype cards.
- v2 CID re-scan:
- Full text capture.
- Category-aware parsing.
- Better address/hours/status extraction.
- Presentation layer phase 2:
- Two-column desktop layout.
- More accurate trust signals.
- Photography strategy.
- Expanded enrichment:
- Airbnb
- TripAdvisor
- Booking.com
- TikTok/Twitter
- Facebook-by-phone
- WhatsApp verification
- Missing CID resolution

**Reconciliation decisions**
- Difference: `TURNOVER.md` lists commercial/product vision ideas; `turnoverCodex.md` emphasizes operational gaps.
Decision: **COMPROMISE.** Keep both: vision ideas are planned opportunities, operational gaps are prerequisites before public promotion.
- Difference: `TURNOVER.md` says photography should be owner-submitted after claim flow; `turnoverCodex.md` does not emphasize this.
Decision: **AGREE with TURNOVER.md.** It is consistent with the no-Instagram-scraping posture and production hardening.

## 6. Design & Key Decisions

### Design Direction

Documented in:
- `docs/paradisio_direction_unified.md`

Direction:
- “Polished Local Warmth” — warm minimalism as mood, polished local board as product.

Tagline:
- “Find Puerto Viejo businesses with confidence.”

Palette:
- Sand backgrounds.
- Jungle green identity.
- Coral CTAs.
- Reef/teal accent for interactive elements.
- Sun yellow accent.

Typography:
- System font stack.
- No Google Fonts dependency.

Map approach:
- List/search is default.
- Map is a prominent toggle, not the default view.

Photography:
- Category-specific CSS placeholders for now.
- No Instagram scraping for display photography.
- Owner-submitted images after claim flow.

Spanish:
- Design for bilingual support now.
- Full translation ships later.

### Product/Technical Decisions

| Decision | Rationale |
|---|---|
| Static site, no backend | Zero infrastructure cost, GitHub Pages hosting, simple Git-based deployment |
| Vanilla JS, no framework | Small bundle, no build step, maximum compatibility |
| CSV as source of truth | Portable, diffable, version-controlled, editable in common tools |
| Opt-out listing model | Every business is listed by default, unlike standard opt-in directories |
| Warm minimalism | Utility-first local product, not luxury travel marketing |
| GoatCounter analytics | Privacy-friendly, open source, low friction |
| Leaflet over Google Maps API | No API key, billing, or usage limits |
| WhatsApp as primary CTA | Matches local business communication patterns in Costa Rica |
| QR codes | Connects physical town presence to digital pages |
| Category shortcuts over hero carousel | Users arrive with intent; utility beats inspiration |
| Generated docs output | GitHub Pages can serve static files directly |
| Source-first edits | Generated files are overwritten by `build.py`; edit source/generator unless intentionally hotfixing |

**Reconciliation decisions**
- Difference: `TURNOVER.md` gives stronger brand/design framing; `turnoverCodex.md` gives lower-level implementation details.
Decision: **COMPROMISE.** Use the brand direction as product guidance and the implementation details as current state.
- Difference: `TURNOVER.md` says GitHub Pages auto-deploys on push; `turnoverCodex.md` cautions no automated rebuild.
Decision: **COMPROMISE.** Pages deployment is automatic from committed `docs/`, but generation is manual.

## 7. Risks & Issues

### Data Risks

- `AGENTS.md` still names `pv_within_5km_enriched_b.csv` with 450 records as canonical. For the current app, use `pv_master_unified.csv`.
- Several planning docs refer to stale 450 or 615 record counts.
- `businesses.json` uses cleaned display names, but `primary_contact.url` text may still include raw CSV business names because `get_primary_contact(row)` can run before name substitution.
- Some records have CIDs but no coordinates.
- 131 records are Uncategorized and area Unknown.
- Instagram fields can disagree or be blank:
- `instagram_confidence`
- `instagram_enrich_confidence`
- `ig_verified`
- `has_whatsapp()` may treat normalized phone as WhatsApp when `whatsapp` is blank, so WhatsApp count may mean “phone usable in wa.me format,” not verified WhatsApp.
- Maps enrichment contains Spanish UI noise and repeated price strings.
- `maps_enrich.json` success indicates extraction succeeded, not field-level accuracy.
- There is a gap between 699 CIDs and 674 Maps enrichment records.

### Frontend/App Risks

- Business detail pages may render “Google Maps verified” and “Instagram verified” trust badges regardless of business-specific verification status. Make these conditional.
- `nav_html()` defines Spanish labels but currently outputs English labels only.
- Category shortcut mapping is lossy:
- “stay” maps only to `hotel`, not hostel/vacation rentals.
- “nightlife” maps to restaurant.
- “transport” maps to services.
- Leaflet and markercluster depend on CDNs; offline/CDN failure breaks maps.
- HTML is assembled with f-strings. Generated detail pages should centrally escape interpolated data before production hardening.
- Generated pages include `data-plausible-*` attributes while analytics script is GoatCounter; event tracking may not be wired as intended.
- Placeholder contact `paradisio@example.com` appears in claim/post flows and should be replaced before public promotion.

### Operational Risks

- Google Maps scraping is fragile and subject to anti-automation/CAPTCHA.
- Existing docs emphasize pacing and direct CID loads.
- Browser automation requires `danger-full-access` on this Windows machine.
- No paid APIs or commercial datasets are allowed.
- No Google login/API key by default.
- Do not modify master datasets unless explicitly instructed.
- Do not recursively delegate from Codex to OpenCode.
- Generated files under `docs/paradisio_app/` can be overwritten by `build.py`.
- `CODEX_ENDPOINT/responses/` and task artifacts contain many historical logs, some large. Use them for delegation history only.
- `screenshots/` contains many large PNG captures; useful evidence, but bulky.
- No integrated test suite for generator/frontend is evident.
- No backend persistence exists for claims, corrections, classifieds, ads, or analytics beyond GoatCounter.

**Reconciliation decisions**
- Difference: `TURNOVER.md` focuses on known CODEX issues and Maps v2; `turnoverCodex.md` gives broader data/frontend/ops risks.
Decision: **AGREE with turnoverCodex.md for risk breadth, while retaining TURNOVER.md’s specific CODEX and Maps notes.**
- Difference: `TURNOVER.md` says authenticated Chrome may be needed; project safety says no Google login.
Decision: **COMPROMISE.** Treat authenticated scraping as blocked unless the user explicitly approves it.

## 8. Agent Onboarding

### Fast Path

1. Read `AGENTS.md` for project rules:
- no paid APIs
- no Google API key
- no Google login unless explicitly approved
- no recursive delegation
- do not modify master datasets unless instructed
- v1/v2 Codex bridge protocols
2. Treat `pv_master_unified.csv` as the current app master.
3. Read `README.md` for public-facing context, but verify counts against current data.
4. Read `paradisio_app/build.py` end to end.
5. Read frontend source:
- `paradisio_app/static/app.js`
- `paradisio_app/static/classifieds.js`
- `paradisio_app/static/tokens.css`
- `paradisio_app/static/styles.css`
6. Inspect generated runtime data:
- `docs/paradisio_app/data/businesses.json`
- `docs/paradisio_app/data/metrics.json`
- `docs/paradisio_app/data/maps_enrich.json`
7. Inspect classifieds source:
- `paradisio_app/data/classifieds.json`
8. Inspect QR output only by count/sample unless QR work is required.
9. For enrichment tasks, read:
- `paradisio_app/maps_enrich.py`
- `stealth_search.py`
- `website_crawl.py`
- `crossref_osm.py`
- `geofilter.py`
- `pvscraper/`
10. For delegation tasks, read:
- `codex_bridge.py`
- `CODEX_ENDPOINT/README.md`
- `CODEX_ENDPOINT/session_orchestrator.py`
- `CODEX_ENDPOINT/session_lib.py`
- `CODEX_ENDPOINT/session_schema.py`

### Initial Context for Any Agent

This is Paradisio, a static web app for Puerto Viejo, Costa Rica business discovery. It currently uses `pv_master_unified.csv` with 750 businesses and 34 data columns. The app is generated by `paradisio_app/build.py` into `docs/paradisio_app/` and served by GitHub Pages at `https://skinnerboxentertainment.github.io/mekatelyu/paradisio_app/`.

All runtime HTML/CSS/JS is static and vanilla. There is no backend. Maps use Leaflet/OpenStreetMap. Analytics uses GoatCounter. QR codes are generated as PNG assets.

Use `pv_master_unified.csv` as current source of truth unless the user explicitly asks about historical files. Do not edit generated `docs/paradisio_app/*` manually unless the task is specifically about generated output; edit source files and rebuild.

### Common Commands

Rebuild static app:
```powershell
python paradisio_app/build.py
```

Generate QR:
```powershell
python paradisio_app/generate_qr.py
```

Run Maps enrichment:
```powershell
python paradisio_app/maps_enrich.py
```

Create v2 Codex session:
```powershell
python CODEX_ENDPOINT\session_orchestrator.py create --title "My Task" --description "Do X"
```

Advance v2 session:
```powershell
python CODEX_ENDPOINT\session_orchestrator.py next --session-id <id> --message "Now change Y"
```

One-shot delegate:
```powershell
python codex_bridge.py "task" --json
```

### Working Rules

- Never rely on generated prose as canonical when code/data disagree.
- Do not edit `docs/paradisio_app/*` manually unless explicitly required.
- Before changing data, confirm whether the user means `pv_master_unified.csv` or older `pv_within_5km_enriched_b.csv`.
- Preserve CSV schema unless asked to migrate it.
- Add new enrichment outputs to assigned files first; merge into master only with explicit instruction.
- Validate app changes by rebuilding and checking generated counts/pages.
- Be cautious with Google/Maps automation.
- Respect pacing.
- Prefer direct CID loads where possible.
- Replace placeholder public contact values before promoting claim/classifieds workflows.

**Reconciliation decisions**
- Difference: `TURNOVER.md` says key files to read include `TURNOVER.md`; this new document supersedes both turnover files.
Decision: **COMPROMISE.** New agents should read this unified document, then `AGENTS.md`, then current code/data.
- Difference: `turnoverCodex.md` says inspect README early; `TURNOVER.md` emphasizes design/status docs.
Decision: **COMPROMISE.** Read README for public framing, design/status docs for product intent, and code/data for truth.

## 9. Troubleshooting

### GitHub Pages Builds Stuck in “queued”

Delete and recreate GitHub Pages:

```powershell
gh api repos/skinnerboxentertainment/mekatelyu/pages -X DELETE
# Wait 30 seconds
Set-Content -Path "$env:TEMP\pages.json" -Value '{"source":{"branch":"master","path":"/docs"}}'
gh api repos/skinnerboxentertainment/mekatelyu/pages -X POST --input "$env:TEMP\pages.json"
```

### Unicode Encoding Errors in `session_orchestrator.py`

Known issue:
- On Windows cp1252 terminals, `session_orchestrator.py` can crash on `print(json.dumps(output))` when Codex output contains Unicode characters such as arrows or emoji.
- The session may already be updated by the bridge before the print crash.

Workarounds:
- Use one-shot calls for tasks that do not need iteration:
```powershell
python codex_bridge.py "task" --json
```

- Read the `.bak` session file after a crash:
```powershell
python -c "import json; d=json.load(open('CODEX_ENDPOINT/sessions/<id>.bak')); print(d['conversation'][-1]['message'])"
```

### Codex Artifact Validation Errors

Known issue:
- Codex sometimes writes plain strings to `artifacts[]` instead of objects like `{"path": "..."}`, causing Pydantic validation errors.

Possible fixes:
- Normalize artifacts to objects.
- Add a `"response"` type to the relevant `EntryType` enum if appropriate.
- Harden schema parsing in the bridge/session layer.

### Maps Enrichment Page Too Sparse

Symptom:
- Some businesses return fewer than about 50 visible text lines.

Likely cause:
- Google Maps served limited content, anti-automation behavior, or incomplete rendering.

Default response:
- Retry later with pacing.
- Use direct CID URLs.
- Preserve raw/full visible text in future v2 runs.

Escalated option:
- Authenticated Chrome profile via CDP pattern in `stealth_search.py`, but only if the user explicitly approves overriding the no-login default.

### Generated Output Does Not Reflect Changes

Likely cause:
- Edited generated files instead of source files.
- Did not rerun `build.py`.
- QR assets need separate generation.

Fix:
```powershell
python paradisio_app/build.py
python paradisio_app/generate_qr.py
```

### Placeholder Public Contact

Known issue:
- `paradisio@example.com` appears in claim and classifieds flows.

Fix:
- Replace with real project contact before production promotion.

### Maps Do Not Load

Likely causes:
- Leaflet CDN failure.
- Markercluster CDN failure.
- Network/offline issue.
- Missing coordinates for specific businesses.

Fix:
- Check browser console.
- Confirm CDN availability.
- Confirm generated records include latitude/longitude.

**Reconciliation decisions**
- Difference: `TURNOVER.md` includes specific GitHub Pages and CODEX troubleshooting; `turnoverCodex.md` includes broader app/data cautions.
Decision: **COMPROMISE.** Keep specific troubleshooting procedures and add operational caveats from `turnoverCodex.md`.

## 10. File Manifest

### Core Source Files

| File | Purpose |
|---|---|
| `pv_master_unified.csv` | Current master dataset for the app, 750 rows, 34 columns |
| `paradisio_app/build.py` | Main static app generator |
| `paradisio_app/generate_qr.py` | QR code PNG and redirect page generator |
| `paradisio_app/maps_enrich.py` | Google Maps CID enrichment crawler |
| `paradisio_app/maps_enrich_report.py` | Enrichment summary reporter |
| `paradisio_app/capture_mobile.py` | Playwright screenshot capture |
| `paradisio_app/data/classifieds.json` | Source classifieds listings |
| `paradisio_app/static/tokens.css` | Design system tokens |
| `paradisio_app/static/styles.css` | Component/page styles |
| `paradisio_app/static/app.js` | Directory, search, filters, and map frontend behavior |
| `paradisio_app/static/classifieds.js` | Classifieds search behavior |
| `paradisio_app/templates/` | Reserved template directory |

### Generated App Output

| File/Directory | Purpose |
|---|---|
| `docs/paradisio_app/index.html` | Main app entry point |
| `docs/paradisio_app/businesses/` | Generated business detail pages |
| `docs/paradisio_app/classifieds/` | Generated classifieds board and detail pages |
| `docs/paradisio_app/qr/` | QR PNGs, redirect pages, print gallery |
| `docs/paradisio_app/data/businesses.json` | Frontend business search index |
| `docs/paradisio_app/data/metrics.json` | Generated app metrics |
| `docs/paradisio_app/data/maps_enrich.json` | Maps enrichment results |
| `docs/paradisio_app/data/maps_checkpoint.json` | Maps enrichment resume checkpoint |
| `docs/paradisio_app/static/` | Copied CSS/JS assets |
| `docs/paradisio_app/screenshots/` | Playwright captures |

### GitHub Pages Root

| File | Purpose |
|---|---|
| `docs/.nojekyll` | Disables Jekyll processing |
| `docs/index.html` | Landing page |
| `docs/directory.html` | Classic interactive directory |
| `docs/gapmap.html` | Grid-based gap scanner |
| `docs/report.html` | Analytical report |
| `docs/audit.html` | Data audit dashboard |
| `docs/paradisio_app/` | Main live app |

### Agent / Delegation Files

| File/Directory | Purpose |
|---|---|
| `AGENTS.md` | Agent operation protocols; contains some stale data-file references |
| `codex_bridge.py` | Thin wrapper around Codex CLI |
| `CODEX_ENDPOINT/` | File-based IPC hub |
| `CODEX_ENDPOINT/session_orchestrator.py` | v2 session CLI |
| `CODEX_ENDPOINT/session_lib.py` | Session helpers |
| `CODEX_ENDPOINT/session_schema.py` | Session schema/validation |
| `CODEX_ENDPOINT/sessions/` | Session state files |
| `CODEX_ENDPOINT/tasks/` | Task artifacts |
| `CODEX_ENDPOINT/responses/` | Bridge responses/audit logs |

### Planning / Reference Docs

| File | Purpose |
|---|---|
| `docs/paradisio_direction_unified.md` | Resolved design direction |
| `docs/paradisio_status_and_ideas.md` | Feature inventory and idea list |
| `docs/paradisio_roadmap.md` | Feasibility/ROI analysis |
| `docs/cid_enrichment_strategy_report.md` | CID enrichment strategy |
| `docs/cid_v2_extraction_methodology.md` | v2 CID methodology |
| `docs/request_classifieds_posting.md` | Classifieds posting research |
| `docs/paradisio_presentation_considerations.md` | Presentation/design considerations |
| `docs/paradisio_build_spec.md` | Original build spec |
| `docs/paradisio_vision.md` | Original vision document |
| `README.md` | Public-facing repo description |

### One-Off / Analysis Scripts

These are not part of the build pipeline unless explicitly reused:

| File | Purpose |
|---|---|
| `_add_cuisine.py` | Add/extract cuisine or subcategory metadata |
| `_extract_cuisine.py` | Cuisine extraction |
| `_cid_postmortem.py` | CID enrichment analysis |
| `_cid_v2_batch_sample.py` | v2 CID sampling |
| `_analyze_sample.py` | Cross-category field pattern analysis |
| `_best_restaurant.py` | Data quality check |
| `_check_cuisine.py` | Cuisine check |
| `_inspect_db.py` | PVS SQLite exploration |
| `_check_reviews.py` | Review inspection |
| `_check_desc.py` | Description inspection |
| `_maps_inspect.py` | Maps page investigation |
| `_httpx_test.py` | HTTP/site investigation |
| `_check_pages.py` | GitHub Pages status check |
| `_check_pages2.py` | GitHub Pages status check |
| `_check_session.py` | CODEX session debugging |
| `_check_bak.py` | CODEX backup/debugging |
| `_get_debate.py` | CODEX session/debug artifact helper |
| `_analyze.py` | Misc data inspection |
| `_check_enrich.py` | Enrichment inspection |
| `_check_qr.py` | QR inspection |

**Final reconciliation note:** This unified document treats `turnoverCodex.md` as stronger on observed implementation details and risks, and `TURNOVER.md` as stronger on product vision, design direction, planned work, and specific operational procedures. Where they differ, the current code/data state wins over older prose.