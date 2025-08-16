document.addEventListener("DOMContentLoaded", () => {
  const optionButtons = document.querySelectorAll(".option-btn");
  const occasionInput = document.getElementById("occasion");
  const otherOccasionGroup = document.getElementById("otherOccasionGroup");
  const specialRequestGroup = document.getElementById("specialRequestGroup");
  const bookingForm = document.getElementById("bookingForm");

  optionButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      // Clear previous selection
      optionButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");

      const value = btn.dataset.value;
      occasionInput.value = value;

      // Toggle Other input
      if (value === "Other") {
        otherOccasionGroup.classList.remove("hidden");
      } else {
        otherOccasionGroup.classList.add("hidden");
      }

      // Toggle Special Request for Date & Birthday
      if (value === "Date" || value === "Birthday Celebrations") {
        specialRequestGroup.classList.remove("hidden");
      } else {
        specialRequestGroup.classList.add("hidden");
      }
    });
  });

  bookingForm.addEventListener("submit", (e) => {
    e.preventDefault();

    const name = document.getElementById("name").value.trim();
    const contact = document.getElementById("contact").value.trim();
    const occasion = occasionInput.value.trim();
    const otherOccasion = document.getElementById("otherOccasion").value.trim();
    const specialRequest = document.getElementById("specialRequest").value.trim();

    if (!name || !contact || !occasion) {
      alert("Please fill in all required fields.");
      return;
    }

    alert(`Booking Confirmed 🎉\n\nName: ${name}\nContact: ${contact}\nOccasion: ${occasion}${occasion === "Other" ? " - " + otherOccasion : ""}\nSpecial Request: ${specialRequest}`);
    bookingForm.reset();
    optionButtons.forEach(b => b.classList.remove("active"));
    otherOccasionGroup.classList.add("hidden");
    specialRequestGroup.classList.add("hidden");
  });
});