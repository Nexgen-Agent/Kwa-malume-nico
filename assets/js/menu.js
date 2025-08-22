/* Config */
const FREE_DELIVERY_THRESHOLD = 280; // R
const DELIVERY_FEE = 35;             // R (used only if below threshold)

/* Simple menu data (replace images/prices as needed) */
const MENU = [
  { id: 'bk_steak', title: 'TITANIC FAMILY KOTA', price: 100, img: 'assets/img/menu/1.jpg' },
  { id: 'bk_wings', title: 'DUNKED WINGS (6pc)', price: 75, img: 'assets/img/menu/2.jpg' },
  { id: 'bk_burger', title: 'BUGATTI KOTA', price: 60, img: 'assets/img/menu/3.jpg' },
  { id: 'bk_ribs', title: 'BURGER', price: 60, img: 'assets/img/menu/4.jpg' },
  { id: 'bk_salad', title: 'RANGE ROVER KOTA', price: 50, img: 'assets/img/menu/5.jpg' },
  { id: 'bk_platter', title: 'DAGWOOD', price: 45, img: 'assets/img/menu/6.jpg' },
  { id: 'bk_burger', title: 'BMW M4 KOTA', price: 40, img: 'assets/img/menu/7.jpg' },
  { id: 'bk_ribs', title: 'DESSERT', price: 40, img: 'assets/img/menu/8.jpg' },
  { id: 'bk_salad', title: 'OMODA KOTA', price: 35, img: 'assets/img/menu/9.jpg' },
  { id: 'bk_platter', title: 'HAVAL KOTA', price: 30, img: 'assets/img/menu/10.jpg' },
];


/* State */
const cart = new Map(); // id -> {id, title, price, qty}

/* Helpers */
const qs = (s, root=document) => root.querySelector(s);
const qsa = (s, root=document) => [...root.querySelectorAll(s)];
const formatR = n => `R${n.toFixed(2)}`;

function addToCart(item) {
  const existing = cart.get(item.id) || { ...item, qty: 0 };
  existing.qty += 1;
  cart.set(item.id, existing);
  refreshCartBar();
}

function changeQty(id, delta) {
  const it = cart.get(id);
  if (!it) return;
  it.qty += delta;
  if (it.qty <= 0) cart.delete(id);
  refreshCartBar();
  renderCartList();
}

function cartTotals() {
  let subtotal = 0;
  cart.forEach(i => subtotal += i.price * i.qty);
  const qualifiesFree = subtotal >= FREE_DELIVERY_THRESHOLD;
  const deliveryFee = qualifiesFree ? 0 : DELIVERY_FEE;
  return { subtotal, qualifiesFree, deliveryFee, total: subtotal + deliveryFee };
}

function refreshCartBar() {
  const count = [...cart.values()].reduce((a,b)=>a+b.qty,0);
  qs('#cart-count').textContent = `${count} item${count===1?'':'s'}`;
  qs('#cart-total').textContent = formatR(cartTotals().total);
  qs('#open-cart').disabled = count === 0;
}

/* Render menu rail */
function renderRail() {
  const rail = qs('#rail');
  rail.innerHTML = '';
  MENU.forEach(m => {
    const card = document.createElement('div');
    card.className = 'food-card';
    card.innerHTML = `
      <img src="${m.img}" alt="${m.title}"/>
      <div class="food-body">
        <div class="food-title">${m.title}</div>
        <div class="food-actions">
          <span class="food-price">${formatR(m.price)}</span>
          <button class="btn gold add-btn" data-id="${m.id}">+ Add</button>
        </div>
      </div>
    `;
    rail.appendChild(card);
  });
  rail.addEventListener('click', e => {
    const btn = e.target.closest('.add-btn');
    if (!btn) return;
    const item = MENU.find(i => i.id === btn.dataset.id);
    addToCart(item);
  });
}

/* Rail arrows */
function setupRailArrows() {
  const rail = qs('#rail');
  const left = qs('.arrow.left');
  const right = qs('.arrow.right');
  const step = 320; // px per click
  left.addEventListener('click', () => rail.scrollBy({ left: -step, behavior: 'smooth' }));
  right.addEventListener('click', () => rail.scrollBy({ left: step, behavior: 'smooth' }));
}

