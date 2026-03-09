/* ===========================
   YULIMO — Main JS
   =========================== */

const navbar = document.getElementById('navbar');
const burger = document.getElementById('burger');
const navLinks = document.getElementById('navLinks');
const body = document.body;
const bookingForm = document.getElementById('bookingForm');
const bookingStatus = document.getElementById('bookingStatus');
const bookingRoomId = document.getElementById('bookingRoomId');
const bookingCheckIn = document.getElementById('bookingCheckIn');
const bookingCheckOut = document.getElementById('bookingCheckOut');
const bookingGuestsCount = document.getElementById('bookingGuestsCount');
const quickForm = document.getElementById('quickBookingForm');
const quickCheckIn = document.getElementById('checkIn');
const quickCheckOut = document.getElementById('checkOut');
const quickGuests = document.getElementById('guests');

window.addEventListener('scroll', () => {
    if (navbar) {
        navbar.classList.toggle('scrolled', window.scrollY > 60);
    }
});

if (burger && navLinks) {
    burger.addEventListener('click', () => {
        navLinks.classList.toggle('open');
        const expanded = navLinks.classList.contains('open');
        burger.setAttribute('aria-expanded', String(expanded));
        body.classList.toggle('menu-open', expanded);
    });

    navLinks.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            navLinks.classList.remove('open');
            burger.setAttribute('aria-expanded', 'false');
            body.classList.remove('menu-open');
        });
    });
}

const today = new Date().toISOString().split('T')[0];
document.querySelectorAll('input[type="date"]').forEach(input => {
    input.min = today;
});

function showBookingStatus(message, type = 'success') {
    if (!bookingStatus) return;
    bookingStatus.textContent = message;
    bookingStatus.className = `form-status show ${type}`;
}

function clearBookingStatus() {
    if (!bookingStatus) return;
    bookingStatus.textContent = '';
    bookingStatus.className = 'form-status';
}

function formatRoomLabel(room) {
    const title = room.name || room.title || room.room_type || room.category || `Номер #${room.id}`;
    const price = room.price ? ` — від ${room.price} грн/ніч` : '';
    return `${title}${price}`;
}

async function loadRooms() {
    if (!bookingRoomId) return;

    bookingRoomId.innerHTML = '<option value="">Завантажуємо доступні номери...</option>';

    try {
        const response = await fetch('/api/rooms/');
        const rooms = await response.json();

        if (!response.ok) {
            throw new Error('Не вдалося отримати список номерів');
        }

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
    } catch (error) {
        bookingRoomId.innerHTML = '<option value="">Не вдалося завантажити номери</option>';
        showBookingStatus('Не вдалося завантажити доступні номери. Перевірте, чи працює API на /api/rooms/.', 'error');
    }
}

if (quickForm) {
    quickForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const checkIn = quickCheckIn?.value;
        const checkOut = quickCheckOut?.value;

        if (checkIn && checkOut && checkIn >= checkOut) {
            alert('Дата виїзду має бути пізніше дати заїзду');
            return;
        }

        if (bookingCheckIn && checkIn) bookingCheckIn.value = checkIn;
        if (bookingCheckOut && checkOut) bookingCheckOut.value = checkOut;
        if (bookingGuestsCount && quickGuests?.value) bookingGuestsCount.value = quickGuests.value;

        document.getElementById('booking')?.scrollIntoView({ behavior: 'smooth' });
    });
}

if (bookingForm) {
    bookingForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        clearBookingStatus();

        const submitButton = bookingForm.querySelector('button[type="submit"]');
        if (!submitButton) return;

        const payload = {
            room_id: Number(bookingRoomId?.value),
            guest_name: document.getElementById('bookingGuestName')?.value.trim(),
            guest_phone: document.getElementById('bookingGuestPhone')?.value.trim(),
            guest_email: document.getElementById('bookingGuestEmail')?.value.trim() || null,
            check_in: bookingCheckIn?.value,
            check_out: bookingCheckOut?.value,
            guests_count: Number(bookingGuestsCount?.value || 1),
            comment: document.getElementById('bookingComment')?.value.trim() || null
        };

        if (!payload.room_id) {
            showBookingStatus('Будь ласка, оберіть номер для бронювання.', 'error');
            return;
        }

        if (!payload.check_in || !payload.check_out || payload.check_in >= payload.check_out) {
            showBookingStatus('Дата виїзду має бути пізніше дати заїзду.', 'error');
            return;
        }

        submitButton.textContent = 'Надсилаємо...';
        submitButton.disabled = true;

        try {
            const response = await fetch('/api/bookings/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const result = await response.json().catch(() => ({}));

            if (!response.ok) {
                throw new Error(result.detail || 'Не вдалося створити бронювання');
            }

            const successMessage = result.total_price
                ? `Бронювання створено! №${result.id}, сума: ${result.total_price} грн. Менеджер зв’яжеться з вами для підтвердження.`
                : 'Бронювання створено успішно. Менеджер зв’яжеться з вами для підтвердження.';

            showBookingStatus(successMessage, 'success');
            bookingForm.reset();
            if (bookingGuestsCount) bookingGuestsCount.value = '2';
            document.querySelectorAll('input[type="date"]').forEach(input => {
                input.min = today;
            });
        } catch (error) {
            showBookingStatus(error.message || 'Сталася помилка під час відправки заявки.', 'error');
        } finally {
            submitButton.textContent = 'Надіслати заявку';
            submitButton.disabled = false;
        }
    });
}

document.querySelectorAll('.social-disabled').forEach(button => {
    button.addEventListener('click', () => {
        alert('Соцмережі скоро з’являться. Поки що телефонуйте або залишайте заявку на сайті.');
    });
});

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
        }
    });
}, { threshold: 0.12 });

document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

loadRooms();
