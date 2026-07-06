# Request: Resolve 134 Business Names to Google Maps Listings

**Target:** Codex Desktop with in-app browser tools
**Requester:** OpenCode
**Date:** 2026-07-06

---

## Task

For each of the 134 business names in `CODEX_ENDPOINT/tasks/osm_scanner/grid_discoveries.csv`,
use your in-app browser to search Google and find the corresponding Google Maps listing,
then extract its CID (when reliably available), Place ID (when available),
coordinates, and phone number.

## Background

These 134 names were extracted via vision AI from Google Maps screenshots of the
Puerto Viejo, Costa Rica area. They are real businesses visible on the map, but we
only have names — no coordinates, no CIDs, no way to verify identity. We need to
resolve each name to its actual Maps pin.

## Instructions

For each business name:

1. **Open your in-app browser** and search Google for: `"{business_name}" Puerto Viejo`
2. **Find the Google Maps result** — look for a `maps.google.com` URL in the search results.
   Results may be wrapped in Google's `/url?...` redirect — follow to the final resolved URL.
3. **Open the Maps link** so the URL resolves to a proper `@lat,lon` format.
   Capture the **final URL after all redirects** as the resolved listing URL. Google
   Maps URLs may contain transient UI or routing state, so do not assume the URL is
   permanently canonical.
4. **Extract** from the **place card page** (not search snippets):
   - `latitude` and `longitude` from the `@lat,lon,zoom` in the final URL
   - **Important:** The `@lat,lon` may be the **map viewport center**, not the business
     pin. Prefer coordinates explicitly tied to the selected listing, such as listing
     coordinates encoded in the Maps URL or data payload. Verify them against the place
     card address and the expected Puerto Viejo-area location. If listing-specific
     coordinates cannot be identified reliably, record the `@lat,lon` viewport center
     and write `approximate viewport coordinates` in `notes`. Never silently present
     viewport coordinates as exact pin coordinates.
   - `google_maps_cid` — record only a reliably identified **numeric Google Maps CID**,
     such as one exposed by a `?cid=XXXXXX` parameter. Do not put a Place ID or encoded
     feature identifier in this field. If no numeric CID can be reliably extracted,
     leave the field blank rather than guessing.
   - `google_place_id` — record a reliably identified Google Place ID when available,
     including one found in a Maps data segment. Do not treat arbitrary `/place/...`
     text or an unverified encoded value as a Place ID.
   - `phone` number — extract only from the **selected Maps place card** (the business's
     own listing panel), not from general search snippets or other businesses on the page.
5. **Rate confidence** using this definition:
   - **high**: name matches and listing address/pin is within 5 km of Puerto Viejo
   - **medium**: plausible name variant and location match, but identity has some ambiguity
   - **low**: no listing, conflicting location, or unresolved ambiguity
6. **Checkpoint** every 20 rows: write what you have so far to
   `CODEX_ENDPOINT/tasks/osm_scanner/grid_resolved.csv` (this is the only output file —
   safe to append incrementally). See constraints below for escaping.

## Output

Write to `CODEX_ENDPOINT/tasks/osm_scanner/grid_resolved.csv` with columns:

```
business_name,google_maps_url,latitude,longitude,google_maps_cid,google_place_id,phone,confidence,notes
```

## Constraints

- Write ONLY to `CODEX_ENDPOINT/tasks/osm_scanner/grid_resolved.csv` (incremental appends are fine)
- Do NOT modify any project source files (no CSVs, no Python files)
- **Preserve all 134 input rows** in original order, including OCR duplicates
- If no Maps result is found, leave listing fields blank and set confidence to "low"
- A missing CID or Place ID does **not** by itself lower confidence. Rate confidence
  from the identity and location match; leave unavailable identifiers blank.
- If multiple names resolve to the same Maps URL, note it in the `notes` field
- **CSV escaping:** names, URLs, phone numbers, and notes may contain commas, quotes, and
  special characters. Use standard CSV quoting (wrap fields in double quotes, escape
  internal quotes as `""`).
- Process all 134 names — prioritize quality over speed
