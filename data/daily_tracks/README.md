# Daily Tracks Folder

This folder contains GPS tracks recorded from smartwatches/GPS devices for each day of the hike.

## File Naming Convention

Use the format: `day_XX.geojson` where XX is the day number (with leading zero)

Examples:
- `day_01.geojson` - Track for Day 1
- `day_02.geojson` - Track for Day 2
- `day_15.geojson` - Track for Day 15

## File Format

**GeoJSON** format (LineString geometry)

## Converting from GPX

Most smartwatches export GPX format. Convert to GeoJSON:

### Online Converters:
- https://mygeodata.cloud/converter/gpx-to-geojson
- https://geojson.io (paste GPX, export as GeoJSON)

### Command Line (using ogr2ogr):
```bash
ogr2ogr -f GeoJSON day_01.geojson track.gpx
```

## Usage

1. Export GPS track from your smartwatch (usually GPX format)
2. Convert to GeoJSON
3. Rename to `day_XX.geojson` (matching day number from actual_position.geojson)
4. Drop file in this folder
5. Refresh the map - the track will automatically load!

## Map Display

- All daily tracks are combined into a single "Actual Track" layer
- Toggle on/off via the Layers control
- Displayed in a different color from the planned route
- Missing days are silently skipped (no errors)

## Notes

- Not all days need tracks - only add files when you have GPS data
- Files load automatically - no code changes needed
- Keep day numbers consistent with `actual_position.geojson`
