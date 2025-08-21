/* ===========================
   Malume Nico — Menu (Interactive Order)
   - Functionalities for a dynamic, user-friendly ordering experience.
   - Shares core animations from home.js for consistent vibe.
=========================== */

const $ = (s, c=document) => c.querySelector(s);
const $$ = (s, c=document) => Array.from(c.querySelectorAll(s));

// ---------- Button gold ripple and glow press ----------
// (Copied directly from home.js)
(function pressGlow(){
  $$('.btn').forEach(btn=>{
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

// ---------- Rails: arrows + drag-to-scroll + swipe glow ----------
// (Adapted from home.js to use .menu-rail-wrap and .menu-rail classes)
function setupRail(section){
  const wrap = section.querySelector('.menu-rail-wrap');
  const rail = section.querySelector('.menu-rail');
  const left = section.querySelector('.arrow.left');
  const right = section.querySelector('.arrow.right');

  const SCROLL = () => Math.max(rail.clientWidth, 260) * 0.6;

  left.addEventListener('click', ()=> { section.classList.add('swipe-glow'); rail.scrollBy({left: -SCROLL(), behavior:'smooth'}); });
  right.addEventListener('click', ()=> { section.classList.add('swipe-glow'); rail.scrollBy({left:  SCROLL(), behavior:'smooth'}); });
  rail.addEventListener('scroll', ()=> { clearTimeout(rail._glowT); rail._glowT = setTimeout(()=>section.classList.remove('swipe-glow'), 400); }, {passive:true});

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
$$('.menu-section').forEach(setupRail);

// ---------- Lazy load guard ----------
// (Adapted for the new .food-card class)
$$('.food-card img').forEach(img=>{
  img.addEventListener('error', ()=> { img.style.background = '#222'; img.alt = 'Photo coming soon'; });
});

// ---------- Ensure background video starts ----------
window.addEventListener('load', ()=>{
  const v = $('.bg-video');
  if (v && v.paused) v.play().catch(()=>{});
});

// ===== MENU PAGE SPECIFIC LOGIC GOES BELOW =====
// (The code for the basket, quantity, and checkout process will be added here)
