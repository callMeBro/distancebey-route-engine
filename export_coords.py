import json

INPUT = "route_leaflet.json"       # your snapped route file
OUTPUT = "coords.txt"              # one "lat,lon" per line

with open(INPUT, "r", encoding="utf-8") as f:
    coords = json.load(f)

with open(OUTPUT, "w", encoding="utf-8") as f:
    for lat, lon in coords:
        f.write(f"{lat:.7f},{lon:.7f}\n")

print(f"✅ Wrote {len(coords)} lines to {OUTPUT}")
