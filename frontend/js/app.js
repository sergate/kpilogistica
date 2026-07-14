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
let expandedZones = {}; // track de zonas expandidas

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
    if (firstZone && firstZone.kpis && firstZone.kpis.length) {
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
    
    // Zona con subcategorías expandibles
    if (zone.type === 'expandable' && zone.subcategories) {
      const zoneHeader = document.createElement('div');
      zoneHeader.className = 'zone-label expandable';
      zoneHeader.innerHTML = `
        <span>${zone.label}</span>
        <span class="expand-icon">▸</span>
      `;
      zoneHeader.addEventListener('click', () => toggleZone(zone.id, wrap));
      wrap.appendChild(zoneHeader);
      
      const subContainer = document.createElement('div');
      subContainer.className = 'subcategories';
      subContainer.style.display = expandedZones[zone.id] ? 'block' : 'none';
      
      zone.subcategories.forEach(sub => {
        const subBtn = document.createElement('button');
        subBtn.className = 'bay subcategory';
        subBtn.dataset.subId = sub.id;
        subBtn.innerHTML = `
          <span class="bay-icon">${sub.icon || '📄'}</span>
          <span class="bay-name">${sub.label}</span>
        `;
        subBtn.addEventListener('click', () => selectSubcategory(sub));
        subContainer.appendChild(subBtn);
      });
      
      wrap.appendChild(subContainer);
      
      if (expandedZones[zone.id]) {
        zoneHeader.querySelector('.expand-icon').textContent = '▾';
      }
    }
    // Zona normal con KPIs
    else if (zone.kpis) {
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
    }
    
    rackZones.appendChild(wrap);
  });
}

function toggleZone(zoneId, wrapElement) {
  expandedZones[zoneId] = !expandedZones[zoneId];
  const subContainer = wrapElement.querySelector('.subcategories');
  const icon = wrapElement.querySelector('.expand-icon');
  
  if (expandedZones[zoneId]) {
    subContainer.style.display = 'block';
    icon.textContent = '▾';
  } else {
    subContainer.style.display = 'none';
    icon.textContent = '▸';
  }
}

function selectSubcategory(sub) {
  // Marcar como activo
  document.querySelectorAll('.bay').forEach(b => b.classList.remove('active'));
  const activeBtn = document.querySelector(`[data-sub-id="${sub.id}"]`);
  if (activeBtn) activeBtn.classList.add('active');
  
  // Ejecutar acción según tipo
  if (sub.action === 'import') {
    showImportModal();
  } else if (sub.action === 'report') {
    loadReport(sub.id);
  }
}

async function loadReport(reportId) {
  main.innerHTML = `<div class="kpi-desc">Cargando reporte...</div>`;
  
  const reportMap = {
    'sp-resumen': { endpoint: '/api/reportes/resumen', title: '📊 Resumen General' },
    'sp-fecha': { endpoint: '/api/reportes/por-fecha', title: '📅 Análisis por Fecha' },
    'sp-marca': { endpoint: '/api/reportes/por-marca', title: '🏷️ Análisis por Marca' },
    'sp-canal': { endpoint: '/api/reportes/por-canal', title: '📦 Análisis por Canal' },
    'sp-categoria': { endpoint: '/api/reportes/por-categoria', title: '📋 Análisis por Categoría' }
  };
  
  const report = reportMap[reportId];
  if (!report) {
    main.innerHTML = '<div class="error-banner">Reporte no encontrado</div>';
    return;
  }
  
  try {
    const data = await fetchJSON(report.endpoint);
    
    if (!data.success) {
      main.innerHTML = `
        <div class="error-banner">
          ${data.message || 'No hay datos disponibles'}<br>
          <small>Por favor, importa archivos primero desde la opción "Importar Datos"</small>
        </div>`;
      return;
    }
    
    renderReport(reportId, report.title, data);
  } catch (err) {
    main.innerHTML = `<div class="error-banner">Error al cargar reporte: ${err.message}</div>`;
  }
}

