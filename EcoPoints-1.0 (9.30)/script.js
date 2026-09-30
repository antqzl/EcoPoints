// Frontend authentication and page switching for the local demo.
// 本地演示所需的前端登录、注册和页面切换逻辑。
const API_BASE = 'http://127.0.0.1:8000';

function byId(id) { return document.getElementById(id); }

function setMessage(element, message, isError = true) {
  if (!element) return;
  element.textContent = message;
  element.classList.toggle('error', isError);
  element.classList.toggle('success', !isError);
}

function showPage(pageId) {
  document.querySelectorAll('.page-view').forEach((page) => page.classList.toggle('active', page.id === pageId));
  document.querySelectorAll('[data-route], .nav-item').forEach((link) => {
    const route = link.dataset.route || ({ Home: 'homePage', Dashboard: 'dashboardPage', EcoPoints: 'ecoPointsPage', Rewards: 'rewardsPage', Profile: 'profilePage', Admin: 'adminPage' }[link.textContent.trim()]);
    link.classList.toggle('active', route === pageId);
  });
  window.scrollTo({ top: 0, behavior: 'smooth' });
  if (pageId === 'rewardsPage') loadRewards();
  if (pageId === 'profilePage') loadProfilePreferences();
}

function saveSession(data, remember) {
  const storage = remember ? localStorage : sessionStorage;
  storage.setItem('ecopoints_token', data.access_token);
  storage.setItem('ecopoints_user', JSON.stringify(data.user));
}

function getToken() {
  return localStorage.getItem('ecopoints_token') || sessionStorage.getItem('ecopoints_token');
}

function clearSession() {
  localStorage.removeItem('ecopoints_token');
  localStorage.removeItem('ecopoints_user');
  sessionStorage.removeItem('ecopoints_token');
  sessionStorage.removeItem('ecopoints_user');
}

async function api(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || `Request failed (${response.status})`);
  return data;
}

function updateUserLabels(user) {
  document.querySelectorAll('.user-name').forEach((item) => { item.textContent = user.full_name; });
  document.querySelectorAll('.user-role').forEach((item) => { item.textContent = user.role; });
}

