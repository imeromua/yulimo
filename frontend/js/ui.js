/* ===========================
   YULIMO — UI-модуль
   Навігація, анімації, стани
   =========================== */

const navbar   = document.getElementById('navbar');
const burger   = document.getElementById('burger');
const navLinks = document.getElementById('navLinks');
const body     = document.body;

// ---------- Навігація — scroll-ефект ----------
if (navbar) {
    window.addEventListener('scroll', () => {
        navbar.classList.toggle('scrolled', window.scrollY > 60);
    }, { passive: true });
}

// ---------- Мобільне меню ----------
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

/**
 * Показати повідомлення статусу форми.
 * @param {HTMLElement|null} el
 * @param {string} message
 * @param {'success'|'error'} type
 */
export function showStatus(el, message, type = 'success') {
    if (!el) return;
    el.textContent = message;
    el.className = `form-status show ${type}`;
}

/**
 * Очистити повідомлення статусу.
 * @param {HTMLElement|null} el
 */
export function clearStatus(el) {
    if (!el) return;
    el.textContent = '';
    el.className = 'form-status';
}

/**
 * Встановити стан кнопки завантаження.
 * @param {HTMLButtonElement|null} btn
 * @param {boolean} loading
 * @param {string} loadingText
 * @param {string} defaultText
 */
export function setButtonLoading(btn, loading, loadingText = 'Завантаження...', defaultText = 'Надіслати') {
    if (!btn) return;
    btn.disabled = loading;
    btn.textContent = loading ? loadingText : defaultText;
}
