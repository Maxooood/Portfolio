if (!requireAuth()) throw '';
if (!hasRole('admin', 'manager')) { window.location.href = '/dashboard'; throw ''; }
initSidebar();

let editingUserId = null;

if (hasRole('admin')) {
  document.getElementById('btn-add-user').style.display = '';
}

async function loadUsers() {
  const role = document.getElementById('f-role').value;
  let url = '/users';
  if (role) url += `?role=${role}`;
  const res = await API.get(url);
  const tbody = document.getElementById('users-tbody');
  if (!res || !res.ok) { tbody.innerHTML = '<tr><td colspan="8" class="text-muted" style="padding:20px">Ошибка загрузки</td></tr>'; return; }
  const users = await res.json();
  if (!users.length) {
    tbody.innerHTML = `<tr><td colspan="8"><div class="empty"><div class="empty-icon">👤</div><div class="empty-text">Пользователи не найдены</div></div></td></tr>`;
    return;
  }
  const isAdmin = hasRole('admin');
  tbody.innerHTML = users.map(u => `
    <tr>
      <td><code>${u.employee_number}</code></td>
      <td>${u.full_name}</td>
      <td>${u.email}</td>
      <td><span class="role-badge">${ROLE_LABELS[u.role]||u.role}</span></td>
      <td>${u.department||'—'}</td>
      <td>${u.phone||'—'}</td>
      <td>${u.is_active ? '<span class="badge badge-completed">Активен</span>' : '<span class="badge badge-cancelled">Неактивен</span>'}</td>
      <td>${isAdmin ? `<button class="btn btn-secondary btn-sm" onclick="openEdit(${JSON.stringify(u).replace(/"/g,'&quot;')})">Ред.</button>` : ''}</td>
    </tr>`).join('');
}

async function submitUser() {
  const num   = document.getElementById('nu-num').value.trim();
  const name  = document.getElementById('nu-name').value.trim();
  const email = document.getElementById('nu-email').value.trim();
  const pass  = document.getElementById('nu-pass').value;
  const role  = document.getElementById('nu-role').value;
  if (!num || !name || !email || !pass || !role) { toast('Заполните обязательные поля', 'error'); return; }

  const res = await API.post('/users', {
    employee_number: num, full_name: name, email, password: pass, role,
    department: document.getElementById('nu-dept').value.trim()  || null,
    phone:      document.getElementById('nu-phone').value.trim() || null,
  });
  if (!res) return;
  if (res.ok) { closeModal('modal-add-user'); toast('Пользователь создан', 'success'); loadUsers(); }
  else toast(await apiError(res), 'error');
}

function openEdit(user) {
  editingUserId = user.id;
  document.getElementById('eu-name').value  = user.full_name;
  document.getElementById('eu-role').value  = user.role;
  document.getElementById('eu-dept').value  = user.department || '';
  document.getElementById('eu-phone').value = user.phone || '';
  document.getElementById('eu-pass').value  = '';
  document.getElementById('eu-active').checked = user.is_active;
  openModal('modal-edit-user');
}

async function saveUser() {
  const payload = {
    full_name:  document.getElementById('eu-name').value.trim(),
    role:       document.getElementById('eu-role').value,
    department: document.getElementById('eu-dept').value.trim()  || null,
    phone:      document.getElementById('eu-phone').value.trim() || null,
    is_active:  document.getElementById('eu-active').checked,
  };
  const pass = document.getElementById('eu-pass').value;
  if (pass) payload.password = pass;

  const res = await API.put(`/users/${editingUserId}`, payload);
  if (!res) return;
  if (res.ok) { closeModal('modal-edit-user'); toast('Пользователь обновлён', 'success'); loadUsers(); }
  else toast(await apiError(res), 'error');
}

loadUsers();
