if (!requireAuth()) throw '';
initSidebar();

let currentPage = 1;

if (hasRole('admin', 'dispatcher', 'shift_manager')) {
  document.getElementById('btn-create').style.display = '';
}

async function loadRequests(page = 1) {
  currentPage = page;
  const status   = document.getElementById('f-status').value;
  const priority = document.getElementById('f-priority').value;
  let url = `/requests?page=${page}&per_page=20`;
  if (status)   url += `&status=${status}`;
  if (priority) url += `&priority=${priority}`;

  const tbody = document.getElementById('req-tbody');
  tbody.innerHTML = '<tr><td colspan="7" class="loading">Загрузка...</td></tr>';

  const res = await API.get(url);
  if (!res) return;
  if (!res.ok) {
    tbody.innerHTML = '<tr><td colspan="7" class="text-muted" style="padding:20px">Ошибка загрузки</td></tr>';
    return;
  }
  const d = await res.json();

  if (!d.items.length) {
    tbody.innerHTML = `<tr><td colspan="7"><div class="empty">
      <div class="empty-icon">📋</div>
      <div class="empty-text">Заявок не найдено</div>
      <div class="empty-sub">Попробуйте изменить фильтры</div>
    </div></td></tr>`;
    document.getElementById('pagination').innerHTML = '';
    return;
  }

  tbody.innerHTML = d.items.map(r => `
    <tr class="row-link" onclick="window.location='/requests/${r.id}'">
      <td><code>${r.request_number}</code></td>
      <td>${r.title}</td>
      <td>${r.equipment ? r.equipment.name : '—'}</td>
      <td>${priorityBadge(r.priority)}</td>
      <td>${statusBadge(r.status)}</td>
      <td>${r.service ? r.service.name : '—'}</td>
      <td>${fmtDate(r.created_at)}</td>
    </tr>`).join('');

  renderPagination(d.page, d.pages);
}

function renderPagination(page, pages) {
  const el = document.getElementById('pagination');
  if (pages <= 1) { el.innerHTML = ''; return; }
  let html = '';
  if (page > 1) html += `<button class="btn btn-secondary btn-sm" onclick="loadRequests(${page-1})">‹</button>`;
  html += `<span>Стр. ${page} / ${pages}</span>`;
  if (page < pages) html += `<button class="btn btn-secondary btn-sm" onclick="loadRequests(${page+1})">›</button>`;
  el.innerHTML = html;
}

/* ── Load selects for create form ─────────────────── */
async function loadFormSelects() {
  const [eqRes, ftRes] = await Promise.all([API.get('/equipment'), API.get('/fault-types')]);
  if (eqRes && eqRes.ok) {
    const items = await eqRes.json();
    const sel = document.getElementById('c-eq');
    sel.innerHTML = '<option value="">— выберите —</option>' +
      items.map(e => `<option value="${e.id}">${e.name} (${e.inventory_number})</option>`).join('');
  }
  if (ftRes && ftRes.ok) {
    const items = await ftRes.json();
    const sel = document.getElementById('c-fault');
    sel.innerHTML = '<option value="">— не выбрано —</option>' +
      items.map(f => `<option value="${f.id}">${f.name}</option>`).join('');
  }
}

async function submitCreate() {
  const title = document.getElementById('c-title').value.trim();
  const desc  = document.getElementById('c-desc').value.trim();
  const eqId  = document.getElementById('c-eq').value;
  if (!title || !desc || !eqId) { toast('Заполните обязательные поля', 'error'); return; }

  const btn = document.getElementById('btn-create-submit');
  btn.disabled = true;

  const payload = {
    title, description: desc,
    equipment_id: parseInt(eqId),
    priority: document.getElementById('c-priority').value,
    notes: document.getElementById('c-notes').value.trim() || null,
  };
  const ftId = document.getElementById('c-fault').value;
  if (ftId) payload.fault_type_id = parseInt(ftId);

  const res = await API.post('/requests', payload);
  btn.disabled = false;
  if (!res) return;
  if (res.ok) {
    const r = await res.json();
    closeModal('modal-create');
    toast('Заявка создана', 'success');
    window.location.href = `/requests/${r.id}`;
  } else {
    toast(await apiError(res), 'error');
  }
}

loadRequests();
loadFormSelects();
