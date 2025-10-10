// Enhanced Malume Nico JavaScript
document.addEventListener("DOMContentLoaded", function() {
    console.log("🍔 Malume Nico - Enhanced DOM loaded");

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

    // ========================
    // ENHANCED CAROUSELS
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
            this.autoPlayDelay = 5000;
            this.touchStartX = 0;
            this.touchEndX = 0;

            this.init();
        }

        init() {
            if (!this.slides.length) {
                console.warn("No slides found in carousel");
                return;
            }

            this.showSlide(this.currentIndex);

            // Event listeners
            if (this.prevBtn) {
                this.prevBtn.addEventListener('click', () => this.prev());
            }
            if (this.nextBtn) {
                this.nextBtn.addEventListener('click', () => this.next());
            }

            // Indicator clicks
            this.indicators.forEach((indicator, index) => {
                indicator.addEventListener('click', () => this.goToSlide(index));
            });

            // Touch support
            this.container.addEventListener('touchstart', (e) => {
                this.touchStartX = e.changedTouches[0].screenX;
            }, { passive: true });

            this.container.addEventListener('touchend', (e) => {
                this.touchEndX = e.changedTouches[0].screenX;
                this.handleSwipe();
            }, { passive: true });

            this.startAutoPlay();

            // Pause on hover/touch
            this.container.addEventListener('mouseenter', () => this.stopAutoPlay());
            this.container.addEventListener('mouseleave', () => this.startAutoPlay());
            this.container.addEventListener('touchstart', () => this.stopAutoPlay(), { passive: true });
            this.container.addEventListener('touchend', () => this.startAutoPlay(), { passive: true });

            console.log(`🎠 Carousel initialized with ${this.slides.length} slides`);
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

            // Add glow effect to container
            this.container.classList.add('carousel-changing');
            setTimeout(() => {
                this.container.classList.remove('carousel-changing');
            }, 600);

            // Reset transition state
            setTimeout(() => {
                this.isTransitioning = false;
            }, 600);
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

        handleSwipe() {
            const swipeThreshold = 50;
            const diff = this.touchStartX - this.touchEndX;

            if (Math.abs(diff) > swipeThreshold) {
                if (diff > 0) {
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

    function initCarousels() {
        const carousels = document.querySelectorAll('.fade-carousel');
        if (carousels.length === 0) {
            console.warn("No carousels found");
            return;
        }

        carousels.forEach(container => {
            new EnhancedCarousel(container);
        });
        
        console.log(`✅ ${carousels.length} carousel(s) initialized`);
    }
    initCarousels();

    // ========================
    // ENHANCED LIGHT BEAMS
    // ========================
    function initEnhancedLightBeams() {
        const lightBeams = document.querySelectorAll('.light-beam');
        const backgroundCaustics = document.querySelector('.background-caustics');

        if (lightBeams.length === 0) {
            console.warn("No light beams found");
            return;
        }

        // Enhanced beam customization
        lightBeams.forEach((beam, index) => {
            const randomDelay = Math.random() * 6;
            const randomDuration = 16 + Math.random() * 8;
            const randomRotation = -5 + Math.random() * 10;
            
            beam.style.setProperty('--beam-rotate', `${randomRotation}deg`);
            beam.style.animationDelay = `${randomDelay}s`;
            beam.style.animationDuration = `${randomDuration}s`;
            
            // Dynamic opacity changes
            setInterval(() => {
                const randomOpacity = 0.3 + Math.random() * 0.4;
                beam.style.opacity = randomOpacity;
            }, 2000 + Math.random() * 3000);
        });

        // Enhanced background caustics
        if (backgroundCaustics) {
            setInterval(() => {
                const positions = Array.from({length: 8}, () => Math.random() * 100);
                backgroundCaustics.style.background = `
                    radial-gradient(circle at ${positions[0]}% ${positions[1]}%, rgba(100, 130, 255, 0.08) 0%, transparent 30%),
                    radial-gradient(circle at ${positions[2]}% ${positions[3]}%, rgba(150, 180, 255, 0.06) 0%, transparent 30%),
                    radial-gradient(circle at ${positions[4]}% ${positions[5]}%, rgba(120, 150, 255, 0.05) 0%, transparent 30%),
                    radial-gradient(circle at ${positions[6]}% ${positions[7]}%, rgba(180, 200, 255, 0.04) 0%, transparent 30%)
                `;
            }, 10000);
        }

        console.log(`💫 ${lightBeams.length} light beam(s) enhanced`);
    }
    initEnhancedLightBeams();

    // ========================
    // INTERACTIVE EFFECTS
    // ========================
    function initInteractiveEffects() {
        // Button ripple effects
        const buttons = document.querySelectorAll('.btn, .nav-btn, .carousel-prev, .carousel-next');
        
        buttons.forEach(btn => {
            btn.addEventListener('click', function(e) {
                // Ripple effect
                const ripple = document.createElement('span');
                ripple.className = 'gold-ripple';
                
                const rect = this.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                ripple.style.width = ripple.style.height = size + 'px';
                ripple.style.left = x + 'px';
                ripple.style.top = y + 'px';
                
                this.appendChild(ripple);
                
                // Remove ripple after animation
                setTimeout(() => {
                    ripple.remove();
                }, 600);
            });
        });

        // Enhanced hover effects for moments
        const moments = document.querySelectorAll('.moment');
        moments.forEach(moment => {
            moment.addEventListener('mouseenter', () => {
                moment.style.transform = 'translateY(-5px) scale(1.02)';
            });
            
            moment.addEventListener('mouseleave', () => {
                moment.style.transform = 'translateY(0) scale(1)';
            });
        });

        console.log("🎭 Interactive effects initialized");
    }
    initInteractiveEffects();

    // ========================
    // PERFORMANCE OPTIMIZATIONS
    // ========================
    function initPerformance() {
        // Lazy load images
        const images = document.querySelectorAll('img');
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src || img.src;
                    img.classList.add('loaded');
                    observer.unobserve(img);
                }
            });
        });

        images.forEach(img => {
            if (img.complete) {
                img.classList.add('loaded');
            } else {
                img.addEventListener('load', () => {
                    img.classList.add('loaded');
                });
            }
            imageObserver.observe(img);
        });

        // Debounced scroll events
        let scrollTimeout;
        window.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                // Scroll-based effects here
            }, 100);
        }, { passive: true });

        console.log("⚡ Performance optimizations applied");
    }
    initPerformance();

    // ========================
    // ERROR HANDLING
    // ========================
    function initErrorHandling() {
        // Image error handling
        document.querySelectorAll('img').forEach(img => {
            img.addEventListener('error', function() {
                console.warn(`Image failed to load: ${this.src}`);
                this.style.background = 'linear-gradient(135deg, #2d3746, #1a202c)';
                this.alt = 'Image coming soon';
            });
        });

        // Video error handling
        const video = document.querySelector('.bg-video');
        if (video) {
            video.addEventListener('error', () => {
                console.warn('Background video failed to load');
                document.body.style.background = 'linear-gradient(135deg, #0a0a1a, #1a1a2e)';
            });
        }

        window.addEventListener('error', (e) => {
            console.error('Script error:', e.error);
        });

        console.log("🛡️ Error handling initialized");
    }
    initErrorHandling();

    console.log("🎉 All Malume Nico features initialized successfully!");
});

// Fallback for carousels
setTimeout(() => {
    const carousels = document.querySelectorAll('.fade-carousel');
    carousels.forEach(container => {
        const activeSlide = container.querySelector('.carousel-slide.active');
        if (!activeSlide) {
            const firstSlide = container.querySelector('.carousel-slide');
            const firstIndicator = container.querySelector('.carousel-indicator');
            if (firstSlide) firstSlide.classList.add('active');
            if (firstIndicator) firstIndicator.classList.add('active');
            console.log("🔄 Carousel fallback applied");
        }
    });
}, 3000);