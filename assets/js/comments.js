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

const $ = (s, c=document) => c.querySelector(s);
const $$ = (s, c=document) => Array.from(c.querySelectorAll(s));
const prefersReduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

// Elements
const ticker = $('#ticker');
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

// ---------- Add bubble to ticker (with reveal) ----------
function addToTicker(user, text){
  const bubble = createBubble(user, text);
  ticker.appendChild(bubble);
  // keep only last N bubbles
  const maxBubbles = 18;
  while (ticker.children.length > maxBubbles) ticker.removeChild(ticker.firstChild);

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
  addToTicker(name, text);
  // random hearts burst near ticker
  const rect = ticker.getBoundingClientRect();
  const x = rect.left + 40 + Math.random() * 120;
  const y = rect.top + rect.height - 30 - Math.random() * 60;
  if(!prefersReduced) popHeart(x, y);
}
let seedTimer = setInterval(randomSeed, 2200);
window.addEventListener('blur', ()=> clearInterval(seedTimer));
window.addEventListener('focus', ()=> seedTimer = setInterval(randomSeed, 2200));

// ---------- Composer submit ----------
composer.addEventListener('submit', (e)=>{
  e.preventDefault();
  const user = nameInput.value.trim() || 'Guest';
  const text = commentInput.value.trim();
  if(!text) return;

  addToTicker(user, text);

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
