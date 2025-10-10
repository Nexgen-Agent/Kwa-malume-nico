// Complete Malume Nico JavaScript with Swipe Navigation
class MalumeNicoApp {
    constructor() {
        this.currentPageIndex = 0;
        this.pages = ['index.html', 'menu.html', 'booking.html', 'comments.html'];
        this.currentPage = this.getCurrentPage();
        this.isTransitioning = false;
        this.touchStartX = 0;
        this.touchStartY = 0;
        this.touchEndX = 0;
        this.touchEndY = 0;
        
        this.init();
    }

    init() {
        console.log("🍔 Malume Nico - Initializing Enhanced App");
        
        this.initLoader();
        this.initBackgroundVideo();
        this.initCarousels();
        this.initLightBeams();
        this.initSwipeNavigation();
        this.initInteractiveEffects();
        this.initPerformance();
        
        console.log("🎉 Malume Nico App Fully Initialized");
    }

    // ========================
    // LOADER FUNCTIONALITY
    // ========================
    initLoader() {
        const loaderOverlay = document.getElementById("loader-overlay");
        const body = document.body;

        if (loaderOverlay) {
            body.classList.add("loading");
            loaderOverlay.style.display = "flex";
            loaderOverlay.style.opacity = "1";

            window.addEventListener("load", () => {
                setTimeout(() => {
                    body.classList.remove("loading");
                    loaderOverlay.style.opacity = "0";
                    setTimeout(() => {
                        loaderOverlay.style.display = "none";
                        console.log("✅ Loader hidden");
                    }, 500);
                }, 1200);
            });

            // Fallback
            setTimeout(() => {
                if (body.classList.contains("loading")) {
                    body.classList.remove("loading");
                    loaderOverlay.style.opacity = "0";
                    setTimeout(() => {
                        loaderOverlay.style.display = "none";
                        console.log("🔄 Loader fallback triggered");
                    }, 500);
                }
            }, 4000);
        }
    }

    // ========================
    // BACKGROUND VIDEO
    // ========================
    initBackgroundVideo() {
        const video = document.querySelector('.bg-video');
        if (!video) {
            console.warn('🎥 Background video element not found');
            return;
        }

        // Force video attributes
        video.setAttribute('autoplay', '');
        video.setAttribute('muted', '');
        video.setAttribute('loop', '');
        video.setAttribute('playsinline', '');
        video.controls = false;

        const playVideo = () => {
            video.play().then(() => {
                console.log('✅ Background video playing');
            }).catch((error) => {
                console.warn('⚠️ Video autoplay prevented:', error);
            });
        };

        if (video.readyState >= 3) {
            playVideo();
        } else {
            video.addEventListener('loadeddata', playVideo);
            video.addEventListener('canplay', playVideo);
        }

        video.addEventListener('error', (e) => {
            console.error('❌ Video error:', e);
            document.body.style.background = 'linear-gradient(135deg, #0a0a1a, #1a1a2e, #16213e)';
        });

        video.style.pointerEvents = 'none';
    }

    // ========================
    // ENHANCED CAROUSELS WITH SWIPE
    // ========================
    initCarousels() {
        const carousels = document.querySelectorAll('.fade-carousel');
        
        carousels.forEach(container => {
            new EnhancedCarousel(container);
        });
        
        console.log(`🎠 ${carousels.length} carousel(s) initialized`);
    }

    // ========================
    // BLUE LIGHT BEAMS
    // ========================
    initLightBeams() {
        const lightBeams = document.querySelectorAll('.light-beam');
        
        if (lightBeams.length === 0) {
            console.warn('💡 No light beams found');
            return;
        }

        lightBeams.forEach((beam, index) => {
            const randomDelay = Math.random() * 8;
            const randomDuration = 18 + Math.random() * 12;
            const randomRotation = -6 + Math.random() * 12;
            
            beam.style.setProperty('--beam-rotate', `${randomRotation}deg`);
            beam.style.animationDelay = `${randomDelay}s`;
            beam.style.animationDuration = `${randomDuration}s`;
            
            // Dynamic opacity for water-like effect
            setInterval(() => {
                const randomOpacity = 0.4 + Math.random() * 0.4;
                beam.style.opacity = randomOpacity;
            }, 3000 + Math.random() * 4000);
        });

        console.log(`💫 ${lightBeams.length} blue light beam(s) activated`);
    }

