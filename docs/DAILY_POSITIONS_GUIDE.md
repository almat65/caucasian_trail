# Daily Position Tracking - Quick Start Guide

## ✅ What's Been Updated

### 1. **New File Structure** ([actual_position.geojson](actual_position.geojson))
Your daily positions now have a clean, organized structure:

```json
{
  "id": 1,
  "day": "Day 1",
  "date": "2026-06-09",
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
- ✅ 5 Tent nights (⛺)
- ✅ 1 Guest house night (🏠)
- ✅ Day 1 has YouTube video embedded
- ✅ Day 6 has photos linked

## 📝 How to Add a New Day

### Step 1: Copy This Template
```json
{
  "type": "Feature",
  "properties": {
    "id": 7,
    "day": "Day 7",
    "date": "2026-06-15",
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
2. **day**: Change to your day number (e.g., "Day 7", "Day 8")
3. **date**: Use YYYY-MM-DD format (e.g., "2026-06-15")
4. **accommodation_type**: Choose: `"tent"`, `"glamping"`, `"hotel"`, or `"guesthouse"`
5. **youtube_url**: Paste full YouTube URL (or leave empty `""`)
6. **notes**: Add any notes about the day
7. **photos**: Add photo filenames like `["day7.jpg", "sunrise.jpg"]`
8. **coordinates**: [longitude, latitude] from Google Maps

### Step 3: Add to File
1. Open [actual_position.geojson](actual_position.geojson)
2. Find the last feature (currently Day 6)
3. Add a **comma** after the closing `}`
4. Paste your new day
5. Save the file
6. Refresh the browser

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

The video will automatically embed in the popup!

## 📸 Photos

1. Add photos to `volodya_photos/` folder
2. Reference by filename only: `["photo.jpg"]`
3. Multiple photos: `["photo1.jpg", "photo2.jpg", "photo3.jpg"]`
4. Photos appear in popup and open full-size when clicked

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
    "day": "Day 7",
    "date": "2026-06-15",
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
- Popup showing "Day 7" with blue color
- Date: 2026-06-15
- Accommodation type: Hotel
- Embedded YouTube video
- Your notes
- 2 clickable photos

---

Need help? Check [actual_position_TEMPLATE.js](actual_position_TEMPLATE.js) for more detailed examples!
