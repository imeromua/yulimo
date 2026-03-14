/* ===========================
   YULIMO Admin — API module
   All requests include Bearer token
   =========================== */

import { getToken, logout } from './auth.js';

const API_BASE = '/api';

/**
 * Base fetch wrapper that automatically adds the Bearer token.
 * Redirects to login on 401.
 */
async function apiFetch(path, options = {}) {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(options.headers || {}),
    };
    const resp = await fetch(path, { ...options, headers });

    if (resp.status === 401) {
        logout();
        throw new Error('Сесія закінчилась, будь ласка увійдіть знову.');
    }

    const json = await resp.json().catch(() => ({}));
    if (!resp.ok) {
        const msg = json?.detail || json?.error || `HTTP ${resp.status}`;
        throw new Error(msg);
    }
    return json;
}

/* ── AUTH ──────────────────────────────────────────── */

/**
 * Log in with email + password.
 * @returns {Promise<{access_token: string, refresh_token: string}>}
 */
export async function login(email, password) {
    const resp = await fetch('/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
    });
    const json = await resp.json().catch(() => ({}));
    if (!resp.ok) {
        throw new Error(json?.detail || 'Помилка входу');
    }
    return json;
}

/* ── BOOKINGS ──────────────────────────────────────── */

/**
 * Fetch all bookings, optionally filtered by status.
 * @param {string} [status] - pending | confirmed | cancelled | completed
 * @returns {Promise<Array>}
 */
export async function getBookings(status = '') {
    const params = status ? `?status=${status}` : '';
    return apiFetch(`${API_BASE}/admin/bookings${params}`);
}

/**
 * Update a booking status.
 * @param {number} id
 * @param {string} status - pending | confirmed | cancelled | completed
 */
export async function updateBookingStatus(id, status) {
    return apiFetch(`${API_BASE}/admin/bookings/${id}/status?status=${status}`, {
        method: 'PATCH',
    });
}

/* ── ROOMS ─────────────────────────────────────────── */

/**
 * Fetch all rooms (including inactive for admin).
 * @returns {Promise<Array>}
 */
export async function getRooms() {
    return apiFetch(`${API_BASE}/rooms/`);
}

/**
 * Create a new room.
 * @param {Object} data
 * @returns {Promise<Object>}
 */
export async function createRoom(data) {
    return apiFetch(`${API_BASE}/rooms/`, {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

/**
 * Update an existing room.
 * @param {number} id
 * @param {Object} data
 * @returns {Promise<Object>}
 */
export async function updateRoom(id, data) {
    return apiFetch(`${API_BASE}/rooms/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(data),
    });
}

/* ── RESTAURANT ────────────────────────────────────── */

/**
 * Fetch menu items (admin view — includes inactive).
 * @param {string} [category]
 * @returns {Promise<Array>}
 */
export async function getMenu(category = '') {
    const params = category ? `?category=${category}` : '';
    return apiFetch(`${API_BASE}/admin/menu${params}`);
}

/**
 * Add a new menu item.
 * @param {Object} data
 * @returns {Promise<Object>}
 */
export async function addMenuItem(data) {
    return apiFetch(`${API_BASE}/restaurant/menu`, {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

/**
 * Update an existing menu item.
 * @param {number} id
 * @param {Object} data
 * @returns {Promise<Object>}
 */
export async function updateMenuItem(id, data) {
    return apiFetch(`${API_BASE}/restaurant/menu/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(data),
    });
}

/**
 * Delete a menu item.
 * @param {number} id
 * @returns {Promise<void>}
 */
export async function deleteMenuItem(id) {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
    const resp = await fetch(`${API_BASE}/restaurant/menu/${id}`, { method: 'DELETE', headers });
    if (resp.status === 401) {
        logout();
        throw new Error('Сесія закінчилась, будь ласка увійдіть знову.');
    }
    if (!resp.ok) {
        const json = await resp.json().catch(() => ({}));
        throw new Error(json?.detail || `HTTP ${resp.status}`);
    }
}

/**
 * Fetch all table reservations.
 * @returns {Promise<Array>}
 */
export async function getTableReservations() {
    return apiFetch(`${API_BASE}/admin/table-reservations`);
}
