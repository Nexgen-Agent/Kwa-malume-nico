// Malume Nico - Web Components Replacement for JavaScript
class MalumeLoader extends HTMLElement {
    connectedCallback() {
        setTimeout(() => {
            this.style.opacity = '0';
            setTimeout(() => {
                this.style.display = 'none';
            }, 600);
        }, 1500);
    }
}

class MalumeHero extends HTMLElement {
    connectedCallback() {
        this.texts = [
            "Welcome Kwa Malume-Nico",
            "The Best Kota in Town", 
            "Come and Chill With Us"
        ];
        this.currentIndex = 0;
        this.element = this.querySelector('h2');
        this.startRotation();
    }

    startRotation() {
        setInterval(() => {
            this.currentIndex = (this.currentIndex + 1) % this.texts.length;
            this.element.textContent = this.texts[this.currentIndex];
        }, 3800);
    }
}

class MalumeCarousel extends HTMLElement {
    connectedCallback() {
        this.slides = Array.from(this.querySelectorAll('.carousel-slide'));
        this.indicators = Array.from(this.querySelectorAll('.carousel-indicator'));
        this.prevBtn = this.querySelector('.carousel-prev');
        this.nextBtn = this.querySelector('.carousel-next');
        
        this.currentIndex = 0;
        this.initCarousel();
    }

    initCarousel() {
        // Set up navigation
        this.prevBtn?.addEventListener('click', () => this.prev());
        this.nextBtn?.addEventListener('click', () => this.next());
        
        // Set up indicators
        this.indicators.forEach((indicator, index) => {
            indicator.addEventListener('click', () => this.goToSlide(index));
        });

        // Auto-play
        this.startAutoPlay();

        // Pause on hover
        this.addEventListener('mouseenter', () => this.stopAutoPlay());
        this.addEventListener('mouseleave', () => this.startAutoPlay());
    }

    showSlide(index) {
        // Hide current
        this.slides[this.currentIndex]?.classList.remove('active');
        this.indicators[this.currentIndex]?.classList.remove('active');

        // Show new
        this.currentIndex = index;
        this.slides[this.currentIndex]?.classList.add('active');
        this.indicators[this.currentIndex]?.classList.add('active');
    }

    next() { this.showSlide((this.currentIndex + 1) % this.slides.length); }
    prev() { this.showSlide((this.currentIndex - 1 + this.slides.length) % this.slides.length); }
    goToSlide(index) { this.showSlide(index); }

    startAutoPlay() {
        this.stopAutoPlay();
        this.autoPlayInterval = setInterval(() => this.next(), 4000);
    }

    stopAutoPlay() {
        if (this.autoPlayInterval) {
            clearInterval(this.autoPlayInterval);
            this.autoPlayInterval = null;
        }
    }
}

class MalumeButton extends HTMLElement {
    connectedCallback() {
        this.addEventListener('click', this.createRipple.bind(this));
    }

    createRipple(event) {
        // Remove and re-add glow effect
        this.classList.remove('glow-press');
        void this.offsetWidth;
        this.classList.add('glow-press');

        // Create ripple
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height) * 1.15;
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        const ripple = document.createElement('span');
        ripple.className = 'gold-ripple';
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';

        this.appendChild(ripple);
        ripple.addEventListener('animationend', () => ripple.remove());
    }
}

class MalumeRail extends HTMLElement {
    connectedCallback() {
        this.wrap = this.querySelector('.rail-wrap');
        this.rail = this.querySelector('.rail');
        this.leftArrow = this.querySelector('.arrow.left');
        this.rightArrow = this.querySelector('.arrow.right');

        if (!this.rail || !this.leftArrow || !this.rightArrow) return;

        this.initRail();
    }

    initRail() {
        const scrollAmount = () => Math.max(this.rail.clientWidth, 260) * 0.6;

        this.leftArrow.addEventListener('click', () => {
            this.classList.add('swipe-glow');
            this.rail.scrollBy({ left: -scrollAmount(), behavior: 'smooth' });
        });

        this.rightArrow.addEventListener('click', () => {
            this.classList.add('swipe-glow');
            this.rail.scrollBy({ left: scrollAmount(), behavior: 'smooth' });
        });

        this.rail.addEventListener('scroll', () => {
            clearTimeout(this.rail._glowT);
            this.rail._glowT = setTimeout(() => {
                this.classList.remove('swipe-glow');
            }, 400);
        });

        // Drag functionality
        this.initDrag();
    }

