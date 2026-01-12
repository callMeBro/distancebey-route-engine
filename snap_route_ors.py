import xml.etree.ElementTree as ET
import requests
import json
from pathlib import Path

import os

API_KEY = os.getenv("ORS_API_KEY")


KML_PATH = "route.kml"          # <-- your input
OUT_GEOJSON = "route.geojson"   # <-- road-following output
OUT_LEAFLET = "route_leaflet.json"

PROFILE = "foot-walking"  # try: foot-walking, cycling-regular, driving-car
CHUNK_SIZE = 40           # safe-ish; if it errors, drop to 25

NS = {"kml": "http://www.opengis.net/kml/2.2"}

def read_kml_points(kml_file):
    xml = Path(kml_file).read_text(encoding="utf-8", errors="ignore")
    root = ET.fromstring(xml)

    coords = []
    for pm in root.findall(".//kml:Placemark", NS):
        c = pm.find(".//kml:Point/kml:coordinates", NS)
        if c is None or not c.text:
            continue
        # KML: "lon,lat,alt"
        parts = c.text.strip().split(",")
        lon = float(parts[0].strip())
        lat = float(parts[1].strip())
        coords.append([lon, lat])  # ORS expects [lon, lat]

    return coords

def ors_directions(coords_chunk):
    url = f"https://api.openrouteservice.org/v2/directions/{PROFILE}/geojson"
    headers = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }
    body = {"coordinates": coords_chunk}

    r = requests.post(url, headers=headers, json=body, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"ORS error {r.status_code}: {r.text[:500]}")
    return r.json()

def chunked(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i:i+size]

def main():
    pts = read_kml_points(KML_PATH)
    if len(pts) < 2:
        raise SystemExit("Need at least 2 points in KML.")

    print(f"✅ KML points: {len(pts)}")

    stitched_line = []

    # We need overlap between chunks so the line connects smoothly
    chunks = list(chunked(pts, CHUNK_SIZE))
    print(f"🧩 Chunks: {len(chunks)} (chunk size {CHUNK_SIZE})")

    for idx, ch in enumerate(chunks):
        # overlap: prepend last point of previous chunk
        if idx > 0:
            ch = [chunks[idx-1][-1]] + ch

        data = ors_directions(ch)
        geom = data["features"][0]["geometry"]["coordinates"]  # [lon,lat] list

        # avoid duplicate join coordinate
        if stitched_line and geom:
            if stitched_line[-1] == geom[0]:
                geom = geom[1:]

        stitched_line.extend(geom)
        print(f"   • chunk {idx+1}/{len(chunks)} -> +{len(geom)} snapped coords")

    geojson = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "properties": {"source": "openrouteservice", "profile": PROFILE},
            "geometry": {"type": "LineString", "coordinates": stitched_line}
        }]
    }

    Path(OUT_GEOJSON).write_text(json.dumps(geojson), encoding="utf-8")
    print(f"✅ wrote {OUT_GEOJSON}")

    # Leaflet likes [lat,lng]
    leaflet = [[lat, lon] for lon, lat in stitched_line]
    Path(OUT_LEAFLET).write_text(json.dumps(leaflet), encoding="utf-8")
    print(f"✅ wrote {OUT_LEAFLET} (Leaflet [lat,lng])")

if __name__ == "__main__":
    main()