function renderReport(reportId, title, data) {
  let html = `
    <div class="report-container">
      <div class="report-header">
        <h2>${title}</h2>
      </div>
  `;
  
  if (reportId === 'sp-resumen') {
    html += renderResumen(data.resumen);
  } else if (reportId === 'sp-fecha') {
    html += renderTable(data.datos, ['fecha', 'cantidad_pedidos', 'total_unidades', 'total_horas', 'productividad']);
  } else if (reportId === 'sp-marca') {
    html += renderTable(data.datos, ['marca', 'cantidad_pedidos', 'total_unidades', 'total_horas', 'productividad']);
  } else if (reportId === 'sp-canal') {
    html += renderTable(data.datos, ['canal', 'cantidad_pedidos', 'total_unidades']);
  } else if (reportId === 'sp-categoria') {
    html += renderTable(data.datos, ['categoria', 'cantidad_pedidos', 'total_unidades', 'total_horas', 'productividad']);
  }
  
  html += '</div>';
  main.innerHTML = html;
}

function renderResumen(resumen) {
  return `
    <div class="report-grid">
      <div class="report-card">
        <h3>👥 Clientes</h3>
        <div class="metric-big">${resumen.clientes.total}</div>
        <div class="metric-label">Total de clientes</div>
        <div class="metric-breakdown">
          ${resumen.clientes.por_canal.map(c => `
            <div class="metric-row">
              <span>${c.canal || 'Sin canal'}</span>
              <span><b>${c.cantidad}</b></span>
            </div>
          `).join('')}
        </div>
      </div>
      
      <div class="report-card">
        <h3>🏪 Pedidos por Tienda</h3>
        <div class="metric-big">${resumen.pedidos_tienda.total}</div>
        <div class="metric-label">Total de pedidos</div>
        <div class="metric-sub">
          <span>Unidades:</span> <b>${resumen.pedidos_tienda.unidades || 0}</b>
        </div>
      </div>
      
      <div class="report-card">
        <h3>📦 Pedidos por Grupo</h3>
        <div class="metric-big">${resumen.pedidos_grupo.total}</div>
        <div class="metric-label">Total de pedidos</div>
        <div class="metric-sub">
          <span>Unidades:</span> <b>${resumen.pedidos_grupo.unidades || 0}</b><br>
          <span>Horas:</span> <b>${resumen.pedidos_grupo.horas || 0}</b><br>
          <span>Productividad:</span> <b>${resumen.pedidos_grupo.productividad || 0} u/h</b>
        </div>
      </div>
    </div>
  `;
}

function renderTable(datos, columns) {
  if (!datos || datos.length === 0) {
    return '<div class="empty-state">No hay datos para mostrar</div>';
  }
  
  const headers = columns.map(col => {
    const labels = {
      'fecha': 'Fecha',
      'marca': 'Marca',
      'canal': 'Canal',
      'categoria': 'Categoría',
      'cantidad_pedidos': 'Pedidos',
      'total_unidades': 'Unidades',
      'total_horas': 'Horas',
      'productividad': 'Productividad'
    };
    return labels[col] || col;
  });
  
  return `
    <div class="report-table-container">
      <table class="report-table">
        <thead>
          <tr>
            ${headers.map(h => `<th>${h}</th>`).join('')}
          </tr>
        </thead>
        <tbody>
          ${datos.map(row => `
            <tr>
              ${columns.map(col => `<td>${row[col] !== null && row[col] !== undefined ? row[col] : '-'}</td>`).join('')}
            </tr>
          `).join('')}
        </tbody>
      </table>
      <div class="table-footer">
        Total de registros: <b>${datos.length}</b>
      </div>
    </div>
  `;
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
  for (const z of ZONES) if (z.kpis && z.kpis.includes(kpiId)) return z.label;
  return '';
}

