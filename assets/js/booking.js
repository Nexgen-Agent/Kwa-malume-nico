
document.addEventListener("DOMContentLoaded", () => {
  const optionButtons = document.querySelectorAll(".option-btn");
  const occasionInput = document.getElementById("occasion");
  const otherOccasionGroup = document.getElementById("otherOccasionGroup");
  const specialRequestGroup = document.getElementById("specialRequestGroup");
  const bookingForm = document.getElementById("bookingForm");

  // Handle occasion button clicks
  optionButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      optionButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");

      const value = btn.dataset.value;
      occasionInput.value = value;

      if (value === "Other") {
        otherOccasionGroup.classList.remove("hidden");
      } else {
        otherOccasionGroup.classList.add("hidden");
      }

      if (value === "Date" || value === "Birthday Celebrations") {
        specialRequestGroup.classList.remove("hidden");
      } else {
        specialRequestGroup.classList.add("hidden");
      }
    });
  });

  // Handle form submission
  bookingForm.addEventListener("submit", (e) => {
    e.preventDefault();

    const name = document.getElementById("name").value.trim();
    const contact = document.getElementById("contact").value.trim();
    const occasion = occasionInput.value.trim();
    const otherOccasion = document.getElementById("otherOccasion").value.trim();
    const specialRequest = document.getElementById("specialRequest").value.trim();
    const date = document.getElementById("booking-date").value;
    const time = document.getElementById("booking-time").value;

    if (!name || !contact || !occasion || !date || !time) {
      alert("⚠️ Please fill in all required fields.");
      return;
    }

    // EmailJS parameters
    const templateParams = {
      name: name,
      contact: contact,
      occasion: occasion === "Other" ? `${occasion} - ${otherOccasion}` : occasion,
      specialRequest: specialRequest || "None",
      date: date,
      time: time,
    };

    // Send via EmailJS
    emailjs.send("service_pdwcuat", "template_rq0e43j", templateParams)
      .then(() => {
        alert(
          `✅ Booking Confirmed & Email Sent!\n\nName: ${name}\nContact: ${contact}\nOccasion: ${templateParams.occasion}\nSpecial Request: ${specialRequest || "None"}\nDate: ${date}\nTime: ${time}`
        );
        bookingForm.reset();
        optionButtons.forEach(b => b.classList.remove("active"));
        otherOccasionGroup.classList.add("hidden");
        specialRequestGroup.classList.add("hidden");
      })
      .catch((error) => {
        console.error("❌ Error sending email:", error);
        alert("Booking saved, but email failed. Please try again.");
      });
  });
});