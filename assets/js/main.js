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

  // Hero rotating title
  const swaps = document.querySelectorAll('.hero-title .swap');
  if (swaps.length) {
    let i = 0;
    function show() {
      swaps.forEach((el, idx) => el.classList.toggle('active', idx === i));
      i = (i + 1) % swaps.length;
    }
    show();
    setInterval(show, 3800);
  }

  // Button gold ripple
  document.querySelectorAll('.btn').forEach(btn => {
    const handler = (e) => {
      btn.classList.remove('glow-press');
      void btn.offsetWidth;
      btn.classList.add('glow-press');
      const x = (e.touches ? e.touches[0].clientX : e.clientX);
      const y = (e.touches ? e.touches[0].clientY : e.clientY);
      const r = document.createElement('span');
      r.className = 'gold-ripple';
      const rect = btn.getBoundingClientRect();
      r.style.width = r.style.height = Math.max(rect.width, rect.height) * 1.15 + 'px';
      r.style.left = (x - rect.left) + 'px';
      r.style.top = (y - rect.top) + 'px';
      btn.appendChild(r);
      r.addEventListener('animationend', () => r.remove());
    };
    btn.addEventListener('click', handler);
    btn.addEventListener('touchstart', handler, { passive: true });
  });

  // Rails: arrows + drag-to-scroll
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

    const release = () => {
      if (!isDown) return;
      isDown = false;
      wrap.style.transform = "";
      setTimeout(() => section.classList.remove('swipe-glow'), 420);
    };
    rail.addEventListener('pointerup', release);
    rail.addEventListener('pointercancel', release);
  }

  // Init all rails
  document.querySelectorAll('.moment').forEach(setupRail);

  // Lazy load guard
  document.querySelectorAll('.card').forEach(img => {
    img.addEventListener('error', () => {
      img.style.background = '#222';
      img.alt = 'Photo coming soon';
    });
  });

  // Ensure background video starts
  window.addEventListener('load', () => {
    const v = document.querySelector('.bg-video');
    if (v && v.paused) v.play().catch(() => {});
  });

  // Auto-scrolling rails
  function autoScrollRail(rail, speed = 0.5) {
    function step() {
      if (rail.scrollLeft + rail.clientWidth >= rail.scrollWidth) {
        rail.scrollLeft = 0;
      } else {
        rail.scrollLeft += speed;
      }
      requestAnimationFrame(step);
    }
    step();
  }

  window.addEventListener("load", () => {
    document.querySelectorAll(".rail").forEach(rail => {
      autoScrollRail(rail, 0.5);
    });
  });
});
