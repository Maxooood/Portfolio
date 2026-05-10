if (!requireAuth()) throw '';
initSidebar();

let REQ = null;

async function loadRequest() {
  const res = await API.get(`/requests/${REQ_ID}`);
  if (!res) return;
  if (!res.ok) { document.getElementById('req-loading').textContent = 'Заявка не найдена'; return; }
  REQ = await res.json();
  renderRequest();
}

function renderRequest() {
  document.getElementById('req-loading').style.display = 'none';
  document.getElementById('req-body').style.display = '';

  document.getElementById('r-number').textContent = REQ.request_number;
  document.getElementById('r-status').innerHTML   = statusBadge(REQ.status);
  document.getElementById('r-priority').innerHTML = priorityBadge(REQ.priority);
  document.getElementById('r-title').textContent  = REQ.title;
  document.getElementById('r-desc').textContent   = REQ.description;
  document.getElementById('r-eq').textContent      = REQ.equipment ? `${REQ.equipment.name} (${REQ.equipment.inventory_number})` : '—';
  document.getElementById('r-fault').textContent   = REQ.fault_type ? REQ.fault_type.name : '—';
  document.getElementById('r-init').textContent    = REQ.initiator ? REQ.initiator.full_name : '—';
  document.getElementById('r-exec').textContent    = REQ.executor_id ? (REQ.executor ? REQ.executor.full_name : `#${REQ.executor_id}`) : '—';
  document.getElementById('r-svc').textContent     = REQ.service ? REQ.service.name : '—';
  document.getElementById('r-notes').textContent   = REQ.notes || '—';
  document.getElementById('r-created').textContent = fmtDate(REQ.created_at);
  document.getElementById('r-completed').textContent = fmtDate(REQ.completed_at);

  renderHistory();
  renderActionBar();
  renderDiagnostic();
  renderRepair();
  renderReport();
}

function renderHistory() {
  const el = document.getElementById('r-history');
  if (!REQ.status_history || !REQ.status_history.length) { el.innerHTML = '<span class="text-muted">Нет записей</span>'; return; }
  el.innerHTML = REQ.status_history.map(h => `
    <div class="tl-item">
      <div class="tl-dot"></div>
      <div class="tl-time">${fmtDate(h.changed_at)}</div>
      <div class="tl-status">${h.old_status ? `${STATUS_LABELS[h.old_status]||h.old_status} → ` : ''}${STATUS_LABELS[h.new_status]||h.new_status}</div>
      ${h.comment ? `<div class="tl-comment">${h.comment}</div>` : ''}
      ${h.changed_by_name ? `<div class="tl-by">${h.changed_by_name}</div>` : ''}
    </div>`).join('');
}

function renderActionBar() {
  const bar = document.getElementById('action-bar');
  const user = API.getUser();
  const s = REQ.status;
  const role = user.role;
  let btns = [];

  if ((s === 'new' || s === 'assigned') && (role === 'dispatcher' || role === 'admin')) {
    btns.push(`<button class="btn btn-primary" onclick="openAssignModal()">Назначить</button>`);
  }
  if (s === 'assigned' && (role === 'executor' || role === 'dispatcher' || role === 'admin')) {
    btns.push(`<button class="btn btn-warning" onclick="confirmStatus('in_progress','В работе','Взять в работу')">Взять в работу</button>`);
  }
  if (s === 'in_progress' && (role === 'executor' || role === 'dispatcher' || role === 'admin') && !REQ.diagnostic) {
    btns.push(`<button class="btn btn-primary" onclick="openModal('modal-diag')">Добавить диагностику</button>`);
  }
  if (s === 'diagnostics_done' && (role === 'executor' || role === 'dispatcher' || role === 'admin') && !REQ.repair) {
    btns.push(`<button class="btn btn-primary" onclick="openModal('modal-repair')">Добавить ремонт</button>`);
  }
  if ((s === 'completed' || s === 'closed') && (role === 'executor' || role === 'dispatcher' || role === 'admin') && !REQ.report) {
    btns.push(`<button class="btn btn-secondary" onclick="openModal('modal-report')">Создать отчёт</button>`);
  }
  if (s === 'completed' && (role === 'dispatcher' || role === 'admin')) {
    btns.push(`<button class="btn btn-success" onclick="confirmStatus('closed','Закрытие','Закрыть заявку')">Закрыть</button>`);
  }
  if ((s === 'new' || s === 'assigned') && (role === 'dispatcher' || role === 'admin' || role === 'shift_manager')) {
    btns.push(`<button class="btn btn-danger" onclick="confirmStatus('cancelled','Отмена','Отменить заявку')">Отменить</button>`);
  }

  bar.innerHTML = btns.join('');
}

