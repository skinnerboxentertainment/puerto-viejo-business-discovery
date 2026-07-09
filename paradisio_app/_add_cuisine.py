"""
Add cuisine/subcategory to business data from Maps enrich + name/description analysis.
"""
import json, csv, re
from pathlib import Path

BUSINESSES_JSON = Path("docs/paradisio_app/data/businesses.json")
ENRICH_PATH = Path("docs/paradisio_app/data/maps_enrich.json")
CSV_PATH = Path("pv_master_unified.csv")

# Load enrich data for subcategory field
with open(ENRICH_PATH, encoding="utf-8") as f:
    enrich = json.load(f)
enrich_by_cid = {}
for r in enrich:
    if r.get("success") and r.get("data", {}).get("subcategory"):
        cid = r.get("cid")
        sub = r["data"]["subcategory"]
        # Clean truncated values
        if len(sub) > 3 and not sub.startswith("(") and "Descripc" not in sub and "Indicac" not in sub:
            enrich_by_cid[cid] = sub

# Load businesses
with open(BUSINESSES_JSON, encoding="utf-8") as f:
    businesses = json.load(f)

# Load CSV for name-based cuisine extraction
with open(CSV_PATH, encoding="utf-8-sig") as f:
    csv_rows = list(csv.DictReader(f))
csv_by_name = {}
for r in csv_rows:
    csv_by_name[r["business_name"].strip()] = r

# Cuisine patterns from names
CUISINE_PATTERNS = [
    (r"(?i)\bpizza\b", "Pizzeria"),
    (r"(?i)\bsushi\b", "Sushi"),
    (r"(?i)\bburger|hamburgues", "Burger"),
    (r"(?i)\btaco|taqueria", "Taco"),
    (r"(?i)\bmariscos|seafood\b", "Seafood"),
    (r"(?i)\bcafe|café|coffee\b", "Cafe"),
    (r"(?i)\bice.?cream|helado|sorbet\b", "Ice Cream"),
    (r"(?i)\bpanaderia|bakery\b", "Bakery"),
    (r"(?i)\bbreakfast|desayuno\b", "Breakfast"),
    (r"(?i)\bvegan|vegetarian\b", "Vegetarian/Vegan"),
    (r"(?i)\bitalian|italiano\b", "Italian"),
    (r"(?i)\bmexican|mexicano|taqueria\b", "Mexican"),
    (r"(?i)\bjapanese|japonés\b", "Japanese"),
    (r"(?i)\bchinese|chino\b", "Chinese"),
    (r"(?i)\bthai\b", "Thai"),
    (r"(?i)\bindian|indio\b", "Indian"),
    (r"(?i)\bcaribbean|caribeño\b", "Caribbean"),
    (r"(?i)\bjuice|zumo\b", "Juice Bar"),
    (r"(?i)\bgrill|asador|parrilla\b", "Grill"),
    (r"(?i)\bsoda\b", "Soda (Costa Rican)"),
    (r"(?i)\bsurf\b", "Surf-related"),
    (r"(?i)\byoga\b", "Yoga"),
    (r"(?i)\bmassage|masaje|spa\b", "Spa/Massage"),
    (r"(?i)\bdental|dentist\b", "Dental"),
    (r"(?i)\bfarmacia|pharmacy\b", "Pharmacy"),
    (r"(?i)\blavanderia|laundry\b", "Laundry"),
    (r"(?i)\bbarber|barberia\b", "Barber"),
    (r"(?i)\bgym|gimnasio\b", "Gym"),
    (r"(?i)\btattoo\b", "Tattoo"),
    (r"(?i)\bsupermarket|super.?mercado|mega.?super\b", "Supermarket"),
    (r"(?i)\bhostel|albergue\b", "Hostel"),
    (r"(?i)\bhotel\b", "Hotel"),
    (r"(?i)\bcabinas\b", "Cabinas"),
    (r"(?i)\bbungalow\b", "Bungalow"),
    (r"(?i)\bvilla\b", "Villa"),
    (r"(?i)\blodge\b", "Lodge"),
    (r"(?i)\brental|vacation\b", "Vacation Rental"),
    (r"(?i)\btour|travel|viaje\b", "Tour Operator"),
    (r"(?i)\bsurf.?school|escuela.?surf\b", "Surf School"),
    (r"(?i)\bbike|bicycle|bicicleta\b", "Bike Rental"),
    (r"(?i)\brent.?a.?car|car.?rental\b", "Car Rental"),
    (r"(?i)\breal.?estate|inmobiliaria\b", "Real Estate"),
]

updated = 0
cuisine_source_map = {}
for biz in businesses:
    cid = biz.get("channels", {}).get("google_maps_cid", "")
    name = biz["name"]
    category = biz.get("category", "").lower().strip()

    # Priority 1: Maps subcategory
    sub = enrich_by_cid.get(cid, "")
    if sub and not sub.startswith("("):
        biz["subcategory"] = sub
        cuisine_source_map[sub] = cuisine_source_map.get(sub, 0) + 1
        updated += 1
        continue

    # Priority 2: Category-based default
    cat_defaults = {
        "restaurant": "Restaurant",
        "hotel": "Hotel",
        "hostel": "Hostel",
        "vacation_rental": "Vacation Rental",
        "tour_company": "Tour Operator",
        "shopping": "Shop",
        "services": "Service",
        "real_estate": "Real Estate",
    }
    if category in cat_defaults:
        biz["subcategory"] = cat_defaults[category]

    # Priority 3: Name-based pattern match (overrides defaults for restaurants)
    for pattern, label in CUISINE_PATTERNS:
        if re.search(pattern, name):
            biz["subcategory"] = label
            cuisine_source_map[label] = cuisine_source_map.get(label, 0) + 1
            updated += 1
            break
    else:
        if category in cat_defaults:
            cuisine_source_map[cat_defaults[category]] = cuisine_source_map.get(cat_defaults[category], 0) + 1

with open(BUSINESSES_JSON, "w", encoding="utf-8") as f:
    json.dump(businesses, f, indent=2, ensure_ascii=False)

print(f"Updated {updated} businesses with subcategory.")
print("\nSubcategory distribution (top 30):")
for label, count in sorted(cuisine_source_map.items(), key=lambda x: -x[1])[:30]:
    print(f"  {label}: {count}")
