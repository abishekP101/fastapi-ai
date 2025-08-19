(function () {
  const $ = (sel) => document.querySelector(sel);
  const form = $('#graph-form');
  const preferenceEl = $('#preference');
  const daysEl = $('#days');
  const messageEl = $('#message');
  const resultsSection = $('#results');
  const itineraryContainer = $('#itinerary-container');
  const accList = document.getElementById('acc-list');

  let map, markersLayer;
  initMap();

  form.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    const preference = preferenceEl.value.trim();
    const days = Number(daysEl.value);
    if (!preference || !Number.isFinite(days)) {
      setMessage('Provide preference and days.', 'error');
      return;
    }
    setMessage('Running graph…', 'loading');
    resultsSection.hidden = true;
    itineraryContainer.innerHTML = '';
    accList.innerHTML = '';
    clearMarkers();

    try {
      const data = await fetchJson('/graph/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ preference, days })
      });
      if (!data.success) throw new Error('Graph generation failed');

      // Render itinerary cards
      const items = Array.isArray(data.combined) && data.combined.length ? data.combined : data.itinerary || [];
      itineraryContainer.innerHTML = items.map(card).join('');
      resultsSection.hidden = false;

      // Render accommodations list and markers
      const accByLocation = data.accommodations || {};
      const markers = [];
      for (const day of items) {
        const location = day.location || '';
        const accs = accByLocation[location] || [];
        accs.forEach((i) => {
          const m = addMarker(i);
          if (m) markers.push(m);
        });
      }
      accList.innerHTML = renderAccList(accByLocation);
      fitToMarkers();
      setMessage('Done.', 'success');
    } catch (e) {
      setMessage(`Error: ${e.message}`, 'error');
    }
  });

  function card(day) {
    const activities = (day.activities || []).map((a) => `<li>${escapeHtml(a)}</li>`).join('');
    const accs = Array.isArray(day.accommodations) ? day.accommodations : [];
    const accHtml = accs.length ? `<div class="acc-inline">${accs.slice(0, 3).map((a) => `<span>${escapeHtml(a.name || '')}</span>`).join('')}</div>` : '';
    return `
      <article class="card">
        <header class="card-header">
          <div class="badge">Day ${day.day ?? ''}</div>
          <h3>${escapeHtml(day.title || '')}</h3>
        </header>
        <div class="card-body">
          <p class="muted">${escapeHtml(day.location || '')}</p>
          ${day.description ? `<p>${escapeHtml(day.description)}</p>` : ''}
          <ul class="activities">${activities}</ul>
          ${accHtml}
        </div>
      </article>
    `;
  }

  function renderAccList(accByLocation) {
    const blocks = Object.entries(accByLocation).map(([loc, arr]) => {
      const items = (arr || []).map((i) => {
        const safeName = escapeHtml(i.name || 'Accommodation');
        const url = i.url ? `<a href="${i.url}" target="_blank" rel="noopener">Link</a>` : '';
        const pos = i.lat != null && i.lon != null ? `(${i.lat.toFixed(4)}, ${i.lon.toFixed(4)})` : '';
        return `<div class="acc-item">${safeName} ${pos} ${url}</div>`;
      }).join('');
      return `<div class="acc-group"><h3>${escapeHtml(loc)}</h3>${items}</div>`;
    });
    return blocks.join('');
  }

  function setMessage(text, type = 'info') {
    messageEl.textContent = text;
    messageEl.className = `message ${type}`;
  }

  async function fetchJson(path, options) {
    const res = await fetch(path, options);
    const text = await res.text();
    try {
      const json = JSON.parse(text);
      if (!res.ok) throw Object.assign(new Error(json.detail || res.statusText), { status: res.status, body: json });
      return json;
    } catch (e) {
      if (e instanceof SyntaxError) {
        throw Object.assign(new Error('Invalid JSON response'), { status: res.status, body: text });
      }
      throw e;
    }
  }

  function initMap() {
    const mapEl = document.getElementById('map');
    if (!mapEl || !window.L) return;
    map = L.map('map').setView([27.3314, 88.6138], 8);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
    markersLayer = L.layerGroup().addTo(map);
  }

  function clearMarkers() {
    if (markersLayer) markersLayer.clearLayers();
  }

  function addMarker(item) {
    if (!map || item.lat == null || item.lon == null) return null;
    const m = L.marker([item.lat, item.lon]).addTo(markersLayer);
    const safeName = escapeHtml(item.name || 'Accommodation');
    const link = item.url ? `<a href="${item.url}" target="_blank" rel="noopener">Open</a>` : '';
    m.bindPopup(`<strong>${safeName}</strong><br/>${link}`);
    return m;
  }

  function fitToMarkers() {
    const bounds = [];
    markersLayer.eachLayer((layer) => {
      if (layer.getLatLng) {
        const ll = layer.getLatLng();
        bounds.push([ll.lat, ll.lng]);
      }
    });
    if (bounds.length) map.fitBounds(bounds, { padding: [20, 20] });
  }

  function escapeHtml(str) {
    return String(str)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#39;');
  }
})();



