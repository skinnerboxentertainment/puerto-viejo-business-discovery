# Paradisio — Unified Design Direction

Resolved between OpenCode and Codex. 2026-07-09.

## Direction: Polished Local Warmth

- Visual mood: warm minimalism
- Product shape: polished local board
- Tagline: **"Find Puerto Viejo businesses with confidence."**
- Design qualities: plainspoken, fast, dense, direct, modest color, local details, no fake luxury tone

## Homepage Layout

1. Sticky header (identity, search, map toggle, language)
2. Category shortcut grid (Eat, Sleep, Tours, Wellness, Shops, Services, Nightlife, Transport)
3. Search as dominant CTA
4. Map preview below search (not default)
5. Featured/recently verified business cards
6. Classifieds board preview
7. Trust note: data source, last updated, claim flow

## Map

- List/search is default view
- Map is a prominent toggle (List | Map)
- Desktop: optional split view
- Mobile: segmented control at top
- Map markers use category colors
- Aggressive clustering

## Photography

- Do NOT scrape Instagram
- v1: category-specific CSS placeholders (food, lodging, tours, etc.)
- Use business-owned images from their websites when available
- Owner-submitted photos after claim flow exists

## Trust Architecture

First trust signals to add:
- Last checked date on every business page
- Source badges (PV Satellite, OSM, Google Maps, Instagram)
- Claimed / unclaimed status
- Verified contact badge
- "Report correction" link per business
- "Data may be incomplete" disclaimer where appropriate

## Audience Paths

Homepage serves four audiences immediately:
- Visitors: search by need ("dinner", "hotel", "laundry")
- Locals: browse by category
- Business owners: claim or correct listing
- Operators/partners: review data quality

## Score Labels

Replace numeric scores with human-readable statuses:
- Verified, Strong, Partial, Limited, Missing, Needs Review

Internal scores retained for ranking logic but not displayed.

## Spanish

Minimum viable for v1:
- Bilingual nav labels (Buscar/Search, Mapa/Map, Categorias/Categories)
- Spanish placeholder text in search
- Category names in both languages
- Empty/error states bilingual
- Trust labels bilingual
- NOT full business descriptions

Templates designed for Spanish string length from the start.

## Design System — Phase 1 Tokens

### Colors
```
--sand-50: #f7f2e8    (background)
--sand-100: #efe4d0   (border)
--surface: #fffaf1    (card surface)
--ink: #17211c        (primary text)
--muted: #66736b      (secondary text)
--faint: #9b9a8f      (tertiary)
--jungle-900: #18382b (identity)
--jungle-700: #245743 (navigation)
--reef-600: #007f7a   (map, interactive)
--coral-500: #ed744f  (primary CTA)
--sun-500: #f2b84b    (badges, highlights)
--border: #ded3bf     (dividers)
```

### Typography
- Body: system font stack
- Headings: system font stack (Fraunces deferred)
- Type scale: 0.8125rem / 0.9375rem / 1.0625rem / 1.125rem / 1.4rem / 1.8rem / 2.4rem

### Spacing
4px base: 4, 8, 12, 16, 24, 32, 48, 64

### Radii
Controls: 6px, Cards: 8px, Pills: 999px

### Shadows
Subtle: `0 1px 2px rgba(23,33,28,.08)`
Hover: `0 8px 24px rgba(23,33,28,.10)`

## CSS Architecture

Custom, no framework:
- tokens.css (design tokens)
- base.css (reset, typography, layout)
- components.css (cards, buttons, nav, search, badges, map)
- pages.css (homepage, business, classifieds)

Vanilla JS only. Bundle target < 50KB.

## Implementation Order

1. Add CSS tokens file
2. Redesign homepage: masthead, category grid, search dominance
3. Redesign business cards around contact availability
4. Add trust signals to business pages
5. Add bilingual nav labels
6. Replace score bars with human labels
7. Map polish: category-colored markers, split view
8. Empty/error states for search