/* Drawer controls */
function openDrawer(id){ const d=qs(id); d.setAttribute('aria-hidden','false'); }
function closeDrawer(id){ const d=qs(id); d.setAttribute('aria-hidden','true'); }

/* Cart drawer content */
function renderCartList() {
  const list = qs('#cart-list');
  const { subtotal, qualifiesFree, deliveryFee, total } = cartTotals();

  // Totals
  qs('#subtotal').textContent = formatR(subtotal);
  qs('#delivery-row').hidden = qualifiesFree;
  qs('#delivery-fee').textContent = formatR(deliveryFee);
  qs('#grand-total').textContent = formatR(total);

  // Free delivery hint visibility
  qs('#free-delivery-hint').style.display = 'block';

  // Items
  list.innerHTML = '';
  if (cart.size === 0) {
    list.innerHTML = `<p class="hint">Your cart is empty. Add some meals from the menu.</p>`;
    qs('#continue-to-mode').disabled = true;
    return;
  }
  qs('#continue-to-mode').disabled = false;

  cart.forEach(item => {
    const row = document.createElement('div');
    row.className = 'cart-item';
    row.innerHTML = `
      <div>
        <div class="item-title">${item.title}</div>
        <div class="summary-note">${formatR(item.price)} each</div>
      </div>
      <div class="item-qty">
        <button class="qty-btn" data-id="${item.id}" data-d="-1">−</button>
        <strong>${item.qty}</strong>
        <button class="qty-btn" data-id="${item.id}" data-d="1">+</button>
        <div class="item-price" style="margin-left:10px">${formatR(item.price*item.qty)}</div>
      </div>
    `;
    list.appendChild(row);
  });

  list.addEventListener('click', e=>{
    const btn = e.target.closest('.qty-btn');
    if(!btn) return;
    changeQty(btn.dataset.id, Number(btn.dataset.d));
  }, { once:true }); // rebind each render
}

/* Mode step behavior */
let selectedMode = null;
let sharedCoords = null;

function setupModeStep(){
  // choose mode
  qsa('.mode-card').forEach(btn=>{
    btn.addEventListener('click', ()=>{
      selectedMode = btn.dataset.mode; // dinein | pickup | delivery
      // reset visibility
      qs('#form-dinein').hidden = true;
      qs('#form-contact').hidden = true;
      qs('#delivery-only').hidden = true;

      if(selectedMode==='dinein'){
        qs('#form-dinein').hidden = false;
      } else {
        qs('#form-contact').hidden = false;
        if(selectedMode==='delivery'){
          qs('#delivery-only').hidden = false;
        }
      }
    });
  });

  // share live location (optional)
  qs('#share-location').addEventListener('click', async ()=>{
    const status = qs('#loc-status');
    status.textContent = 'Requesting location...';
    if(!('geolocation' in navigator)){
      status.textContent = 'Location not supported on this device.';
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos)=>{
        sharedCoords = {
          lat: pos.coords.latitude.toFixed(6),
          lng: pos.coords.longitude.toFixed(6)
        };
        status.textContent = `Location attached (${sharedCoords.lat}, ${sharedCoords.lng})`;
      },
      (err)=>{
        status.textContent = 'Unable to get location.';
        console.error(err);
      },
      { enableHighAccuracy:true, timeout:10000, maximumAge:0 }
    );
  });

  // to summary (dine-in)
  qs('#to-summary-dinein').addEventListener('click', ()=>{
    const table = qs('#table-number').value.trim();
    if(!table){ qs('#table-number').focus(); return; }
    showSummary({ mode:'Dine-In', table });
  });

  // to summary (pickup/delivery)
  qs('#to-summary-contact').addEventListener('click', ()=>{
    const phone = qs('#contact-phone').value.trim();
    const email = qs('#contact-email').value.trim();
    if(!phone){ qs('#contact-phone').focus(); return; }
    if(!email){ qs('#contact-email').focus(); return; }
    const payload = { mode: selectedMode==='pickup' ? 'Pickup' : 'Delivery', phone, email };
    if(selectedMode==='delivery'){
      payload.address = qs('#address').value.trim();
      payload.coords = sharedCoords;
    }
    showSummary(payload);
  });
}

