"""Simplify daily track GeoJSON lines using Visvalingam-Whyatt, targeting a fixed point density.

Reads every data/daily_tracks/day_*.geojson, simplifies each LineString to
roughly 100 points per 10 km (i.e. 10 points/km) of real-world line length,
and writes the result to data/daily_tracks_simplified/ with the same filename.

Pure-stdlib implementation (no numpy/pyproj/simplification) because this project's
venv is on a pre-release Python (3.15) for which those packages have no compiled wheels yet.
"""

import heapq
import json
import math
from pathlib import Path

POINTS_PER_KM = 10  # 100 points per 10 km
MIN_POINTS = 2
EARTH_RADIUS_KM = 6371.0088

SRC_DIR = Path(__file__).parent / "data" / "daily_tracks"
DST_DIR = Path(__file__).parent / "data" / "daily_tracks_simplified"


def haversine_km(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def line_length_km(coords: list[list[float]]) -> float:
    return sum(
        haversine_km(coords[i][0], coords[i][1], coords[i + 1][0], coords[i + 1][1])
        for i in range(len(coords) - 1)
    )


def _triangle_area(a: list[float], b: list[float], c: list[float]) -> float:
    return abs((b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])) / 2.0


def _vw_importance_order(coords: list[list[float]]) -> list[int]:
    """Indices ordered most-important-first (VW removal rank), endpoints always first."""
    n = len(coords)
    if n <= 2:
        return list(range(n))

    prev: list[int | None] = [i - 1 for i in range(n)]
    nxt: list[int | None] = [i + 1 for i in range(n)]
    prev[0] = None
    nxt[n - 1] = None
    alive = [True] * n
    current_area = [0.0] * n

    def area(i: int) -> float:
        p, q = prev[i], nxt[i]
        if p is None or q is None:
            return math.inf
        return _triangle_area(coords[p], coords[i], coords[q])

    heap: list[tuple[float, int, int]] = []
    counter = 0

    def push(i: int) -> None:
        nonlocal counter
        if prev[i] is None or nxt[i] is None:
            return
        a = area(i)
        current_area[i] = a
        counter += 1
        heapq.heappush(heap, (a, counter, i))

    for i in range(n):
        push(i)

    removal_order: list[int] = []
    while heap:
        a, _, i = heapq.heappop(heap)
        # Stale entry: node was already removed, or a later push recorded a different area for it.
        if not alive[i] or prev[i] is None or nxt[i] is None or a != current_area[i]:
            continue

        removal_order.append(i)
        alive[i] = False
        p, q = prev[i], nxt[i]
        if p is not None:
            nxt[p] = q
        if q is not None:
            prev[q] = p
        if p is not None:
            push(p)
        if q is not None:
            push(q)

    return [0, n - 1] + list(reversed(removal_order))


def simplify_linestring(coords: list[list[float]]) -> list[list[float]]:
    n = len(coords)
    if n <= MIN_POINTS:
        return coords

    target_n = max(MIN_POINTS, round(line_length_km(coords) * POINTS_PER_KM))
    if target_n >= n:
        return coords

    importance_order = _vw_importance_order(coords)
    kept_idx = sorted(importance_order[:target_n])
    return [coords[i] for i in kept_idx]


def simplify_geometry(geometry: dict) -> dict:
    gtype = geometry["type"]
    if gtype == "LineString":
        return {"type": gtype, "coordinates": simplify_linestring(geometry["coordinates"])}
    if gtype == "MultiLineString":
        return {
            "type": gtype,
            "coordinates": [simplify_linestring(line) for line in geometry["coordinates"]],
        }
    return geometry


def simplify_file(src_path: Path, dst_path: Path) -> None:
    data = json.loads(src_path.read_text(encoding="utf-8"))

    total_before = total_after = 0
    for feature in data["features"]:
        before = _count_points(feature["geometry"])
        feature["geometry"] = simplify_geometry(feature["geometry"])
        after = _count_points(feature["geometry"])
        total_before += before
        total_after += after

    dst_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    print(f"{src_path.name}: {total_before} -> {total_after} points")


def _count_points(geometry: dict) -> int:
    if geometry["type"] == "LineString":
        return len(geometry["coordinates"])
    if geometry["type"] == "MultiLineString":
        return sum(len(line) for line in geometry["coordinates"])
    return 0


def main() -> None:
    DST_DIR.mkdir(parents=True, exist_ok=True)
    for src_path in sorted(SRC_DIR.glob("day_*.geojson")):
        simplify_file(src_path, DST_DIR / src_path.name)


if __name__ == "__main__":
    main()
