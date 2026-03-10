/* ===========================
   YULIMO — API-модуль
   Всі звернення до бекенду
   =========================== */

const API_BASE = '/api';

/**
 * Базова обгортка fetch із обробкою помилок і стандартними заголовками.
 * @param {string} path  - URL відносно кореня
 * @param {RequestInit} options
 * @returns {Promise<any>}
 */
async function apiFetch(path, options = {}) {
    const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
    const resp = await fetch(path, { ...options, headers });
    const json = await resp.json().catch(() => ({}));
    if (!resp.ok) {
        const msg = json?.detail || json?.error || `HTTP ${resp.status}`;
        throw new Error(msg);
    }
    return json;
}

/**
 * Завантажити список активних номерів.
 * @returns {Promise<Array>}
 */
export async function fetchRooms() {
    return apiFetch(`${API_BASE}/rooms/`);
}

/**
 * Відправити нове бронювання.
 * @param {Object} payload
 * @returns {Promise<Object>}
 */
export async function submitBooking(payload) {
    return apiFetch(`${API_BASE}/bookings/`, {
        method: 'POST',
        body: JSON.stringify(payload),
    });
}

/**
 * Перевірити доступність номеру.
 * @param {number} roomId
 * @param {string} checkIn  - ISO date string
 * @param {string} checkOut - ISO date string
 * @returns {Promise<{available: boolean}>}
 */
export async function checkAvailability(roomId, checkIn, checkOut) {
    const params = new URLSearchParams({ room_id: roomId, check_in: checkIn, check_out: checkOut });
    return apiFetch(`${API_BASE}/bookings/check-availability?${params}`);
}
