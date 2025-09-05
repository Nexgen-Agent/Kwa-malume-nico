/* Malume Nico - Home
Shares the same "water glass + gold glow" feel as comments page
- Vertical sections; each has a horizontal swipe rail
Drag to scroll, arrow buttons, 3D lift on cards
Performance-friendly: GPU transforms, rAF batching, lazy images
*/

// Fixed utility functions
const $ = (s, $c = document) => $c.querySelector(s);
const $$ = (s, $c = document) => Array.from($c.querySelectorAll(s));

//
// Hero rotating title
//
(function rotateHero(){
  const swaps = $$('.hero-title .swap');
  if (!swaps.length) return;
  
  let i = 0;
  function show(){
    swaps.forEach((el, idx) => el.classList.toggle('active', idx === i));
  }
  
  // Show first one immediately
  show();
  
  setInterval(() => {
    i = (i + 1) % swaps.length;
    show();
  }, 3800);
})();

//
// Button gold ripple
//
(function pressGlow(){
  // This function now only targets elements with the ".ripple-btn" class
  $$('.ripple-btn').forEach(btn=>{
    const handler = (e)=>{
      btn.classList.remove('glow-press'); void btn.offsetWidth; btn.classList.add('glow-press');
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
      r.addEventListener('animationend', ()=> r.remove());
    };
    btn.addEventListener('click', handler);
    btn.addEventListener('touchstart', handler, {passive:true});
  });
})();


//
// Rails: arrows + drag-to-scroll + swipe glow
//
function setupRail(section){
  const wrap = section.querySelector('.rail-wrap');
  const rail = section.querySelector('.rail');
  const left = section.querySelector('.arrow.left');
  const right = section.querySelector('.arrow.right');
  const SCROLL = () => Math.max(rail.clientWidth, 260) * 0.6;

  left.addEventListener('click', () => {
    section.classList.add('swipe-glow');
    rail.scrollBy({left: -SCROLL(), behavior: 'smooth'});
  });

  right.addEventListener('click', () => {
    section.classList.add('swipe-glow');
    rail.scrollBy({left: SCROLL(), behavior: 'smooth'});
  });

  rail.addEventListener('scroll', () => {
    /* remove glow after motion */
    clearTimeout(rail._glowT);
    rail._glowT = setTimeout(() => section.classList.remove('swipe-glow'), 400);
  }, {passive: true});

  // Drag to scroll (mouse + touch via Pointer Events)
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
    // mini 3D tilt
    const tilt = Math.max(-1, Math.min(1, dx / 80));
    wrap.style.transform = `perspective(1200px) rotateY(${tilt * 4}deg)`;
  });

  const release = e => {
    if (!isDown) return;
    isDown = false;
    wrap.style.transform = '';
    setTimeout(() => section.classList.remove('swipe-glow'), 420);
  };
  
  rail.addEventListener('pointerup', release);
  rail.addEventListener('pointercancel', release);
}

// Init all rails
$$('.moment').forEach(setupRail);

//
// Lazy load guard (if images missing, avoid console noise)
//
$$('.card').forEach(img => {
  img.addEventListener('error', () => {
    img.style.background = '#222';
    img.alt = 'Photo coming soon';
  });
});

//
// Ensure background video starts
//
window.addEventListener('load', () => {
  const v = $('.bg-video');
  if (v && v.paused) v.play().catch(() => {});
});

// ========================
// LOADER FUNCTIONALITY
// ========================
document.addEventListener("DOMContentLoaded", () => {
  const loaderOverlay = document.getElementById("loader-overlay");
  const body = document.body;

  if (loaderOverlay) {
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
      }, 600);
    });

    // Fallback in case load event doesn't fire
    setTimeout(() => {
      if (body.classList.contains("loading")) {
        body.classList.remove("loading");
        loaderOverlay.style.opacity = "0";
        setTimeout(() => {
          loaderOverlay.style.display = "none";
        }, 600);
      }
    }, 5000);
  }
});

// ========================
// LIGHT BEAMS & FADE ANIMATIONS
// ========================

// Liquid light effects
function enhanceWithLiquidLight() {
  // Add enhanced water effect to glass elements
  $$('.glass.water').forEach(glass => {
    glass.classList.add('enhanced-water');
  });
  
  // Add shine effect to gold buttons
  $$('.btn.gold').forEach(btn => {
    btn.classList.add('enhanced');
  });
  
  console.log('Liquid light enhancements applied');
}

// Randomize light beams for natural effect
function randomizeLightBeams() {
  $$('.light-beam').forEach((beam, index) => {
    beam.style.animationDelay = `${Math.random() * 5}s`;
  });
  console.log('Light beams randomized');
}

