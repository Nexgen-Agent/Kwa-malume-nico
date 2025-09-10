/* ===========================
   Malume Nico — Comments (Live Vibes)
   - iPhone-style translucent “water” UI
   - 10s looping venue video behind
   - IG Live style comments ticker
   - Floating ❤️ hearts on new comments
   - Email handoff (no backend required)
   - Gold press ripple on buttons
   - Performance tuned (GPU transforms, rAF batching)
=========================== */

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

const $ = (s, c=document) => c.querySelector(s);
const $$ = (s, c=document) => Array.from(c.querySelectorAll(s));
const prefersReduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

// Elements
const stage = $('#stage');
const composer = $('#composer');
const nameInput = $('#name');
const commentInput = $('#comment');
const emailBtn = $('#emailBtn');
const sendBtn = $('#sendBtn');
const heartsLayer = $('#hearts');

// ---------- Press ripple / gold halo ----------
(function pressGlow(){
  const handler = (e)=>{
    const btn = e.currentTarget;
    btn.classList.remove('glow-press');
    void btn.offsetWidth; // restart CSS anim
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
    r.addEventListener('animationend', ()=> r.remove());
  };
  $$('.btn').forEach(b=>{
    b.addEventListener('click', handler);
    b.addEventListener('touchstart', handler, {passive:true});
  });
})();

// ---------- Hearts pop ----------
function popHeart(x, y){
  const h = document.createElement('div');
  h.className = 'heart';
  h.textContent = ['❤️','💛','💖','🧡'][Math.floor(Math.random()*4)];
  const jitterX = (Math.random() * 40) - 20;
  h.style.left = (x + jitterX) + 'px';
  h.style.top = (y - 20) + 'px';
  heartsLayer.appendChild(h);
  h.addEventListener('animationend', ()=> h.remove());
}

// ---------- Comment bubble creation ----------
function createBubble(user, text){
  const wrap = document.createElement('div');
  wrap.className = 'bubble';
  const u = document.createElement('span'); u.className='user'; u.textContent = user;
  const t = document.createElement('span'); t.className='text'; t.textContent = text;
  wrap.append(u, t);
  return wrap;
}

// ---------- Add bubble to stage (with reveal) ----------
function addToStage(user, text){
  const bubble = createBubble(user, text);
  bubble.style.marginBottom = '6px'; // Add 6px spacing
  stage.appendChild(bubble);

  // trigger reveal
  requestAnimationFrame(()=> bubble.classList.add('show'));
}

// ---------- Simulated live feed (can delete when backend exists) ----------
const seedUsers = ['Thando','Lerato','Sizwe','Nico','Aisha','Sipho','Naledi','Bongani','Zola','Mpho'];
const seedTexts = [
  'This place is pure joy!',
  'Unity vibes 🔥',
  'Best kota in the city!',
  'We’re bringing the whole squad!',
  'The energy is unmatched.',
  'Birthday here was unforgettable!',
  'Love the golden glow ✨',
  'Come and chill with us 😍',
  'Family time felt special.',
  'Weekend sorted!'
];

function randomSeed(){
  const name = seedUsers[Math.floor(Math.random()*seedUsers.length)];
  const text = seedTexts[Math.floor(Math.random()*seedTexts.length)];
  addToStage(name, text);
  // random hearts burst near the bottom of the stage
  const rect = stage.getBoundingClientRect();
  const x = rect.left + 40 + Math.random() * 120;
  const y = rect.bottom - 30 - Math.random() * 60;
  if(!prefersReduced) popHeart(x, y);
}
let seedTimer = setInterval(randomSeed, 1500); // 1.5 seconds between each comment
window.addEventListener('blur', ()=> clearInterval(seedTimer));
window.addEventListener('focus', ()=> seedTimer = setInterval(randomSeed, 1500));

// ---------- Composer submit ----------
composer.addEventListener('submit', (e)=>{
  e.preventDefault();
  const user = nameInput.value.trim() || 'Guest';
  const text = commentInput.value.trim();
  if(!text) return;

  addToStage(user, text);

  // hearts where the send button is
  const rect = sendBtn.getBoundingClientRect();
  popHeart(rect.left + rect.width/2, rect.top);

  // optional: prepare email handoff in background
  prepareMailto(user, text);

  commentInput.value = '';
  commentInput.focus();
});

// ---------- Email handoff (no backend required) ----------
function prepareMailto(user, text){
  const subject = encodeURIComponent('Malume Nico — Live Comment');
  const body = encodeURIComponent(`Name: ${user}\nComment: ${text}\n\nSource: Comments Page`);
  const to = 'hello@malumenico.co.za'; // change to your inbox
  emailBtn.href = `mailto:${to}?subject=${subject}&body=${body}`;
}
emailBtn.addEventListener('click', ()=>{
  // extra hearts on email click
  const r = emailBtn.getBoundingClientRect();
  popHeart(r.left + r.width/2, r.top);
});

// ---------- Accessibility & quality-of-life ----------
(function focusRing(){
  function add(){ document.documentElement.classList.add('kb'); }
  function remove(){ document.documentElement.classList.remove('kb'); }
  window.addEventListener('keydown', e=>{ if(e.key === 'Tab') add(); }, { once:true });
  window.addEventListener('mousedown', remove);
})();

// ---------- Optional: ensure video starts quickly ----------
window.addEventListener('load', ()=>{
  const v = document.querySelector('.bg-video');
  if (v && v.paused) v.play().catch(()=>{ /* ignored */ });
});

function addToStage(user, text){
  const bubble = createBubble(user, text);
  bubble.style.marginBottom = '12px'; // This line adds vertical space
  stage.appendChild(bubble);

  // trigger reveal
  requestAnimationFrame(()=> bubble.classList.add('show'));
}
