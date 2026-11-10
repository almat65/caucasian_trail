"""Merge all data/daily_tracks_simplified/day_NN.geojson files into one single-line track.

Concatenates each day's LineString coordinates (sorted by day number) into a single
LineString feature and writes it to data/track_simplified.geojson.
"""

import json
import re
from pathlib import Path

SRC_DIR = Path(__file__).parent / "data" / "daily_tracks_simplified"
DST_PATH = Path(__file__).parent / "data" / "track_simplified.geojson"

DAY_RE = re.compile(r"^day_(\d+)\.geojson$")


def day_number(path: Path) -> int | None:
    m = DAY_RE.match(path.name)
    return int(m.group(1)) if m else None


def main() -> None:
    day_files = sorted(
        (p for p in SRC_DIR.glob("day_*.geojson") if day_number(p) is not None),
        key=day_number,
    )

    merged_coords: list[list[float]] = []
    for path in day_files:
        data = json.loads(path.read_text(encoding="utf-8"))
        for feature in data["features"]:
            if feature["geometry"]["type"] == "LineString":
                merged_coords.extend(feature["geometry"]["coordinates"])

    result = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "LineString", "coordinates": merged_coords},
                "properties": {"name": "Track"},
            }
        ],
    }

    DST_PATH.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
    print(f"Merged {len(day_files)} day files -> {DST_PATH.name} ({len(merged_coords)} points)")


if __name__ == "__main__":
    main()
