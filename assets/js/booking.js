document.getElementById("bookingForm").addEventListener("submit", function(event) {
  event.preventDefault();

  const name = document.getElementById("name").value;
  const date = document.getElementById("date").value;
  const time = document.getElementById("time").value;
  const notes = document.getElementById("notes").value;

  const confirmationBox = document.getElementById("confirmation");

  confirmationBox.innerHTML = `
    <h3>Booking Confirmed ✅</h3>
    <p><strong>Name:</strong> ${name}</p>
    <p><strong>Date:</strong> ${date}</p>
    <p><strong>Time:</strong> ${time}</p>
    <p><strong>Notes:</strong> ${notes || "None"}</p>
  `;

  confirmationBox.style.display = "block";

  // Reset form after submission
  document.getElementById("bookingForm").reset();
});