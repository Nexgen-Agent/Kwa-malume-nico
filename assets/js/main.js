/* Malume Nico - Main JavaScript */
document.addEventListener("DOMContentLoaded", function() {
    console.log("Malume Nico - DOM loaded");

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
    // HERO TEXT ROTATION
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

        // Show first one immediately
        show();

        // Rotate every 3.8 seconds
        setInterval(() => {
            i = (i + 1) % swaps.length;
            show();
        }, 3800);
    }
    initHeroRotation();

    // ========================
    // BUTTON EFFECTS
    // ========================
    function initButtonEffects() {
        const buttons = document.querySelectorAll('.btn');

        buttons.forEach(btn => {
            const handler = (e) => {
                // Remove and re-add glow effect
                btn.classList.remove('glow-press');
                void btn.offsetWidth; // Trigger reflow
                btn.classList.add('glow-press');

                // Create ripple effect
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
    initButtonEffects();

    // ========================
    // SCROLLING RAILS
    // ========================
    function initScrollingRails() {
        const moments = document.querySelectorAll('.moment');

        moments.forEach(section => {
            const wrap = section.querySelector('.rail-wrap');
            const rail = section.querySelector('.rail');
            const left = section.querySelector('.arrow.left');
            const right = section.querySelector('.arrow.right');

            if (!rail || !left || !right) return;

            const SCROLL = () => Math.max(rail.clientWidth, 260) * 0.6;

            // Arrow click handlers
            left.addEventListener('click', () => {
                section.classList.add('swipe-glow');
                rail.scrollBy({ left: -SCROLL(), behavior: 'smooth' });
            });

            right.addEventListener('click', () => {
                section.classList.add('swipe-glow');
                rail.scrollBy({ left: SCROLL(), behavior: 'smooth' });
            });

            // Remove glow after scrolling
            rail.addEventListener('scroll', () => {
                clearTimeout(rail._glowT);
                rail._glowT = setTimeout(() => {
                    section.classList.remove('swipe-glow');
                }, 400);
            }, { passive: true });

            // Drag to scroll functionality
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

                // Add tilt effect during drag
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
    initScrollingRails();

    // ========================
    // FADE CAROUSELS
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
            if (!this.slides.length) return;

            this.showSlide(this.currentIndex);

            // Event listeners
            if (this.prevBtn) this.prevBtn.addEventListener('click', () => this.prev());
            if (this.nextBtn) this.nextBtn.addEventListener('click', () => this.next());

            // Indicator clicks
            this.indicators.forEach((indicator, index) => {
                indicator.addEventListener('click', () => this.goToSlide(index));
            });

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
            new FadeCarousel(container);
        });
    }
    initCarousels();

    // ========================
// LIQUID LIGHT BEAM EFFECTS
// ========================
function initLiquidLight() {
    console.log("Initializing liquid light effects...");
    
    // Add enhanced classes for water effects
    document.querySelectorAll('.glass.water').forEach(glass => {
        glass.classList.add('enhanced-water');
    });

    document.querySelectorAll('.btn.gold').forEach(btn => {
        btn.classList.add('enhanced');
    });

    // Initialize light beams with random delays and enhanced performance
    const lightOverlay = document.querySelector('.liquid-light-overlay');
    if (lightOverlay) {
        optimizeLightBeams(lightOverlay);
        setupLightBeamInteractions();
    }

    // Adjust for reduced motion preference
    handleReducedMotion();

    // Setup resize handler for responsive light beams
    setupLightBeamResizeHandler();

    console.log("Liquid light effects initialized");
}

function optimizeLightBeams(container) {
    const beams = container.querySelectorAll('.light-beam');
    
    beams.forEach((beam, index) => {
        // Randomize animation delays for more natural effect
        const randomDelay = Math.random() * 8;
        beam.style.animationDelay = `${randomDelay}s`;
        
        // Add performance optimizations
        beam.style.willChange = 'transform, opacity';
        beam.style.backfaceVisibility = 'hidden';
        beam.style.transform = 'translateZ(0)';
        
        // Add data attributes for tracking
        beam.setAttribute('data-beam-index', index);
        beam.setAttribute('data-animation-state', 'running');
    });

    // Add mutation observer to handle visibility changes
    setupBeamVisibilityObserver(container);
}

function setupLightBeamInteractions() {
    // Pause beams when user interacts with important content
    const interactiveElements = document.querySelectorAll('.moment, .carousel-container, .btn');
    
    interactiveElements.forEach(element => {
        element.addEventListener('mouseenter', () => {
            reduceBeamIntensity(0.3);
        });
        
        element.addEventListener('mouseleave', () => {
            restoreBeamIntensity();
        });
        
        element.addEventListener('touchstart', () => {
            reduceBeamIntensity(0.2);
        }, { passive: true });
        
        element.addEventListener('touchend', () => {
            setTimeout(restoreBeamIntensity, 1000);
        }, { passive: true });
    });

    // Handle page visibility changes (tab switching)
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            pauseBeams();
        } else {
            resumeBeams();
        }
    });
}

function reduceBeamIntensity(factor = 0.5) {
    const beams = document.querySelectorAll('.light-beam');
    beams.forEach(beam => {
        beam.style.opacity = factor;
        beam.style.animationPlayState = 'slow';
    });
}

function restoreBeamIntensity() {
    const beams = document.querySelectorAll('.light-beam');
    beams.forEach(beam => {
        beam.style.opacity = '';
        beam.style.animationPlayState = 'running';
    });
}

function pauseBeams() {
    const beams = document.querySelectorAll('.light-beam');
    beams.forEach(beam => {
        beam.style.animationPlayState = 'paused';
        beam.setAttribute('data-animation-state', 'paused');
    });
}

function resumeBeams() {
    const beams = document.querySelectorAll('.light-beam');
    beams.forEach(beam => {
        beam.style.animationPlayState = 'running';
        beam.setAttribute('data-animation-state', 'running');
    });
}

function handleReducedMotion() {
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    
    if (reducedMotion) {
        console.log("Reduced motion preference detected - adjusting light effects");
        
        const beams = document.querySelectorAll('.light-beam');
        beams.forEach(beam => {
            beam.style.animationDuration = '20s';
            beam.style.opacity = '0.1';
            beam.style.animationTimingFunction = 'linear';
        });

        // Also adjust background caustics
        const backgroundCaustics = document.querySelector('.background-caustics');
        if (backgroundCaustics) {
            backgroundCaustics.style.animationDuration = '30s';
            backgroundCaustics.style.opacity = '0.05';
        }
    }
}

function setupLightBeamResizeHandler() {
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            console.log("Window resized - optimizing light beams");
            optimizeLightBeamsForViewport();
        }, 250);
    });
}

