// Leaflet-based player: cumulative polyline + slider-based seek/speed controls.

// Closest track vertex to a POI's coordinate -- used to decide when playback has "reached" it.
function nearestTrackIndex(coords, [lon, lat]) {
  let bestI = 0;
  let bestD = Infinity;
  for (let i = 0; i < coords.length; i++) {
    const dx = coords[i][0] - lon;
    const dy = coords[i][1] - lat;
    const d = dx * dx + dy * dy;
    if (d < bestD) {
      bestD = d;
      bestI = i;
    }
  }
  return bestI;
}

// Fill in your own free-tier keys to enable the providers below that need one.
const API_KEYS = {
  stadia: '',
  thunderforest: '',
  maptiler: '',
};

// Raster basemaps. Each entry feeds an L.tileLayer directly; keyed ones are skipped until an API key is set above.
const BASEMAPS = {
  osm: {
    label: 'OpenStreetMap',
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    options: { attribution: '\u00a9 OpenStreetMap contributors', maxZoom: 19 },
  },
  opentopo: {
    label: 'OpenTopoMap (terrain)',
    url: 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
    options: {
      attribution: '\u00a9 OpenStreetMap contributors, SRTM | \u00a9 OpenTopoMap (CC-BY-SA)',
      maxZoom: 17,
    },
  },
  esriImagery: {
    label: 'Esri World Imagery',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    options: { attribution: '\u00a9 Esri', maxZoom: 19 },
  },
  esriTopo: {
    label: 'Esri World Topo',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
    options: { attribution: '\u00a9 Esri', maxZoom: 19 },
  },
  stadiaTerrain: {
    label: 'Stadia Stamen Terrain',
    url: `https://tiles.stadiamaps.com/tiles/stamen_terrain/{z}/{x}/{y}.png?api_key=${API_KEYS.stadia}`,
    options: { attribution: '\u00a9 Stadia Maps, \u00a9 Stamen Design, \u00a9 OpenStreetMap contributors', maxZoom: 18 },
    needsKey: 'stadia',
  },
  thunderforestOutdoors: {
    label: 'Thunderforest Outdoors',
    url: `https://{s}.tile.thunderforest.com/outdoors/{z}/{x}/{y}.png?apikey=${API_KEYS.thunderforest}`,
    options: { attribution: '\u00a9 Thunderforest, \u00a9 OpenStreetMap contributors', maxZoom: 22 },
    needsKey: 'thunderforest',
  },
  thunderforestLandscape: {
    label: 'Thunderforest Landscape',
    url: `https://{s}.tile.thunderforest.com/landscape/{z}/{x}/{y}.png?apikey=${API_KEYS.thunderforest}`,
    options: { attribution: '\u00a9 Thunderforest, \u00a9 OpenStreetMap contributors', maxZoom: 22 },
    needsKey: 'thunderforest',
  },
  maptilerOutdoor: {
    label: 'MapTiler Outdoor',
    url: `https://api.maptiler.com/maps/outdoor-v2/{z}/{x}/{y}.png?key=${API_KEYS.maptiler}`,
    options: { attribution: '\u00a9 MapTiler, \u00a9 OpenStreetMap contributors', maxZoom: 20 },
    needsKey: 'maptiler',
  },
};
const DEFAULT_BASEMAP = 'osm';

