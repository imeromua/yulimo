/* ===========================
   YULIMO — Main JS
   =========================== */

const navbar = document.getElementById('navbar');
const burger = document.getElementById('burger');
const navLinks = document.getElementById('navLinks');
const body = document.body;

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

const quickForm = document.getElementById('quickBookingForm');
if (quickForm) {
    quickForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const checkIn = document.getElementById('checkIn').value;
        const checkOut = document.getElementById('checkOut').value;

        if (checkIn && checkOut && checkIn >= checkOut) {
            alert('Дата виїзду має бути пізніше дати заїзду');
            return;
        }

        document.getElementById('booking')?.scrollIntoView({ behavior: 'smooth' });
    });
}

const bookingForm = document.getElementById('bookingForm');
if (bookingForm) {
    bookingForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = bookingForm.querySelector('button[type="submit"]');
        if (!btn) return;

        btn.textContent = 'Надсилаємо...';
        btn.disabled = true;

        await new Promise(resolve => setTimeout(resolve, 1200));

        btn.textContent = 'Заявка відправлена! Ми зв’яжемось з вами ✅';
        btn.style.background = '#4caf50';
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
