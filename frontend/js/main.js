/* ===========================
   YULIMO — Точка входу
   =========================== */

import { setMinDates } from './utils.js';
import './ui.js';
import { loadRooms } from './booking.js';

// Встановлюємо мінімальні дати для всіх date-інпутів
setMinDates();

// Завантажуємо номери для форми бронювання
loadRooms();
