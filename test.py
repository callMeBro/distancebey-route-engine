import xml.etree.ElementTree as ET
import json

tree = ET.parse("route.kml")
root = tree.getroot()

ns = {'kml': 'http://www.opengis.net/kml/2.2'}
coords = []

for elem in root.findall('.//kml:coordinates', ns):
    raw = elem.text.strip().split()
    for point in raw:
        lng, lat, *_ = point.split(',')
        coords.append([float(lat), float(lng)])

with open("route.json", "w") as f:
    json.dump(coords, f, indent=2)

print("✅ points:", len(coords))
