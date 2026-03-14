/* ===========================
   YULIMO — Content Loader
   Завантажує контент і налаштування з API
   та підставляє значення в DOM за атрибутами
   data-content і data-setting
   =========================== */

async function fetchContent() {
    try {
        const resp = await fetch('/api/content');
        const json = await resp.json();
        if (!json.success) return {};
        return json.data || {};
    } catch {
        return {};
    }
}

async function fetchSettings() {
    try {
        const resp = await fetch('/api/settings');
        const json = await resp.json();
        if (!json.success) return {};
        return json.data || {};
    } catch {
        return {};
    }
}

function applyData(attrName, data) {
    for (const [key, value] of Object.entries(data)) {
        if (!value) continue;
        document.querySelectorAll(`[${attrName}="${key}"]`).forEach(el => {
            const href = el.getAttribute('href') || '';
            if (href.startsWith('tel:')) {
                el.setAttribute('href', `tel:${value}`);
                el.textContent = value;
            } else if (href.startsWith('mailto:')) {
                el.setAttribute('href', `mailto:${value}`);
                el.textContent = value;
            } else {
                el.textContent = value;
            }
        });
    }
}

Promise.allSettled([fetchContent(), fetchSettings()]).then(([contentResult, settingsResult]) => {
    if (contentResult.status === 'fulfilled') {
        applyData('data-content', contentResult.value);
    }
    if (settingsResult.status === 'fulfilled') {
        applyData('data-setting', settingsResult.value);
    }
});
