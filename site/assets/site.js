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
      btn.textContent = open ? btn.dataset.close : btn.dataset.open;
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

  // Contact form: sends through Web3Forms when a key is set, otherwise opens the visitor's email app
  var form = document.getElementById("contact-form");
  if (form) {
    var status = form.querySelector(".form-status");
    var submit = form.querySelector("button[type=submit]");
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var name = form.elements.name.value.trim();
      var from = form.elements.email.value.trim();
      var msg = form.elements.message.value.trim();
      if (!form.dataset.key) {
        var body = msg + "\n\n— " + name + (from ? " (" + from + ")" : "");
        location.href = "mailto:" + form.dataset.to + "?subject=" +
          encodeURIComponent("Website message from " + name) + "&body=" + encodeURIComponent(body);
        return;
      }
      if (form.elements.botcheck.checked) return;
      submit.disabled = true;
      status.className = "form-status";
      status.textContent = form.dataset.sending;
      fetch("https://api.web3forms.com/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({
          access_key: form.dataset.key,
          subject: "Website message from " + name,
          from_name: "giorgosbatzios.com",
          name: name, email: from, replyto: from, message: msg,
          page: location.href
        })
      }).then(function (r) { return r.json(); }).then(function (j) {
        if (!j.success) throw new Error(j.message || "failed");
        form.reset();
        status.className = "form-status ok";
        status.textContent = form.dataset.sent;
      }).catch(function () {
        status.className = "form-status err";
        status.textContent = form.dataset.failed + " " + form.dataset.to;
      }).finally(function () { submit.disabled = false; });
    });
  }
})();

/* ================= motion & depth ================= */
(function () {
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var head = document.querySelector(".site-head");

  // Header tightens after scrolling a little
  function onScrollHead() { if (head) head.classList.toggle("scrolled", window.scrollY > 24); }
  window.addEventListener("scroll", onScrollHead, { passive: true });
  onScrollHead();
  if (reduce) return;

  // Soft reveal: only for things that start below the first screen, so nothing visible ever blinks
  if ("IntersectionObserver" in window) {
    var sel = ".page-head .lede, .split, .sel, .index a, .year, .show, .featured, .card, .track, .proj, .acad, .entry, .side > div, .contact > *, .article > *, .sec-title, .pager";
    var groups = new Map();
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    document.querySelectorAll(sel).forEach(function (el) {
      var r = el.getBoundingClientRect();
      if (r.top < window.innerHeight * 0.92) return; // already on screen: leave it alone
      var p = el.parentElement, n = groups.get(p) || 0;
      groups.set(p, n + 1);
      el.style.setProperty("--d", Math.min(n % 3, 2) * 0.08 + "s"); // small stagger inside rows
      el.classList.add("reveal");
      io.observe(el);
    });
  }

  // Depth: the two home photos move a little slower than the page
  // (wide screens only: on phones the photos sit right under the text)
  var layers = window.matchMedia("(min-width: 761px)").matches ? Array.prototype.slice.call(document.querySelectorAll(".hero-img, .split-img")) : [];
  // Sound-wave divider
  var canvas = document.querySelector(".wave");
  var ctx = canvas && canvas.getContext ? canvas.getContext("2d") : null;
  var energy = 0.18, lastY = window.scrollY, t = 0, W = 0, H = 0, dpr = 1, mouseX = -1;
  if (ctx) {
    canvas.parentElement.classList.add("live");
    var size = function () {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      W = canvas.clientWidth; H = canvas.clientHeight;
      canvas.width = W * dpr; canvas.height = H * dpr;
    };
    size();
    window.addEventListener("resize", size);
    canvas.parentElement.addEventListener("pointermove", function (e) {
      var r = canvas.getBoundingClientRect(); mouseX = (e.clientX - r.left) / r.width; energy = Math.min(energy + 0.06, 1.4);
    });
    canvas.parentElement.addEventListener("pointerleave", function () { mouseX = -1; });
  }
  var accent = getComputedStyle(document.documentElement).getPropertyValue("--accent").trim() || "#b9472f";

  function drawWave() {
    var mid = H / 2, n = Math.max(80, Math.floor(W / 4));
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, W, H);
    var grad = ctx.createLinearGradient(0, 0, W, 0);
    grad.addColorStop(0, "rgba(255,255,255,0)");
    grad.addColorStop(0.18, "rgba(255,255,255,.55)");
    grad.addColorStop(0.82, "rgba(255,255,255,.55)");
    grad.addColorStop(1, "rgba(255,255,255,0)");
    ctx.strokeStyle = grad; ctx.lineWidth = 1.2; ctx.beginPath();
    var peakX = 0, peakY = mid;
    for (var i = 0; i <= n; i++) {
      var x = i / n, env = Math.sin(Math.PI * x); // fade to flat at both ends
      var m = mouseX >= 0 ? Math.exp(-Math.pow((x - mouseX) * 7, 2)) * 1.6 : 0;
      var y = Math.sin(x * 38 + t * 3.1) * 0.55 + Math.sin(x * 91 - t * 4.7) * 0.3 + Math.sin(x * 13 + t * 1.3) * 0.4;
      var yy = mid + y * env * (H * 0.36) * Math.min(energy + m * 0.5, 1.6);
      if (i === 0) ctx.moveTo(x * W, yy); else ctx.lineTo(x * W, yy);
      if (Math.abs(yy - mid) > Math.abs(peakY - mid) && env > 0.3) { peakX = x * W; peakY = yy; }
    }
    ctx.stroke();
    // a small red "playhead" travelling along the line
    var px = ((t * 0.06) % 1) * W, pe = Math.sin(Math.PI * px / W);
    ctx.fillStyle = accent; ctx.globalAlpha = pe;
    ctx.beginPath(); ctx.arc(px, mid, 3, 0, Math.PI * 2); ctx.fill();
    ctx.globalAlpha = 1;
  }

  var ticking = false;
  function frame() {
    var y = window.scrollY, v = Math.abs(y - lastY); lastY = y;
    energy += Math.min(v / 120, 0.5);            // scrolling makes the wave move more
    energy += (0.18 - energy) * 0.04;            // then it settles back to a gentle idle
    t += 0.016 * (0.6 + energy);
    var vh = window.innerHeight;
    layers.forEach(function (el) {
      var r = el.getBoundingClientRect();
      if (r.bottom < -200 || r.top > vh + 200) return;
      var off = (r.top + r.height / 2 - vh / 2) * -0.08;
      el.style.translate = "0 " + off.toFixed(1) + "px";
    });
    if (ctx) {
      var wr = canvas.getBoundingClientRect();
      if (wr.bottom > 0 && wr.top < vh) drawWave();
    }
    requestAnimationFrame(frame);
  }
  if (layers.length || ctx) requestAnimationFrame(frame);

  // Gentle 3D tilt toward the mouse (desktop only)
  if (window.matchMedia("(hover: hover) and (pointer: fine)").matches) {
    document.querySelectorAll(".sel .thumb, .proj .thumb, .acad .thumb, .featured .yt").forEach(function (el) {
      el.classList.add("tilt");
      el.addEventListener("pointermove", function (e) {
        var r = el.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
        el.classList.add("tilting");
        el.style.transform = "perspective(900px) rotateX(" + (-y * 6).toFixed(2) + "deg) rotateY(" + (x * 8).toFixed(2) + "deg) translateZ(0)";
      });
      el.addEventListener("pointerleave", function () { el.classList.remove("tilting"); el.style.transform = ""; });
    });
  }
})();
