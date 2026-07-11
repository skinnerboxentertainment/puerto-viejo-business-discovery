"""
Fix blank categories in master CSV using v3 parser inferences.
Reads maps_parsed_v3.json for inferred_category, updates master CSV.
"""
import csv
import json
from pathlib import Path
from collections import Counter

BASE = Path(".")
MASTER_CSV = BASE / "pv_master_unified.csv"
PARSED_V3 = BASE / "docs" / "paradisio_app" / "data" / "maps_parsed_v3.json"

# Load v3 parsed data (inferred categories keyed by CID)
inferred = {}
parsed = json.load(open(PARSED_V3, encoding="utf-8"))
for p in parsed:
    cid = p.get("cid", "")
    ic = p.get("inferred_category")
    subcat = p.get("fields", {}).get("subcategory", {}).get("value", "")
    if cid and ic:
        inferred[cid] = {"category": ic, "subcategory": subcat}

print(f"Loaded {len(inferred)} inferred categories from v3 parser")

# Read master CSV, update blank categories
rows = list(csv.DictReader(open(MASTER_CSV, encoding="utf-8-sig")))
fields = csv.DictReader(open(MASTER_CSV, encoding="utf-8-sig")).fieldnames

blank_before = sum(1 for r in rows if not r.get("category", "").strip())
print(f"Blank categories before: {blank_before}")

fixed = 0
changes = Counter()
for r in rows:
    cat = r.get("category", "").strip()
    if cat:
        continue  # Already categorized
    cid = r.get("google_maps_cid", "").strip()
    if not cid or cid not in inferred:
        continue
    ic = inferred[cid]["category"]
    if ic != "unknown":
        r["category"] = ic
        fixed += 1
        changes[ic] += 1

blank_after = sum(1 for r in rows if not r.get("category", "").strip())
print(f"Blank categories after: {blank_after}")
print(f"Fixed: {fixed}")
print("\nCategory distribution of fixes:")
for cat, count in changes.most_common():
    print(f"  {cat}: {count}")

# Write updated CSV
with open(MASTER_CSV, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for r in rows:
        w.writerow(r)
print(f"\nUpdated: {MASTER_CSV}")
