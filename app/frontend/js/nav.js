// ── Shared navigation & theme helpers ──────────────────────

function toggleTheme() {
  const html = document.documentElement;
  const isLight = html.getAttribute('data-theme') === 'light';
  html.setAttribute('data-theme', isLight ? 'dark' : 'light');
  localStorage.setItem('mtm-theme', isLight ? 'dark' : 'light');
  const toggle = document.getElementById('themeToggle');
  if (toggle) toggle.checked = !isLight;
  const icon = document.querySelector('.side-theme-toggle i');
  if (icon) {
    icon.className = isLight ? 'fa-solid fa-moon' : 'fa-solid fa-sun';
  }
}

function loadSavedTheme() {
  const saved = localStorage.getItem('mtm-theme') || 'dark';
  document.documentElement.setAttribute('data-theme', saved);
  const toggle = document.getElementById('themeToggle');
  if (toggle) toggle.checked = saved === 'light';
  const icon = document.querySelector('.side-theme-toggle i');
  if (icon) icon.className = saved === 'light' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
}

function toggleMenu() {
  document.getElementById('sideMenu')?.classList.toggle('open');
  document.getElementById('menuOverlay')?.classList.toggle('active');
}

function closeMenu() {
  document.getElementById('sideMenu')?.classList.remove('open');
  document.getElementById('menuOverlay')?.classList.remove('active');
}

// Load user info into side menu
function loadUserInMenu() {
  const user = JSON.parse(sessionStorage.getItem('mtm_user') || '{}');
  const nameEl = document.querySelector('.side-name');
  const handleEl = document.querySelector('.side-handle');
  const avatarEl = document.querySelector('.side-avatar');
  if (nameEl && user.name) nameEl.textContent = user.name;
  if (handleEl && user.username) handleEl.textContent = user.username;
  if (avatarEl && user.avatar) {
    avatarEl.innerHTML = `<img src="${user.avatar}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;" />`;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  loadSavedTheme();
  loadUserInMenu();
});
