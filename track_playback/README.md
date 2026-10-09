# Track Playback — User Guide

This app shows a GPS track being drawn gradually on a map, like a replay, with waypoints
(POIs) that appear as the track passes them. No programming knowledge needed to update
the track or tweak how it looks — just follow the steps below.

## 1. Preparing your track file

Raw GPS tracks often have way too many points (thousands), which makes the replay choppy
or pointlessly slow to load. We simplify the track first, then put it in this project.

### Step 1 — Simplify the track with Mapshaper

1. Go to **https://mapshaper.org/**.
2. Drag and drop your original `.geojson` track file onto the page.
3. In the simplification panel, choose the **"Visvalingam / weighted area"** option
   (it's the third option in the list).
4. Set the simplification slider/value to **1%**.
5. Click **Export** and download the simplified `.geojson` file.

### Step 2 — Check the point density (should be ~100 points per 10 km)

We want roughly **100 points for every 10 km** of track — enough detail to look smooth,
without being excessive.

1. Open the simplified `.geojson` file in a text editor and copy its contents.
2. Go to **https://www.bookify.com/apps/route-length-calculator**.
3. Paste the GeoJSON content in and check the results:
   - It tells you the total route length (e.g. 60 km).
   - Count the points in the file (or use the point count the tool shows, if available).
4. Check the ratio: for example, a 60 km route should have around **600 points**
   (60 km ÷ 10 km × 100 points = 600 points).
   - **Too many points** (e.g. 1,500 for 60 km) → go back to Mapshaper and simplify a
     bit more (increase the percentage removed, i.e. lower the "kept" %).
   - **Too few points** (e.g. 200 for 60 km) → simplify less (keep a higher %).

### Step 3 — Put the file into the project

1. Rename your simplified file to exactly: **`track.geojson`**
2. Copy it into the `json` folder of this project, replacing the existing file:
   ```
   json/track.geojson
   ```
3. Refresh the app in your browser — it will automatically load the new track.

## 2. Editing the waypoints (POIs)

Waypoints are the little emoji markers (⛺ 💧 📸 …) that appear on the map once the
replay passes their location, along with a text label.

Open **`json/POI.geojson`** in a text editor. It looks like this:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": { "type": "Point", "coordinates": [39.76918053, 43.86044283] },
      "properties": { "emoji": "⛺", "label": "Camp night 1" }
    },
    {
      "type": "Feature",
      "geometry": { "type": "Point", "coordinates": [39.6798875, 43.80441731] },
      "properties": { "emoji": "💧", "label": "Water refill" }
    }
  ]
}
```

To add, remove, or change a waypoint:
- **`coordinates`**: `[longitude, latitude]` — note longitude comes **first**. You can get
  these from Google Maps (right-click a spot → the numbers shown are `latitude, longitude`,
  so just swap the order), or from Mapshaper/any GIS tool.
- **`emoji`**: any single emoji, shown as the marker icon.
- **`label`**: the text shown next to the marker.

To add a new waypoint, copy one of the `{ "type": "Feature", ... }` blocks, paste it
before the closing `]`, add a comma after the previous one, and fill in your own
coordinates/emoji/label.

## 3. Customizing playback speed

Speed is controlled in **`app.js`**, in a block near the top called `speed`:

```js
export const speed = {
  minDurationS: 5,  // fastest (slider all the way to the right)
  maxDurationS: 35, // slowest (slider all the way to the left)
  ...
};
```

- `minDurationS` = how many seconds the **full replay** takes at the fastest slider
  setting. Lower number = faster.
- `maxDurationS` = how many seconds the full replay takes at the slowest slider setting.
  Higher number = slower.

Example: if you want the replay to always take between 10 and 60 seconds, change it to:

```js
export const speed = {
  minDurationS: 10,
  maxDurationS: 60,
  ...
};
```

No other changes needed — the Speed slider in the app automatically uses these values.

## 4. Customizing the look (symbology)

### Track lines

In **`player.js`**, look for these two lines:

```js
const fullTrack = L.polyline(latlngs, { color: '#dc2626', weight: 3, opacity: 0.55 }).addTo(map);
const drawn = L.polyline([], { color: '#2563eb', weight: 4 }).addTo(map);
```

- `fullTrack` is the **red** line showing the whole route ahead of time (toggled by the
  "Show full track" checkbox).
- `drawn` is the **blue** line showing progress so far.
- `color`: any color, written as a hex code (e.g. `#dc2626` is red, `#16a34a` is green,
  `#000000` is black). You can pick colors visually at **https://htmlcolorcodes.com/**.
- `weight`: line thickness in pixels. Bigger number = thicker line.
- `opacity`: 0 (invisible) to 1 (fully solid).

### The moving marker (current position)

Just below, the small circle that marks the current position:

```js
const head = L.circleMarker(latlngs[0], {
  radius: 6,
  color: '#dc2626',
  fillColor: '#ef4444',
  fillOpacity: 1,
}).addTo(map);
```

- `radius`: size of the circle in pixels.
- `color`: outline color.
- `fillColor`: inside color.

### POI markers and labels

The emoji size is set in **`style.css`**:

```css
.poi-icon {
  font-size: 20px;
  line-height: 26px;
  text-align: center;
}
```
Change `font-size` to make the emoji bigger/smaller.

The text label style (black text with a white outline) is also in **`style.css`**:

```css
.poi-label {
  font-size: 13px;
  font-weight: 700;
  color: #000;
  -webkit-text-stroke: 3px #fff;
  ...
}
```
- `font-size`: text size.
- `color`: text color.
- `-webkit-text-stroke`: the thickness and color of the white outline around the text.

## 5. Running the app

This app needs to be opened through a local web address (`http://localhost:...`), not by
double-clicking `index.html` directly — double-clicking won't load the track/POI files
correctly due to browser security restrictions.

### Easiest way — VS Code + Live Server (no command line needed)

1. Install **VS Code**: https://code.visualstudio.com/ (just a normal installer).
2. Open VS Code, click the **Extensions** icon in the left sidebar (four squares icon),
   search for **"Live Server"** (by Ritwick Dey), and click **Install**.
3. In VS Code, go to **File → Open Folder** and open this project's folder.
4. In the file list on the left, right-click **`index.html`** and choose
   **"Open with Live Server"**.
5. Your browser opens automatically at a working address — the app just works.

### Alternative — if Node.js is already installed

Open a terminal in this folder and run:
```
npx serve .
```
Then open the web address it prints (usually `http://localhost:3000` or similar) in your
browser.
