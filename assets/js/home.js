/* Malume Nico — Home
   - Shares the same “water glass + gold glow” feel as comments page
   - Vertical sections; each has a horizontal swipe rail
   - Drag to scroll, arrow buttons, 3D lift on cards
   - Performance-friendly: GPU transforms, rAF batching, lazy images
*/

const $ = (s, c=document) => c.querySelector(s);
const $$ = (s, c=document) => Array.from(c.querySelectorAll(s));

// ---------- Hero rotating title ----------
(function rotateHero(){
  const swaps = $$('.hero-title .swap');
  if(!swaps.length) return;
  let i = 0;
  function show(){
    swaps.forEach((el,idx)=> el.classList.toggle('active', idx === i));
    i = (i + 1) % swaps.length;
  }
  show();
  setInterval(show, 3800);
})();

// ---------- Button gold ripple ----------
(function pressGlow(){
  $$('.btn').forEach(btn=>{
    const handler = (e)=>{
      // This stops the browser from immediately following the link
      e.preventDefault();

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

      // Listen for the end of the ripple animation
      r.addEventListener('animationend', ()=> {
        r.remove();
        // If the element is a link, manually navigate to the href
        if (btn.tagName === 'A' && btn.href) {
            window.location.href = btn.href;
        }
      });
    };
    btn.addEventListener('click', handler);
    btn.addEventListener('touchstart', handler, {passive:false});
  });
})();

// ---------- Rails: arrows + drag-to-scroll + swipe glow ----------
function setupRail(section){
  const wrap = section.querySelector('.rail-wrap');
  const rail = section.querySelector('.rail');
  const left = section.querySelector('.arrow.left');
  const right = section.querySelector('.arrow.right');

  const SCROLL = () => Math.max(rail.clientWidth, 260) * 0.6;

  left.addEventListener('click', ()=> { section.classList.add('swipe-glow'); rail.scrollBy({left: -SCROLL(), behavior:'smooth'}); });
  right.addEventListener('click', ()=> { section.classList.add('swipe-glow'); rail.scrollBy({left:  SCROLL(), behavior:'smooth'}); });
  rail.addEventListener('scroll', ()=> { /* remove glow after motion */ clearTimeout(rail._glowT); rail._glowT = setTimeout(()=>section.classList.remove('swipe-glow'), 400); }, {passive:true});

  // Drag to scroll (mouse + touch via Pointer Events)
  let isDown=false, startX=0, startLeft=0;
  rail.addEventListener('pointerdown', e=>{
    isDown=true; rail.setPointerCapture(e.pointerId);
    startX=e.clientX; startLeft=rail.scrollLeft; section.classList.add('swipe-glow');
  });
  rail.addEventListener('pointermove', e=>{
    if(!isDown) return;
    const dx = e.clientX - startX;
    rail.scrollLeft = startLeft - dx;
    // mini 3D tilt
    const tilt = Math.max(-1, Math.min(1, dx/80));
    wrap.style.transform = `perspective(1200px) rotateY(${tilt*4}deg)`;
  });
  const release = e=>{
    if(!isDown) return;
    isDown=false; wrap.style.transform = '';
    setTimeout(()=>section.classList.remove('swipe-glow'), 420);
  };
  rail.addEventListener('pointerup', release);
  rail.addEventListener('pointercancel', release);
}

// Init all rails
$$('.moment').forEach(setupRail);

// ---------- Lazy load guard (if images missing, avoid console noise) ----------
$$('.card').forEach(img=>{
  img.addEventListener('error', ()=> { img.style.background = '#222'; img.alt = 'Photo coming soon'; });
});

// ---------- Ensure background video starts ----------
window.addEventListener('load', ()=>{
  const v = $('.bg-video');
  if (v && v.paused) v.play().catch(()=>{});
});

document.addEventListener('DOMContentLoaded', () => {
  const loaderOverlay = document.getElementById('loader-overlay');
  const liquid = document.querySelector('.liquid');
  const body = document.body;

  // Add a class to the body to prevent interaction
  body.classList.add('loading');
  
  // Calculate duration based on network connection (downlink speed)
  const networkInfo = navigator.connection;
  let duration = 3000; // Default duration for slow networks

  if (networkInfo && networkInfo.downlink) {
    // Make the animation faster for faster networks
    // For example, 1000ms for fast connections (>5Mbps)
    duration = 1500 / networkInfo.downlink; 
  }

  // Set the animation duration dynamically
  liquid.style.transitionDuration = `${duration}ms`;

  // Start the filling animation
  liquid.style.height = '100%';

  window.addEventListener('load', () => {
    // The page is fully loaded, wait for the animation to complete
    setTimeout(() => {
      // Remove blur and loader
      body.style.filter = 'none';
      loaderOverlay.style.opacity = '0';
      
      // After transition, remove from DOM and allow interaction
      setTimeout(() => {
        loaderOverlay.style.display = 'none';
        body.classList.remove('loading');
      }, 500); 
    }, duration);
  });
});

