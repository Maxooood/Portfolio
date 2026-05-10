if (!requireAuth()) throw '';
initSidebar();

async function loadStats() {
  if (!hasRole('admin', 'manager', 'dispatcher')) return;
  const res = await API.get('/analytics/summary');
  if (!res || !res.ok) return;
  const d = await res.json();

  const area = document.getElementById('stats-area');
  const statuses = ['new','assigned','in_progress','diagnostics_done','repair_in_progress','completed','closed','cancelled'];
  const byStatus = statuses.map(s =>
    `<div class="stat-card"><div class="stat-value">${d.by_status[s]||0}</div><div class="stat-label">${STATUS_LABELS[s]}</div></div>`
  ).join('');

  area.innerHTML = `
    <div class="stats-grid mb-6">
      <div class="stat-card"><div class="stat-value">${d.total_requests}</div><div class="stat-label">Всего заявок</div></div>
      <div class="stat-card"><div class="stat-value">${d.closed_count}</div><div class="stat-label">Закрыто</div></div>
      <div class="stat-card"><div class="stat-value">${d.avg_resolution_hours != null ? d.avg_resolution_hours + 'ч' : '—'}</div><div class="stat-label">Среднее время закрытия</div></div>
      ${byStatus}
    </div>`;
}

async function loadRecent() {
  const res = await API.get('/requests?per_page=15&page=1');
  if (!res) return;
  const tbody = document.getElementById('recent-tbody');
  if (!res.ok) { tbody.innerHTML = '<tr><td colspan="6" class="text-muted" style="padding:20px">Не удалось загрузить заявки</td></tr>'; return; }
  const d = await res.json();
  if (!d.items.length) {
    tbody.innerHTML = '<tr><td colspan="6"><div class="empty"><div class="empty-icon">📋</div><div class="empty-text">Заявок пока нет</div></div></td></tr>';
    return;
  }
  tbody.innerHTML = d.items.map(r => `
    <tr class="row-link" onclick="window.location='/requests/${r.id}'">
      <td><code>${r.request_number}</code></td>
      <td>${r.title}</td>
      <td>${r.equipment ? r.equipment.name : '—'}</td>
      <td>${priorityBadge(r.priority)}</td>
      <td>${statusBadge(r.status)}</td>
      <td>${fmtDate(r.created_at)}</td>
    </tr>`).join('');
}

loadStats();
loadRecent();