    initDrag() {
        let isDown = false, startX = 0, startLeft = 0;

        this.rail.addEventListener('pointerdown', (e) => {
            isDown = true;
            this.rail.setPointerCapture(e.pointerId);
            startX = e.clientX;
            startLeft = this.rail.scrollLeft;
            this.classList.add('swipe-glow');
        });

        this.rail.addEventListener('pointermove', (e) => {
            if (!isDown) return;
            const dx = e.clientX - startX;
            this.rail.scrollLeft = startLeft - dx;
            
            const tilt = Math.max(-1, Math.min(1, dx / 80));
            if (this.wrap) this.wrap.style.transform = `perspective(1200px) rotateY(${tilt * 4}deg)`;
        });

        const release = () => {
            if (!isDown) return;
            isDown = false;
            if (this.wrap) this.wrap.style.transform = "";
            setTimeout(() => this.classList.remove('swipe-glow'), 420);
        };

        this.rail.addEventListener('pointerup', release);
        this.rail.addEventListener('pointercancel', release);
    }
}

class MalumeBackgroundVideo extends HTMLElement {
    connectedCallback() {
        const video = document.querySelector('.bg-video');
        if (video && video.paused) {
            video.play().catch(() => {
                console.log("Video autoplay prevented");
            });
        }
    }
}

class MalumeLightBeams extends HTMLElement {
    connectedCallback() {
        // Add enhanced classes
        document.querySelectorAll('.glass.water').forEach(glass => {
            glass.classList.add('enhanced-water');
        });

        document.querySelectorAll('.btn.gold').forEach(btn => {
            btn.classList.add('enhanced');
        });

        // Randomize light beams
        document.querySelectorAll('.light-beam').forEach((beam, index) => {
            beam.style.animationDelay = `${Math.random() * 5}s`;
        });

        // Reduced motion support
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            document.querySelectorAll('.light-beam').forEach(beam => {
                beam.style.animationDuration = '20s';
                beam.style.opacity = '0.1';
            });
        }
    }
}

// Register all custom elements
customElements.define('malume-loader', MalumeLoader);
customElements.define('malume-hero', MalumeHero);
customElements.define('malume-carousel', MalumeCarousel);
customElements.define('malume-button', MalumeButton);
customElements.define('malume-rail', MalumeRail);
customElements.define('malume-bg-video', MalumeBackgroundVideo);
customElements.define('malume-light-beams', MalumeLightBeams);

// Initialize everything when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log("Malume Nico Web Components initialized");
    
    // Convert existing elements to web components
    convertToWebComponents();
});

function convertToWebComponents() {
    // Convert loader
    const loader = document.getElementById('loader-overlay');
    if (loader) loader.setAttribute('is', 'malume-loader');

    // Convert hero section
    const heroSection = document.querySelector('#welcome .moment-head');
    if (heroSection) heroSection.setAttribute('is', 'malume-hero');

    // Convert carousels
    document.querySelectorAll('.fade-carousel').forEach(carousel => {
        carousel.setAttribute('is', 'malume-carousel');
    });

    // Convert buttons
    document.querySelectorAll('.btn').forEach(button => {
        button.setAttribute('is', 'malume-button');
    });

    // Convert rail sections
    document.querySelectorAll('.moment').forEach(moment => {
        if (moment.querySelector('.rail')) {
            moment.setAttribute('is', 'malume-rail');
        }
    });

    // Initialize background video
    document.body.setAttribute('is', 'malume-bg-video');
    
    // Initialize light beams
    document.body.setAttribute('is', 'malume-light-beams');
}

// Error handling for images
document.querySelectorAll('.card img, .carousel-slide img').forEach(img => {
    img.addEventListener('error', () => {
        img.style.background = 'linear-gradient(135deg, #333, #555)';
        img.alt = 'Photo coming soon';
    });
});

console.log("Malume Nico Web Components loaded");