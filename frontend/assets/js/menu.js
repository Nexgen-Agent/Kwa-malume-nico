/* menu.js — scoped: runs only on pages with body.menu-page
   Features:
   - Renders menu items into rails
   - Add / remove / qty controls
   - Dine-in vs Delivery handling
   - Free delivery for orders >= R280
   - Cart drawer UI and small animations (ripple + glow)
*/

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

(function () {
  if (!document.body.classList.contains('menu-page')) return;

  /* ---------- Data ---------- */
  const menuItems = [
    { id: 1, name: "Titanic Family Kota", price: 100, img: "assets/img/menu/1.jpg" },
    { id: 2, name: "Dunked Wings", price: 75, img: "assets/img/menu/2.jpg" },
    { id: 3, name: "Bugatti Kota", price: 60, img: "assets/img/menu/3.jpg" },
    { id: 4, name: "Burger", price: 60, img: "assets/img/menu/4.jpg" },
    { id: 5, name: "Range Rover Kota", price: 50, img: "assets/img/menu/5.jpg" },
    { id: 6, name: "Dagwood", price: 45, img: "assets/img/menu/6.jpg" },
    { id: 7, name: "BMW M4 Kota", price: 40, img: "assets/img/menu/7.jpg" },
    { id: 8, name: "Dessert", price: 40, img: "assets/img/menu/8.jpg" },
    { id: 9, name: "Omoda Kota", price: 35, img: "assets/img/menu/9.jpg" },
    { id: 10, name: "Haval Kota", price: 30, img: "assets/img/menu/10.jpg" }
  ];

  /* ---------- State ---------- */
  let cart = []; // { id, name, price, qty }
  let orderMode = null; // 'dinein' | 'delivery' | null

  /* ---------- Elements ---------- */
  const menuRoot = document.getElementById('menu');
  const btnDine = document.getElementById('btnDineIn');
  const btnDel = document.getElementById('btnDelivery');
  const dineinBlock = document.getElementById('dineinBlock');
  const deliveryBlock = document.getElementById('deliveryBlock');
  const cartCount = document.getElementById('cartCount');
  const cartSummary = document.getElementById('cartSummary');
  const openCartBtn = document.getElementById('openCartBtn');
  const cartDrawer = document.getElementById('cartDrawer');
  const drawerBackdrop = document.getElementById('drawerBackdrop');
  const closeCartBtn = document.getElementById('closeCartBtn');
  const cartList = document.getElementById('cartList');
  const subTotalEl = document.getElementById('subTotal');
  const deliveryFeeEl = document.getElementById('deliveryFee');
  const grandTotalEl = document.getElementById('grandTotal');
  const freeNote = document.getElementById('freeNote');
  const checkoutBtn = document.getElementById('checkoutBtn');
  const clearCartBtn = document.getElementById('clearCartBtn');
  const toastEl = document.getElementById('toast');

  /* ---------- Helpers ---------- */
  function findCartItem(id) { return cart.find(i => i.id === id); }
  function saveState() { /* optional: persist cart to localStorage */ }
  function showToast(text, ms = 1600) {
    toastEl.textContent = text;
    toastEl.classList.add('show');
    toastEl.setAttribute('aria-hidden', 'false');
    setTimeout(() => {
      toastEl.classList.remove('show');
      toastEl.setAttribute('aria-hidden', 'true');
    }, ms);
  }

  /* ---------- Render: menu as single rail (all items) ---------- */
  function renderMenu() {
    // For simplicity we render a single rail "All Items" — you can split into categories later.
    menuRoot.innerHTML = '';
    const railWrap = document.createElement('section');
    railWrap.className = 'food-rail glass water';
    const head = document.createElement('div');
    head.className = 'moment-head';
    head.innerHTML = `<h2>All Kotas & Meals</h2><p class="hint">Tap an item to add. Adjust quantity in cart.</p>`;
    railWrap.appendChild(head);

    const wrap = document.createElement('div');
    wrap.className = 'rail-wrap';

    const left = document.createElement('button');
    left.className = 'arrow left btn';
    left.setAttribute('aria-label', 'Scroll left');
    left.innerHTML = `<svg viewBox="0 0 24 24" width="20" height="20"><path d="M15 4L7 12l8 8" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
    wrap.appendChild(left);

    const rail = document.createElement('div');
    rail.className = 'rail';
    rail.setAttribute('data-section', 'all');

    menuItems.forEach(item => {
      const card = document.createElement('article');
      card.className = 'food-card';

      card.innerHTML = `
        <img loading="lazy" src="${item.img}" alt="${item.name}" />
        <div class="food-body">
          <div>
            <div class="food-title">${item.name}</div>
            <div class="food-price">R${item.price}</div>
          </div>
          <div class="food-actions">
            <div class="qty-chip">Quick add</div>
            <button class="btn gold add-btn" data-id="${item.id}" type="button">Add</button>
          </div>
        </div>
      `;
      rail.appendChild(card);
    });

    wrap.appendChild(rail);

    const right = document.createElement('button');
    right.className = 'arrow right btn';
    right.setAttribute('aria-label', 'Scroll right');
    right.innerHTML = `<svg viewBox="0 0 24 24" width="20" height="20"><path d="M9 4l8 8-8 8" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
    wrap.appendChild(right);

    railWrap.appendChild(wrap);
    menuRoot.appendChild(railWrap);

    // arrow scrolling
    left.addEventListener('click', () => scrollRail(rail, -320));
    right.addEventListener('click', () => scrollRail(rail, +320));

    // add button handlers (delegation)
    rail.addEventListener('click', (e) => {
      const btn = e.target.closest('.add-btn');
      if (!btn) return;
      const id = Number(btn.dataset.id);
      addToCart(id, e);
    });

    // enable horizontal swipe / drag on rail
    makeScrollable(rail);
  }

  function scrollRail(rail, delta) {
    rail.scrollBy({ left: delta, behavior: 'smooth' });
  }

  function makeScrollable(el) {
    // simple drag scrolling for touch/desktop
    let isDown = false, startX, scrollLeft;
    el.addEventListener('pointerdown', (e) => {
      isDown = true;
      el.setPointerCapture(e.pointerId);
      startX = e.clientX;
      scrollLeft = el.scrollLeft;
    });
    el.addEventListener('pointermove', (e) => {
      if (!isDown) return;
      const dx = e.clientX - startX;
      el.scrollLeft = scrollLeft - dx;
    });
    ['pointerup','pointercancel','pointerleave'].forEach(evt => {
      el.addEventListener(evt, () => { isDown = false; });
    });
  }

  /* ---------- Cart logic ---------- */
  function addToCart(id, e) {
    const item = menuItems.find(m => m.id === id);
    if (!item) return;
    const existing = findCartItem(id);
    if (existing) existing.qty++;
    else cart.push({ id: item.id, name: item.name, price: item.price, qty: 1 });

    updateCartUI();

    // small ripple & glow on button
    const btn = (e && e.target) ? e.target.closest('.btn') : null;
    if (btn) {
      pressRipple(btn, e);
      btn.classList.add('glow-press');
      setTimeout(()=>btn.classList.remove('glow-press'), 700);
    }
    showToast(`${item.name} added`);
  }

  function pressRipple(btn, e) {
    if (!btn) return;
    const rect = btn.getBoundingClientRect();
    const x = (e && e.clientX) ? (e.clientX - rect.left) : rect.width/2;
    const y = (e && e.clientY) ? (e.clientY - rect.top) : rect.height/2;
    const r = document.createElement('span');
    r.className = 'gold-ripple';
    r.style.left = x + 'px';
    r.style.top = y + 'px';
    const size = Math.max(rect.width, rect.height) * 1.2;
    r.style.width = r.style.height = size + 'px';
    btn.appendChild(r);
    r.addEventListener('animationend', ()=> r.remove(), { once: true });
  }

  function updateCartUI() {
    // update count & summary
    const totalQty = cart.reduce((s,i) => s + i.qty, 0);
    const subTotal = cart.reduce((s,i) => s + i.price * i.qty, 0);
    cartCount.textContent = totalQty;
    cartSummary.textContent = `R${subTotal} — ${totalQty} item${totalQty !== 1 ? 's' : ''}`;

    // update drawer contents
    renderCartList();
    updateTotals();
  }

  function renderCartList() {
    cartList.innerHTML = '';
    if (cart.length === 0) {
      cartList.innerHTML = `<div class="hint">Cart is empty. Add something delicious.</div>`;
      return;
    }
    cart.forEach((c, idx) => {
      const itemEl = document.createElement('div');
      itemEl.className = 'cart-item';
      itemEl.innerHTML = `
        <div>
          <div class="item-title">${c.name}</div>
          <div class="item-price">R${c.price} each</div>
        </div>
        <div style="text-align:right">
          <div class="item-qty">
            <button class="qty-btn" data-idx="${idx}" data-op="dec">−</button>
            <span style="min-width:28px;display:inline-block;text-align:center">${c.qty}</span>
            <button class="qty-btn" data-idx="${idx}" data-op="inc">+</button>
          </div>
          <div class="item-price" style="margin-top:8px">R${c.price * c.qty}</div>
        </div>
      `;
      cartList.appendChild(itemEl);
    });

    // attach qty listeners
    cartList.querySelectorAll('.qty-btn').forEach(b => {
      b.addEventListener('click', (ev) => {
        const idx = Number(b.dataset.idx);
        const op = b.dataset.op;
        if (op === 'inc') cart[idx].qty++;
        else {
          cart[idx].qty--;
          if (cart[idx].qty <= 0) cart.splice(idx, 1);
        }
        updateCartUI();
      });
    });
  }

  function updateTotals() {
    const subTotal = cart.reduce((s,i) => s + i.price * i.qty, 0);
    subTotalEl.textContent = `R${subTotal}`;

    // delivery logic
    let deliveryFee = 0;
    if (orderMode === 'delivery') {
      deliveryFee = subTotal >= 280 ? 0 : 30; // simple flat fee if below threshold
      deliveryFeeEl.textContent = deliveryFee === 0 ? 'R0' : `R${deliveryFee}`;
      freeNote.textContent = subTotal >= 280 ? '🎉 Free delivery applied' : 'Free delivery on R280+';
      deliveryRowVisibility(true);
    } else {
      deliveryFeeEl.textContent = 'R0';
      deliveryRowVisibility(false);
      freeNote.textContent = 'Dine-in orders do not require delivery';
    }

    const grand = subTotal + (deliveryFee || 0);
    grandTotalEl.textContent = `R${grand}`;
    // small safety: keep aria states
  }

  function deliveryRowVisibility(show) {
    const row = document.getElementById('deliveryRow');
    if (!row) return;
    row.style.display = show ? 'flex' : 'none';
  }

  /* ---------- Drawer controls ---------- */
  openCartBtn.addEventListener('click', () => toggleDrawer(true));
  closeCartBtn.addEventListener('click', () => toggleDrawer(false));
  drawerBackdrop.addEventListener('click', () => toggleDrawer(false));
  clearCartBtn.addEventListener('click', () => {
    cart = [];
    updateCartUI();
    showToast('Cart cleared');
  });

  function toggleDrawer(open) {
    cartDrawer.setAttribute('aria-hidden', (!open).toString());
    if (open) cartDrawer.querySelector('.drawer-panel').focus?.();
  }

  /* ---------- Mode selection ---------- */
  btnDine.addEventListener('click', () => setMode('dinein'));
  btnDel.addEventListener('click', () => setMode('delivery'));

  function setMode(mode) {
    orderMode = mode;
    if (mode === 'dinein') {
      dineinBlock.classList.remove('hidden');
      deliveryBlock.classList.add('hidden');
      btnDine.classList.add('gold');
      btnDel.classList.remove('gold');
    } else {
      deliveryBlock.classList.remove('hidden');
      dineinBlock.classList.add('hidden');
      btnDel.classList.add('gold');
      btnDine.classList.remove('gold');
    }
    updateTotals();
  }

  /* ---------- Checkout ---------- */
  checkoutBtn.addEventListener('click', () => {
    if (cart.length === 0) { showToast('Cart is empty'); return; }

    const subTotal = cart.reduce((s,i) => s + i.price * i.qty, 0);
    if (orderMode === 'dinein') {
      const table = document.getElementById('tableNumber').value.trim();
      if (!table) { showToast('Enter table number'); return; }
      // simulate send
      showToast(`Dine-in order confirmed (Table ${table})`);
      // reset
      cart = []; updateCartUI(); toggleDrawer(false);
    } else if (orderMode === 'delivery') {
      const phone = document.getElementById('phone').value.trim();
      const email = document.getElementById('email').value.trim();
      if (!phone || !email) { showToast('Enter phone & email'); return; }
      // check free delivery threshold (we used 280)
      const deliveryFee = subTotal >= 280 ? 0 : 30;
      const grand = subTotal + deliveryFee;
      showToast(`Order confirmed! Total R${grand}`);
      // here you would POST to backend
      cart = []; updateCartUI(); toggleDrawer(false);
    } else {
      showToast('Select Dine-in or Delivery');
    }
  });

  /* ---------- Init ---------- */
  function init() {
    renderMenu();
    updateCartUI();
    deliveryRowVisibility(false);

    // keyboard accessibility: Esc closes drawer
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') toggleDrawer(false);
    });
  }

  /* ---------- Start ---------- */
  init();

})();

