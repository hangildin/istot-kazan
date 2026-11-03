(() => {
  'use strict';
  const menu = document.querySelector('.menu-toggle');
  const nav = document.getElementById('navigation');
  if (menu && nav) {
    menu.addEventListener('click', () => {
      const isOpen = menu.getAttribute('aria-expanded') === 'true';
      menu.setAttribute('aria-expanded', String(!isOpen));
      menu.setAttribute('aria-label', isOpen ? 'Открыть меню' : 'Закрыть меню');
      nav.classList.toggle('open', !isOpen);
    });
    nav.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
      nav.classList.remove('open');
      menu.setAttribute('aria-expanded', 'false');
      menu.setAttribute('aria-label', 'Открыть меню');
    }));
    document.addEventListener('click', e => {
      if (nav.classList.contains('open') && !nav.contains(e.target) && !menu.contains(e.target)) {
        nav.classList.remove('open'); menu.setAttribute('aria-expanded','false'); menu.setAttribute('aria-label','Открыть меню'); menu.setAttribute('aria-label','Открыть меню');
      }
    });
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') {
        nav.classList.remove('open'); menu.setAttribute('aria-expanded','false'); menu.setAttribute('aria-label','Открыть меню');
      }
    });
  }
  const gallery = document.getElementById('lightbox');
  if (gallery && gallery.showModal) {
    const photo = gallery.querySelector('img');
    const caption = gallery.querySelector('.lightbox-caption');
    document.querySelectorAll('a.gallery-photo').forEach(a => {
      a.addEventListener('click', e => {
        e.preventDefault();
        photo.src = a.href;
        photo.alt = a.querySelector('img')?.alt || 'Фотография пространства';
        caption.textContent = a.dataset.caption || '';
        gallery.showModal();
      });
    });
    gallery.querySelector('.lightbox-close')?.addEventListener('click', () => gallery.close());
    gallery.addEventListener('click', e => {if (e.target === gallery) gallery.close();});
    gallery.addEventListener('close', () => {photo.removeAttribute('src');});
  }
  const y = document.getElementById('current-year');
  if (y) y.textContent = String(new Date().getFullYear());
})();