function renderDiagnostic() {
  if (!REQ.diagnostic) return;
  const d = REQ.diagnostic;
  document.getElementById('diag-card').style.display = '';
  document.getElementById('diag-body').innerHTML = `
    <div class="detail-grid">
      <div class="detail-item"><div class="detail-label">Причина</div><div class="detail-value">${d.cause}</div></div>
      <div class="detail-item"><div class="detail-label">Методы</div><div class="detail-value">${d.methods_used||'—'}</div></div>
      <div class="detail-item"><div class="detail-label">Инструменты</div><div class="detail-value">${d.tools_used||'—'}</div></div>
      <div class="detail-item"><div class="detail-label">Требуется ремонт</div><div class="detail-value">${d.repair_required ? 'Да' : 'Нет'}</div></div>
      <div class="detail-item"><div class="detail-label">Примечания</div><div class="detail-value">${d.notes||'—'}</div></div>
    </div>`;
}

function renderRepair() {
  if (!REQ.repair) return;
  const r = REQ.repair;
  document.getElementById('repair-card').style.display = '';
  let matsHtml = '';
  if (r.materials && r.materials.length) {
    matsHtml = `<table style="margin-top:10px"><thead><tr><th>Материал</th><th>Кол-во</th><th>Ед.</th><th>Стоимость</th></tr></thead><tbody>
      ${r.materials.map(m=>`<tr><td>${m.name}</td><td>${m.quantity}</td><td>${m.unit||'—'}</td><td>${m.cost!=null?m.cost+'₽':'—'}</td></tr>`).join('')}
    </tbody></table>`;
  }
  document.getElementById('repair-body').innerHTML = `
    <div class="detail-grid mb-4">
      <div class="detail-item"><div class="detail-label">Работы</div><div class="detail-value">${r.operations}</div></div>
      <div class="detail-item"><div class="detail-label">Трудозатраты</div><div class="detail-value">${r.labor_hours!=null?r.labor_hours+' ч':'—'}</div></div>
      <div class="detail-item"><div class="detail-label">Примечания</div><div class="detail-value">${r.notes||'—'}</div></div>
      <div class="detail-item"><div class="detail-label">Завершён</div><div class="detail-value">${fmtDate(r.completed_at)}</div></div>
    </div>${matsHtml}`;
}

function renderReport() {
  if (!REQ.report) return;
  const r = REQ.report;
  document.getElementById('report-card').style.display = '';
  document.getElementById('report-body').innerHTML = `
    <div class="detail-grid">
      <div class="detail-item"><div class="detail-label">Резюме</div><div class="detail-value">${r.summary}</div></div>
      <div class="detail-item"><div class="detail-label">Заключение</div><div class="detail-value">${r.conclusion}</div></div>
      <div class="detail-item"><div class="detail-label">Рекомендации</div><div class="detail-value">${r.recommendations||'—'}</div></div>
      <div class="detail-item"><div class="detail-label">Создан</div><div class="detail-value">${fmtDate(r.created_at)}</div></div>
    </div>`;
}

/* ── Status change via modal ─────────────────────── */
function confirmStatus(newStatus, label, btnLabel) {
  document.getElementById('ms-title').textContent = label;
  document.getElementById('ms-confirm').textContent = btnLabel;
  document.getElementById('ms-confirm').onclick = () => doStatusChange(newStatus);
  document.getElementById('ms-comment').value = '';
  openModal('modal-status');
}

async function doStatusChange(newStatus) {
  const comment = document.getElementById('ms-comment').value.trim();
  const res = await API.put(`/requests/${REQ_ID}/status`, { status: newStatus, comment: comment || null });
  if (!res) return;
  if (res.ok) {
    closeModal('modal-status');
    toast('Статус обновлён', 'success');
    await loadRequest();
  } else {
    toast(await apiError(res), 'error');
  }
}

