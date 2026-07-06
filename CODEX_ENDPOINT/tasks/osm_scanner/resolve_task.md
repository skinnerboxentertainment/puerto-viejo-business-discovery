# Task: Resolve 134 business names to Google Maps URLs, CIDs, and coordinates

**Goal:** For each of the 134 business names in `grid_discoveries.csv`, find the
corresponding Google Maps listing and extract its CID, lat/lon, and phone.

**Why this matters:** These names were extracted from Maps screenshots via
vision AI. They are real businesses visible on Google Maps, but we only have
names — no coordinates, no CIDs, no way to verify identity.

## Instructions

For each business name:

1. Search Google for: `"{business_name}" Puerto Viejo`
2. If a Google Maps result appears, open it or extract from the search snippet:
   - **Maps URL** (click the result → the maps.google.com URL)
   - **CID** (numeric ID in `?cid=XXXX` or `!1sXXXX!8b` in the URL)
   - **Latitude/Longitude** (from `@lat,lon,zoom` in the URL)
   - **Phone number** if visible in the snippet
   - **Status** — is it clearly the same business? (high confidence / medium / low)
3. If no clear Maps result, note "not found" — don't guess.

## Output format

Append to `CODEX_ENDPOINT/tasks/osm_scanner/grid_resolved.csv`
with columns:

```
business_name,google_maps_url,latitude,longitude,google_maps_cid,phone,confidence,notes
```

## Key rules

- Only write to `CODEX_ENDPOINT/tasks/osm_scanner/grid_resolved.csv`
- Do NOT modify any project source files
- Be honest about confidence — if the search lands on a different city's
  result with the same name, mark it low confidence
- If multiple names resolve to the same Maps URL, note it (potential OCR dupes)

Process all 134 names. Batch by skipping obvious OCR variants that share
the same Maps result.
