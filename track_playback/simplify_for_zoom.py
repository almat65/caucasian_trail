"""Further simplify track_playback/json/track_simplified.geojson for zoom 10-11 display.

Re-runs Visvalingam-Whyatt on the already-simplified track, but stops based on a
meters-deviation threshold derived from Web Mercator ground resolution at TARGET_ZOOM,
instead of a fixed point-count target. A zig-zag smaller than PIXEL_TOLERANCE screen
pixels at that zoom is visually indistinguishable from a straight line and gets dropped;
real turns (large deviation) are kept regardless of how many points that takes.

Zoom 11 is the stricter of the 10-11 range (smaller meters/pixel), so satisfying it
also satisfies zoom 10.
"""

import heapq
import json
import math
from pathlib import Path

TARGET_ZOOM = 11
PIXEL_TOLERANCE = 1.0  # drop zig-zags under this many screen pixels

SRC = Path(__file__).parent / "json" / "track_simplified.geojson"
DST = Path(__file__).parent / "json" / "track_simplified_zoom11.geojson"


def meters_per_pixel(zoom: float, lat_deg: float) -> float:
    return 156543.03392804097 * math.cos(math.radians(lat_deg)) / (2 ** zoom)


def _project(lon: float, lat: float, lat0: float) -> tuple[float, float]:
    """Local equirectangular projection to meters; accurate for the short distances between neighbors."""
    x = lon * 111320.0 * math.cos(math.radians(lat0))
    y = lat * 110574.0
    return x, y


def _triangle_area_m2(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float]) -> float:
    return abs((b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])) / 2.0


def simplify_by_deviation(coords: list[list[float]], threshold_m: float) -> list[list[float]]:
    n = len(coords)
    if n <= 2:
        return coords

    lat0 = sum(c[1] for c in coords) / n
    pts_m = [_project(lon, lat, lat0) for lon, lat in coords]

    prev: list[int | None] = [i - 1 for i in range(n)]
    nxt: list[int | None] = [i + 1 for i in range(n)]
    prev[0] = None
    nxt[n - 1] = None
    alive = [True] * n
    current_dev = [0.0] * n

    def deviation(i: int) -> float:
        p, q = prev[i], nxt[i]
        if p is None or q is None:
            return math.inf
        area = _triangle_area_m2(pts_m[p], pts_m[i], pts_m[q])
        base = math.hypot(pts_m[q][0] - pts_m[p][0], pts_m[q][1] - pts_m[p][1])
        return (2 * area / base) if base > 0 else math.inf

    heap: list[tuple[float, int, int]] = []
    counter = 0

    def push(i: int) -> None:
        nonlocal counter
        if prev[i] is None or nxt[i] is None:
            return
        d = deviation(i)
        current_dev[i] = d
        counter += 1
        heapq.heappush(heap, (d, counter, i))

    for i in range(n):
        push(i)

    while heap:
        d, _, i = heap[0]
        # Stale entry: node already removed, or a later push recorded a different deviation for it.
        if not alive[i] or prev[i] is None or nxt[i] is None or d != current_dev[i]:
            heapq.heappop(heap)
            continue
        if d >= threshold_m:
            break
        heapq.heappop(heap)
        alive[i] = False
        p, q = prev[i], nxt[i]
        nxt[p] = q
        prev[q] = p
        push(p)
        push(q)

    return [coords[i] for i in range(n) if alive[i]]


def main() -> None:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    coords = data["features"][0]["geometry"]["coordinates"]
    lat0 = sum(c[1] for c in coords) / len(coords)
    threshold_m = meters_per_pixel(TARGET_ZOOM, lat0) * PIXEL_TOLERANCE

    simplified = simplify_by_deviation(coords, threshold_m)
    data["features"][0]["geometry"]["coordinates"] = simplified

    DST.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    print(f"zoom {TARGET_ZOOM} threshold: {threshold_m:.1f} m/px (lat {lat0:.2f})")
    print(f"{len(coords)} -> {len(simplified)} points ({len(simplified) / len(coords):.1%} kept)")
    print(f"written to {DST}")


if __name__ == "__main__":
    main()