/* Show summary */
function showSummary(meta){
  const sb = qs('#summary-block');
  const { subtotal, qualifiesFree, deliveryFee, total } = cartTotals();

  let itemsHtml = '';
  cart.forEach(i => {
    itemsHtml += `
      <div class="summary-line">
        <span>${i.title} × ${i.qty}</span>
        <strong>${formatR(i.price*i.qty)}</strong>
      </div>`;
  });

  const metaLines = [];
  metaLines.push(`<div class="summary-line"><span>Method</span><strong>${meta.mode}</strong></div>`);
  if(meta.table)  metaLines.push(`<div class="summary-line"><span>Table</span><strong>${meta.table}</strong></div>`);
  if(meta.phone)  metaLines.push(`<div class="summary-line"><span>Phone</span><strong>${meta.phone}</strong></div>`);
  if(meta.email)  metaLines.push(`<div class="summary-line"><span>Email</span><strong>${meta.email}</strong></div>`);
  if(meta.address)metaLines.push(`<div class="summary-line"><span>Address</span><strong>${meta.address||'-'}</strong></div>`);
  if(meta.coords) metaLines.push(`<div class="summary-line"><span>Live Location</span><strong>${meta.coords.lat}, ${meta.coords.lng}</strong></div>`);

  sb.innerHTML = `
    <h4>Items</h4>
    ${itemsHtml || '<p class="hint">Empty.</p>'}
    <hr style="border:none;border-top:1px dashed rgba(255,255,255,.25);margin:10px 0"/>
    ${metaLines.join('')}
    <div style="height:10px"></div>
    <div class="summary-line"><span>Subtotal</span><strong>${formatR(subtotal)}</strong></div>
    <div class="summary-line"><span>Delivery Fee</span><strong>${qualifiesFree?'FREE':formatR(deliveryFee)}</strong></div>
    <div class="summary-line" style="font-weight:900"><span>Total</span><strong>${formatR(total)}</strong></div>
    <p class="hint">Free delivery applies from R${FREE_DELIVERY_THRESHOLD}.</p>
  `;

  // keep meta for "place order"
  qs('#place-order').dataset.meta = JSON.stringify(meta);

  // open summary drawer
  openDrawer('#summary-drawer');
}

/* Init */
document.addEventListener('DOMContentLoaded', ()=>{
  renderRail();
  setupRailArrows();
  refreshCartBar();

  // open/close cart drawer
  qs('#open-cart').addEventListener('click', ()=>{
    renderCartList();
    openDrawer('#cart-drawer');
  });
  qs('#close-cart').addEventListener('click', ()=> closeDrawer('#cart-drawer'));
  qs('#cart-backdrop').addEventListener('click', ()=> closeDrawer('#cart-drawer'));

  // continue to mode
  qs('#continue-to-mode').addEventListener('click', ()=>{
    closeDrawer('#cart-drawer');
    openDrawer('#mode-drawer');
  });
  qs('#close-mode').addEventListener('click', ()=> closeDrawer('#mode-drawer'));
  qs('#mode-backdrop').addEventListener('click', ()=> closeDrawer('#mode-drawer'));

  setupModeStep();

  // summary close
  qs('#close-summary').addEventListener('click', ()=> closeDrawer('#summary-drawer'));
  qs('#summary-backdrop').addEventListener('click', ()=> closeDrawer('#summary-drawer'));

  // place order (front-end demo)
  qs('#place-order').addEventListener('click', ()=>{
    const meta = JSON.parse(qs('#place-order').dataset.meta || '{}');
    console.log('ORDER PLACED', { items:[...cart.values()], ...meta, totals:cartTotals() });

    alert('🔥 Order placed!\n\nCheck the console for payload (ready to POST to backend).');

    // reset flow
    cart.clear();
    refreshCartBar();
    closeDrawer('#summary-drawer');
    closeDrawer('#mode-drawer');
  });
});