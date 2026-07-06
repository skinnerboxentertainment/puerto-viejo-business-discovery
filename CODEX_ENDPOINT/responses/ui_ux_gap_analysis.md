# UI/UX Gap Analysis - Live Site Review

Reviewed: 2026-07-06  
Target: https://skinnerboxentertainment.github.io/puerto-viejo-business-discovery/

## Review basis

The live GitHub Pages assets were reachable. I confirmed the deployed `directory.html`, `metrics.json`, and `businesses.json` are accessible, with `metrics.json` reporting 754 total records and 481 mapped records. The in-app browser was unavailable in this Codex session and Playwright was not installed locally, so I could not do pixel-level rendered click testing. Findings below are based on the reachable live assets plus the current `docs/` HTML source, which appears to match the deployed pages.

## P0 - Broken

None found from source/live asset inspection.

No obvious hard failure prevents the main pages from loading data: `metrics.json`, `businesses.json`, and `businesses.geojson` are referenced consistently, and the live data files respond.

## P1 - Important

### 1. Gap Map is missing the shared nav bar

`gapmap.html` has no top navigation, while Home, Directory, and Report do. This directly contributes to the "disconnected site" complaint. Once a user lands on Gap Map, there is no obvious route to Directory, Report, Home, or CSV except browser back.

Recommended fix: add the same nav structure used by the other pages, with links to Home, Directory, Report, CSV, and optionally GitHub.

### 2. Contextual cross-links are mostly absent

The nav bar exists on most pages, but the pages do not link to each other at the task level:

- Directory cards can focus the same-page map, but cannot open that business or location in Gap Map.
- Gap Map cell business lists are plain text only. They do not link to the business in Directory.
- Report tables are read-only summaries. Category/area rows do not link to filtered Directory views.
- Directory does not offer contextual links like "view coverage gaps for this area" or "open report for this category."

Recommended fix: add URL-driven state and contextual links:

- `directory.html?q=<business>` or `directory.html?area=<area>&category=<category>`
- `gapmap.html?lat=<lat>&lon=<lon>&business=<id-or-name>`
- Report category/area rows link into Directory filters.
- Gap Map cell business names link into Directory search/focus.

### 3. Directory "View on map" does not mean Gap Map

The audit prompt asks whether a Directory card can open its location on the Gap Map. Currently "View on map" only pans the embedded Directory map. That is useful, but it does not satisfy cross-page navigation and may be ambiguous because the site also has a page named "Gap Map."

Recommended fix: either rename the current button to "Focus on directory map" and add "Open in Gap Map," or make the button group explicit.

### 4. Report still contains stale/static duplicate area data

`report.html` dynamically builds an "Areas - Business Distribution" table from `businesses.json`, then later includes a second hard-coded "Areas - Business Distribution" table with old-looking values totaling 450 records:

- Cocles 84
- Hone Creek 20
- Playa Chiquita 54
- Playa Negra 69
- Puerto Viejo 199
- Punta Uva 24

This conflicts with the current 754-record dataset and the stated rebuild goal that all tables load dynamically. Users will see two area sections and may trust the stale one.

Recommended fix: remove the hard-coded duplicate table or convert it to dynamic data from `businesses.json`/`metrics.json`.

### 5. Mobile navigation hides all links on Home and Directory

At mobile widths, Home and Directory hide `.nav-links a`, leaving only the title. Report does not apply the same hide rule because its nav links are not wrapped in `.nav-links`, so Report likely remains navigable while Home/Directory do not. Gap Map has no nav at all.

This creates inconsistent and sometimes dead-end mobile navigation.

Recommended fix: use a compact mobile nav pattern across all pages: wrapped horizontal links, a simple menu button, or a second row of links. Do not fully remove navigation links without a replacement.

### 6. Gap Map mobile layout is likely cramped

Gap Map uses a fixed horizontal flex layout with a `260px` side panel and no mobile media query. On narrow screens, opening a cell panel will squeeze the map severely or force horizontal overflow.

