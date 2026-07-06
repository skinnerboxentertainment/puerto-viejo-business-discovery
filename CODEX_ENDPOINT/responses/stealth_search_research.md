# Stealth Google Search Pipeline Research

## 1. Executive summary

The recommended approach is not a high-speed scraper. For 615 records on a consumer Windows machine, the most realistic free pipeline is a slow, resumable, human-supervised Chrome workflow using a real installed Chrome profile, conservative pacing, session caps, and extraction from Google Maps pages rather than raw Google Search HTML. Use Google Search only as a resolver from business name to Maps place URL, then extract coordinates, place ID tokens, phone, website, social links, and booking links from the Maps page and page data. Avoid CAPTCHA by pacing, batching, and stopping early when friction appears; do not try to defeat CAPTCHA mechanically. Expect 20-40 reliable lookups per day per residential IP/profile if using Google Search heavily, with higher throughput only when using cached prior URLs, OSM/PVS/Booking/Facebook/Instagram cross-links, or non-Google discovery first.

## 2. Anti-fingerprinting techniques

### What makes Playwright/headless Chrome detectable

Playwright and bundled Chromium can be detected through several signals:

- Browser automation flags such as `navigator.webdriver`.
- Launch arguments and missing browser features that differ from a normal user session.
- Fresh, empty browser profiles with no browsing history, cookies, cache, extensions, saved permissions, or realistic site storage.
- Repetitive navigation patterns: same URL shape, same dwell time, no mouse/keyboard variation, no scroll behavior, immediate DOM extraction, and fixed inter-request delays.
- Headless rendering differences, GPU/WebGL differences, font lists, media devices, canvas/audio fingerprints, timezone/language mismatches, and screen metrics.
- Network behavior: one IP doing repeated similar Google searches with no broader browsing context.

The important point is that browser fingerprint is only one part of the model. Even a perfect browser fingerprint can be rate-limited if the behavioral pattern is obviously automated.

### Canvas/WebGL/audio mitigations

Fingerprint randomization plugins are not a complete solution. They can reduce obvious static fingerprints, but they often create inconsistent fingerprints across APIs. Inconsistency is itself suspicious: for example, a Windows Chrome user agent with unusual fonts, mismatched GPU strings, odd canvas noise, or changing WebGL values inside one session.

Practical mitigations that are worth using:

- Use real installed Chrome or Edge, not Playwright's bundled Chromium, for production runs.
- Use a persistent browser profile dedicated to this project.
- Keep locale, timezone, language, geolocation, and viewport internally consistent: Costa Rica or US English is plausible, but avoid arbitrary mixes.
- Keep GPU acceleration enabled unless it causes rendering failures.
- Use normal headed mode.
- Use a stable viewport close to a common desktop size, with occasional small variation between sessions.
- Avoid aggressive fingerprint spoofing unless a specific detection problem is observed.

Mitigations that are usually not worth relying on:

- Random canvas/audio/WebGL noise as a primary defense.
- Rotating user agents while keeping the same profile.
- Launching many fresh contexts with no cookies.
- Pretending to be mobile unless the workflow is built around normal mobile behavior.

### Real Chrome profile vs Chrome for Testing

A real installed Chrome profile is materially better than Chrome for Testing or bundled Chromium because it looks and behaves more like an actual user environment. It has normal update cadence, a normal executable path, persistent site storage, real GPU behavior, installed fonts, and human browsing residue.

It is not sufficient by itself. A real Chrome profile can still get CAPTCHA if it performs too many similar Google searches. The observed result, where headed Playwright worked briefly and then hit CAPTCHA, is consistent with behavioral/rate detection rather than only a bad browser binary.

### Login status

Do not log in with a valuable personal Google account for mass scraping. Login can increase trust for normal use, but it also links all activity to the account and may cause account-level friction or policy issues. For this project, the better default is a persistent non-logged-in Chrome profile with cookies and consent state preserved.

If login is tested, use a dedicated low-value account and treat it as a pilot only. Do not scale around it.

## 3. Recommended search strategy

### Core principle