    // ========================
    // SWIPE NAVIGATION SYSTEM
    // ========================
    initSwipeNavigation() {
        const swipeContainer = document.body;
        let currentSwipeTarget = null;

        // Touch start
        swipeContainer.addEventListener('touchstart', (e) => {
            this.touchStartX = e.changedTouches[0].screenX;
            this.touchStartY = e.changedTouches[0].screenY;
            currentSwipeTarget = e.target;
        }, { passive: true });

        // Touch end
        swipeContainer.addEventListener('touchend', (e) => {
            this.touchEndX = e.changedTouches[0].screenX;
            this.touchEndY = e.changedTouches[0].screenY;
            this.handleSwipeGesture(currentSwipeTarget);
        }, { passive: true });

        // Mouse swipe simulation for desktop
        let mouseDownX = 0;
        let mouseDownY = 0;
        
        swipeContainer.addEventListener('mousedown', (e) => {
            mouseDownX = e.clientX;
            mouseDownY = e.clientY;
            currentSwipeTarget = e.target;
        });

        swipeContainer.addEventListener('mouseup', (e) => {
            const mouseUpX = e.clientX;
            const mouseUpY = e.clientY;
            const deltaX = mouseUpX - mouseDownX;
            const deltaY = mouseUpY - mouseDownY;
            
            // Only trigger if it's a horizontal swipe and not a click
            if (Math.abs(deltaX) > 50 && Math.abs(deltaY) < 30) {
                this.touchStartX = mouseDownX;
                this.touchEndX = mouseUpX;
                this.handleSwipeGesture(currentSwipeTarget);
            }
        });

        console.log("👆 Swipe navigation initialized");
    }

    handleSwipeGesture(target) {
        const swipeThreshold = 50;
        const deltaX = this.touchStartX - this.touchEndX;
        const deltaY = this.touchStartY - this.touchEndY;

        // Check if it's a horizontal swipe (not vertical scroll)
        if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > swipeThreshold) {
            // Check if target is inside a carousel
            const isInCarousel = target.closest('.fade-carousel') || 
                                target.closest('.carousel-slide') ||
                                target.closest('.carousel-container');

            if (isInCarousel) {
                // Handle carousel swipe
                this.handleCarouselSwipe(deltaX > 0 ? 'right' : 'left', target);
            } else {
                // Handle page navigation swipe
                this.handlePageSwipe(deltaX > 0 ? 'right' : 'left');
            }
        }
    }

    handleCarouselSwipe(direction, target) {
        const carousel = target.closest('.fade-carousel');
        if (carousel) {
            const carouselInstance = carousel._carouselInstance;
            if (carouselInstance) {
                if (direction === 'left') {
                    carouselInstance.next();
                } else {
                    carouselInstance.prev();
                }
                console.log(`🔄 Carousel swiped ${direction}`);
            }
        }
    }

    handlePageSwipe(direction) {
        if (this.isTransitioning) return;

        const currentIndex = this.pages.indexOf(this.currentPage);
        let nextIndex;

        if (direction === 'left') {
            nextIndex = (currentIndex + 1) % this.pages.length;
        } else {
            nextIndex = (currentIndex - 1 + this.pages.length) % this.pages.length;
        }

        const nextPage = this.pages[nextIndex];
        console.log(`🌐 Swiping to ${nextPage}`);

        this.navigateToPage(nextPage);
    }

    navigateToPage(page) {
        this.isTransitioning = true;
        
        // Create page transition effect
        const transition = document.createElement('div');
        transition.className = 'page-transition active';
        document.body.appendChild(transition);

        setTimeout(() => {
            window.location.href = page;
        }, 400);
    }

    getCurrentPage() {
        const path = window.location.pathname;
        return path.substring(path.lastIndexOf('/') + 1) || 'index.html';
    }

    // ========================
    // INTERACTIVE EFFECTS
    // ========================
    initInteractiveEffects() {
        // Button effects
        const buttons = document.querySelectorAll('.btn, .nav-btn, .carousel-prev, .carousel-next');
        
        buttons.forEach(btn => {
            btn.addEventListener('click', this.createRippleEffect);
        });

        // Hover effects for moments
        const moments = document.querySelectorAll('.moment');
        moments.forEach(moment => {
            moment.addEventListener('mouseenter', () => {
                moment.style.transform = 'translateY(-8px) scale(1.02)';
                moment.style.transition = 'transform 0.3s ease';
            });
            
            moment.addEventListener('mouseleave', () => {
                moment.style.transform = 'translateY(0) scale(1)';
            });
        });

        console.log("🎭 Interactive effects initialized");
    }

    createRippleEffect(e) {
        const ripple = document.createElement('span');
        ripple.className = 'gold-ripple';
        
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = (e.clientX || e.touches[0].clientX) - rect.left - size / 2;
        const y = (e.clientY || e.touches[0].clientY) - rect.top - size / 2;
        
        ripple.style.cssText = `
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            position: absolute;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(255,255,255,0.8) 0%, rgba(168,192,255,0.4) 30%, rgba(100,130,255,0.2) 60%, transparent 70%);
            transform: scale(0);
            animation: rippleOut 0.6s ease-out forwards;
            pointer-events: none;
        `;
        
        this.style.position = 'relative';
        this.style.overflow = 'hidden';
        this.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    }

    // ========================
    // PERFORMANCE OPTIMIZATIONS
    // ========================
    initPerformance() {
        // Lazy load images
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src || img.src;
                        img.classList.add('loaded');
                        imageObserver.unobserve(img);
                    }
                });
            });

            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }

        console.log("⚡ Performance optimizations applied");
    }
}

