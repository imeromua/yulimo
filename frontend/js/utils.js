/* ===========================
   YULIMO — Утиліти
   =========================== */

/**
 * Форматує рядок-мітку для вибору номеру у формі.
 * @param {Object} room
 * @returns {string}
 */
export function formatRoomLabel(room) {
    const title = room.name || room.title || room.room_type || `Номер #${room.id}`;
    const price = room.price ? ` — від ${room.price} грн/ніч` : '';
    return `${title}${price}`;
}

/**
 * Повертає сьогоднішню дату у форматі YYYY-MM-DD.
 * @returns {string}
 */
export function todayISO() {
    return new Date().toISOString().split('T')[0];
}

/**
 * Встановлює атрибут min = сьогодні для всіх date-інпутів.
 */
export function setMinDates() {
    const today = todayISO();
    document.querySelectorAll('input[type="date"]').forEach(input => {
        input.min = today;
    });
}

/**
 * Дебаунс-обгортка функції.
 * @param {Function} fn
 * @param {number} delay - мс
 * @returns {Function}
 */
export function debounce(fn, delay = 300) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delay);
    };
}
