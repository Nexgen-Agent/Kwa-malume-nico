// -------------------- Menu Data --------------------
const menuItems = [
  { id: 1, name: "Titanic Family Kota", price: 100, img: "assets/img/menu/1.jpg" },
  { id: 2, name: "Danked Wings", price: 75, img: "assets/img/menu/2.jpg" },
  { id: 3, name: "Bugatti Kota", price: 60, img: "assets/img/menu/3.jpg" },
  { id: 4, name: "Burger", price: 60, img: "assets/img/menu/4.jpg" },
  { id: 5, name: "Range Rover Kota", price: 50, img: "assets/img/menu/5.jpg" },
  { id: 6, name: "Dagwood", price: 45, img: "assets/img/menu/6.jpg" },
  { id: 7, name: "BMW M4 Kota", price: 40, img: "assets/img/menu/7.jpg" },
  { id: 8, name: "Dessert", price: 40, img: "assets/img/menu/8.jpg" },
  { id: 9, name: "Omoda Kota", price: 35, img: "assets/img/menu/9.jpg" },
  { id: 10, name: "Haval Kota", price: 30, img: "assets/img/menu/10.jpg" }
];

let cart = [];
let orderType = "";

// -------------------- Render Menu --------------------
const menuDiv = document.getElementById("menu");

menuItems.forEach(item => {
  const card = document.createElement("div");
  card.classList.add("card", "glass", "water");

  card.innerHTML = `
    <img src="${item.img}" alt="${item.name}" class="menu-img">
    <div class="card-body">
      <h3>${item.name}</h3>
      <p>R${item.price}</p>
      <button class="btn gold" onclick="addToCart(${item.id}, event)">Add to Cart</button>
    </div>
  `;

  menuDiv.appendChild(card);
});

// -------------------- Add to Cart --------------------
function addToCart(id, e) {
  const item = menuItems.find(m => m.id === id);

  // if already in cart, increase qty
  const existing = cart.find(i => i.id === id);
  if (existing) {
    existing.qty++;
  } else {
    cart.push({ ...item, qty: 1 });
  }
  updateCart();

  // Ripple animation
  const btn = e.target;
  const ripple = document.createElement("span");
  ripple.classList.add("gold-ripple");
  ripple.style.left = `${e.offsetX}px`;
  ripple.style.top = `${e.offsetY}px`;
  btn.appendChild(ripple);
  setTimeout(() => ripple.remove(), 700);

  // Glow press effect
  btn.classList.add("glow-press");
  setTimeout(() => btn.classList.remove("glow-press"), 800);
}

// -------------------- Update Cart --------------------
function updateCart() {
  const cartList = document.getElementById("cart-items");
  cartList.innerHTML = "";

  let total = 0;
  cart.forEach((item, index) => {
    total += item.price * item.qty;

    const li = document.createElement("li");
    li.classList.add("cart-item");

    li.innerHTML = `
      ${item.name} x${item.qty} - R${item.price * item.qty}
      <button class="btn ghost" onclick="removeFromCart(${index})">✖</button>
    `;

    cartList.appendChild(li);
  });

  document.getElementById("total").textContent = `Total: R${total}`;

  if (orderType === "delivery") {
    document.getElementById("delivery-note").textContent =
      total >= 280 ? "🎉 Free Delivery Applied!" : "🚚 Delivery Fee Applies (Orders < R280)";
  } else {
    document.getElementById("delivery-note").textContent = "";
  }
}

// -------------------- Remove from Cart --------------------
function removeFromCart(index) {
  if (cart[index].qty > 1) {
    cart[index].qty--;
  } else {
    cart.splice(index, 1);
  }
  updateCart();
}

// -------------------- Set Order Type --------------------
function setOrderType(type) {
  orderType = type;

  if (type === "dinein") {
    document.getElementById("dinein-section").classList.remove("hidden");
    document.getElementById("delivery-section").classList.add("hidden");
  } else {
    document.getElementById("delivery-section").classList.remove("hidden");
    document.getElementById("dinein-section").classList.add("hidden");
  }

  updateCart(); // refresh delivery note if needed
}

// -------------------- Checkout --------------------
function checkout() {
  if (cart.length === 0) {
    alert("Your cart is empty!");
    return;
  }

  if (orderType === "dinein") {
    const table = document.getElementById("tableNumber").value;
    if (!table) {
      alert("Please enter your table number.");
      return;
    }
    alert(`✅ Dine-in order placed for Table ${table}!`);
  } else if (orderType === "delivery") {
    const phone = document.getElementById("phone").value;
    const email = document.getElementById("email").value;
    if (!phone || !email) {
      alert("Please enter both phone and email.");
      return;
    }
    alert(`✅ Delivery order confirmed!\nPhone: ${phone}\nEmail: ${email}`);
  } else {
    alert("Please select Dine-in or Delivery first.");
  }
}