Avoid CAPTCHAs rather than trying to solve them. CAPTCHA is a stop signal, not a challenge to automate around. The pipeline should preserve partial progress and pause automatically at the first sign of friction.

### Batch plan

Use a staged resolver:

1. Pre-normalize candidate names.
2. Query local/master data first for existing CID, Maps URL, coordinates, phone, website, and social links.
3. Use non-Google sources for obvious enrichment before touching Google Search:
   - Existing PVS cache and `pvscraper_full.db`.
   - OSM fields and website/social tags.
   - Existing grid discovery outputs.
   - Direct website pages for Instagram/Facebook/WhatsApp/Booking links.
   - Booking.com or Facebook indexed URLs already present in current data.
4. Search Google only for unresolved records.
5. Use Maps page extraction after the search result resolves to a listing.
6. Write one JSONL/CSV checkpoint row per attempted business immediately after each attempt.

### Pacing

Recommended initial pacing for Google Search:

- Delay before search: 45-120 seconds, randomized.
- Dwell on results page before clicking: 8-25 seconds.
- Dwell on Maps listing before extraction: 15-45 seconds.
- Scroll/pan lightly on Maps page only when needed to reveal fields.
- Maximum searches per micro-session: 8-12.
- Rest between micro-sessions: 30-90 minutes.
- Maximum searches per day from one IP/profile: start with 25-40; only increase if a multi-day pilot shows no CAPTCHA.

Avoid fixed delays such as exactly 30 seconds. Use randomized delays with broad ranges and stop conditions. A realistic controller should adapt:

- If pages load normally and no friction appears, continue until the micro-session cap.
- If Google shows "unusual traffic", CAPTCHA, blank SERP, redirect loops, or repeated consent/login prompts, stop the session immediately.
- If result quality drops, increase delay and reduce the next batch size.

### Session rotation

Use one dedicated persistent profile, not many synthetic profiles. Rotating fingerprints is less useful than preserving a credible long-lived browser state.

Suggested state layout:

- `profiles/chrome_pv_google/` persistent user data directory.
- `checkpoints/search_attempts.jsonl` append-only attempts.
- `checkpoints/resolved_places.jsonl` successful resolved listing records.
- `checkpoints/failures.csv` unresolved names with reason codes.
- `logs/session_YYYYMMDD_HHMM.json` for runtime telemetry.

Only rotate profile if the current profile is persistently blocked for days. If rotating, also reduce volume; a new profile plus same IP and same behavior is not a clean reset.

### IP strategy

Google tracks a combination of IP, browser/profile cookies, account status, device/browser fingerprint, query pattern, and behavior. Residential IP is better than data center IP. VPNs and public proxies often make CAPTCHA more likely.

For a free, consumer-machine workflow:

- Prefer the normal residential connection.
- Do not use cheap/free proxy lists.
- If blocked, stop and wait. A router reconnect may or may not change IP, but IP rotation alone will not fix bad behavior.
- Do not parallelize Google Search across browser instances from the same IP.

### CAPTCHA recovery

Recommended procedure:

1. Detect CAPTCHA or "unusual traffic" page.
2. Save screenshot, current URL, business name, and session log.
3. Stop the automated run immediately.
4. Do not keep retrying the same query.
5. Wait at least 12-24 hours before another Google Search batch.
6. On next run, cut batch size by 50% and double the median delay.
7. Optionally allow manual CAPTCHA solving only if the browser is already open and the operator chooses to continue. Still pause after solving; do not immediately resume at scale.

No paid CAPTCHA-solving service fits the "no paid APIs" constraint. Free CAPTCHA solvers are unreliable, often violate service expectations, and add security risk. The operational strategy should be avoidance.

## 4. Extraction method

### Search result to Maps listing

For each business, generate a small set of query variants and stop after the first confident listing:

- `"Business Name" "Puerto Viejo"`
- `"Business Name" "Puerto Viejo de Talamanca"`
- `"Business Name" "Limón" Costa Rica`
- `Business Name site:google.com/maps Puerto Viejo`

Do not run all variants by default. Try the most specific query first; only use fallback variants when the result is missing or ambiguous.

On the search result page, prefer links in this order:

