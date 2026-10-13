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
  }
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
      <label><input id="showLabels" type="checkbox" checked /> Show labels</label>
      <label><input id="showStats" type="checkbox" checked /> Show stats</label>
      <label>Basemap
        <select id="basemapSelect">${basemapOptions}</select>
      </label>
      <span id="count"></span>
    </div>
    <div id="statsPanel" class="panel panel-stats">
      <table class="stats-table">
        <tr><th>Day</th><td id="statDay"></td></tr>
        <tr><th>From</th><td id="statFrom"></td></tr>
        <tr><th>To</th><td id="statTo"></td></tr>
        <tr><th>Distance</th><td id="statDistance"></td></tr>
        <tr><th>Elevation gain</th><td id="statElevation"></td></tr>
      </table>
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

  const fullTrack = L.polyline(latlngs, { color: '#2563eb', weight: 3, opacity: 0.55 }).addTo(map);
  const drawn = L.polyline([], { color: '#dc2626', weight: 4 }).addTo(map);
  const head = L.circleMarker(latlngs[0], {
    radius: 6,
    color: '#dc2626',
    fillColor: '#ef4444',
    fillOpacity: 1,
  }).addTo(map);

  // Hidden until playback reaches each POI's nearest point on the track.
  const poiMarkers = pois.map((poi) => {
    const index = nearestTrackIndex(coords, poi.coordinates);
    const marker = L.circleMarker([poi.coordinates[1], poi.coordinates[0]], {
      radius: 6,
      color: '#dc2626',
      weight: 4,
      fillColor: '#fff',
      fillOpacity: 0,
      opacity: 0,
    }).addTo(map);
    // Label sits north-west of the marker, text anchored at its south-east corner.
    if (poi.label) marker.bindTooltip(poi.label, { permanent: true, direction: 'left', offset: [0, -8], className: 'poi-label' });

    return { marker, index, poi };
  });

  const player = createPlayer(coords.length);
  const playBtn = root.querySelector('#playBtn');
  const speedInput = root.querySelector('#speedRange');
  const seekInput = root.querySelector('#seekRange');
  const showFullTrackInput = root.querySelector('#showFullTrack');
  const showLabelsInput = root.querySelector('#showLabels');
  const showStatsInput = root.querySelector('#showStats');
  const statsPanel = root.querySelector('#statsPanel');
  const countEl = root.querySelector('#count');

  showFullTrackInput.addEventListener('change', () => {
    if (showFullTrackInput.checked) fullTrack.addTo(map);
    else map.removeLayer(fullTrack);
  });

  // Last playback index, kept so the checkbox can recompute tooltip visibility without waiting for the next tick.
  let lastIndex = 0;
  const updateLabelVisibility = () => {
    poiMarkers.forEach(({ marker, index: poiIndex }) => {
      const tooltip = marker.getTooltip();
      if (!tooltip) return;
      const visible = lastIndex >= poiIndex && showLabelsInput.checked;
      tooltip.setOpacity(visible ? 0.9 : 0);
    });
  };
  showLabelsInput.addEventListener('change', updateLabelVisibility);

  // Current "leg": last POI reached and the next one still ahead, by day order (not track distance).
  const updateStats = () => {
    let prevI = 0;
    for (let i = 0; i < poiMarkers.length; i++) {
      if (poiMarkers[i].index <= lastIndex) prevI = i;
      else break;
    }
    const prev = poiMarkers[prevI].poi;
    const next = poiMarkers[Math.min(prevI + 1, poiMarkers.length - 1)].poi;
    root.querySelector('#statDay').textContent = next.day ?? '';
    root.querySelector('#statFrom').textContent = prev.label ?? '';
    root.querySelector('#statTo').textContent = next.label ?? '';
    root.querySelector('#statDistance').textContent = next.distanceKm != null ? `${next.distanceKm} km` : '';
    root.querySelector('#statElevation').textContent = next.elevationGain != null ? `${next.elevationGain} m` : '';
  };

  showStatsInput.addEventListener('change', () => {
    statsPanel.style.display = showStatsInput.checked ? '' : 'none';
  });

  // Drag the stats panel by pointer; switches from centered transform to absolute left/top on first grab.
  let dragOffset = null;
  statsPanel.addEventListener('pointerdown', (e) => {
    const rect = statsPanel.getBoundingClientRect();
    dragOffset = { dx: e.clientX - rect.left, dy: e.clientY - rect.top };
    statsPanel.style.transform = 'none';
    statsPanel.style.left = `${rect.left}px`;
    statsPanel.style.top = `${rect.top}px`;
    statsPanel.setPointerCapture(e.pointerId);
  });
  statsPanel.addEventListener('pointermove', (e) => {
    if (!dragOffset) return;
    statsPanel.style.left = `${e.clientX - dragOffset.dx}px`;
    statsPanel.style.top = `${e.clientY - dragOffset.dy}px`;
  });
  statsPanel.addEventListener('pointerup', (e) => {
    dragOffset = null;
    statsPanel.releasePointerCapture(e.pointerId);
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
    lastIndex = index;
    poiMarkers.forEach(({ marker, index: poiIndex }) => {
      const visible = index >= poiIndex;
      marker.setStyle({ opacity: visible ? 1 : 0, fillOpacity: visible ? 1 : 0 });
      const tooltip = marker.getTooltip();
      if (tooltip) tooltip.setOpacity(visible && showLabelsInput.checked ? 0.9 : 0);
    });
    updateStats();
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
