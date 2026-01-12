Marathon Route Snapper

This repo contains the tooling I built to convert a hand-drawn marathon route into a road-following, shippable GPS route.

What started as “just draw the route” turned into a deep dive into mapping accuracy, routing graphs, snapping constraints, and real-world tradeoffs.

This project exists because straight lines ≠ roads, and maps that look correct can still be unusable.

Problem

Hand-drawn coordinates can drift over water

Points that are too far apart cause routing errors

Official race diagrams are ceremonial, not machine-usable

Google My Maps snapping is limited and opaque

Precision without context creates worse results, not better ones

The goal was not perfect ceremonial accuracy —
the goal was a clean, realistic, road-following route that users can actually run against.

Solution

Exported raw route data from Google My Maps (KML)

Parsed and normalized coordinates in Python

Snapped points to real road graphs using OpenRouteService

Chunked requests to respect API limits

Reconstructed a continuous route with:

No water crossings

Same start/end

Minor, expected detours

Exported results to formats usable by web maps and apps

Result:
A road-snapped approximation that is slightly longer (~+1 mile) but far more realistic for training and simulation.

This tradeoff is intentional.

Tech Stack

Python

OpenRouteService API

KML / GeoJSON / custom coordinate exports

Leaflet-compatible output

Command-line scripts (no UI, by design)

Files

snap_route_ors.py — snaps raw points to road graph

export_coords.py — exports clean coordinate lists

coords.txt — final route coordinates

route.geojson — map-ready route

route_leaflet.json — Leaflet-friendly format

Important Notes

This is an approximation, not an official race route

Routing engines optimize for road legality, not ceremony

Small detours are expected behavior, not bugs

Exact perfection is often worse than usable accuracy

Shipping beats obsessing.

Why This Exists

This repo documents the invisible work behind “simple” map features —
and why building real products means making engineering tradeoffs, not chasing illusions of perfection.
