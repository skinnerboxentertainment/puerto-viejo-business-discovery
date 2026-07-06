# Request: UI/UX Gap Analysis — Live Site Review

**Target:** CODEX
**From:** OpenCode
**Date:** 2026-07-06

---

Visit the live site and conduct a fresh UI/UX audit:

**https://skinnerboxentertainment.github.io/puerto-viejo-business-discovery/**

## What's changed since last audit

The prior audit was done against page source. This one should be against the
live rendered site. The following fixes have been applied:

- Landing page: full redesign with map preview, metric strip, nav bar
- Directory: two-pane layout (sidebar + sticky map), dynamic stats, multi-field search
- Report: fully rebuilt — all tables load dynamically from businesses.json
- Gap Map: zero-biz cells hidden, markers now clickable without grid blocking
- Categories normalized (cafe; restaurant → restaurant)
- Nav bar added to all pages
- metrics.json created as single source of truth

## What to evaluate

### 1. Cross-linking and navigation
The user reports the site feels disconnected — pages don't link between each
other naturally. Specifically:
- From the Directory, can you get to the Report or Gap Map without using the
  nav bar? Are there contextual cross-links?
- From the Gap Map, can you get from a cell's business list to that business
  in the Directory?
- From a business card in the Directory, can you open its location on the
  Gap Map?
- Does every page clearly communicate what the other pages offer?

### 2. Page-level UX

**Landing page:**
- Does the map + metric strip give enough context?
- Are the CTAs clear about what each destination offers?
- Any obvious visual issues?

**Directory page:**
- Does the search work correctly now?
- Is the two-pane layout intuitive?
- Any issues with the "Show more" pattern?
- Mobile experience?

**Report page:**
- Did the dynamic tables load correctly?
- Is the map working?
- Any visible stale data?

**Gap Map:**
- Do markers show popups when clicked?
- Do grid labels open the side panel?
- Is the zero-cell hiding working?

### 3. Consistency
- Are the nav bars consistent across pages?
- Do colors, fonts, spacing feel like one product?
- Any weird gaps or visual breaks?

### 4. Mobile
- How does each page look at mobile width?

## Deliverable

Write your findings to `CODEX_ENDPOINT/responses/ui_ux_gap_analysis.md`

Focus on things that are actually broken or missing, not stylistic preferences.
Priority-order: P0 (broken), P1 (important), P2 (polish).

If you cannot access the live URL, note that and analyze from the page source
in `docs/` instead.
