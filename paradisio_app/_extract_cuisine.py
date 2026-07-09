"""
Re-parse Maps text samples to extract cuisine/subcategory labels.
Runs over existing maps_enrich.json, adds a 'subcategory' field.
"""
import json
import re
from pathlib import Path

ENRICH_PATH = Path("docs/paradisio_app/data/maps_enrich.json")

with open(ENRICH_PATH, encoding="utf-8") as f:
    data = json.load(f)

cuisine_found = {}
total_with_text = 0
for r in data:
    if not r.get("success") or not r.get("text_sample"):
        continue
    total_with_text += 1
    text = r["text_sample"]
    lines = text.split("\n")
    for i, line in enumerate(lines):
        line = line.strip()
        # Rating line like "4.1" 
        if re.match(r"^\d\.\d$", line):
            # Next non-empty line is likely the subcategory/cuisine
            for j in range(i + 1, min(i + 5, len(lines))):
                nxt = lines[j].strip()
                if nxt and not re.match(r"^\d\.\d$", nxt) and len(nxt) > 2 and len(nxt) < 60:
                    r.setdefault("data", {})["subcategory"] = nxt
                    cuisine_found[nxt] = cuisine_found.get(nxt, 0) + 1
                    break

print(f"Total with text samples: {total_with_text}")
print(f"\nSubcategories found ({len(cuisine_found)} unique):")
for label, count in sorted(cuisine_found.items(), key=lambda x: -x[1]):
    print(f"  {label}: {count}")

# Save updated enrich data
with open(ENRICH_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\nUpdated maps_enrich.json with subcategory field.")
