/* Malume Nico - Home - Fixed Loader Issue */
document.addEventListener("DOMContentLoaded", function() {
  console.log('DOM fully loaded and parsed');
  
  // ========================
  // LOADER FUNCTIONALITY - FIXED
  // ========================
  const loaderOverlay = document.getElementById("loader-overlay");
  const body = document.body;
  
  // Make sure loader is visible initially
  if (loaderOverlay) {
    loaderOverlay.style.display = 'flex';
    loaderOverlay.style.opacity = '1';
    body.classList.add('loading');
  }

  // Wait for window load (all resources)
  window.addEventListener("load", function() {
    console.log('All page resources loaded');
    
    if (loaderOverlay) {
      // Fade out loader
      loaderOverlay.style.opacity = "0";
      body.classList.remove('loading');
      
      // Remove after fade completes
      setTimeout(() => {
        loaderOverlay.style.display = "none";
      }, 600);
    }
  });

  // Fallback: If load event doesn't fire, hide loader after 3 seconds
  setTimeout(() => {
    if (loaderOverlay && loaderOverlay.style.opacity !== '0') {
      console.log('Fallback: Hiding loader after timeout');
      loaderOverlay.style.opacity = "0";
      body.classList.remove('loading');
      setTimeout(() => {
        loaderOverlay.style.display = "none";
      }, 600);
    }
  }, 3000);

  // ========================
  // EXISTING FUNCTIONALITY
  // ========================
  
  // Hero rotating title
  (function rotateHero() {
    const swaps = document.querySelectorAll('.hero-title .swap');
    if (!swaps.length) return;

    let i = 0;
    function show() {
      swaps.forEach((el, idx) => el.classList.toggle('active', idx === i));
      i = (i + 1) % swaps.length;
    }

    show();
    setInterval(show, 3800);
  })();

  // Button gold ripple
  (function pressGlow() {
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
      this.autoPlayDelay = 4000;
      
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
      }, 500);
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
    const carousels = document.querySelectorAll('.fade-carousel');
    console.log(`Found ${carousels.length} fade carousels to initialize`);
    
    carousels.forEach((container, index) => {
      console.log(`Initializing carousel ${index + 1}`);
      new FadeCarousel(container);
    });
  }

  // Initialize fade carousels
  initFadeCarousels();

  // Lazy load guard
  document.querySelectorAll('.card').forEach(img => {
    img.addEventListener('error', () => {
      img.style.background = '#222';
      img.alt = 'Photo coming soon';
    });
  });

  // Ensure background video starts
  const v = document.querySelector('.bg-video');
  if (v && v.paused) {
    v.play().catch(() => {});
  }
});

// Liquid Light Overlay Elements (keep these in your HTML)
/*
<div class="liquid-light-overlay">
  <div class="light-beam"></div>
  <div class="light-beam"></div>
  <div class="light-beam"></div>
</div>

<div class="background-caustics"></div>
*/