// Menu data
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

// Render menu
const menuDiv = document.getElementById("menu");
menuItems.forEach(item => {
  const card = document.createElement("div");
  card.classList.add("card");
  card.innerHTML = `
    <img src="${item.img}" alt="${item.name}">
    <div class="card-body">
      <h3>${item.name}</h3>
      <p>R${item.price}</p>
      <button onclick="addToCart(${item.id})">Add to Cart</button>
    </div>
  `;
  menuDiv.appendChild(card);
});

// Add to cart
function addToCart(id) {
  const item = menuItems.find(m => m.id === id);
  cart.push(item);
  updateCart();

  // Small animation (reaction)
  alert(`${item.name} added ✅`);
}

// Update cart
function updateCart() {
  const cartList = document.getElementById("cart-items");
  cartList.innerHTML = "";

  let total = 0;
  cart.forEach((item, index) => {
    total += item.price;
    const li = document.createElement("li");
    li.textContent = `${item.name} - R${item.price}`;
    cartList.appendChild(li);
  });

  document.getElementById("total").textContent = `Total: R${total}`;

  if (orderType === "delivery") {
    document.getElementById("delivery-note").textContent =
      total >= 280 ? "🎉 Free Delivery Applied!" : "🚚 Delivery Fee Applies (Orders < R280)";
  }
}

// Set order type
function setOrderType(type) {
  orderType = type;
  if (type === "dinein") {
    document.getElementById("dinein-section").classList.remove("hidden");
    document.getElementById("delivery-section").classList.add("hidden");
  } else {
    document.getElementById("delivery-section").classList.remove("hidden");
    document.getElementById("dinein-section").classList.add("hidden");
  }
}

// Checkout
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