// Adjust animation for reduced motion preference
function adjustAnimationSpeed() {
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const lightBeams = $$('.light-beam');
  
  if (reducedMotion && lightBeams.length > 0) {
    lightBeams.forEach(beam => {
      beam.style.animationDuration = '20s';
      beam.style.opacity = '0.1';
    });
    console.log('Reduced motion applied to light beams');
  }
}

// ========================
// FADE CAROUSEL FUNCTIONALITY
// ========================

class FadeCarousel {
  constructor(container) {
    this.container = container;
    this.track = container.querySelector('.carousel-track');
    this.slides = Array.from(container.querySelectorAll('.carousel-slide'));
    this.indicators = Array.from(container.querySelectorAll('.carousel-indicator'));
    this.prevBtn = container.querySelector('.carousel-prev');
    this.nextBtn = container.querySelector('.carousel-next');

    this.currentIndex = 0;
    this.isTransitioning = false;
    this.autoPlayInterval = null;
    this.autoPlayDelay = 4000; // 4 seconds between transitions

    this.init();
  }

  init() {
    // Set initial active state
    this.showSlide(this.currentIndex);

    // Event listeners
    this.prevBtn.addEventListener('click', () => this.prev());
    this.nextBtn.addEventListener('click', () => this.next());

    // Indicator clicks
    this.indicators.forEach((indicator, index) => {
      indicator.addEventListener('click', () => this.goToSlide(index));
    });

    // Start autoplay
    this.startAutoPlay();

    // Pause on hover
    this.container.addEventListener('mouseenter', () => this.stopAutoPlay());
    this.container.addEventListener('mouseleave', () => this.startAutoPlay());

    // Touch events for mobile
    this.container.addEventListener('touchstart', () => this.stopAutoPlay(), { passive: true });
    this.container.addEventListener('touchend', () => this.startAutoPlay(), { passive: true });
  }

  showSlide(index) {
    if (this.isTransitioning) return;

    this.isTransitioning = true;

    // Hide current slide
    this.slides[this.currentIndex].classList.remove('active');
    this.indicators[this.currentIndex]?.classList.remove('active');

    // Update current index (with looping)
    this.currentIndex = index;
    if (this.currentIndex < 0) this.currentIndex = this.slides.length - 1;
    if (this.currentIndex >= this.slides.length) this.currentIndex = 0;

    // Show new slide
    this.slides[this.currentIndex].classList.add('active');
    this.indicators[this.currentIndex]?.classList.add('active');

    // Reset transitioning state after animation completes
    setTimeout(() => {
      this.isTransitioning = false;
    }, 500); // Match CSS transition duration
  }

  next() {
    this.showSlide(this.currentIndex + 1);
  }

  prev() {
    this.showSlide(this.currentIndex - 1);
  }

  goToSlide(index) {
    if (index === this.currentIndex) return;
    this.showSlide(index);
  }

  startAutoPlay() {
    this.stopAutoPlay();
    this.autoPlayInterval = setInterval(() => {
      this.next();
    }, this.autoPlayDelay);
  }

  stopAutoPlay() {
    if (this.autoPlayInterval) {
      clearInterval(this.autoPlayInterval);
      this.autoPlayInterval = null;
    }
  }
}

// Initialize all carousels
function initFadeCarousels() {
  const carousels = $$('.fade-carousel');
  if (carousels.length === 0) return; // Only run if carousels exist
  
  console.log(`Found ${carousels.length} fade carousels to initialize`);

  carousels.forEach((container, index) => {
    console.log(`Initializing carousel ${index + 1}`);
    new FadeCarousel(container);
  });
}

// ========================
// INITIALIZE EVERYTHING
// ========================

// Main initialization
document.addEventListener('DOMContentLoaded', function() {
  console.log('Initializing all features');
  
  // Initialize fade carousels (if they exist)
  initFadeCarousels();
  
  // Initialize liquid light effects (if they exist)
  enhanceWithLiquidLight();
  
  // Randomize light beams after a short delay
  setTimeout(() => {
    if ($$('.light-beam').length > 0) {
      randomizeLightBeams();
    }
  }, 1000);
  
  // Check user motion preference
  adjustAnimationSpeed();
  
  // Listen for changes in motion preference
  window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', adjustAnimationSpeed);
});

// Fallback for carousels
setTimeout(() => {
  const carousels = $$('.fade-carousel');
  const anyActive = $('.carousel-slide.active');

  if (carousels.length > 0 && !anyActive) {
    console.log('Fallback: Re-initializing carousels');
    initFadeCarousels();
  }
}, 2000);