1. Knowledge panel or local pack link pointing to a single `google.com/maps/place/...` listing.
2. Organic result with `google.com/maps/place/...`.
3. `maps.google.com/?cid=...` or `google.com/maps?cid=...`.
4. Search-result Maps tab link only as a fallback, because it often points to a Maps search page rather than a resolved place.

Reject links that point to generic Maps searches unless the subsequent Maps page clearly resolves to one place.

### CID extraction

A Maps link does not always contain a decimal CID. In current Google Maps URLs, the listing is often represented by:

- Hex feature ID pair in the URL, e.g. `!1s0x...:0x...`.
- Place URL slug and coordinates.
- `cid=` or `ludocid=` in some search/redirect URLs.
- Internal script data containing CID-like or place identifiers.

Extraction order:

1. Parse `cid=` and `ludocid=` from URLs.
2. Parse `!1s0xHEX:0xHEX` from Maps place URLs. The second hex value is commonly convertible to decimal CID. Example: `0x3deab4612af37052` converts to decimal `4462858310644424786`.
3. Parse coordinates from:
   - `@lat,lon,zoom`
   - `!3dLAT!4dLON`
   - page embedded data if URL coordinates differ from place coordinates.
4. Search page HTML and script payloads for `ludocid`, `cid`, `0x...:0x...`, `place_id`, `data-item-id`, and canonical Maps URLs.
5. If only coordinates and a strong listing URL are available, save as medium confidence and leave CID blank rather than fabricating.

The existing pilot missed CIDs because it looked primarily for decimal `cid=` and did not convert the hex feature ID pair from `!1s0x...:0x...`. Adding this conversion should recover many CIDs from URLs already being captured.

### Contact and link extraction

From the Maps listing page:

- Phone: prefer `button[data-item-id^="phone:tel:"]`, `a[href^="tel:"]`, or visible phone text near the phone action.
- Website: prefer `a[data-item-id="authority"]`, buttons/anchors labeled Website, or canonical external URL.
- Facebook/Instagram/Booking: Google Maps may expose these as direct website links only rarely. More reliably:
  - Visit the business website if present and extract outbound social/booking links.
  - Search existing local cache and prior enrichment columns.
  - Use organic Google results only for unresolved social links, not as the primary path for every record.
- WhatsApp: derive only from explicit `wa.me`, `api.whatsapp.com`, visible WhatsApp links, or phone numbers marked as WhatsApp by source; otherwise leave blank or inferred separately.

### Confidence model

Write each result with evidence fields:

- `business_name`
- `query`
- `resolved_name`
- `maps_url`
- `cid`
- `cid_source`: `url_param`, `hex_feature_id`, `page_data`, `none`
- `lat`
- `lon`
- `phone`
- `website`
- `instagram_url`
- `facebook_url`
- `booking_url`
- `confidence`: `high`, `medium`, `low`
- `evidence`: short reason
- `attempted_at`
- `session_id`

High confidence requires at least one of:

- Exact or near-exact name match plus CID.
- Exact or near-exact name match plus coordinates within the Puerto Viejo 5 km area and a phone/website corroboration.

Medium confidence:

- Good name match and Maps place URL but no CID.
- Generic Maps search page that resolves visually to one likely listing.

Low confidence:

- Multiple similarly named listings.
- No Maps listing, only organic/social result.
- Listing outside the target radius.

## 5. Time/scale estimate

The original timing estimates are arithmetically correct but operationally optimistic if all 615 use Google Search in one run:

- 30 seconds/search: 5.1 hours raw runtime, high CAPTCHA risk.
- 60 seconds/search: 10.3 hours raw runtime, still high if continuous.
- 120 seconds/search: 20.5 hours raw runtime, safer but still too dense as a single session.

Realistic free throughput on one residential IP/profile:

- Conservative Google Search throughput: 25-40 searches/day.
- Aggressive but still cautious throughput: 60-80 searches/day split into many micro-sessions, with elevated CAPTCHA risk.
- Sustainable elapsed time for 615 pure Google searches: 8-20 days.
- If prefiltering reduces Google searches to 150-250 unresolved records: 3-8 days.