async function signIn(email, password, remember) {
  const data = await api('/api/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) });
  saveSession(data, remember);
  updateUserLabels(data.user);
  showPage('homePage');
}

async function registerAccount(payload) {
  const data = await api('/api/auth/register', { method: 'POST', body: JSON.stringify(payload) });
  saveSession(data, true);
  updateUserLabels(data.user);
  byId('registerModal').hidden = true;
  showPage('homePage');
}

function wireNavigation() {
  document.querySelectorAll('[data-route], .nav-item, .nav-dash-btn').forEach((button) => button.addEventListener('click', (event) => {
    event.preventDefault();
    const route = button.dataset.route || (button.classList.contains('nav-dash-btn') ? 'dashboardPage' : ({ Home: 'homePage', Dashboard: 'dashboardPage', EcoPoints: 'ecoPointsPage', Rewards: 'rewardsPage', Profile: 'profilePage', Admin: 'adminPage' }[button.textContent.trim()]));
    if (route) showPage(route);
  }));
}

async function loadRewards() {
  const grid = byId('rewardsGrid');
  if (!grid) return;
  try {
    const rewards = await api('/api/rewards');
    grid.innerHTML = rewards.map((reward) => {
      const icon = reward.name.includes('Bottle') ? '♻' : '☕';
      const available = reward.stock > 0;
      return `<article class="reward-item"><div class="reward-icon">${icon}</div><div class="reward-copy"><span class="reward-label">${available ? 'Available now' : 'Out of stock'}</span><h2>${reward.name}</h2><p>${reward.description}</p><strong>${reward.points_cost} pts</strong></div><button class="btn-primary reward-redeem" data-reward-id="${reward.id}" ${available ? '' : 'disabled'}>${available ? 'Redeem' : 'Out of stock'}</button><small>${available ? `${reward.stock} left` : 'Check back later'}</small></article>`;
    }).join('');
    grid.querySelectorAll('.reward-redeem').forEach((button) => button.addEventListener('click', () => redeemReward(Number(button.dataset.rewardId), button)));
  } catch (error) {
    grid.innerHTML = '<div class="empty-state">Unable to load rewards. Make sure the API server is running.</div>';
  }
}

async function redeemReward(rewardId, button) {
  const message = byId('rewardMessage');
  button.disabled = true;
  try {
    const result = await api(`/api/rewards/${rewardId}/redeem`, { method: 'POST', headers: { Authorization: `Bearer ${getToken()}` } });
    setMessage(message, `${result.message}. ${result.remaining_points} points remaining.`, false);
    byId('shopBalance').textContent = `${result.remaining_points} pts`;
    await loadRewards();
  } catch (error) {
    setMessage(message, error.message);
    button.disabled = false;
  }
}

function loadProfilePreferences() {
  const stored = JSON.parse(localStorage.getItem('ecopoints_profile') || '{}');
  if (stored.name) byId('profileNameInput').value = stored.name;
  if (stored.email) byId('profileEmailInput').value = stored.email;
  if (stored.phone) byId('profilePhoneInput').value = stored.phone;
  if (stored.language) byId('languageSetting').value = stored.language;
  if (stored.picture) { byId('profileAvatar').style.backgroundImage = `url(${stored.picture})`; byId('profileAvatar').textContent = ''; }
  if (stored.font) byId('fontSetting').value = stored.font;
  if (stored.theme === 'dark') byId('themeSetting').checked = true;
  if (stored.notifications !== undefined) byId('notificationSetting').checked = stored.notifications;
  applyPreferences();
}

function applyPreferences() {
  document.body.classList.toggle('large-text', byId('fontSetting')?.value === 'large');
  document.body.classList.toggle('dark-mode', Boolean(byId('themeSetting')?.checked));
}

document.addEventListener('DOMContentLoaded', () => {
  if (window.lucide) window.lucide.createIcons();
  const loginForm = byId('loginForm');
  const authMessage = byId('authMessage');
  const registerMessage = byId('registerMessage');
  const registerModal = byId('registerModal');

  loginForm?.addEventListener('submit', async (event) => {
    event.preventDefault();
    setMessage(authMessage, 'Signing in...', false);
    try {
      await signIn(byId('email').value.trim(), byId('password').value, byId('rememberMe').checked);
    } catch (error) {
      setMessage(authMessage, error.message);
    }
  });

  byId('togglePassword')?.addEventListener('click', () => {
    const password = byId('password');
    password.type = password.type === 'password' ? 'text' : 'password';
  });

  byId('googleSignInBtn')?.addEventListener('click', () => {
    setMessage(authMessage, 'Google Sign-In is not configured for this local demo. Use email registration or the demo account.');
  });

  byId('registerLink')?.addEventListener('click', (event) => {
    event.preventDefault(); registerModal.hidden = false; byId('registerName')?.focus();
  });
  document.querySelectorAll('[data-close-register]').forEach((button) => button.addEventListener('click', () => { registerModal.hidden = true; }));

  byId('registerForm')?.addEventListener('submit', async (event) => {
    event.preventDefault();
    setMessage(registerMessage, 'Creating account...', false);
    try {
      await registerAccount({
        full_name: byId('registerName').value.trim(),
        email: byId('registerEmail').value.trim(),
        password: byId('registerPassword').value,
      });
    } catch (error) {
      setMessage(registerMessage, error.message);
    }
  });

  wireNavigation();
  byId('logoutBtn')?.addEventListener('click', () => { clearSession(); showPage('loginPage'); });
  byId('saveProfileBtn')?.addEventListener('click', () => {
    const previous = JSON.parse(localStorage.getItem('ecopoints_profile') || '{}');
    const profile = { ...previous, name: byId('profileNameInput').value.trim(), email: byId('profileEmailInput').value.trim(), phone: byId('profilePhoneInput').value.trim(), language: byId('languageSetting').value, font: byId('fontSetting').value, theme: byId('themeSetting').checked ? 'dark' : 'light', notifications: byId('notificationSetting').checked };
    localStorage.setItem('ecopoints_profile', JSON.stringify(profile));
    byId('profileName').textContent = profile.name || 'EcoPoints member';
    byId('profileEmail').textContent = profile.email;
    byId('profileAvatar').textContent = (profile.name || 'EP').split(' ').map((part) => part[0]).join('').slice(0, 2).toUpperCase();
    setMessage(byId('profileMessage'), 'Profile preferences saved.', false);
  });
  byId('profilePictureInput')?.addEventListener('change', (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => { byId('profileAvatar').style.backgroundImage = `url(${reader.result})`; byId('profileAvatar').textContent = ''; const profile = JSON.parse(localStorage.getItem('ecopoints_profile') || '{}'); profile.picture = reader.result; localStorage.setItem('ecopoints_profile', JSON.stringify(profile)); };
    reader.readAsDataURL(file);
  });
  ['languageSetting', 'fontSetting', 'themeSetting', 'notificationSetting'].forEach((id) => byId(id)?.addEventListener('change', applyPreferences));
  document.querySelectorAll('[data-admin-action]').forEach((button) => button.addEventListener('click', () => setMessage(byId('adminMessage'), `${button.textContent.trim()} is ready for backend integration.`, false)));
  const savedUser = localStorage.getItem('ecopoints_user') || sessionStorage.getItem('ecopoints_user');
  if (getToken() && savedUser) {
    updateUserLabels(JSON.parse(savedUser));
    showPage('homePage');
  }
});
