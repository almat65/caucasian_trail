import { mount } from './player.js';

// Pure, player-agnostic playback driver: advances `index` based on elapsed wall-clock time
// (points/second), not a fixed-FPS assumption, so the configured duration holds on any display.
// No real timestamps exist in the source data, so "speed" is a target total playback duration.
export function createPlayer(total) {
  const listeners = new Set();
  const player = {
    total,
    index: 0,
    playing: false,
    pointsPerSecond: 1,
    _progress: 0,
    _lastTime: 0,
    _raf: null,
    subscribe(fn) {
      listeners.add(fn);
      fn(player.index, player.total);
      return () => listeners.delete(fn);
    },
    _emit() {
      listeners.forEach((fn) => fn(player.index, player.total));
    },
    play() {
      if (player.playing) return;
      player.playing = true;
      player._lastTime = performance.now();
      const step = (now) => {
        if (!player.playing) return;
        const dtSeconds = (now - player._lastTime) / 1000;
        player._lastTime = now;
        player._progress = Math.min(player.total, player._progress + player.pointsPerSecond * dtSeconds);
        player.index = Math.floor(player._progress);
        player._emit();
        if (player.index >= player.total) {
          player.playing = false;
          return;
        }
        player._raf = requestAnimationFrame(step);
      };
      player._raf = requestAnimationFrame(step);
    },
    pause() {
      player.playing = false;
      if (player._raf) cancelAnimationFrame(player._raf);
    },
    seek(index) {
      player.index = Math.max(0, Math.min(player.total, Math.round(index)));
      player._progress = player.index;
      player._emit();
    },
    setSpeed(pointsPerSecond) {
      player.pointsPerSecond = Math.max(0.001, pointsPerSecond);
    },
  };
  return player;
}

// Single place to tune playback speed: range (seconds) + slider-to-duration curve.
// A given slider position should feel equally fast on every track regardless of point count,
// so speed is expressed as total playback duration (seconds), not raw points/tick.
export const speed = {
  minDurationS: 5, // fastest (slider at max)
  maxDurationS: 30, // slowest (slider at min)

  durationForSlider(sliderValue, sliderMin, sliderMax) {
    const t = (sliderValue - sliderMin) / (sliderMax - sliderMin);
    return this.maxDurationS - t * (this.maxDurationS - this.minDurationS);
  },

  pointsPerSecond(total, sliderValue, sliderMin, sliderMax) {
    return total / this.durationForSlider(sliderValue, sliderMin, sliderMax);
  },
};

const appRoot = document.getElementById('appRoot');
const statusEl = document.getElementById('status');
const sectionSelect = document.getElementById('sectionSelect');

// Each video section plays back a day-range subset; "full" is the whole journey.
// Add new sections here as POI_section{N}.geojson / track_smoothed_section{N}.geojson land in json/.
const SECTIONS = [
  { id: 'section1', type: 'section', poiPath: 'json/POI_section1.geojson', trackPath: 'json/track_smoothed_section1.geojson' },
  { id: 'section2', type: 'section', poiPath: 'json/POI_section2.geojson', trackPath: 'json/track_smoothed_section2.geojson' },
  { id: 'section3', type: 'section', poiPath: 'json/POI_section3.geojson', trackPath: 'json/track_smoothed_section3.geojson' },
  { id: 'section5', type: 'section', poiPath: 'json/POI_section5.geojson', trackPath: 'json/track_smoothed_section5.geojson' },
  { id: 'full', type: 'full', poiPath: 'json/POI_full.geojson', trackPath: 'json/track_simplified_full.geojson' },
];

async function loadTrackCoords(path) {
  const res = await fetch(path);
  const geojson = await res.json();
  return geojson.features[0].geometry.coordinates; // [lon, lat][]
}

async function loadPois(path) {
  const res = await fetch(path);
  const geojson = await res.json();
  return geojson.features.map((f) => ({
    coordinates: f.geometry.coordinates, // [lon, lat]
    emoji: f.properties.emoji,
    label: f.properties.location,
    id: f.properties.id,
    day: f.properties.day,
    distanceKm: f.properties.distance_km,
    elevationGain: f.properties.elevation_gain,
  }));
}

// `day` is a free-form string (e.g. "9-10" for a rest day), so `id` is used as the day number instead.
function dayRangeLabel(pois) {
  const ids = pois.map((p) => p.id).filter((id) => id != null);
  if (!ids.length) return '';
  const min = Math.min(...ids);
  const max = Math.max(...ids);
  return min === max ? `Day ${min}` : `Days ${min}\u2013${max}`;
}

// Fetches each section's (small) POI file up front to label the dropdown, and caches the
// parsed POIs so picking a section later doesn't re-fetch them.
async function buildSectionOptions() {
  await Promise.all(SECTIONS.map(async (section) => {
    section.pois = await loadPois(section.poiPath);
    const range = dayRangeLabel(section.pois);
    section.label = section.type === 'full' ? `Full Track (${range})` : range;
  }));
  sectionSelect.innerHTML = SECTIONS
    .map((s, i) => `<option value="${s.id}"${i === 0 ? ' selected' : ''}>${s.label}</option>`)
    .join('');
}

let currentPlayer = null;
let loadGeneration = 0;

async function loadSection(id) {
  const section = SECTIONS.find((s) => s.id === id);
  const generation = ++loadGeneration;
  statusEl.textContent = `Loading ${section.label}\u2026`;
  const coords = await loadTrackCoords(section.trackPath);
  if (generation !== loadGeneration) return; // a newer selection superseded this one

  if (currentPlayer) currentPlayer.destroy();
  statusEl.textContent = `${coords.length.toLocaleString()} points`;
  currentPlayer = await mount({ root: appRoot, coords, pois: section.pois });
}

// Not a top-level await: mount()'s dynamic re-import of this module must see it fully
// evaluated first, otherwise the two imports deadlock each other.
async function start() {
  await buildSectionOptions();
  sectionSelect.addEventListener('change', () => loadSection(sectionSelect.value));
  await loadSection(SECTIONS[0].id);
}

start();