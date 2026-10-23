"""Produce a smooth (spline-rounded), evenly-spaced track for zoom 10 display.

Point-dropping simplification (see simplify_for_zoom.py) only deletes vertices --
whatever remains is still a straight line between the original jagged points, so
corners stay sharp. This script instead:

1. Picks "key point" anchors with the same deviation-threshold VW, tuned to
   TARGET_ZOOM's pixel resolution.
2. Fits a centripetal Catmull-Rom spline through those anchors -- passes exactly
   through each anchor, but bends smoothly in between instead of going straight.
   Centripetal parametrization avoids the loops/overshoot that plain (uniform)
   Catmull-Rom can produce on sharp zig-zags.
3. Resamples the spline at a uniform ~50 m arc-length spacing for the final track.

All math is done in a local equirectangular projection (meters) centered on the
track's average latitude, then projected back to lon/lat for output.
"""

import heapq
import json
import math
from pathlib import Path

TARGET_ZOOM = 8
PIXEL_TOLERANCE = 1.0  # anchor threshold: drop zig-zags under this many screen pixels
RESAMPLE_SPACING_M = 50.0
DENSE_STEP_M = 5.0  # spline sampling resolution before the final resample
MIN_SAMPLES_PER_SEGMENT = 8
ALPHA = 0.5  # centripetal Catmull-Rom

SRC = Path(__file__).parent / "json" / "track_simplified.geojson"
DST = Path(__file__).parent / "json" / "track_smoothed_zoom8.geojson"


def meters_per_pixel(zoom: float, lat_deg: float) -> float:
    return 156543.03392804097 * math.cos(math.radians(lat_deg)) / (2 ** zoom)


def _project(lon: float, lat: float, lat0: float) -> tuple[float, float]:
    x = lon * 111320.0 * math.cos(math.radians(lat0))
    y = lat * 110574.0
    return x, y


def _unproject(x: float, y: float, lat0: float) -> tuple[float, float]:
    lon = x / (111320.0 * math.cos(math.radians(lat0)))
    lat = y / 110574.0
    return lon, lat


def _triangle_area_m2(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float]) -> float:
    return abs((b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])) / 2.0


def pick_anchors(pts_m: list[tuple[float, float]], threshold_m: float) -> list[tuple[float, float]]:
    """Visvalingam-Whyatt, removing points while their deviation stays below threshold_m."""
    n = len(pts_m)
    if n <= 2:
        return pts_m

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

    return [pts_m[i] for i in range(n) if alive[i]]


def _reflect(a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:
    """Virtual point mirroring b through a, used as a boundary control point."""
    return (2 * a[0] - b[0], 2 * a[1] - b[1])


def _lerp(pa, pb, ta, tb, t):
    if tb == ta:
        return pa
    f = (t - ta) / (tb - ta)
    return (pa[0] + (pb[0] - pa[0]) * f, pa[1] + (pb[1] - pa[1]) * f)


def _segment_samples(p0, p1, p2, p3, n_samples):
    def tj(ti, pi, pj):
        d = math.hypot(pj[0] - pi[0], pj[1] - pi[1]) ** ALPHA
        return ti + (d if d > 1e-9 else 1e-6)

    t0 = 0.0
    t1 = tj(t0, p0, p1)
    t2 = tj(t1, p1, p2)
    t3 = tj(t2, p2, p3)

    points = []
    for i in range(n_samples):
        t = t1 + (t2 - t1) * i / n_samples
        a1 = _lerp(p0, p1, t0, t1, t)
        a2 = _lerp(p1, p2, t1, t2, t)
        a3 = _lerp(p2, p3, t2, t3, t)
        b1 = _lerp(a1, a2, t0, t2, t)
        b2 = _lerp(a2, a3, t1, t3, t)
        points.append(_lerp(b1, b2, t1, t2, t))
    return points


def fit_spline(anchors: list[tuple[float, float]]) -> list[tuple[float, float]]:
    n = len(anchors)
    if n <= 2:
        return anchors

    dense: list[tuple[float, float]] = []
    for i in range(n - 1):
        p1, p2 = anchors[i], anchors[i + 1]
        p0 = anchors[i - 1] if i > 0 else _reflect(anchors[0], anchors[1])
        p3 = anchors[i + 2] if i + 2 < n else _reflect(anchors[-1], anchors[-2])
        chord_m = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        n_samples = max(MIN_SAMPLES_PER_SEGMENT, math.ceil(chord_m / DENSE_STEP_M))
        dense.extend(_segment_samples(p0, p1, p2, p3, n_samples))
    dense.append(anchors[-1])
    return dense


def resample_uniform(dense: list[tuple[float, float]], spacing_m: float) -> list[tuple[float, float]]:
    out = [dense[0]]
    accum = 0.0  # distance covered since the last emitted point, carried across segments
    for i in range(len(dense) - 1):
        a, b = dense[i], dense[i + 1]
        seg_len = math.hypot(b[0] - a[0], b[1] - a[1])
        if seg_len == 0:
            continue
        seg_pos = 0.0
        while accum + (seg_len - seg_pos) >= spacing_m:
            seg_pos += spacing_m - accum
            accum = 0.0
            f = seg_pos / seg_len
            out.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
        accum += seg_len - seg_pos
    if out[-1] != dense[-1]:
        out.append(dense[-1])
    return out


def main() -> None:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    coords = data["features"][0]["geometry"]["coordinates"]
    lat0 = sum(c[1] for c in coords) / len(coords)
    threshold_m = meters_per_pixel(TARGET_ZOOM, lat0) * PIXEL_TOLERANCE

    pts_m = [_project(lon, lat, lat0) for lon, lat in coords]
    anchors = pick_anchors(pts_m, threshold_m)
    dense = fit_spline(anchors)
    resampled = resample_uniform(dense, RESAMPLE_SPACING_M)

    out_coords = [list(_unproject(x, y, lat0)) for x, y in resampled]
    data["features"][0]["geometry"]["coordinates"] = out_coords

    DST.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    print(f"zoom {TARGET_ZOOM} anchor threshold: {threshold_m:.1f} m (lat {lat0:.2f})")
    print(f"{len(coords)} points -> {len(anchors)} anchors -> {len(resampled)} smoothed points")
    print(f"written to {DST}")


if __name__ == "__main__":
    main()
