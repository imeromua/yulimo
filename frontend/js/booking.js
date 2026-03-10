/* ===========================
   YULIMO — Модуль бронювань
   =========================== */

import { fetchRooms, submitBooking } from './api.js';
import { formatRoomLabel, setMinDates } from './utils.js';
import { clearStatus, setButtonLoading, showStatus } from './ui.js';

const bookingForm      = document.getElementById('bookingForm');
const bookingStatus    = document.getElementById('bookingStatus');
const bookingRoomId    = document.getElementById('bookingRoomId');
const bookingCheckIn   = document.getElementById('bookingCheckIn');
const bookingCheckOut  = document.getElementById('bookingCheckOut');
const bookingGuests    = document.getElementById('bookingGuestsCount');
const quickForm        = document.getElementById('quickBookingForm');
const quickCheckIn     = document.getElementById('checkIn');
const quickCheckOut    = document.getElementById('checkOut');
const quickGuests      = document.getElementById('guests');

// ---------- Заповнити список номерів ----------
export async function loadRooms() {
    if (!bookingRoomId) return;

    bookingRoomId.innerHTML = '<option value="">Завантажуємо доступні номери...</option>';
    bookingRoomId.disabled = true;

    try {
        const rooms = await fetchRooms();

        if (!Array.isArray(rooms) || rooms.length === 0) {
            bookingRoomId.innerHTML = '<option value="">Наразі немає доступних номерів</option>';
            return;
        }

        bookingRoomId.innerHTML = '<option value="">Оберіть номер</option>';
        rooms.forEach(room => {
            const option = document.createElement('option');
            option.value = room.id;
            option.textContent = formatRoomLabel(room);
            bookingRoomId.appendChild(option);
        });
    } catch {
        bookingRoomId.innerHTML = '<option value="">Не вдалося завантажити номери</option>';
        showStatus(bookingStatus, 'Не вдалося завантажити номери. Спробуйте пізніше.', 'error');
    } finally {
        bookingRoomId.disabled = false;
    }
}

// ---------- Швидка форма пошуку (hero) ----------
if (quickForm) {
    quickForm.addEventListener('submit', e => {
        e.preventDefault();
        const ci = quickCheckIn?.value;
        const co = quickCheckOut?.value;

        if (ci && co && ci >= co) {
            alert('Дата виїзду має бути пізніше дати заїзду');
            return;
        }

        if (bookingCheckIn && ci)  bookingCheckIn.value  = ci;
        if (bookingCheckOut && co) bookingCheckOut.value = co;
        if (bookingGuests && quickGuests?.value) bookingGuests.value = quickGuests.value;

        document.getElementById('booking')?.scrollIntoView({ behavior: 'smooth' });
    });
}

// ---------- Головна форма бронювання ----------
if (bookingForm) {
    bookingForm.addEventListener('submit', async e => {
        e.preventDefault();
        clearStatus(bookingStatus);

        const submitBtn = bookingForm.querySelector('button[type="submit"]');

        const payload = {
            room_id:      Number(bookingRoomId?.value),
            guest_name:   document.getElementById('bookingGuestName')?.value.trim(),
            guest_phone:  document.getElementById('bookingGuestPhone')?.value.trim(),
            guest_email:  document.getElementById('bookingGuestEmail')?.value.trim() || null,
            check_in:     bookingCheckIn?.value,
            check_out:    bookingCheckOut?.value,
            guests_count: Number(bookingGuests?.value || 1),
            comment:      document.getElementById('bookingComment')?.value.trim() || null,
        };

        if (!payload.room_id) {
            showStatus(bookingStatus, 'Будь ласка, оберіть номер для бронювання.', 'error');
            return;
        }

        if (!payload.check_in || !payload.check_out || payload.check_in >= payload.check_out) {
            showStatus(bookingStatus, 'Дата виїзду має бути пізніше дати заїзду.', 'error');
            return;
        }

        setButtonLoading(submitBtn, true, 'Надсилаємо...', 'Надіслати заявку');

        try {
            const result = await submitBooking(payload);
            const msg = result.total_price
                ? `Бронювання створено! №${result.id}, сума: ${result.total_price} грн. Менеджер зв'яжеться з вами.`
                : 'Бронювання успішно створено. Менеджер зв\'яжеться з вами.';

            showStatus(bookingStatus, msg, 'success');
            bookingForm.reset();
            if (bookingGuests) bookingGuests.value = '2';
            setMinDates();
        } catch (err) {
            showStatus(bookingStatus, err.message || 'Сталася помилка. Спробуйте пізніше.', 'error');
        } finally {
            setButtonLoading(submitBtn, false, '', 'Надіслати заявку');
        }
    });
}
