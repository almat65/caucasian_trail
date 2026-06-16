# Daily Position Tracking - Quick Start Guide

## ✅ What's Been Updated

### 1. **New File Structure** ([actual_position.geojson](actual_position.geojson))
Your daily positions now have a clean, organized structure with statistics tracking:

```json
{
  "id": 1,
  "day": "1",
  "date": "2026-06-09",
  "location": "Khiv Village",
  "distance_km": 28,
  "elevation_gain": 1450,
  "accommodation_type": "tent",
  "youtube_url": "https://www.youtube.com/shorts/yH0g2j4q_Ak",
  "notes": "Your notes here",
  "photos": ["photo1.jpg", "photo2.jpg"]
}
```

### 2. **Four Accommodation Types**
Each type has its own icon and color:

| Type | Icon | Color | Label |
|------|------|-------|-------|
| `tent` | ⛺ | Green | Tent Camping |
| `glamping` | 🏕️ | Orange | Glamping |
| `guesthouse` | 🏠 | Purple | Guest House |
| `hotel` | 🏨 | Blue | Hotel |

### 3. **Current Data**
Your map now shows:
- ✅ Overnight stops with accommodation icons
- ✅ Daily distance and elevation gain statistics
- ✅ Real-time progress tracking on main page
- ✅ YouTube videos embedded in map popups
- ✅ Photo carousel with multiple images
- ✅ Bilingual support (English/Russian)

## 📝 How to Add a New Day

### Step 1: Copy This Template
```json
{
  "type": "Feature",
  "properties": {
    "id": 7,
    "day": "7",
    "date": "2026-06-15",
    "location": "Village Name",
    "distance_km": 28,
    "elevation_gain": 1450,
    "accommodation_type": "tent",
    "youtube_url": "",
    "notes": "",
    "photos": []
  },
  "geometry": {
    "type": "Point",
    "coordinates": [47.123456, 42.654321]
  }
}
```

### Step 2: Fill in Your Details
1. **id**: Use the next sequential number (e.g., if last is 6, use 7)
2. **day**: Use just the number as string (e.g., "7", "8", or "10-12" for multi-day stays)
3. **date**: Use YYYY-MM-DD format (e.g., "2026-06-15")
4. **location**: Name of nearest village or landmark (e.g., "Khiv Village", "Near Bazarduzu Pass")
5. **distance_km**: Distance covered that day in kilometers (use 0 for rest days)
6. **elevation_gain**: Elevation gained that day in meters (use 0 for rest days)
7. **accommodation_type**: Choose: `"tent"`, `"glamping"`, `"hotel"`, or `"guesthouse"`
8. **youtube_url**: Paste full YouTube URL (or leave empty `""`)
9. **notes**: Add any notes about the day
10. **photos**: Add photo filenames from assets/photos/ like `["day7.jpg", "sunrise.jpg"]`
11. **coordinates**: [longitude, latitude] from Google Maps

### Step 3: Add to File
1. Open [actual_position.geojson](actual_position.geojson)
2. Find the last feature
3. Add a **comma** after the closing `}`
4. Paste your new day
5. Save the file
6. Refresh the browser - progress stats update automatically!

## 🗺️ Getting GPS Coordinates

### From Google Maps:
1. Right-click on location
2. Click "What's here?"
3. Copy coordinates (shown at bottom)
4. **IMPORTANT**: Swap the order!
   - Google shows: `42.123456, 47.654321` (latitude, longitude)
   - GeoJSON needs: `[47.654321, 42.123456]` (longitude, latitude)

## 🎬 YouTube Videos

Any YouTube URL format works:
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/shorts/VIDEO_ID`

The video will automatically embed in the popup and appear in the media carousel!

## 📸 Photos

1. Add photos to `assets/photos/` folder
2. Reference by filename only: `["photo.jpg"]`
3. Multiple photos: `["photo1.jpg", "photo2.jpg", "photo3.jpg"]`
4. Photos appear in media carousel alongside videos (swipeable)
5. Clicking a photo opens it full-size in new tab

## 🎨 Legend

The updated legend shows:
- Hiking Track (blue line)
- **Daily Accommodations:**
  - ⛺ Tent
  - 🏕️ Glamping
  - 🏠 Guest House
  - 🏨 Hotel
- **Points of Interest:**
  - ⛰️ Passes
  - 🌊 River Crossings
  - ⚠️ Danger Zones
  - 🚧 Checkpoints

## ⚠️ Common Mistakes to Avoid

1. ❌ Forgetting comma between features
2. ❌ Using single quotes `'` instead of double quotes `"`
3. ❌ Wrong coordinate order (remember: longitude first!)
4. ❌ Typo in accommodation_type (must be exact: "tent", not "Tent")
5. ❌ Invalid JSON (use a JSON validator if unsure)

## 📁 Files Reference

- **[actual_position.geojson](actual_position.geojson)** - Your daily positions data
- **[actual_position_TEMPLATE.js](actual_position_TEMPLATE.js)** - Detailed template with examples
- **[app.js](app.js)** - Updated to handle accommodation types
- **[map.html](map.html)** - Updated legend

## 🧪 Testing

Visit: **http://localhost:8000/map.html**

- Look for your accommodation markers (⛺🏕️🏠🏨)
- Click on markers to see popups
- Check that YouTube videos embed correctly
- Verify photos display and open when clicked

## 🚀 Example: Adding Day 7

```json
{
  "type": "Feature",
  "properties": {
    "id": 7,
    "day": "7",
    "date": "2026-06-15",
    "location": "Khiv Village",
    "distance_km": 0,
    "elevation_gain": 0,
    "accommodation_type": "hotel",
    "youtube_url": "https://www.youtube.com/watch?v=xyz123",
    "notes": "Rest day in town. Hot shower was amazing!",
    "photos": ["day7_hotel.jpg", "day7_food.jpg"]
  },
  "geometry": {
    "type": "Point",
    "coordinates": [47.456789, 42.123456]
  }
}
```

This would add:
- 🏨 Blue hotel marker on the map
- Popup showing "Day 7" (translated: День 7 in Russian)
- Date: 2026-06-15
- Location: Khiv Village
- Rest day statistics: 0 km, 0 m elevation
- Accommodation type: Hotel
- Embedded YouTube video in carousel
- Your notes
- 2 photos in carousel (swipeable with video)

---

Need help? Check [actual_position_TEMPLATE.js](actual_position_TEMPLATE.js) for more detailed examples!