The key optimization is to avoid searching all 615. Use existing Maps URLs, PVS cache, OSM, websites, and prior grid discoveries first. The Google Search workload should be the residual set, not the full set.

## 6. Architecture diagram

```text
Input candidates CSV
        |
        v
Name normalization + dedupe
        |
        v
Local enrichment pass
  - master CSV
  - PVS cache / SQLite
  - OSM exports
  - prior grid outputs
        |
        v
Unresolved queue with priority + query variants
        |
        v
Rate-limited Chrome controller
  - real installed Chrome
  - persistent profile
  - headed mode
  - adaptive delays
  - CAPTCHA/block detector
        |
        v
Google Search resolver
  - SERP link selection
  - Maps place URL validation
        |
        v
Google Maps listing extractor
  - CID URL params
  - hex feature ID to decimal CID
  - coordinates
  - phone
  - website
        |
        v
Website/social extractor
  - Instagram
  - Facebook
  - WhatsApp
  - Booking.com
        |
        v
Append-only checkpoints
  - attempts JSONL
  - resolved JSONL
  - failures CSV
  - session logs/screenshots
        |
        v
Human review queue
        |
        v
Integration into master dataset
```

## 7. Risk analysis

| Risk | Likelihood | Impact | Mitigation |
|---|---:|---:|---|
| CAPTCHA after a few searches | High if continuous; medium with pacing | Stops run | Use micro-sessions, 45-120s randomized delays, 8-12 searches/session, stop immediately on friction |
| Persistent IP/profile block | Medium | Delays project by days | Pause 24h, reduce volume, avoid VPN/proxies, preserve logs |
| Search result resolves to generic Maps search, not a place | High | Missing CID/coords | Click only confident place links; if generic Maps opens, wait for single-place resolution or mark medium/low |
| CID absent from URL | High | Incomplete enrichment | Convert `!1s0x...:0x...` hex feature IDs to decimal CID; inspect script data for `ludocid` |
| Wrong business due to duplicate names | Medium | Bad master data | Use target radius, name similarity, category, phone/website corroboration, human review for ambiguous matches |
| Google page structure changes | Medium | Extractor breaks | Keep extraction layered: URL parse first, DOM second, page-data regex third, screenshot/log on failure |
| Social links not present on Maps | High | Missing IG/Facebook/Booking | Extract from official website and existing local sources; use search only for unresolved social fields |
| Logged-in Google account flagged | Medium | Account friction | Do not use a personal account; default to non-logged-in persistent profile |
| VPN/proxy increases CAPTCHA | High | Lower throughput | Use residential connection; avoid free proxy rotation |
| Windows/Playwright process issues | Medium | Flaky runs | Use installed Chrome channel with persistent user data dir; keep GPU enabled; run headed; checkpoint after every record |
| Antivirus/network filtering causes slow loads | Low-medium | Timeouts and false failures | Increase timeouts, log network errors, whitelist local project directory only if necessary |
| Continuous overnight run hits block unseen | High | Wasted attempts | Run supervised micro-sessions; block detector must stop the whole run and write state |

## Implementation notes

Use Playwright only as a controller for a real browser:

```python
browser = playwright.chromium.launch_persistent_context(
    user_data_dir="profiles/chrome_pv_google",
    channel="chrome",
    headless=False,
    viewport={"width": 1365, "height": 850},
    locale="en-US",
    timezone_id="America/Costa_Rica",
)
```

Do not set a fake user agent unless there is a specific mismatch to fix. Do not use Playwright's bundled Chromium for the production run. Do not use `--disable-blink-features=AutomationControlled` as the only mitigation; it may help with one signal but does not address behavior, profile state, or rate limits.

The highest-value immediate code fix is CID conversion from Maps hex feature IDs. The pilot output already contains URLs like:

```text
.../data=!4m9!3m8!1s0x8fa651006b8032f5:0x3deab4612af37052!...
```

The decimal CID can be derived from the second hex token:

```python
int("0x3deab4612af37052", 16)
```

This means many "coordinates found, no CID" records may be recoverable without additional Google searches.

