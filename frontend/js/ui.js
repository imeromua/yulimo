/* ===========================
   YULIMO — UI-модуль
   Навігація, анімації, стани
   =========================== */

const navbar   = document.getElementById('navbar');
const burger   = document.getElementById('burger');
const navLinks = document.getElementById('navLinks');
const body     = document.body;

// ---------- Навігація — scroll-ефект ----------
function updateNavbar() {
    if (!navbar) return;
    // На мобільних (<= 768px) navbar завжди темний
    if (window.innerWidth <= 768) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.toggle('scrolled', window.scrollY > 60);
    }
}

if (navbar) {
    updateNavbar(); // встановлюємо одразу при завантаженні
    window.addEventListener('scroll', updateNavbar, { passive: true });
    window.addEventListener('resize', updateNavbar, { passive: true });
}

// ---------- Мобільне меню ----------
if (burger && navLinks) {
    burger.addEventListener('click', () => {
        const open = navLinks.classList.toggle('open');
        burger.classList.toggle('active', open);
        burger.setAttribute('aria-expanded', String(open));
        body.classList.toggle('menu-open', open);
    });

    navLinks.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            navLinks.classList.remove('open');
            burger.classList.remove('active');
            burger.setAttribute('aria-expanded', 'false');
            body.classList.remove('menu-open');
        });
    });

    // Закрити меню при кліку на кнопку «Забронювати» у nav
    document.querySelector('.nav-btn')?.addEventListener('click', () => {
        navLinks.classList.remove('open');
        burger.classList.remove('active');
        burger.setAttribute('aria-expanded', 'false');
        body.classList.remove('menu-open');
    });
}

// ---------- Анімація появи секцій ----------
const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
        }
    });
}, { threshold: 0.12 });

document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

// ---------- Кнопки соцмереж (заглушка) ----------
document.querySelectorAll('.social-disabled').forEach(button => {
    button.addEventListener('click', () => {
        alert('Соцмережі скоро з\'являться. Поки що телефонуйте або залишайте заявку на сайті.');
    });
});

// ---------- Утиліти статусу ----------

export function showStatus(el, message, type = 'success') {
    if (!el) return;
    el.textContent = message;
    el.className = `form-status show ${type}`;
}

export function clearStatus(el) {
    if (!el) return;
    el.textContent = '';
    el.className = 'form-status';
}

export function setButtonLoading(btn, loading, loadingText = 'Завантаження...', defaultText = 'Надіслати') {
    if (!btn) return;
    btn.disabled = loading;
    btn.textContent = loading ? loadingText : defaultText;
}
