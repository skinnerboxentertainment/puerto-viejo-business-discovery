import json
with open("docs/paradisio_app/data/maps_enrich.json") as f:
    data = json.load(f)
s = sum(1 for r in data if r["success"])
r = sum(1 for r in data if r["success"] and r["data"] and r["data"]["rating"])
print(f"Total results: {len(data)}, Success: {s}, With ratings: {r}")
if data and data[0]["success"]:
    print("Sample keys:", list(data[0]["data"].keys()) if data[0]["data"] else "no data")
    if data[0]["data"]:
        for k, v in data[0]["data"].items():
            print(f"  {k}: {v}")