/* ── Assign ──────────────────────────────────────── */
async function openAssignModal() {
  const [usersRes, svcsRes] = await Promise.all([
    API.get('/users?role=executor'),
    API.get('/services'),
  ]);
  if (usersRes && usersRes.ok) {
    const users = await usersRes.json();
    document.getElementById('a-executor').innerHTML =
      '<option value="">— не выбрано —</option>' +
      users.map(u => `<option value="${u.id}">${u.full_name}</option>`).join('');
  }
  if (svcsRes && svcsRes.ok) {
    const svcs = await svcsRes.json();
    document.getElementById('a-service').innerHTML =
      '<option value="">— не выбрано —</option>' +
      svcs.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
  }
  openModal('modal-assign');
}

async function doAssign() {
  const execId = document.getElementById('a-executor').value;
  const svcId  = document.getElementById('a-service').value;
  const comment = document.getElementById('a-comment').value.trim();
  const payload = { status: 'assigned', comment: comment || null };
  if (execId) payload.executor_id = parseInt(execId);
  if (svcId)  payload.service_id  = parseInt(svcId);
  const res = await API.put(`/requests/${REQ_ID}/status`, payload);
  if (!res) return;
  if (res.ok) { closeModal('modal-assign'); toast('Заявка назначена', 'success'); await loadRequest(); }
  else toast(await apiError(res), 'error');
}

/* ── Diagnostic ──────────────────────────────────── */
async function doDiag() {
  const cause = document.getElementById('d-cause').value.trim();
  if (!cause) { toast('Укажите причину неисправности', 'error'); return; }
  const res = await API.post(`/requests/${REQ_ID}/diagnostic`, {
    cause,
    methods_used: document.getElementById('d-methods').value.trim() || null,
    tools_used:   document.getElementById('d-tools').value.trim()   || null,
    notes:        document.getElementById('d-notes').value.trim()   || null,
    repair_required: document.getElementById('d-repair').checked,
  });
  if (!res) return;
  if (res.ok) { closeModal('modal-diag'); toast('Диагностика сохранена', 'success'); await loadRequest(); }
  else toast(await apiError(res), 'error');
}

/* ── Repair ──────────────────────────────────────── */
function addMatRow() {
  const row = document.createElement('div');
  row.className = 'mat-row';
  row.innerHTML = `
    <input type="text"   placeholder="Название">
    <input type="number" placeholder="Кол-во" min="0" step="0.1">
    <input type="text"   placeholder="Ед.">
    <input type="number" placeholder="Цена ₽" min="0">
    <button class="btn btn-danger btn-sm" onclick="this.parentElement.remove()">×</button>`;
  document.getElementById('mat-list').appendChild(row);
}

async function doRepair() {
  const ops = document.getElementById('rp-ops').value.trim();
  if (!ops) { toast('Укажите выполненные работы', 'error'); return; }
  const hours = parseFloat(document.getElementById('rp-hours').value) || null;
  const materials = [];
  document.querySelectorAll('#mat-list .mat-row').forEach(row => {
    const inputs = row.querySelectorAll('input');
    const name = inputs[0].value.trim();
    if (name) materials.push({
      name,
      quantity: parseFloat(inputs[1].value) || 1,
      unit: inputs[2].value.trim() || null,
      cost: parseFloat(inputs[3].value) || null,
    });
  });
  const res = await API.post(`/requests/${REQ_ID}/repair`, {
    operations: ops,
    labor_hours: hours,
    notes: document.getElementById('rp-notes').value.trim() || null,
    completed: document.getElementById('rp-done').checked,
    materials,
  });
  if (!res) return;
  if (res.ok) { closeModal('modal-repair'); toast('Ремонт сохранён', 'success'); await loadRequest(); }
  else toast(await apiError(res), 'error');
}

/* ── Report ──────────────────────────────────────── */
async function doReport() {
  const summary    = document.getElementById('rpt-summary').value.trim();
  const conclusion = document.getElementById('rpt-conclusion').value.trim();
  if (!summary || !conclusion) { toast('Заполните обязательные поля', 'error'); return; }
  const res = await API.post(`/requests/${REQ_ID}/report`, {
    summary, conclusion,
    recommendations: document.getElementById('rpt-rec').value.trim() || null,
  });
  if (!res) return;
  if (res.ok) { closeModal('modal-report'); toast('Отчёт создан', 'success'); await loadRequest(); }
  else toast(await apiError(res), 'error');
}

loadRequest();
