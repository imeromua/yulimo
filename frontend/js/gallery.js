/* ===========================
   YULIMO — Gallery Lightbox
   Клік по .gallery-card → слайдер
   =========================== */

const GALLERY_GROUPS = {
    forest:  ['lis.jpg', 'lis2.jpg'],
    rooms:   [
        'standart nomer.jpg', 'nomer standart2.jpg', 'nomer standart5.jpg',
        'nomer standart6.jpg', 'nomer lyuks.jpg', 'nomer lyuks2.jpg',
        'nomer lyuks-11.jpg', 'nomer lyuks-12.jpg', 'nomer lyuks-13.jpg',
        'nomer lyuks-14.jpg', 'nomer-lyuks.jpg',
    ],
    food:    [
        'restoran.jpg', 'restoran-15.jpg', 'restoran-16.jpg', 'restoran-17.jpg',
        'restoran-18.jpg', 'restoran-19.jpg', 'restoran-20.jpg',
    ],
    spa:     [
        'sauna-banya-21.jpg', 'sauna-banya-22.jpg', 'sauna-banya-23.jpg',
        'sauna-banya-24.jpg', 'sauna-banya-25.jpg',
    ],
    cottage: [
        'kotedzh.jpg', 'kotedzh2.jpg', 'kotedzh3.jpg', 'kotedzh4.jpg',
        'kotedzh5.jpg', 'kotedzh8-08.jpg', 'kotedzh8-09.jpg', 'kotedzh8-10.jpg',
    ],
};

let currentGroup  = [];
let currentIndex  = 0;

const lightbox  = document.getElementById('lightbox');
const lbImg     = document.getElementById('lb-img');
const lbCounter = document.getElementById('lb-counter');
const lbClose   = document.getElementById('lb-close');
const lbPrev    = document.getElementById('lb-prev');
const lbNext    = document.getElementById('lb-next');

function openLightbox(group, index) {
    currentGroup = group;
    currentIndex = index;
    updateLightbox();
    lightbox.classList.add('open');
    document.body.style.overflow = 'hidden';
}

function closeLightbox() {
    lightbox.classList.remove('open');
    document.body.style.overflow = '';
    lbImg.src = '';
}

function updateLightbox() {
    const filename = currentGroup[currentIndex];
    lbImg.src = `/images/${filename}`;
    lbImg.alt = filename.replace(/\.[^.]+$/, '');
    lbCounter.textContent = `${currentIndex + 1} / ${currentGroup.length}`;
    lbPrev.style.display = currentGroup.length > 1 ? '' : 'none';
    lbNext.style.display = currentGroup.length > 1 ? '' : 'none';
}

function showPrev() {
    currentIndex = (currentIndex - 1 + currentGroup.length) % currentGroup.length;
    updateLightbox();
}

function showNext() {
    currentIndex = (currentIndex + 1) % currentGroup.length;
    updateLightbox();
}

/* ── Event listeners ──────────────────────────── */

lbClose.addEventListener('click', closeLightbox);
lbPrev.addEventListener('click', showPrev);
lbNext.addEventListener('click', showNext);

lightbox.addEventListener('click', (e) => {
    if (e.target === lightbox) closeLightbox();
});

document.addEventListener('keydown', (e) => {
    if (!lightbox.classList.contains('open')) return;
    if (e.key === 'Escape')     closeLightbox();
    if (e.key === 'ArrowLeft')  showPrev();
    if (e.key === 'ArrowRight') showNext();
});

/* ── Bind gallery cards ───────────────────────── */

document.querySelectorAll('.gallery-card[data-gallery]').forEach((card) => {
    card.addEventListener('click', () => {
        const groupKey = card.dataset.gallery;
        const group    = GALLERY_GROUPS[groupKey];
        if (!group || !group.length) return;
        openLightbox(group, 0);
    });
});