// Get a reference to the rails and arrows
const foodRails = document.querySelectorAll('.rail');
const leftArrows = document.querySelectorAll('.arrow.left');
const rightArrows = document.querySelectorAll('.arrow.right');

// A function to scroll the rail
const scrollRail = (rail, direction) => {
  const cardWidth = rail.querySelector('.food-card').offsetWidth;
  const scrollAmount = cardWidth * direction;
  rail.scrollBy({
    left: scrollAmount,
    behavior: 'smooth'
  });
};

// Add event listeners to the left arrows
leftArrows.forEach((arrow, index) => {
  arrow.addEventListener('click', () => {
    scrollRail(foodRails[index], -1); // Scroll left
  });
});

// Add event listeners to the right arrows
rightArrows.forEach((arrow, index) => {
  arrow.addEventListener('click', () => {
    scrollRail(foodRails[index], 1); // Scroll right
  });
});

async function sendOrder(payload){
  try {
    const res = await fetch('/api/orders', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
    }
    const data = await res.json();
    return data; // { id, status, total }
  } catch (error) {
    console.error("Failed to send order:", error);
  }
}

async function loadMenu(){
  try {
    const res = await fetch('/api/menu', { headers: { 'Accept': 'application/json' }});
    if (res.status === 304) {
      console.log('Menu data is cached and up-to-date.');
      return;
    }
    if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
    }
    const items = await res.json();
    console.log('Menu items loaded:', items);
    // You would add your code here to render the items on the page.
    return items;
  } catch (error) {
    console.error("Failed to load menu:", error);
  }
}

