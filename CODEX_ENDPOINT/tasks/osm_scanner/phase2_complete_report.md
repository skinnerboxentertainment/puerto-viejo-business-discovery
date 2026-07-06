# Phase 2 Grid Scan — Complete Results

## Pipeline

```
193 grid points → 255 screenshots → 52 Codex vision batches → 268 raw names → 134 unique new discoveries
```

## Discovery sources

| Source | Original | New (unique) | Method |
|--------|:--------:|:------------:|--------|
| OSM cross-ref | 117 | 31 | Existing repo data |
| Codex web search | 2 | 2 | Web directory search |
| **Grid scan (Phase 2)** | **255** | **134** | **Maps screenshots + Codex vision** |
| **Total** | | **167** | |

## Grid scan enrichment results

| Metric | Count |
|--------|:-----:|
| Total grid names extracted | 268 |
| After dedup (unique) | 251 |
| New vs. known 481 | **134 new** |
| With contact info found via web | 6 |
| With phone | 5 |
| With website | 3 |
| With Instagram | 1 |
| With Facebook | 2 |
| With Google Maps CID | 0 |

## Key files

| File | Description |
|------|-------------|
| `screenshots/` | 255 PNG screenshots from the grid |
| `vision_results.json` | All 268 raw names + batch audit |
| `grid_discoveries.csv` | 134 clean new discoveries |
| `grid_discoveries_deduped.csv` | All 251 groups with variant tracking |
| `CODEX_ENDPOINT/tasks/osm_scanner/grid_enriched.csv` | 134 with web enrichment results |
| `neighborhood_scanner/scan_targets.csv` | The 193 grid points used |

## What's next

The 134 new names need Instagram verification + further deep-enrichment
(website scraping, phone normalization, CID lookup). Most are small local
businesses (cabinas, vacation rentals, massage/tour services) with limited
web presence, so many contact fields will remain blank.

Total project dataset would be: 450 (PVS) + 31 (OSM) + 134 (grid) = **615 records**.
