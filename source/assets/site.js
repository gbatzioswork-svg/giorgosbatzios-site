(function () {
  // When opened from a folder on your computer, point folder links at their index.html
  if (location.protocol === "file:") {
    document.querySelectorAll("a[href]").forEach(function (a) {
      var h = a.getAttribute("href");
      if (!/^[a-z]+:/i.test(h) && !h.startsWith("#") && /\/$/.test(h)) a.setAttribute("href", h + "index.html");
    });
  }

  // Mobile menu
  var btn = document.querySelector(".menu-btn");
  var nav = document.getElementById("nav");
  if (btn && nav) {
    btn.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      btn.textContent = open ? "Close" : "Menu";
    });
  }
  // Close the desktop dropdown when clicking elsewhere
  document.addEventListener("click", function (e) {
    document.querySelectorAll(".nav details[open]").forEach(function (d) {
      if (!d.contains(e.target)) d.removeAttribute("open");
    });
  });

  // YouTube: load the player only when someone presses play
  document.querySelectorAll(".yt button").forEach(function (b) {
    b.addEventListener("click", function () {
      var box = b.parentNode;
      var f = document.createElement("iframe");
      f.src = "https://www.youtube-nocookie.com/embed/" + box.dataset.id + "?autoplay=1&rel=0";
      f.title = box.dataset.title || "YouTube video";
      f.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture";
      f.allowFullscreen = true;
      box.replaceChildren(f);
    });
  });

  // Studio filters
  var filters = document.querySelector(".filters");
  if (filters) {
    var cards = document.querySelectorAll("[data-cats]");
    filters.addEventListener("click", function (e) {
      var b = e.target.closest("button");
      if (!b) return;
      filters.querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
      var cat = b.dataset.cat;
      cards.forEach(function (c) {
        c.hidden = cat !== "all" && c.dataset.cats.split("|").indexOf(cat) === -1;
      });
    });
  }

  // Contact form: opens the visitor's email app with the message filled in
  var form = document.getElementById("contact-form");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var name = form.elements.name.value.trim();
      var from = form.elements.email.value.trim();
      var msg = form.elements.message.value.trim();
      var body = msg + "\n\n— " + name + (from ? " (" + from + ")" : "");
      location.href = "mailto:" + form.dataset.to + "?subject=" +
        encodeURIComponent("Website message from " + name) + "&body=" + encodeURIComponent(body);
    });
  }
})();
