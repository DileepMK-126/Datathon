const API_BASE = import.meta.env.VITE_API_URL || '/api';

export async function getApi(path) {
  const token = localStorage.getItem('sentinel_access_token');
  const response = await fetch(`${API_BASE}${path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!response.ok) throw new Error(`API request failed (${response.status})`);
  return response.json();
}

export async function postApi(path, body = null) {
  const token = localStorage.getItem('sentinel_access_token');
  const headers = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  if (body) {
    headers['Content-Type'] = 'application/json';
  }
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!response.ok) throw new Error(`API request failed (${response.status})`);
  return response.json();
}

export async function signIn(username, password) {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.detail || 'Sign-in failed');
  localStorage.setItem('sentinel_access_token', payload.access_token);
  return payload;
}
