if (!requireAuth()) throw '';
initSidebar();

let allEquipment = [];
let editingId = null;

if (hasRole('admin', 'dispatcher')) {
  document.getElementById('btn-add-eq').style.display = '';
}

async function loadEquipment() {
  const status = document.getElementById('f-status').value;
  let url = '/equipment';
  if (status) url += `?status=${status}`;
  const res = await API.get(url);
  const tbody = document.getElementById('eq-tbody');
  if (!res || !res.ok) { tbody.innerHTML = '<tr><td colspan="7" class="text-muted" style="padding:20px">Ошибка загрузки</td></tr>'; return; }
  allEquipment = await res.json();
  renderTable(allEquipment);
}

function renderTable(items) {
  const tbody = document.getElementById('eq-tbody');
  if (!items.length) {
    tbody.innerHTML = `<tr><td colspan="7"><div class="empty"><div class="empty-icon">⚙</div><div class="empty-text">Оборудование не найдено</div></div></td></tr>`;
    return;
  }
  tbody.innerHTML = items.map(e => `
    <tr class="row-link" onclick="openDetail(${e.id})">
      <td><code>${e.inventory_number}</code></td>
      <td>${e.name}</td>
      <td>${e.equipment_type||'—'}</td>
      <td>${e.department||'—'}</td>
      <td>${e.location||'—'}</td>
      <td>${[e.manufacturer, e.model].filter(Boolean).join(' / ')||'—'}</td>
      <td>${eqBadge(e.status)}</td>
    </tr>`).join('');
}

function filterByDept() {
  const q = document.getElementById('f-dept').value.toLowerCase();
  renderTable(allEquipment.filter(e => !q || (e.department||'').toLowerCase().includes(q)));
}

function openDetail(id) {
  const e = allEquipment.find(x => x.id === id);
  if (!e) return;
  editingId = id;
  document.getElementById('eq-detail-title').textContent = e.name;
  document.getElementById('eq-detail-body').innerHTML = `
    <div class="detail-grid">
      <div class="detail-item"><div class="detail-label">Инв. номер</div><div class="detail-value">${e.inventory_number}</div></div>
      <div class="detail-item"><div class="detail-label">Тип</div><div class="detail-value">${e.equipment_type||'—'}</div></div>
      <div class="detail-item"><div class="detail-label">Отдел</div><div class="detail-value">${e.department||'—'}</div></div>
      <div class="detail-item"><div class="detail-label">Местонахождение</div><div class="detail-value">${e.location||'—'}</div></div>
      <div class="detail-item"><div class="detail-label">Производитель</div><div class="detail-value">${e.manufacturer||'—'}</div></div>
      <div class="detail-item"><div class="detail-label">Модель</div><div class="detail-value">${e.model||'—'}</div></div>
      <div class="detail-item"><div class="detail-label">Год выпуска</div><div class="detail-value">${e.year_of_manufacture||'—'}</div></div>
      <div class="detail-item"><div class="detail-label">Статус</div><div class="detail-value">${eqBadge(e.status)}</div></div>
    </div>`;

  const canEdit = hasRole('admin', 'dispatcher');
  const editArea = document.getElementById('eq-edit-area');
  const saveBtn  = document.getElementById('btn-eq-save');
  if (canEdit) {
    editArea.style.display = '';
    saveBtn.style.display  = '';
    document.getElementById('eq-edit-status').value = e.status;
    document.getElementById('eq-edit-loc').value    = e.location || '';
  } else {
    editArea.style.display = 'none';
    saveBtn.style.display  = 'none';
  }
  openModal('modal-eq-detail');
}

async function saveEquipment() {
  const res = await API.put(`/equipment/${editingId}`, {
    status:   document.getElementById('eq-edit-status').value,
    location: document.getElementById('eq-edit-loc').value.trim() || null,
  });
  if (!res) return;
  if (res.ok) { closeModal('modal-eq-detail'); toast('Оборудование обновлено', 'success'); loadEquipment(); }
  else toast(await apiError(res), 'error');
}

async function submitEquipment() {
  const name = document.getElementById('ne-name').value.trim();
  const inv  = document.getElementById('ne-inv').value.trim();
  if (!name || !inv) { toast('Заполните обязательные поля', 'error'); return; }
  const year = parseInt(document.getElementById('ne-year').value) || null;
  const res = await API.post('/equipment', {
    name, inventory_number: inv,
    equipment_type: document.getElementById('ne-type').value.trim()  || null,
    department:     document.getElementById('ne-dept').value.trim()  || null,
    location:       document.getElementById('ne-loc').value.trim()   || null,
    manufacturer:   document.getElementById('ne-mfr').value.trim()   || null,
    model:          document.getElementById('ne-model').value.trim() || null,
    year_of_manufacture: year,
  });
  if (!res) return;
  if (res.ok) { closeModal('modal-add-eq'); toast('Оборудование добавлено', 'success'); loadEquipment(); }
  else toast(await apiError(res), 'error');
}

loadEquipment();
