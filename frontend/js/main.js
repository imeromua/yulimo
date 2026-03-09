/* ===========================
   YULIMO — Main JS
   =========================== */

// Navbar scroll effect
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 60);
});

// Burger menu
const burger = document.getElementById('burger');
const navLinks = document.getElementById('navLinks');

burger.addEventListener('click', () => {
    navLinks.classList.toggle('open');
});

navLinks.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => navLinks.classList.remove('open'));
});

// Set min dates for booking inputs
const today = new Date().toISOString().split('T')[0];
document.querySelectorAll('input[type="date"]').forEach(input => {
    input.min = today;
});

// Quick booking form
const quickForm = document.getElementById('quickBookingForm');
if (quickForm) {
    quickForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const checkIn  = document.getElementById('checkIn').value;
        const checkOut = document.getElementById('checkOut').value;
        if (checkIn && checkOut && checkIn >= checkOut) {
            alert('Дата виїзду має бути пізніше дати заїзду');
            return;
        }
        document.getElementById('booking').scrollIntoView({ behavior: 'smooth' });
    });
}

// Booking form submit
const bookingForm = document.getElementById('bookingForm');
if (bookingForm) {
    bookingForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = bookingForm.querySelector('button[type="submit"]');
        btn.textContent = 'Надсилаємо...';
        btn.disabled = true;

        // TODO: інтеграція з API
        await new Promise(r => setTimeout(r, 1200));

        btn.textContent = 'Заявка відправлена! Ми зв’яжемось з вами ✅';
        btn.style.background = '#4caf50';
    });
}

// Scroll reveal animation
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, { threshold: 0.1 });

document.querySelectorAll('.feature-card, .room-card, .service-card, .contact-item').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(el);
});
