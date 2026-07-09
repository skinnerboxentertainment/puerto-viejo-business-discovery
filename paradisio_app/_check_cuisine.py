import csv
with open("pv_master_unified.csv", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))
restaurants = [r for r in rows if r.get("category","").strip() == "restaurant"]
print(f"Restaurants: {len(restaurants)}")
cuisine_keywords = ["italian", "mexican", "caribbean", "japanese", "chinese", "french", "indian", "thai", "seafood", "pizza", "burger", "breakfast", "cafe", "bar", "grill", "sushi", "vegan", "vegetarian", "bakery", "ice cream", "juice", "coffee", "pancake", "taco", "soda", "mariscos"]
found = {}
for r in restaurants:
    desc = (r.get("description_full","") + " " + r.get("business_name","")).lower()
    for kw in cuisine_keywords:
        if kw in desc:
            found[kw] = found.get(kw, 0) + 1
print("Cuisine mentions in names + descriptions:")
for kw, c in sorted(found.items(), key=lambda x: -x[1]):
    print(f"  {kw}: {c}")
print()
print("Sample restaurant names:")
for r in restaurants[:15]:
    ig = r.get("instagram_handle","")[:15]
    print(f"  {r['business_name'][:50]:50s} {r['area']:20s} IG={ig:15s}")