// ==================== BACKEND CONNECTION ====================

// Replace your existing loadMenu function with this:
async function loadMenu(){
    try {
        const res = await fetch('http://localhost:4000/menu', { 
            headers: { 'Accept': 'application/json' }
        });
        
        if (res.status === 304) {
            console.log('Menu data is cached and up-to-date.');
            return menuItems; // Use existing local data
        }
        
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        
        const items = await res.json();
        console.log('Menu items loaded from backend:', items.length);
        
        // Replace local menuItems with backend data
        menuItems.length = 0; // Clear existing items
        items.forEach(item => {
            menuItems.push({
                id: item.id,
                name: item.name,
                price: item.price,
                img: item.img || `assets/img/menu/default.jpg`
            });
        });
        
        // Re-render menu with real data
        renderMenu();
        return items;
        
    } catch (error) {
        console.error("Failed to load menu from backend, using local data:", error);
        return menuItems; // Fallback to local data
    }
}

// Replace your existing sendOrder function with this:
async function sendOrder(payload){
    try {
        const res = await fetch('http://localhost:4000/orders', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify(payload)
        });
        
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        
        const data = await res.json();
        console.log('Order submitted successfully:', data);
        return data;
        
    } catch (error) {
        console.error("Failed to send order:", error);
        throw error; // Re-throw to handle in checkout
    }
}