function optimizeLightBeamsForViewport() {
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    const beams = document.querySelectorAll('.light-beam');
    
    // Adjust beam sizes based on viewport
    if (viewportWidth < 768) {
        // Mobile optimization
        beams.forEach(beam => {
            beam.style.height = '80px';
            beam.style.filter = 'blur(12px)';
        });
    } else {
        // Desktop settings
        beams.forEach(beam => {
            beam.style.height = '120px';
            beam.style.filter = 'blur(15px)';
        });
    }
    
    // Adjust beam count for very small screens
    if (viewportWidth < 480) {
        const lightOverlay = document.querySelector('.liquid-light-overlay');
        const existingBeams = lightOverlay.querySelectorAll('.light-beam');
        
        if (existingBeams.length > 2) {
            // Remove extra beams on very small screens
            for (let i = 2; i < existingBeams.length; i++) {
                existingBeams[i].remove();
            }
        }
    }
}

function setupBeamVisibilityObserver(container) {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Beams are visible, ensure they're running
                resumeBeams();
            } else {
                // Beams are not visible, pause to save resources
                pauseBeams();
            }
        });
    }, {
        threshold: 0.1 // Trigger when at least 10% visible
    });

    observer.observe(container);
}

// Enhanced light beam performance monitoring
function monitorLightBeamPerformance() {
    let frameCount = 0;
    let lastTime = performance.now();
    
    function checkPerformance(currentTime) {
        frameCount++;
        
        if (currentTime - lastTime >= 1000) {
            const fps = Math.round((frameCount * 1000) / (currentTime - lastTime));
            
            if (fps < 50) {
                // If FPS is low, reduce beam complexity
                reduceBeamComplexity();
            }
            
            frameCount = 0;
            lastTime = currentTime;
        }
        
        requestAnimationFrame(checkPerformance);
    }
    
    requestAnimationFrame(checkPerformance);
}

function reduceBeamComplexity() {
    const beams = document.querySelectorAll('.light-beam');
    beams.forEach(beam => {
        beam.style.filter = 'blur(8px)';
        beam.style.opacity = '0.4';
    });
}

// Initialize light beams when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Wait a bit longer for light beams to ensure they work
    setTimeout(() => {
        initLiquidLight();
        monitorLightBeamPerformance();
    }, 100);
});

// Fallback for light beams if they don't initialize properly
setTimeout(() => {
    const beams = document.querySelectorAll('.light-beam');
    const anyBeamsAnimated = document.querySelector('.light-beam[style*="animation-delay"]');
    
    if (beams.length > 0 && !anyBeamsAnimated) {
        console.log("Light beams not animated - applying fallback");
        initLiquidLight();
    }
}, 2000);

// Export functions for potential manual control
window.LightBeamController = {
    init: initLiquidLight,
    pause: pauseBeams,
    resume: resumeBeams,
    reduceIntensity: reduceBeamIntensity,
    restoreIntensity: restoreBeamIntensity
};

console.log("Light beam JavaScript loaded");

    // ========================
    // BACKGROUND VIDEO
    // ========================
    function initBackgroundVideo() {
        const video = document.querySelector('.bg-video');
        if (video && video.paused) {
            video.play().catch(() => {
                console.log("Video autoplay prevented");
            });
        }
    }
    window.addEventListener('load', initBackgroundVideo);

    // ========================
    // ERROR HANDLING FOR IMAGES
    // ========================
    function handleImageErrors() {
        document.querySelectorAll('.card img').forEach(img => {
            img.addEventListener('error', () => {
                img.style.background = '#222';
                img.alt = 'Photo coming soon';
            });
        });
    }
    handleImageErrors();

    console.log("All JavaScript features initialized");
});

// Fallback for slow loading elements
setTimeout(() => {
    // Re-initialize carousels if they didn't load properly
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