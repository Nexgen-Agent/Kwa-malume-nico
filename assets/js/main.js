/* Malume Nico - Enhanced JavaScript with Swipe Navigation */
document.addEventListener("DOMContentLoaded", function() {
    console.log("Malume Nico - DOM loaded with enhanced features");

    // ========================
    // SWIPE NAVIGATION SYSTEM
    // ========================
    let touchStartX = 0;
    let touchEndX = 0;
    const swipeThreshold = 50; // Minimum swipe distance

    // Page navigation map
    const pageNavigation = {
        'index.html': { left: 'menu.html', right: 'comments.html' },
        'menu.html': { left: 'booking.html', right: 'index.html' },
        'booking.html': { left: 'comments.html', right: 'menu.html' },
        'comments.html': { left: 'index.html', right: 'booking.html' }
    };

    function getCurrentPage() {
        const path = window.location.pathname;
        return path.substring(path.lastIndexOf('/') + 1) || 'index.html';
    }

    function handleSwipeGesture() {
        const swipeDistance = touchStartX - touchEndX;
        
        // Check if it's a significant horizontal swipe
        if (Math.abs(swipeDistance) > swipeThreshold) {
            const currentPage = getCurrentPage();
            const direction = swipeDistance > 0 ? 'left' : 'right';
            const nextPage = pageNavigation[currentPage]?.[direction];
            
            if (nextPage) {
                console.log(`Swiping ${direction} to ${nextPage}`);
                navigateToPage(nextPage);
            }
        }
    }

    function navigateToPage(page) {
        // Add transition effect
        const transition = document.createElement('div');
        transition.className = 'page-swipe-transition active';
        document.body.appendChild(transition);
        
        setTimeout(() => {
            window.location.href = page;
        }, 300);
    }

    // Touch event handlers for page navigation
    document.addEventListener('touchstart', e => {
        // Only handle swipes outside of carousels
        if (!e.target.closest('.fade-carousel') && !e.target.closest('.carousel-slide')) {
            touchStartX = e.changedTouches[0].screenX;
        }
    }, { passive: true });

    document.addEventListener('touchend', e => {
        // Only handle swipes outside of carousels
        if (!e.target.closest('.fade-carousel') && !e.target.closest('.carousel-slide')) {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipeGesture();
        }
    }, { passive: true });

    // ========================
    // ENHANCED CAROUSELS WITH SWIPE
    // ========================
    class EnhancedCarousel {
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
            
            this.touchStartX = 0;
            this.touchEndX = 0;

            this.init();
        }

        init() {
            if (!this.slides.length) return;

            this.showSlide(this.currentIndex);

            // Event listeners for buttons
            if (this.prevBtn) this.prevBtn.addEventListener('click', () => this.prev());
            if (this.nextBtn) this.nextBtn.addEventListener('click', () => this.next());

            // Indicator clicks
            this.indicators.forEach((indicator, index) => {
                indicator.addEventListener('click', () => this.goToSlide(index));
            });

            // Touch events for carousel swipe
            this.container.addEventListener('touchstart', (e) => {
                this.touchStartX = e.changedTouches[0].screenX;
            }, { passive: true });

            this.container.addEventListener('touchend', (e) => {
                this.touchEndX = e.changedTouches[0].screenX;
                this.handleCarouselSwipe();
            }, { passive: true });

            this.startAutoPlay();

            // Pause on hover/touch
            this.container.addEventListener('mouseenter', () => this.stopAutoPlay());
            this.container.addEventListener('mouseleave', () => this.startAutoPlay());
            this.container.addEventListener('touchstart', () => this.stopAutoPlay(), { passive: true });
            this.container.addEventListener('touchend', () => this.startAutoPlay(), { passive: true });
        }

        showSlide(index) {
            if (this.isTransitioning || !this.slides.length) return;

            this.isTransitioning = true;

            // Hide current slide
            this.slides[this.currentIndex].classList.remove('active');
            if (this.indicators[this.currentIndex]) {
                this.indicators[this.currentIndex].classList.remove('active');
            }

            // Update index with looping
            this.currentIndex = index;
            if (this.currentIndex < 0) this.currentIndex = this.slides.length - 1;
            if (this.currentIndex >= this.slides.length) this.currentIndex = 0;

            // Show new slide
            this.slides[this.currentIndex].classList.add('active');
            if (this.indicators[this.currentIndex]) {
                this.indicators[this.currentIndex].classList.add('active');
            }

            // Reset transition state
            setTimeout(() => {
                this.isTransitioning = false;
            }, 500);
        }

        handleCarouselSwipe() {
            const swipeThreshold = 30;
            const deltaX = this.touchStartX - this.touchEndX;

            if (Math.abs(deltaX) > swipeThreshold) {
                if (deltaX > 0) {
                    this.next();
                } else {
                    this.prev();
                }
            }
        }

        next() { this.showSlide(this.currentIndex + 1); }
        prev() { this.showSlide(this.currentIndex - 1); }

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

    function initCarousels() {
        const carousels = document.querySelectorAll('.fade-carousel');
        carousels.forEach(container => {
            new EnhancedCarousel(container);
        });
        console.log(`Enhanced ${carousels.length} carousel(s) with swipe support`);
    }

    // ========================
    // LOADER FUNCTIONALITY
    // ========================
    const loaderOverlay = document.getElementById("loader-overlay");
    const body = document.body;

    if (loaderOverlay) {
        // Show loader immediately
        body.classList.add("loading");
        loaderOverlay.style.display = "flex";
        loaderOverlay.style.opacity = "1";

        // Hide loader when everything is loaded
        window.addEventListener("load", function() {
            setTimeout(() => {
                body.classList.remove("loading");
                loaderOverlay.style.opacity = "0";
                setTimeout(() => {
                    loaderOverlay.style.display = "none";
                }, 600);
            }, 1000);
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

    // ========================
    // BLUE LIGHT BEAMS
    // ========================
    function initBlueLightBeams() {
        const lightBeams = document.querySelectorAll('.light-beam');
        
        // Randomize light beam animations for more natural effect
        lightBeams.forEach((beam, index) => {
            const randomDelay = Math.random() * 8;
            const randomDuration = 12 + Math.random() * 10;
            beam.style.animationDelay = `${randomDelay}s`;
            beam.style.animationDuration = `${randomDuration}s`;
        });

        console.log(`Blue light beams activated: ${lightBeams.length} beams`);
    }

    // ========================
    // BACKGROUND VIDEO
    // ========================
    function initBackgroundVideo() {
        const video = document.querySelector('.bg-video');
        if (video && video.paused) {
            video.play().catch(() => {
                console.log("Video autoplay prevented - user interaction required");
            });
        }
    }

    // ========================
    // EXISTING FUNCTIONALITY
    // ========================
    function initHeroRotation() {
        const swaps = document.querySelectorAll('.hero-title .swap');
        if (!swaps.length) return;

        let i = 0;
        function show() {
            swaps.forEach((el, idx) => {
                el.classList.toggle('active', idx === i);
            });
        }

        show();
        setInterval(() => {
            i = (i + 1) % swaps.length;
            show();
        }, 3800);
    }

    function initButtonEffects() {
        const buttons = document.querySelectorAll('.btn');

        buttons.forEach(btn => {
            const handler = (e) => {
                btn.classList.remove('glow-press');
                void btn.offsetWidth;
                btn.classList.add('glow-press');

                const x = e.clientX || (e.touches && e.touches[0].clientX);
                const y = e.clientY || (e.touches && e.touches[0].clientY);

                if (x && y) {
                    const r = document.createElement('span');
                    r.className = 'gold-ripple';

                    const rect = btn.getBoundingClientRect();
                    const size = Math.max(rect.width, rect.height) * 1.15;

                    r.style.width = r.style.height = size + 'px';
                    r.style.left = (x - rect.left) + 'px';
                    r.style.top = (y - rect.top) + 'px';

                    btn.appendChild(r);
                    r.addEventListener('animationend', () => r.remove());
                }
            };

            btn.addEventListener('click', handler);
            btn.addEventListener('touchstart', handler, { passive: true });
        });
    }

    function initScrollingRails() {
        const moments = document.querySelectorAll('.moment');

        moments.forEach(section => {
            const wrap = section.querySelector('.rail-wrap');
            const rail = section.querySelector('.rail');
            const left = section.querySelector('.arrow.left');
            const right = section.querySelector('.arrow.right');

            if (!rail || !left || !right) return;

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
                rail._glowT = setTimeout(() => {
                    section.classList.remove('swipe-glow');
                }, 400);
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
                if (wrap) wrap.style.transform = `perspective(1200px) rotateY(${tilt * 4}deg)`;
            });

            const release = () => {
                if (!isDown) return;
                isDown = false;
                if (wrap) wrap.style.transform = "";
                setTimeout(() => section.classList.remove('swipe-glow'), 420);
            };

            rail.addEventListener('pointerup', release);
            rail.addEventListener('pointercancel', release);
        });
    }

    // ========================
    // INITIALIZE EVERYTHING
    // ========================
    initHeroRotation();
    initButtonEffects();
    initScrollingRails();
    initCarousels();
    initBlueLightBeams();
    initBackgroundVideo();

    console.log("All enhanced features initialized - Swipe navigation ready!");
});

// Fallback for slow loading elements
setTimeout(() => {
    const carousels = document.querySelectorAll('.fade-carousel');
    const anyActive = document.querySelector('.carousel-slide.active');

    if (carousels.length > 0 && !anyActive) {
        carousels.forEach(container => {
            const track = container.querySelector('.carousel-track');
            const slides = container.querySelectorAll('.carousel-slide');
            if (track && slides.length > 0) {
                slides[0].classList.add('active');
                const indicator = container.querySelector('.carousel-indicator');
                if (indicator) indicator.classList.add('active');
            }
        });
    }
}, 2000);