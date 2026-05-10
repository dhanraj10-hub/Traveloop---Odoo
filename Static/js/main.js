// ═══════════════════════════════════════════════════
//  TRAVELOOP — Main JavaScript
// ═══════════════════════════════════════════════════

// ── TOAST NOTIFICATIONS ──────────────────────────
function showToast(msg, type = 'default') {
  const t = document.getElementById('toast');
  if (!t) return;
  t.textContent = msg;
  t.style.background = type === 'error' ? '#E05A3A' : '#1A1A1A';
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3000);
}

// ── MODAL ─────────────────────────────────────────
function openModal(id) {
  const m = document.getElementById(id);
  if (m) m.classList.add('open');
}
function closeModal(id) {
  const m = document.getElementById(id);
  if (m) m.classList.remove('open');
}

// Close modal on overlay click
document.addEventListener('click', e => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('open');
  }
});

// ── API HELPER ────────────────────────────────────
async function api(url, method = 'GET', data = null) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' }
  };
  if (data) opts.body = JSON.stringify(data);
  const res = await fetch(url, opts);
  return res.json();
}

// ── CITY SEARCH ──────────────────────────────────
function initCitySearch(inputId, resultsId, onSelect) {
  const input = document.getElementById(inputId);
  const results = document.getElementById(resultsId);
  if (!input || !results) return;

  let debounce;
  input.addEventListener('input', () => {
    clearTimeout(debounce);
    debounce = setTimeout(async () => {
      const q = input.value.trim();
      if (!q) { results.style.display = 'none'; return; }
      const cities = await fetch('/api/cities/search?q=' + encodeURIComponent(q)).then(r => r.json());
      results.innerHTML = '';
      if (!cities.length) { results.style.display = 'none'; return; }
      cities.forEach(city => {
        const el = document.createElement('div');
        el.className = 'search-item';
        el.innerHTML = `
          <div>
            <div class="search-item-name">📍 ${city.name}</div>
            <div class="search-item-sub">${city.country} · Cost: ${city.cost_index}</div>
          </div>
          <span class="badge badge-amber">★ ${city.popularity}</span>
        `;
        el.onclick = () => {
          results.style.display = 'none';
          onSelect(city);
        };
        results.appendChild(el);
      });
      results.style.display = 'block';
    }, 250);
  });

  document.addEventListener('click', e => {
    if (!input.contains(e.target) && !results.contains(e.target)) {
      results.style.display = 'none';
    }
  });
}

// ── ACTIVITY SEARCH ──────────────────────────────
function initActivitySearch(inputId, resultsId, onSelect) {
  const input = document.getElementById(inputId);
  const results = document.getElementById(resultsId);
  if (!input || !results) return;

  let debounce;
  input.addEventListener('input', () => {
    clearTimeout(debounce);
    debounce = setTimeout(async () => {
      const q = input.value.trim();
      const cat = document.getElementById('activityCatFilter')?.value || '';
      const url = `/api/activities/search?q=${encodeURIComponent(q)}&category=${cat}`;
      const acts = await fetch(url).then(r => r.json());
      results.innerHTML = '';
      if (!acts.length) { results.style.display = 'none'; return; }
      acts.slice(0, 8).forEach(act => {
        const el = document.createElement('div');
        el.className = 'search-item';
        const colors = { sightseeing:'#2A7D6F', food:'#E8A030', adventure:'#E05A3A', culture:'#6B48FF', wellness:'#EC4899' };
        el.innerHTML = `
          <div>
            <div class="search-item-name" style="color:${colors[act.category]||'#333'}">🎯 ${act.name}</div>
            <div class="search-item-sub">${act.category} · ${act.duration} · $${act.cost}</div>
          </div>
          <button class="btn btn-primary btn-sm">Add</button>
        `;
        el.querySelector('button').onclick = e => { e.stopPropagation(); onSelect(act); };
        results.appendChild(el);
      });
      results.style.display = 'block';
    }, 250);
  });
}

// ── CONFIRM DELETE ────────────────────────────────
function confirmDelete(msg, onConfirm) {
  if (confirm(msg)) onConfirm();
}

// ── FORMAT CURRENCY ──────────────────────────────
function fmt(n) {
  return '$' + parseFloat(n || 0).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// ── DATE DIFF (days) ─────────────────────────────
function daysBetween(a, b) {
  return Math.ceil((new Date(b) - new Date(a)) / 86400000);
}

// ── ACTIVE NAV ───────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const path = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(link => {
    if (link.getAttribute('href') === path) link.classList.add('active');
  });
});