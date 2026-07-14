/* =========================================================
   Panel de KPIs — frontend
   Consume la API del backend (FastAPI). Si el frontend se
   sirve desde un origen distinto al backend, ajustar API_BASE.
   ========================================================= */
const API_BASE = ''; // '' = mismo origen. Ej: 'http://localhost:8000' si se sirve aparte.

const STATUS_LABEL = { ok: 'En objetivo', warn: 'Atención', bad: 'Fuera de objetivo' };

const rackZones = document.getElementById('rack-zones');
const rackFoot = document.getElementById('rack-foot');
const main = document.getElementById('main');

let ZONES = [];
let KPI_META = {}; // id -> {code, name, status} liviano, para el sidebar
let currentKpi = null;

async function fetchJSON(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`Error ${res.status} al pedir ${path}`);
  return res.json();
}

async function init() {
  try {
    const [zones, kpis] = await Promise.all([
      fetchJSON('/api/zones'),
      fetchJSON('/api/kpis'),
    ]);
    ZONES = zones;
    Object.entries(kpis).forEach(([id, k]) => {
      KPI_META[id] = { code: k.code, name: k.name, status: k.status };
    });

    buildSidebar();
    rackFoot.textContent = 'Conectado a la API';

    const firstZone = ZONES[0];
    if (firstZone && firstZone.kpis.length) {
      selectKpi(firstZone.kpis[0]);
    }
  } catch (err) {
    rackFoot.textContent = 'Sin conexión con la API';
    main.innerHTML = `
      <div class="error-banner">
        No se pudo conectar con la API (${API_BASE || 'mismo origen'}/api).
        Verificá que el backend esté corriendo.<br>
        Detalle: ${err.message}
      </div>`;
  }
}

function buildSidebar() {
  rackZones.innerHTML = '';
  ZONES.forEach(zone => {
    const wrap = document.createElement('div');
    wrap.className = 'zone';
    wrap.innerHTML = `<div class="zone-label">${zone.label}</div>`;
    zone.kpis.forEach(kpiId => {
      const kpi = KPI_META[kpiId];
      if (!kpi) return;
      const btn = document.createElement('button');
      btn.className = 'bay';
      btn.dataset.kpi = kpiId;
      btn.innerHTML = `
        <span class="bay-code">${kpi.code}</span>
        <span class="bay-name">${kpi.name}</span>
        <span class="bay-dot ${kpi.status}"></span>
      `;
      btn.addEventListener('click', () => selectKpi(kpiId));
      wrap.appendChild(btn);
    });
    rackZones.appendChild(wrap);
  });
}

function sparkline(history) {
  const points = history && history.length ? history : [0, 0];
  const w = 100, h = 34;
  const step = w / (points.length - 1 || 1);
  const max = Math.max(...points), min = Math.min(...points);
  const norm = v => h - ((v - min) / (max - min || 1)) * h;
  const d = points.map((v, i) => `${i === 0 ? 'M' : 'L'} ${i * step} ${norm(v)}`).join(' ');
  return `<svg viewBox="0 0 ${w} ${h}" width="100%" height="46" preserveAspectRatio="none">
    <path d="${d}" fill="none" stroke="#2F6F6B" stroke-width="2" vector-effect="non-scaling-stroke"/>
  </svg>`;
}

function zoneLabelFor(kpiId) {
  for (const z of ZONES) if (z.kpis.includes(kpiId)) return z.label;
  return '';
}

async function selectKpi(id) {
  currentKpi = id;
  document.querySelectorAll('.bay').forEach(b => b.classList.toggle('active', b.dataset.kpi === id));

  main.innerHTML = `<div class="kpi-desc">Cargando…</div>`;

  try {
    const d = await fetchJSON(`/api/kpis/${id}`);
    main.innerHTML = `
      <div class="main-top">
        <div>
          <div class="kpi-eyebrow"><span class="code">${d.code}</span> ${zoneLabelFor(id)}</div>
          <h2 class="kpi-title">${d.name}</h2>
          <p class="kpi-desc">${d.desc}</p>
        </div>
        <div class="status-chip ${d.status}">${STATUS_LABEL[d.status]}</div>
      </div>

      <div class="grid">
        <div class="card">
          <div class="card-value">
            <span class="num">${d.value}</span>
            <span class="unit">${d.unit}</span>
          </div>
          <div class="spark-wrap">
            <div class="spark-label">Últimos 14 días</div>
            ${sparkline(d.history)}
          </div>
          <div class="target-row">
            <span>Meta: <b>${d.target}</b></span>
            <span>Variación: <b>${d.delta}</b></span>
          </div>
        </div>

        <div class="card breakdown">
          <h3>Desglose</h3>
          ${d.breakdown.map(([name, val]) => `
            <div class="bd-row">
              <span class="bd-name">${name}</span>
              <span class="bd-bar-track"><span class="bd-bar-fill" style="width:${val}%"></span></span>
              <span class="bd-val">${val}%</span>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  } catch (err) {
    main.innerHTML = `<div class="error-banner">No se pudo cargar el KPI "${id}". ${err.message}</div>`;
  }
}

init();
