import json
import math
from pathlib import Path

def haversine_m(a, b):
    lat1, lon1 = a
    lat2, lon2 = b
    R = 6371000.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    x = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(x))

def is_same_point(a, b, eps=1e-6):
    return abs(a[0] - b[0]) < eps and abs(a[1] - b[1]) < eps

# Optional: Ramer–Douglas–Peucker simplification (keeps shape, fewer points)
def rdp(points, epsilon_m=5.0):
    if len(points) < 3:
        return points

    def to_xy(p, ref_lat):
        lat, lon = p
        x = math.radians(lon) * 6371000.0 * math.cos(math.radians(ref_lat))
        y = math.radians(lat) * 6371000.0
        return (x, y)

    ref_lat = points[0][0]
    xy = [to_xy(p, ref_lat) for p in points]

    def perp_dist(i, a, b):
        px, py = xy[i]
        ax, ay = xy[a]
        bx, by = xy[b]
        dx = bx - ax
        dy = by - ay
        if dx == 0 and dy == 0:
            return math.hypot(px - ax, py - ay)
        t = ((px - ax)*dx + (py - ay)*dy) / (dx*dx + dy*dy)
        t = max(0.0, min(1.0, t))
        cx = ax + t*dx
        cy = ay + t*dy
        return math.hypot(px - cx, py - cy)

    keep = [False] * len(points)
    keep[0] = True
    keep[-1] = True

    stack = [(0, len(points)-1)]
    while stack:
        a, b = stack.pop()
        max_d = 0.0
        idx = None
        for i in range(a+1, b):
            d = perp_dist(i, a, b)
            if d > max_d:
                max_d = d
                idx = i
        if idx is not None and max_d > epsilon_m:
            keep[idx] = True
            stack.append((a, idx))
            stack.append((idx, b))

    return [p for i, p in enumerate(points) if keep[i]]

INFILE = Path("route_leaflet.json")
OUTFILE = Path("route_leaflet_clean.json")

# Tune these
MIN_STEP_METERS = 3.0   # drop points closer than this to previous kept point (jitter)
RDP_EPS_METERS = 5.0    # set to 0 to disable simplify

points = json.loads(INFILE.read_text(encoding="utf-8"))

# 1) remove exact consecutive duplicates only
dedup = []
for p in points:
    if not dedup or not is_same_point(p, dedup[-1]):
        dedup.append(p)

# 2) drop jitter points too close together (preserves true overlaps)
filtered = [dedup[0]]
for p in dedup[1:]:
    if haversine_m(filtered[-1], p) >= MIN_STEP_METERS:
        filtered.append(p)

# 3) optional simplify (also preserves overlaps, but reduces density)
final = filtered
if RDP_EPS_METERS and RDP_EPS_METERS > 0:
    final = rdp(filtered, epsilon_m=RDP_EPS_METERS)

OUTFILE.write_text(json.dumps(final, indent=2), encoding="utf-8")

print("✅ input points:", len(points))
print("✅ after dedup:", len(dedup))
print("✅ after jitter filter:", len(filtered))
print("✅ after simplify:", len(final))
print("✅ wrote:", OUTFILE)