async function selectKpi(id) {
  currentKpi = id;
  document.querySelectorAll('.bay').forEach(b => b.classList.toggle('active', b.dataset.kpi === id));

  // Si es el KPI de productividad de picking (B-03), mostrar modal de importación
  if (id === 'pick-prod') {
    showImportModal();
    return;
  }

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

// ==================== FUNCIONES DE IMPORTACIÓN ====================

function showImportModal() {
  const modal = document.getElementById('import-modal');
  modal.style.display = 'flex';
  
  // Configurar listeners para mostrar nombre de archivo
  ['clientes', 'tienda', 'grupo'].forEach(type => {
    const input = document.getElementById(`file-${type}`);
    const display = document.getElementById(`filename-${type}`);
    input.addEventListener('change', (e) => {
      display.textContent = e.target.files[0]?.name || 'Ningún archivo seleccionado';
    });
  });
}

function closeImportModal() {
  const modal = document.getElementById('import-modal');
  modal.style.display = 'none';
  
  // Limpiar archivos seleccionados
  ['clientes', 'tienda', 'grupo'].forEach(type => {
    document.getElementById(`file-${type}`).value = '';
    document.getElementById(`filename-${type}`).textContent = 'Ningún archivo seleccionado';
  });
  document.getElementById('upload-status').innerHTML = '';
}

async function processFiles() {
  const clientesFile = document.getElementById('file-clientes').files[0];
  const tiendaFile = document.getElementById('file-tienda').files[0];
  const grupoFile = document.getElementById('file-grupo').files[0];
  
  const status = document.getElementById('upload-status');
  
  // Validar que todos los archivos estén seleccionados
  if (!clientesFile || !tiendaFile || !grupoFile) {
    status.innerHTML = '<div class="status-error">⚠️ Debes seleccionar los 3 archivos</div>';
    return;
  }
  
  // Validar extensiones
  if (!clientesFile.name.endsWith('.xlsx')) {
    status.innerHTML = '<div class="status-error">⚠️ El archivo de clientes debe ser .xlsx</div>';
    return;
  }
  
  if (!tiendaFile.name.endsWith('.csv') || !grupoFile.name.endsWith('.csv')) {
    status.innerHTML = '<div class="status-error">⚠️ Los archivos de pedidos deben ser .csv</div>';
    return;
  }
  
  status.innerHTML = '<div class="status-loading">⏳ Procesando archivos...</div>';
  
  try {
    const formData = new FormData();
    formData.append('clientes', clientesFile);
    formData.append('pedidos_tienda', tiendaFile);
    formData.append('pedidos_grupo', grupoFile);
    
    const response = await fetch(`${API_BASE}/api/upload-files`, {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Error al procesar archivos');
    }
    
    const result = await response.json();
    
    status.innerHTML = `
      <div class="status-success">
        ✅ Datos procesados correctamente<br>
        <small>
          Clientes: ${result.registros.clientes} | 
          Pedidos Tienda: ${result.registros.pedidos_tienda} | 
          Pedidos Grupo: ${result.registros.pedidos_grupo}
        </small><br>
        <small>Productividad calculada: <b>${result.productividad.value} u/h</b></small>
      </div>
    `;
    
    // Cerrar modal después de 2 segundos
    setTimeout(() => {
      closeImportModal();
      // Recargar el sidebar para reflejar cambios
      init();
    }, 2000);
    
  } catch (err) {
    status.innerHTML = `<div class="status-error">❌ Error: ${err.message}</div>`;
  }
}

async function clearImportData() {
  const status = document.getElementById('upload-status');
  
  if (!confirm('¿Estás seguro de borrar todos los datos importados? Esta acción no se puede deshacer.')) {
    return;
  }
  
  status.innerHTML = '<div class="status-loading">⏳ Borrando datos...</div>';
  
  try {
    const response = await fetch(`${API_BASE}/api/clear-data`, {
      method: 'DELETE'
    });
    
    if (!response.ok) {
      throw new Error('Error al borrar datos');
    }
    
    status.innerHTML = '<div class="status-success">✅ Datos borrados correctamente</div>';
    
    setTimeout(() => {
      status.innerHTML = '';
    }, 2000);
    
  } catch (err) {
    status.innerHTML = `<div class="status-error">❌ Error: ${err.message}</div>`;
  }
}

init();
