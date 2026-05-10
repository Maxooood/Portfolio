/* ── Token / user storage ───────────────────────── */
const API = {
  base: '/api',

  getToken() { return localStorage.getItem('toir_token'); },
  setToken(t) { localStorage.setItem('toir_token', t); },
  clearAuth() { localStorage.removeItem('toir_token'); localStorage.removeItem('toir_user'); },
  getUser()  { const u = localStorage.getItem('toir_user'); return u ? JSON.parse(u) : null; },
  setUser(u) { localStorage.setItem('toir_user', JSON.stringify(u)); },

  async call(method, path, data) {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    const token = this.getToken();
    if (token) opts.headers['Authorization'] = `Bearer ${token}`;
    if (data !== undefined) opts.body = JSON.stringify(data);
    let res;
    try { res = await fetch(this.base + path, opts); }
    catch (e) { throw new Error('Ошибка сети. Проверьте подключение.'); }
    if (res.status === 401) { this.clearAuth(); window.location.href = '/login'; return null; }
    return res;
  },

  get(path)       { return this.call('GET',    path); },
  post(path, d)   { return this.call('POST',   path, d); },
  put(path, d)    { return this.call('PUT',    path, d); },
  delete(path)    { return this.call('DELETE', path); },
};

/* ── Auth guard ─────────────────────────────────── */
function requireAuth() {
  if (!API.getToken()) { window.location.href = '/login'; return false; }
  return true;
}

function logout() { API.clearAuth(); window.location.href = '/login'; }

/* ── Labels & helpers ───────────────────────────── */
const ROLE_LABELS = {
  admin: 'Администратор', manager: 'Руководитель',
  dispatcher: 'Диспетчер', executor: 'Исполнитель', shift_manager: 'Нач. смены',
};
const STATUS_LABELS = {
  new: 'Новая', assigned: 'Назначена', in_progress: 'В работе',
  diagnostics_done: 'Диагностика', repair_in_progress: 'Ремонт',
  completed: 'Выполнена', closed: 'Закрыта', cancelled: 'Отменена',
};
const PRIORITY_LABELS = { low: 'Низкий', medium: 'Средний', high: 'Высокий', critical: 'Критический' };
const EQ_STATUS_LABELS = {
  operational: 'Работает', under_maintenance: 'Обслуживание',
  broken: 'Сломано', decommissioned: 'Списано',
};

function statusBadge(s)   { return `<span class="badge badge-${s}">${STATUS_LABELS[s]||s}</span>`; }
function priorityBadge(p) { return `<span class="badge badge-${p}">${PRIORITY_LABELS[p]||p}</span>`; }
function eqBadge(s)       { return `<span class="badge badge-${s}">${EQ_STATUS_LABELS[s]||s}</span>`; }

function fmtDate(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleString('ru-RU', { day:'2-digit', month:'2-digit', year:'numeric', hour:'2-digit', minute:'2-digit' });
}

function hasRole(...roles) {
  const u = API.getUser(); return u && roles.includes(u.role);
}

/* ── Sidebar init ───────────────────────────────── */
function initSidebar() {
  const user = API.getUser();
  if (!user) return;
  const nameEl = document.getElementById('sb-name');
  const roleEl = document.getElementById('sb-role');
  if (nameEl) nameEl.textContent = user.full_name;
  if (roleEl) roleEl.textContent = ROLE_LABELS[user.role] || user.role;

  document.querySelectorAll('[data-roles]').forEach(el => {
    const roles = el.dataset.roles.split(',');
    el.style.display = roles.includes(user.role) ? '' : 'none';
  });

  const path = window.location.pathname;
  document.querySelectorAll('.sidebar-nav a').forEach(a => {
    const href = a.getAttribute('href');
    const active = href === path || (href !== '/dashboard' && path.startsWith(href));
    a.classList.toggle('active', active);
  });
}

/* ── Toast ──────────────────────────────────────── */
function toast(msg, type = 'info') {
  let box = document.getElementById('toast-container');
  if (!box) { box = document.createElement('div'); box.id = 'toast-container'; document.body.appendChild(box); }
  const el = document.createElement('div');
  el.className = `toast toast-${type}`;
  el.textContent = msg;
  box.appendChild(el);
  setTimeout(() => el.remove(), 4000);
}

/* ── Modal helpers ──────────────────────────────── */
function openModal(id)  { document.getElementById(id).classList.add('open'); }
function closeModal(id) { document.getElementById(id).classList.remove('open'); }

/* ── Error text from API response ───────────────── */
async function apiError(res) {
  try { const j = await res.json(); return j.error || `Ошибка ${res.status}`; }
  catch { return `Ошибка ${res.status}`; }
}
