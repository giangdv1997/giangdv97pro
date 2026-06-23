/* =====================================================================
   CV / PORTFOLIO  —  interactions
   ===================================================================== */
(function () {
  'use strict';

  const $  = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];

  /* ---------- Theme (light/dark) + nhớ lựa chọn ---------- */
  const root = document.documentElement;
  const saved = localStorage.getItem('cv-theme');
  if (saved) root.setAttribute('data-theme', saved);
  else if (window.matchMedia('(prefers-color-scheme: dark)').matches)
    root.setAttribute('data-theme', 'dark');

  $('#themeToggle')?.addEventListener('click', () => {
    const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    localStorage.setItem('cv-theme', next);
  });

  /* ---------- Năm hiện tại ở footer ---------- */
  const y = $('#year'); if (y) y.textContent = new Date().getFullYear();

  /* ---------- In / Lưu PDF ---------- */
  $('#printBtn')?.addEventListener('click', () => window.print());

  /* ---------- Menu mobile ---------- */
  const burger = $('#burger');
  const links  = $('.nav__links');
  burger?.addEventListener('click', () => links.classList.toggle('open'));
  $$('.nav__links a').forEach(a =>
    a.addEventListener('click', () => links.classList.remove('open')));

  /* ---------- Reveal khi cuộn tới ---------- */
  const revealIO = new IntersectionObserver((entries, obs) => {
    entries.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('in'); obs.unobserve(e.target); }
    });
  }, { threshold: 0.12 });
  $$('.reveal').forEach(el => revealIO.observe(el));

  /* ---------- Đổ thanh kỹ năng ---------- */
  const barIO = new IntersectionObserver((entries, obs) => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      const li = e.target;
      li.style.setProperty('--w', (li.dataset.level || 0) + '%');
      li.classList.add('show');
      obs.unobserve(li);
    });
  }, { threshold: 0.4 });
  $$('.bars li').forEach(li => barIO.observe(li));

  /* ---------- Đếm số ở Hero ---------- */
  const countIO = new IntersectionObserver((entries, obs) => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      const el = e.target, target = +el.dataset.count || 0;
      let n = 0;
      const step = Math.max(1, Math.ceil(target / 28));
      const tick = () => {
        n = Math.min(target, n + step);
        el.textContent = n;
        if (n < target) requestAnimationFrame(tick);
      };
      tick();
      obs.unobserve(el);
    });
  }, { threshold: 0.6 });
  $$('.stat__num').forEach(el => countIO.observe(el));

  /* ---------- Highlight mục đang xem trên nav ---------- */
  const navLinks = $$('.nav__links a');
  const sections = navLinks
    .map(a => $(a.getAttribute('href')))
    .filter(Boolean);
  const navIO = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      const id = '#' + e.target.id;
      navLinks.forEach(a => a.classList.toggle('active', a.getAttribute('href') === id));
    });
  }, { rootMargin: '-45% 0px -50% 0px' });
  sections.forEach(s => navIO.observe(s));

  /* ---------- Nút lên đầu trang ---------- */
  const toTop = $('#toTop');
  window.addEventListener('scroll', () => {
    toTop?.classList.toggle('show', window.scrollY > 600);
  }, { passive: true });
  toTop?.addEventListener('click', () =>
    window.scrollTo({ top: 0, behavior: 'smooth' }));

  /* ---------- Hiệu ứng gõ chữ ở dòng terminal ---------- */
  const typeEl = $('#typeLine');
  if (typeEl) {
    const words = ['whoami', 'fullstack --skills', 'cat strengths.md', 'deploy --to vetc'];
    let wi = 0, ci = 0, deleting = false;
    const loop = () => {
      const w = words[wi];
      typeEl.textContent = deleting ? w.slice(0, ci--) : w.slice(0, ci++);
      let delay = deleting ? 45 : 95;
      if (!deleting && ci > w.length) { deleting = true; delay = 1600; }
      else if (deleting && ci < 0) { deleting = false; wi = (wi + 1) % words.length; ci = 0; delay = 350; }
      setTimeout(loop, delay);
    };
    loop();
  }
})();
