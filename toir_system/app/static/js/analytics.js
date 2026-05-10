if (!requireAuth()) throw '';
if (!hasRole('admin', 'manager', 'dispatcher')) { window.location.href = '/dashboard'; throw ''; }
initSidebar();

async function loadSummary() {
  const res = await API.get('/analytics/summary');
  const cards = document.getElementById('summary-cards');
  if (!res || !res.ok) { cards.innerHTML = '<div class="text-muted">Ошибка загрузки</div>'; return; }
  const d = await res.json();

  cards.innerHTML = `
    <div class="stat-card"><div class="stat-value">${d.total_requests}</div><div class="stat-label">Всего заявок</div></div>
    <div class="stat-card"><div class="stat-value">${d.closed_count}</div><div class="stat-label">Закрыто</div></div>
    <div class="stat-card"><div class="stat-value">${d.avg_resolution_hours != null ? d.avg_resolution_hours : '—'}</div><div class="stat-label">Ср. время закрытия (ч)</div></div>
    <div class="stat-card"><div class="stat-value">${d.by_status['new']||0}</div><div class="stat-label">Новых</div></div>
    <div class="stat-card"><div class="stat-value">${(d.by_status['in_progress']||0) + (d.by_status['diagnostics_done']||0) + (d.by_status['repair_in_progress']||0)}</div><div class="stat-label">В работе</div></div>`;

  const statusOrder = ['new','assigned','in_progress','diagnostics_done','repair_in_progress','completed','closed','cancelled'];
  document.getElementById('by-status-tbody').innerHTML = statusOrder.map(s =>
    `<tr><td>${statusBadge(s)}</td><td class="text-right"><strong>${d.by_status[s]||0}</strong></td></tr>`
  ).join('');

  const priOrder = ['critical','high','medium','low'];
  document.getElementById('by-priority-tbody').innerHTML = priOrder.map(p =>
    `<tr><td>${priorityBadge(p)}</td><td class="text-right"><strong>${d.by_priority[p]||0}</strong></td></tr>`
  ).join('');
}

async function loadFaults() {
  const res = await API.get('/analytics/equipment-faults');
  const tbody = document.getElementById('faults-tbody');
  if (!res || !res.ok) { tbody.innerHTML = '<tr><td colspan="3" class="text-muted" style="padding:20px">Ошибка загрузки</td></tr>'; return; }
  const items = await res.json();
  if (!items.length) { tbody.innerHTML = '<tr><td colspan="3" class="text-muted" style="padding:20px">Нет данных</td></tr>'; return; }
  tbody.innerHTML = items.map(r => `
    <tr>
      <td><code>${r.inventory_number}</code></td>
      <td>${r.equipment_name}</td>
      <td><strong>${r.fault_count}</strong></td>
    </tr>`).join('');
}

async function loadPerformance() {
  if (!hasRole('admin', 'manager')) return;
  document.getElementById('perf-card').style.display = '';
  const res = await API.get('/analytics/service-performance');
  const tbody = document.getElementById('perf-tbody');
  if (!res || !res.ok) { tbody.innerHTML = '<tr><td colspan="3" class="text-muted" style="padding:20px">Ошибка загрузки</td></tr>'; return; }
  const items = await res.json();
  if (!items.length) { tbody.innerHTML = '<tr><td colspan="3" class="text-muted" style="padding:20px">Нет данных</td></tr>'; return; }
  tbody.innerHTML = items.map(r => `
    <tr>
      <td>${r.service_name}</td>
      <td>${r.total_requests}</td>
      <td>${r.avg_resolution_hours != null ? r.avg_resolution_hours : '—'}</td>
    </tr>`).join('');
}

loadSummary();
loadFaults();
loadPerformance();
