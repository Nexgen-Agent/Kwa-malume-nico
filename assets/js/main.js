/* Malume Nico - Home
Shares the same "water glass + gold glow" feel as comments page
- Vertical sections; each has a horizontal swipe rail
Drag to scroll, arrow buttons, 3D lift on cards
Performance-friendly: GPU transforms, rAF batching, lazy images
*/

// Loader Functionality
document.addEventListener("DOMContentLoaded", () => {
  const loaderOverlay = document.getElementById("loader-overlay");
  const body = document.body;

  // Make sure the body is blurred and the loader is visible immediately.
  body.classList.add("loading");

  // This waits for ALL content (images, videos, etc.) to finish loading.
  window.addEventListener("load", () => {
    // When everything is loaded, remove the blur.
    body.classList.remove("loading");

    // Fade out and then remove the loader.
    loaderOverlay.style.opacity = "0";
    setTimeout(() => {
      loaderOverlay.style.display = "none";
    }, 600); // This must match the CSS transition duration
  });
});

// A small utility function to select elements
const $ = (s, $c = document) => $c.querySelector(s);
const $$ = (s, $c = document) => Array.from($c.querySelectorAll(s));

// Hero rotating title
(function rotateHero() {
  const swaps = $$('.hero-title .swap');
  if (!swaps.length) return;

  let i = 0;
  function show() {
    swaps.forEach((el, idx) => el.classList.toggle('active', idx === i));
    i = (i + 1) % swaps.length;
  }

  // The original code had a bug here. `show()` was not being called initially, and the interval was not set up correctly.
  show();
  setInterval(show, 3800);
})();

// Button gold ripple
(function pressGlow() {
  $$('.btn').forEach(btn => {
    const handler = (e) => {
      btn.classList.remove('glow-press');
      void btn.offsetWidth;
      btn.classList.add('glow-press');

      const x = (e.touches ? e.touches[0].clientX : e.clientX);
      const y = (e.touches ? e.touches[0].clientY : e.clientY);

      const r = document.createElement('span');
      r.className = 'gold-ripple';

      const rect = btn.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height) * 1.15;

      r.style.width = r.style.height = size + 'px';
      r.style.left = (x - rect.left) + 'px';
      r.style.top = (y - rect.top) + 'px';
      btn.appendChild(r);

      r.addEventListener('animationend', () => r.remove());
    };

    btn.addEventListener('click', handler);
    btn.addEventListener('touchstart', handler, { passive: true });
  });
})();

// Rails: arrows + drag-to-scroll + swipe glow
function setupRail(section) {
  const wrap = section.querySelector('.rail-wrap');
  const rail = section.querySelector('.rail');
  const left = section.querySelector('.arrow.left');
  const right = section.querySelector('.arrow.right');
  const SCROLL = () => Math.max(rail.clientWidth, 260) * 0.6;

  left.addEventListener('click', () => {
    section.classList.add('swipe-glow');
    rail.scrollBy({ left: -SCROLL(), behavior: 'smooth' });
  });

  right.addEventListener('click', () => {
    section.classList.add('swipe-glow');
    rail.scrollBy({ left: SCROLL(), behavior: 'smooth' });
  });

  rail.addEventListener('scroll', () => {
    clearTimeout(rail._glowT);
    rail._glowT = setTimeout(() => section.classList.remove('swipe-glow'), 400);
  }, { passive: true });

  // Drag to scroll
  let isDown = false, startX = 0, startLeft = 0;
  rail.addEventListener('pointerdown', e => {
    isDown = true;
    rail.setPointerCapture(e.pointerId);
    startX = e.clientX;
    startLeft = rail.scrollLeft;
    section.classList.add('swipe-glow');
  });

  rail.addEventListener('pointermove', e => {
    if (!isDown) return;
    const dx = e.clientX - startX;
    rail.scrollLeft = startLeft - dx;
    const tilt = Math.max(-1, Math.min(1, dx / 80));
    wrap.style.transform = `perspective(1200px) rotateY(${tilt * 4}deg)`;
  });

  const release = e => {
    if (!isDown) return;
    isDown = false;
    wrap.style.transform = "";
    setTimeout(() => section.classList.remove('swipe-glow'), 420);
  };
  rail.addEventListener('pointerup', release);
  rail.addEventListener('pointercancel', release);
}

// Init all rails
$$('.moment').forEach(setupRail);

// Lazy load guard
$$('.card').forEach(img => {
  img.addEventListener('error', () => {
    img.style.background = '#222';
    img.alt = 'Photo coming soon';
  });
});

// Ensure background video starts
// The original code had a bug here. `$$('.bg-video')` returns an array, but `.paused` is a property of a single video element.
window.addEventListener('load', () => {
  const v = document.querySelector('.bg-video');
  if (v && v.paused) {
    v.play().catch(() => {});
  }
});