Recommended fix: below ~768px, stack the panel under the map or make it a bottom sheet/drawer.

## P2 - Polish / Usability

### 1. Pages do not clearly explain what sibling pages offer

Home does this reasonably well through CTAs and footer cards. Directory, Report, and Gap Map do not. A user in Directory sees only filters/cards/map; there is no local prompt explaining when to use Report or Gap Map. Gap Map especially lacks context beyond "scan quadrant by quadrant for gaps."

Recommended fix: add compact contextual action rows, not large marketing copy:

- Directory: "Need coverage metrics? View Report. Looking for spatial gaps? Open Gap Map."
- Gap Map: "Click a cell to inspect businesses. Open a business in Directory for full contact/social data."
- Report: "Use Directory for record-level search; use Gap Map for spatial coverage review."

### 2. Directory show-more count can become stale after clicking Show more

`showMore` increases `displayCount` and re-renders cards, but does not update `#resultCount`. The text can still say "showing first 100" after more records are visible.

Recommended fix: update `resultCount` inside the show-more handler or centralize count rendering in `renderCards`.

### 3. Directory highlight can apply to the button instead of the card

When clicking the "View on map" button, `focusMap(..., this)` passes the button element. The function then adds `.highlighted` to the button, but the CSS highlight selector is `.card.highlighted`, so the card does not visibly highlight from button clicks. Clicking the card itself works because `this` is the card.

Recommended fix: pass `this.closest('.card')` from the button handler.

### 4. Search appears broad enough, but no deep-link or visible active filter summary

Search includes name, category, area, Instagram handle, phone, Facebook, and website. That likely fixes the prior multi-field search gap. However, there is no URL state and no compact active-filter summary beyond control values, which limits shareability and cross-linking from Report/Gap Map.

Recommended fix: add query-string state for search, area, category, and enrichment filters.

### 5. Report area table has a duplicated "Area" column

The dynamic area table columns are `Area`, `Total`, `With Instagram`, `Area`, and the last column repeats the area name. This looks like a placeholder where distance or coverage was intended.

Recommended fix: remove the repeated column or replace it with a meaningful field.

### 6. Visual consistency is close but Gap Map feels like a separate app

Home, Directory, and Report share light background, dark blue nav/header, similar typography, and card styling. Gap Map uses a dark standalone tool UI, different header style, no nav, and different spacing. The dark map tool can be valid, but the missing shared nav makes it feel disconnected.

Recommended fix: keep the dark scanner surface if desired, but add the shared product nav and align title/link treatment.

## Page-level notes

### Landing page

The landing page gives good high-level context: map preview, metric strip, source chips, and CTAs are clear. The footer cards also help explain the three destinations. No major functional issue found from source inspection.

Mobile issue: nav links are hidden under 768px with no replacement.

### Directory

The two-pane layout is structurally intuitive on desktop: filters/list on the left, sticky map on the right. Search is implemented across multiple fields and should work for the requested dimensions.

Important gaps are cross-linking and mobile nav. The show-more count and button highlight are smaller interaction bugs.

### Report

Dynamic metrics and category/data-quality tables are present. The map is wired to `businesses.geojson`. The major issue is the stale duplicate static area table and the duplicated column in the dynamic area table.

### Gap Map

Source indicates the recent marker/grid fix is present: grid rectangles are `interactive: false`, non-empty cell labels are clickable, and zero-business cells are not rendered. Marker popups are bound in `updateMarkers`, so markers should show popups when clicked.

Main issues are missing nav, no business-to-Directory links in the cell panel, and weak mobile behavior.

## Highest-impact next fixes

1. Add shared nav to Gap Map and mobile nav to all pages.
2. Add query-string state to Directory and Gap Map, then wire contextual links between Directory cards, Gap Map cell businesses, and Report rows.
3. Remove the stale static area table from Report.
4. Fix Directory show-more count and button highlight behavior.