// Enhanced Carousel Class
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
        this.autoPlayDelay = 5000;

        // Store instance for swipe access
        container._carouselInstance = this;

        this.init();
    }

    init() {
        if (!this.slides.length) return;

        this.showSlide(this.currentIndex);

        // Button events
        if (this.prevBtn) this.prevBtn.addEventListener('click', () => this.prev());
        if (this.nextBtn) this.nextBtn.addEventListener('click', () => this.next());

        // Indicator events
        this.indicators.forEach((indicator, index) => {
            indicator.addEventListener('click', () => this.goToSlide(index));
        });

        // Touch events for carousel
        this.container.addEventListener('touchstart', (e) => {
            this.touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });

        this.container.addEventListener('touchend', (e) => {
            this.touchEndX = e.changedTouches[0].screenX;
            this.handleCarouselSwipe();
        }, { passive: true });

        this.startAutoPlay();

        // Pause on interaction
        this.container.addEventListener('mouseenter', () => this.stopAutoPlay());
        this.container.addEventListener('mouseleave', () => this.startAutoPlay());
        this.container.addEventListener('touchstart', () => this.stopAutoPlay(), { passive: true });
    }

    showSlide(index) {
        if (this.isTransitioning) return;

        this.isTransitioning = true;

        // Hide current
        this.slides[this.currentIndex].classList.remove('active');
        if (this.indicators[this.currentIndex]) {
            this.indicators[this.currentIndex].classList.remove('active');
        }

        // Update index
        this.currentIndex = index;
        if (this.currentIndex < 0) this.currentIndex = this.slides.length - 1;
        if (this.currentIndex >= this.slides.length) this.currentIndex = 0;

        // Show new
        this.slides[this.currentIndex].classList.add('active');
        if (this.indicators[this.currentIndex]) {
            this.indicators[this.currentIndex].classList.add('active');
        }

        setTimeout(() => {
            this.isTransitioning = false;
        }, 600);
    }

    next() { this.showSlide(this.currentIndex + 1); }
    prev() { this.showSlide(this.currentIndex - 1); }
    goToSlide(index) { this.showSlide(index); }

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

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new MalumeNicoApp();
});

// Add ripple animation to CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes rippleOut {
        to {
            transform: scale(2.5);
            opacity: 0;
        }
    }
    
    .gold-ripple {
        animation: rippleOut 0.6s ease-out forwards;
    }
`;
document.head.appendChild(style);