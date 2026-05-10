if (API.getToken()) window.location.href = '/dashboard';

document.getElementById('login-form').addEventListener('submit', async e => {
  e.preventDefault();
  const btn = document.getElementById('login-btn');
  const errEl = document.getElementById('login-error');
  errEl.classList.remove('show');
  btn.disabled = true;
  btn.textContent = 'Вход...';

  const res = await API.post('/auth/login', {
    email: document.getElementById('email').value.trim(),
    password: document.getElementById('password').value,
  });

  btn.disabled = false;
  btn.textContent = 'Войти';

  if (!res) return;

  if (res.ok) {
    const data = await res.json();
    API.setToken(data.access_token);
    API.setUser(data.user);
    window.location.href = '/dashboard';
  } else {
    const j = await res.json();
    errEl.textContent = j.error || 'Ошибка входа';
    errEl.classList.add('show');
  }
});
