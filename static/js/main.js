/**
 * Aida Hotel — Premium interactions
 */
(function () {
  'use strict';

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function initHeaderScroll() {
    const header = document.querySelector('.site-header');
    if (!header) return;

    const onScroll = () => {
      header.classList.toggle('is-scrolled', window.scrollY > 40);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  function initMobileMenu() {
    const toggle = document.querySelector('.menu-toggle');
    const mobileNav = document.querySelector('.mobile-nav');
    if (!toggle || !mobileNav) return;

    const close = () => {
      toggle.classList.remove('is-open');
      mobileNav.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');
      toggle.setAttribute('aria-label', toggle.dataset.labelOpen || 'Open menu');
      document.body.style.overflow = '';
      toggle.focus();
    };

    toggle.dataset.labelOpen = toggle.getAttribute('aria-label') || 'Open menu';

    toggle.addEventListener('click', () => {
      const isOpen = toggle.classList.toggle('is-open');
      mobileNav.classList.toggle('is-open', isOpen);
      toggle.setAttribute('aria-expanded', String(isOpen));
      toggle.setAttribute('aria-label', isOpen ? 'Close menu' : toggle.dataset.labelOpen);
      document.body.style.overflow = isOpen ? 'hidden' : '';
      if (isOpen) {
        const first = mobileNav.querySelector('a');
        if (first) first.focus();
      }
    });

    mobileNav.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', close);
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && mobileNav.classList.contains('is-open')) close();
    });
  }

  function initHeroSlider() {
    const slider = document.querySelector('.hero-slider');
    if (!slider) return;

    const slides = slider.querySelectorAll('.hero-slide');
    const dots = slider.querySelectorAll('.hero-dot');
    if (slides.length <= 1) return;

    let current = 0;
    let timer = null;
    const interval = prefersReducedMotion ? 0 : 6000;

    function goTo(index) {
      slides[current].classList.remove('active');
      if (dots[current]) {
        dots[current].classList.remove('active');
        dots[current].setAttribute('aria-selected', 'false');
      }
      current = (index + slides.length) % slides.length;
      slides[current].classList.add('active');
      if (dots[current]) {
        dots[current].classList.add('active');
        dots[current].setAttribute('aria-selected', 'true');
      }
    }

    function next() { goTo(current + 1); }

    function startAuto() {
      if (interval <= 0) return;
      stopAuto();
      timer = setInterval(next, interval);
    }

    function stopAuto() {
      if (timer) { clearInterval(timer); timer = null; }
    }

    dots.forEach((dot, i) => {
      dot.setAttribute('role', 'tab');
      dot.setAttribute('aria-selected', i === 0 ? 'true' : 'false');
      dot.addEventListener('click', () => { goTo(i); startAuto(); });
    });

    slider.addEventListener('mouseenter', stopAuto);
    slider.addEventListener('mouseleave', startAuto);
    startAuto();
  }

  function initScrollReveal() {
    const reveals = document.querySelectorAll('.reveal');
    if (!reveals.length) return;

    if (prefersReducedMotion || !('IntersectionObserver' in window)) {
      reveals.forEach((el) => el.classList.add('is-visible'));
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
    );

    reveals.forEach((el) => observer.observe(el));
  }

  function initGalleryLightbox() {
    const items = document.querySelectorAll('[data-lightbox]');
    if (!items.length) return;

    let lightbox = document.querySelector('.lightbox');
    if (!lightbox) {
      lightbox = document.createElement('div');
      lightbox.className = 'lightbox';
      lightbox.setAttribute('role', 'dialog');
      lightbox.setAttribute('aria-modal', 'true');
      lightbox.setAttribute('aria-label', 'Gallery');
      lightbox.innerHTML = `
        <button class="lightbox-close" type="button" aria-label="Close">&times;</button>
        <button class="lightbox-prev" type="button" aria-label="Previous">&#8249;</button>
        <button class="lightbox-next" type="button" aria-label="Next">&#8250;</button>
        <img src="" alt="">
        <p class="lightbox-caption"></p>
      `;
      document.body.appendChild(lightbox);
    }

    const images = Array.from(items).map((item) => ({
      src: item.dataset.lightboxSrc || item.querySelector('img')?.src || '',
      caption: item.dataset.lightboxCaption || item.querySelector('figcaption')?.textContent || '',
    }));

    let currentIndex = 0;
    let lastFocus = null;
    const imgEl = lightbox.querySelector('img');
    const captionEl = lightbox.querySelector('.lightbox-caption');
    const closeBtn = lightbox.querySelector('.lightbox-close');
    const prevBtn = lightbox.querySelector('.lightbox-prev');
    const nextBtn = lightbox.querySelector('.lightbox-next');

    function show(index) {
      currentIndex = (index + images.length) % images.length;
      const item = images[currentIndex];
      imgEl.src = item.src;
      imgEl.alt = item.caption;
      captionEl.textContent = item.caption;
      lightbox.classList.add('is-open');
      document.body.style.overflow = 'hidden';
      closeBtn.focus();
    }

    function close() {
      lightbox.classList.remove('is-open');
      document.body.style.overflow = '';
      if (lastFocus) lastFocus.focus();
    }

    items.forEach((item, i) => {
      const open = (e) => {
        e.preventDefault();
        lastFocus = item;
        show(i);
      };
      item.addEventListener('click', open);
      item.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') open(e);
      });
    });

    closeBtn.addEventListener('click', close);
    prevBtn.addEventListener('click', () => show(currentIndex - 1));
    nextBtn.addEventListener('click', () => show(currentIndex + 1));

    lightbox.addEventListener('click', (e) => {
      if (e.target === lightbox) close();
    });

    document.addEventListener('keydown', (e) => {
      if (!lightbox.classList.contains('is-open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') show(currentIndex - 1);
      if (e.key === 'ArrowRight') show(currentIndex + 1);
    });
  }

  function initStatCountUp() {
    const stats = document.querySelectorAll('[data-stat-value], [data-count]');
    if (!stats.length) return;

    const animate = (el) => {
      const raw = el.dataset.count || el.dataset.statValue || el.textContent.trim();
      const match = String(raw).match(/^(\d+(?:\.\d+)?)(.*)$/);
      if (!match) return;
      const target = parseFloat(match[1]);
      const suffix = match[2] || '';
      const isFloat = String(match[1]).includes('.');
      const duration = prefersReducedMotion ? 0 : 1600;
      if (duration === 0) {
        el.textContent = raw;
        return;
      }
      const start = performance.now();
      const tick = (now) => {
        const progress = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const value = target * eased;
        el.textContent = (isFloat ? value.toFixed(1) : Math.round(value)) + suffix;
        if (progress < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    };

    if (!('IntersectionObserver' in window)) {
      stats.forEach(animate);
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            animate(entry.target);
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.5 }
    );
    stats.forEach((el) => observer.observe(el));
  }

  function syncRoomSelection(card) {
    const checkbox = card.querySelector('.room-checkbox');
    if (!checkbox) return;
    card.classList.toggle('is-selected', checkbox.checked && !checkbox.disabled);
  }

  function clearRoomSelection() {
    const hidden = document.getElementById('id_room_ids');
    if (hidden) hidden.value = '';
    document.querySelectorAll('.room-select-card').forEach((card) => {
      const checkbox = card.querySelector('.room-checkbox');
      if (checkbox) checkbox.checked = false;
      card.classList.remove('is-selected');
    });
    const price = document.getElementById('price-summary');
    if (price) price.innerHTML = '';
    if (typeof htmx !== 'undefined') {
      htmx.trigger(document.body, 'roomSelectionChanged');
    }
  }

  function initRoomSelection() {
    document.body.addEventListener('change', (e) => {
      if (!e.target.classList.contains('room-checkbox')) return;
      const card = e.target.closest('.room-select-card');
      if (card) syncRoomSelection(card);
      const checked = Array.from(document.querySelectorAll('.room-checkbox:checked')).map((cb) => cb.value);
      const hidden = document.getElementById('id_room_ids');
      if (hidden) hidden.value = checked.join(',');
      if (typeof htmx !== 'undefined') {
        htmx.trigger(document.body, 'roomSelectionChanged');
      }
    });

    document.body.addEventListener('htmx:afterSwap', (e) => {
      if (e.detail.target?.id === 'room-grid') {
        clearRoomSelection();
        e.detail.target.querySelectorAll('.room-select-card').forEach(syncRoomSelection);
      }
    });
  }

  function initBookingDates() {
    const form = document.querySelector('[data-js-booking]');
    if (!form) return;

    const checkIn = form.querySelector('#id_check_in');
    const checkOut = form.querySelector('#id_check_out');
    const guests = form.querySelector('#id_guests_count');
    const roomType = form.querySelector('#id_room_type');
    if (!checkIn || !checkOut) return;

    const today = new Date();
    const iso = (d) => d.toISOString().slice(0, 10);
    if (!checkIn.min) checkIn.min = iso(today);

    const syncCheckoutMin = () => {
      if (!checkIn.value) {
        checkOut.min = checkIn.min;
        return;
      }
      const next = new Date(checkIn.value + 'T12:00:00');
      next.setDate(next.getDate() + 1);
      checkOut.min = iso(next);
      if (checkOut.value && checkOut.value <= checkIn.value) {
        checkOut.value = iso(next);
      }
    };

    const syncGuestCapacity = () => {
      if (!guests || !roomType) return;
      const opt = roomType.selectedOptions[0];
      const capacity = parseInt(opt?.dataset.capacity || '10', 10);
      guests.max = String(capacity);
      if (parseInt(guests.value || '1', 10) > capacity) {
        guests.value = String(capacity);
      }
    };

    checkIn.addEventListener('change', syncCheckoutMin);
    roomType?.addEventListener('change', syncGuestCapacity);
    syncCheckoutMin();
    syncGuestCapacity();
  }

  function initSubmitLoading() {
    document.querySelectorAll('form[data-js-booking], form[data-js-contact]').forEach((form) => {
      form.addEventListener('submit', () => {
        const btn = form.querySelector('[data-submit-btn]');
        if (!btn || btn.classList.contains('is-loading')) return;
        btn.classList.add('is-loading');
        btn.disabled = true;
      });
    });
  }

  function initActiveNav() {
    const path = window.location.pathname.replace(/\/$/, '') || '/';
    document.querySelectorAll('.main-nav a, .mobile-nav a').forEach((link) => {
      const href = link.getAttribute('href').replace(/\/$/, '') || '/';
      const isHome = href === '/' || href.endsWith('/');
      const active = isHome
        ? path === '/' || path.match(/\/[a-z]{2}$/)
        : path.includes(href.split('/').filter(Boolean).pop());
      if (active || (href !== '/' && path.startsWith(href))) {
        link.classList.add('is-active');
      }
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    initHeaderScroll();
    initMobileMenu();
    initHeroSlider();
    initScrollReveal();
    initGalleryLightbox();
    initStatCountUp();
    initRoomSelection();
    initBookingDates();
    initSubmitLoading();
    initActiveNav();
  });
})();
