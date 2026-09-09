// ---------------------------------------------------------------------------
// map-controls.js  –  Custom Leaflet controls, coordinate tool, UI toggles
// ---------------------------------------------------------------------------

// ── Go to Last Position button ──────────────────────────────────────────────

L.Control.GoToLastPosition = L.Control.extend({
    onAdd: function(map) {
        const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');
        const button = L.DomUtil.create('button', 'go-to-last-position-btn', container);
        button.innerHTML = '📍';
        const lang = localStorage.getItem('preferred-language') || 'en';
        button.title = translations[lang]['go-to-last-position'];
        button.setAttribute('aria-label', translations[lang]['go-to-last-position']);
        L.DomEvent.disableClickPropagation(button);
        L.DomEvent.on(button, 'click', function() { goToLastPosition(); });
        return container;
    }
});
L.control.goToLastPosition = function(opts) { return new L.Control.GoToLastPosition(opts); };
L.control.goToLastPosition({ position: 'topleft' }).addTo(map);

// ── Coordinate tool button ──────────────────────────────────────────────────

let coordinateToolActive = false;
let coordinateTooltip = null;

L.Control.CoordinateTool = L.Control.extend({
    onAdd: function(map) {
        const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');
        const button = L.DomUtil.create('button', 'coordinate-tool-btn', container);
        button.innerHTML = '⊕';
        const lang = localStorage.getItem('preferred-language') || 'en';
        button.title = translations[lang]['coordinates-label'];
        button.setAttribute('aria-label', translations[lang]['coordinates-label']);
        L.DomEvent.disableClickPropagation(button);
        L.DomEvent.on(button, 'click', function() { toggleCoordinateTool(); });
        return container;
    }
});
L.control.coordinateTool = function(opts) { return new L.Control.CoordinateTool(opts); };
L.control.coordinateTool({ position: 'topleft' }).addTo(map);

// ── Legend button ───────────────────────────────────────────────────────────

L.Control.LegendButton = L.Control.extend({
    onAdd: function(map) {
        const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');
        const button = L.DomUtil.create('button', 'legend-btn', container);
        button.innerHTML = '📋';
        const lang = localStorage.getItem('preferred-language') || 'en';
        button.title = translations[lang]['legend-title'];
        button.setAttribute('aria-label', translations[lang]['legend-title']);
        L.DomEvent.disableClickPropagation(button);
        L.DomEvent.on(button, 'click', function() { toggleLegend(); });
        return container;
    }
});
L.control.legendButton = function(opts) { return new L.Control.LegendButton(opts); };
L.control.legendButton({ position: 'topleft' }).addTo(map);

// Scale control
L.control.scale({ position: 'topright', imperial: false, maxWidth: 150 }).addTo(map);

// ── Coordinate tool logic ───────────────────────────────────────────────────

function toggleCoordinateTool() {
    coordinateToolActive = !coordinateToolActive;
    const button = document.querySelector('.coordinate-tool-btn');
    if (coordinateToolActive) {
        button.classList.add('active');
    } else {
        button.classList.remove('active');
        if (coordinateTooltip && map.hasLayer(coordinateTooltip)) {
            map.closeTooltip(coordinateTooltip);
        }
    }
}

map.on('mousemove', function(e) {
    if (!coordinateToolActive) return;
    const lat = e.latlng.lat.toFixed(6);
    const lng = e.latlng.lng.toFixed(6);
    if (!coordinateTooltip) {
        coordinateTooltip = L.tooltip({
            permanent: true,
            className: 'coordinate-tooltip',
            direction: 'top',
            offset: [0, -10]
        });
    }
    coordinateTooltip
        .setLatLng(e.latlng)
        .setContent(`<strong>Lat:</strong> ${lat}<br><strong>Lng:</strong> ${lng}<br><em>Click to copy</em>`);
    if (!map.hasLayer(coordinateTooltip)) coordinateTooltip.addTo(map);
});

map.on('click', function(e) {
    if (!coordinateToolActive) return;
    if (e.originalEvent.target.closest('.leaflet-marker-icon') ||
        e.originalEvent.target.closest('.leaflet-popup')) return;

    const lat = e.latlng.lat.toFixed(6);
    const lng = e.latlng.lng.toFixed(6);

    navigator.clipboard.writeText(`${lat}, ${lng}`).then(function() {
        const lang = localStorage.getItem('preferred-language') || 'en';
        if (coordinateTooltip) {
            coordinateTooltip.setContent(
                `<strong style="color: #4CAF50;">${translations[lang]['coordinates-copied']}</strong>`
            );
            setTimeout(function() {
                coordinateToolActive = false;
                const button = document.querySelector('.coordinate-tool-btn');
                if (button) button.classList.remove('active');
                if (map.hasLayer(coordinateTooltip)) map.closeTooltip(coordinateTooltip);
            }, 1000);
        }
    }).catch(function(err) {
        console.error('Failed to copy coordinates:', err);
    });
});

// ── UI toggles ──────────────────────────────────────────────────────────────

function goToLastPosition() {
    if (lastPositionCoords && lastPositionCoords.length >= 2) {
        map.setView([lastPositionCoords[1], lastPositionCoords[0]], 13, {
            animate: true,
            duration: 1
        });
    }
}

function toggleLegend() {
    const legend = document.querySelector('.map-legend');
    const button = document.querySelector('.legend-btn');
    legend.classList.toggle('collapsed');
    if (button) {
        button.classList.toggle('active', !legend.classList.contains('collapsed'));
    }
}

function togglePanel() {
    const panel  = document.querySelector('.daily-positions-panel');
    const button = document.querySelector('.panel-toggle');
    const legend = document.querySelector('.map-legend');
    panel.classList.toggle('collapsed');
    button.textContent = panel.classList.contains('collapsed') ? '+' : '−';
    legend.classList.toggle('panel-collapsed', panel.classList.contains('collapsed'));
}

// Remove card highlight when any popup closes
map.on('popupclose', function() {
    document.querySelectorAll('.position-card').forEach(c => c.classList.remove('active'));
});