export async function mount({ root, coords, pois = [] }) {
  const { createPlayer, speed } = await import('./app.js');

  const basemapOptions = Object.entries(BASEMAPS)
    .map(([key, { label, needsKey }]) => {
      const missingKey = needsKey && !API_KEYS[needsKey];
      const selected = key === DEFAULT_BASEMAP ? ' selected' : '';
      const suffix = missingKey ? ' (needs API key)' : '';
      return `<option value="${key}"${selected}>${label}${suffix}</option>`;
    })
    .join('');

  root.innerHTML = `
    <div id="map" class="map"></div>
    <div class="panel panel-top-left">
      <button id="playBtn">\u25b6 Play</button>
      <label>Speed
        <input id="speedRange" type="range" min="1" max="100" value="50" />
      </label>
      <label>Seek
        <input id="seekRange" type="range" min="0" max="${coords.length}" value="0" />
      </label>
      <label><input id="showFullTrack" type="checkbox" checked /> Show full track</label>
      <label>Basemap
        <select id="basemapSelect">${basemapOptions}</select>
      </label>
      <span id="count"></span>
    </div>
  `;

  const latlngs = coords.map(([lon, lat]) => [lat, lon]);

  const map = L.map(root.querySelector('#map'));
  const basemapSelect = root.querySelector('#basemapSelect');
  let baseLayer;
  const setBasemap = (key) => {
    const config = BASEMAPS[key] ?? BASEMAPS[DEFAULT_BASEMAP];
    if (config.needsKey && !API_KEYS[config.needsKey]) {
      alert(`Add your ${config.needsKey} API key to API_KEYS in player.js to use ${config.label}.`);
      basemapSelect.value = DEFAULT_BASEMAP;
      return setBasemap(DEFAULT_BASEMAP);
    }
    if (baseLayer) map.removeLayer(baseLayer);
    baseLayer = L.tileLayer(config.url, config.options).addTo(map);
  };
  setBasemap(DEFAULT_BASEMAP);
  map.fitBounds(L.latLngBounds(latlngs), { padding: [20, 20] });

  const fullTrack = L.polyline(latlngs, { color: '#dc2626', weight: 3, opacity: 0.55 }).addTo(map);
  const drawn = L.polyline([], { color: '#2563eb', weight: 4 }).addTo(map);
  const head = L.circleMarker(latlngs[0], {
    radius: 6,
    color: '#dc2626',
    fillColor: '#ef4444',
    fillOpacity: 1,
  }).addTo(map);

  // Hidden until playback reaches each POI's nearest point on the track.
  const poiMarkers = pois.map((poi) => {
    const index = nearestTrackIndex(coords, poi.coordinates);
    const icon = L.divIcon({ className: 'poi-icon', html: poi.emoji, iconSize: [26, 26] });
    const marker = L.marker([poi.coordinates[1], poi.coordinates[0]], { icon, opacity: 0 }).addTo(map);
    if (poi.label) marker.bindTooltip(poi.label, { permanent: true, direction: 'right', className: 'poi-label' });
    return { marker, index };
  });

  const player = createPlayer(coords.length);
  const playBtn = root.querySelector('#playBtn');
  const speedInput = root.querySelector('#speedRange');
  const seekInput = root.querySelector('#seekRange');
  const showFullTrackInput = root.querySelector('#showFullTrack');
  const countEl = root.querySelector('#count');

  showFullTrackInput.addEventListener('change', () => {
    if (showFullTrackInput.checked) fullTrack.addTo(map);
    else map.removeLayer(fullTrack);
  });

  basemapSelect.addEventListener('change', () => setBasemap(basemapSelect.value));

  const applySpeed = () => {
    player.setSpeed(speed.pointsPerSecond(coords.length, Number(speedInput.value), 1, 100));
  };
  applySpeed();
  speedInput.addEventListener('input', applySpeed);
  seekInput.addEventListener('input', () => player.seek(Number(seekInput.value)));

  playBtn.addEventListener('click', () => {
    if (player.playing) {
      player.pause();
      playBtn.textContent = '\u25b6 Play';
      return;
    }
    if (player.index >= player.total) player.seek(0);
    player.play();
    playBtn.textContent = '\u23f8 Pause';
  });

  const unsubscribe = player.subscribe((index, total) => {
    drawn.setLatLngs(latlngs.slice(0, Math.max(1, index)));
    head.setLatLng(latlngs[Math.max(0, index - 1)]);
    poiMarkers.forEach(({ marker, index: poiIndex }) => {
      const visible = index >= poiIndex;
      marker.setOpacity(visible ? 1 : 0);
      const tooltip = marker.getTooltip();
      if (tooltip) tooltip.setOpacity(visible ? 0.9 : 0);
    });
    seekInput.value = String(index);
    countEl.textContent = `${index.toLocaleString()} / ${total.toLocaleString()}`;
    if (index >= total) playBtn.textContent = '\u25b6 Replay';
  });

  return {
    destroy() {
      unsubscribe();
      player.pause();
      map.remove();
    },
  };
}
