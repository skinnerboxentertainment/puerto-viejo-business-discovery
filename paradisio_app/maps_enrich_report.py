import json
from pathlib import Path

path = Path("docs/paradisio_app/data/maps_enrich.json")
if not path.exists():
    print("No results yet")
    exit()

with open(path, encoding="utf-8") as f:
    data = json.load(f)

total = len(data)
succeeded = sum(1 for r in data if r["success"])
rated = sum(1 for r in data if r["success"] and r["data"] and r["data"]["rating"])
with_phone = sum(1 for r in data if r["success"] and r["data"] and r["data"]["phone"])
with_website = sum(1 for r in data if r["success"] and r["data"] and r["data"]["website"])
with_address = sum(1 for r in data if r["success"] and r["data"] and r["data"]["address"])
with_hours = sum(1 for r in data if r["success"] and r["data"] and (r["data"]["check_in"] or r["data"]["check_out"]))
with_amenities = sum(1 for r in data if r["success"] and r["data"] and len(r["data"]["amenities"]) > 3)
with_prices = sum(1 for r in data if r["success"] and r["data"] and len(r["data"]["prices"]) > 0)

print(f"Results: {total}, Success: {succeeded}")
print(f"  Ratings:     {rated}")
print(f"  Phones:      {with_phone}")
print(f"  Websites:    {with_website}")
print(f"  Addresses:   {with_address}")
print(f"  Hours:       {with_hours}")
print(f"  Amenities:   {with_amenities}")
print(f"  Prices:      {with_prices}")

# Check checkpoint for remaining
ckpt = Path("docs/paradisio_app/data/maps_checkpoint.json")
if ckpt.exists():
    with open(ckpt, encoding="utf-8") as f:
        cp = json.load(f)
    remaining = 699 - len(cp["completed"])
    print(f"\nCheckpoint: {len(cp['completed'])} done, {remaining} remaining")
