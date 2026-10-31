// Minimal vanilla JavaScript shared by all app pages.

document.addEventListener("DOMContentLoaded", function () {
  // Mobile navigation toggle
  var toggle = document.getElementById("nav-toggle");
  var menu = document.getElementById("nav-menu");
  if (toggle && menu) {
    toggle.addEventListener("click", function () {
      var isHidden = menu.classList.toggle("hidden");
      menu.classList.toggle("flex", !isHidden);
      toggle.setAttribute("aria-expanded", String(!isHidden));
    });
  }

  // Close buttons on flash messages
  document.querySelectorAll(".flash-close").forEach(function (button) {
    button.addEventListener("click", function () {
      button.closest(".flash").remove();
    });
  });
});
