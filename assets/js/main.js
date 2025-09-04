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

// ========================
// FADE CAROUSEL FUNCTIONALITY - FIXED
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

// Initialize all carousels when page loads
function initFadeCarousels() {
  const carousels = document.querySelectorAll('.fade-carousel');
  console.log(`Found ${carousels.length} fade carousels to initialize`);
  
  carousels.forEach((container, index) => {
    console.log(`Initializing carousel ${index + 1}`);
    new FadeCarousel(container);
  });
}

// Remove the old rail functionality since we're using fade carousels now
function removeOldRailFunctionality() {
  // Remove event listeners from old rail system if they exist
  const rails = document.querySelectorAll('.rail');
  rails.forEach(rail => {
    rail.replaceWith(rail.cloneNode(true)); // This removes all event listeners
  });
}

// Main initialization
document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM fully loaded and parsed');
  
  // Remove old scrolling functionality
  removeOldRailFunctionality();
  
  // Initialize the fade carousels
  initFadeCarousels();
  
  // Your existing button functionality
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

  // Lazy load guard
  $$('.card').forEach(img => {
    img.addEventListener('error', () => {
      img.style.background = '#222';
      img.alt = 'Photo coming soon';
    });
  });

  // Ensure background video starts
  window.addEventListener('load', () => {
    const v = document.querySelector('.bg-video');
    if (v && v.paused) {
      v.play().catch(() => {});
    }
  });
});

// Fallback: If carousels aren't initialized after 1 second, try again
setTimeout(() => {
  const carousels = document.querySelectorAll('.fade-carousel');
  const anyActive = document.querySelector('.carousel-slide.active');
  
  if (carousels.length > 0 && !anyActive) {
    console.log('Fallback: Re-initializing carousels');
    initFadeCarousels();
  }
}, 1000);

<!-- Liquid Light Overlay -->
<div class="liquid-light-overlay">
  <div class="light-beam"></div>
  <div class="light-beam"></div>
  <div class="light-beam"></div>
</div>

<!-- Background Caustics -->
<div class="background-caustics"></div>