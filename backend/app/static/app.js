(function () {
  const $ = (sel) => document.querySelector(sel);
  const form = $('#graph-form');
  const preferenceEl = $('#preference');
  const daysEl = $('#days');
  const messageEl = $('#message');
  const resultsSection = $('#results');
  const itineraryContainer = $('#itinerary-container');
  const accList = document.getElementById('acc-list');

  // Map removed

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

    try {
  const data = await fetchJson('/generate-full-itinerary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ preference, days })
      });
  if (!data.success) throw new Error('Itinerary generation failed');

  // Render itinerary cards
  const items = Array.isArray(data.itinerary) ? data.itinerary : [];
  itineraryContainer.innerHTML = items.map(card).join('');
  resultsSection.hidden = false;

  // Render hotels/homestays list only
  const hotelsByLocation = data.hotels || {};
  accList.innerHTML = renderAccList(hotelsByLocation);
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
        return `<div class="acc-item">${safeName} ${url}</div>`;
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

  // Map-related functions removed

  function escapeHtml(str) {
    return String(str)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#39;');
  }
})();