// Update your checkout function to use backend
checkoutBtn.addEventListener('click', async () => {
    if (cart.length === 0) { 
        showToast('Cart is empty'); 
        return; 
    }

    const subTotal = cart.reduce((s,i) => s + i.price * i.qty, 0);
    
    try {
        if (orderMode === 'dinein') {
            const table = document.getElementById('tableNumber').value.trim();
            if (!table) { 
                showToast('Enter table number'); 
                return; 
            }
            
            const orderData = {
                mode: 'dinein',
                customer_name: 'Guest', // You can add name input later
                table_number: table,
                items: cart.map(item => ({
                    menu_item_id: item.id,
                    qty: item.qty
                })),
                total: subTotal
            };
            
            const result = await sendOrder(orderData);
            showToast(`Order #${result.id} confirmed for Table ${table}!`);
            
        } else if (orderMode === 'delivery') {
            const phone = document.getElementById('phone').value.trim();
            const email = document.getElementById('email').value.trim();
            if (!phone || !email) { 
                showToast('Enter phone & email'); 
                return; 
            }
            
            const deliveryFee = subTotal >= 280 ? 0 : 30;
            const grandTotal = subTotal + deliveryFee;
            
            const orderData = {
                mode: 'delivery',
                customer_name: 'Guest', // You can add name input later
                phone: phone,
                email: email,
                items: cart.map(item => ({
                    menu_item_id: item.id,
                    qty: item.qty
                })),
                total: grandTotal
            };
            
            const result = await sendOrder(orderData);
            showToast(`Order #${result.id} confirmed! Total R${grandTotal}`);
            
        } else {
            showToast('Select Dine-in or Delivery');
            return;
        }
        
        // Clear cart on success
        cart = []; 
        updateCartUI(); 
        toggleDrawer(false);
        
    } catch (error) {
        showToast('Failed to place order. Please try again.');
        console.error('Checkout error:', error);
    }
});

// Load real menu data when page loads
document.addEventListener('DOMContentLoaded', () => {
    // After your existing loader code, add:
    setTimeout(() => {
        loadMenu().then(menuData => {
            if (menuData && menuData.length > 0) {
                console.log('Menu loaded successfully from backend');
            }
        });
    }, 1000);
});
