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
  minDurationS: 10, // fastest (slider at max)
  maxDurationS: 570, // slowest (slider at min)

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

async function loadTrack() {
  statusEl.textContent = 'Loading track\u2026';
  const res = await fetch('json/track.geojson');
  const geojson = await res.json();
  return geojson.features[0].geometry.coordinates; // [lon, lat][]
}

async function loadPois() {
  const res = await fetch('json/POI.geojson');
  const geojson = await res.json();
  return geojson.features.map((f) => ({
    coordinates: f.geometry.coordinates, // [lon, lat]
    emoji: f.properties.emoji,
    label: f.properties.label,
  }));
}

// Not a top-level await: mount()'s dynamic re-import of this module must see it fully
// evaluated first, otherwise the two imports deadlock each other.
async function start() {
  const [coords, pois] = await Promise.all([loadTrack(), loadPois()]);
  statusEl.textContent = `${coords.length.toLocaleString()} points`;
  await mount({ root: appRoot, coords, pois });
}

start();