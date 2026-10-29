/* GB EDITOR — edits source/content.json of giorgosbatzios.com through the site's own Worker (/api/*).
   Preview = save the draft to the "preview" branch and wait for Cloudflare to build it.
   Push    = merge "preview" into "main" (the live site) and wait for the live build. */
(() => {
  "use strict";

  // ------------------------------------------------------------------ state
  let C = null;                 // the content being edited
  let saved = "";               // JSON of the content as last saved
  let head = "";                // commit of the preview branch we are editing on top of
  let unpublished = false;      // preview has changes that are not live yet
  let PREVIEW_URL = "https://preview-giorgosbatzios.gbatzios-work.workers.dev";
  let LIVE_URL = "https://www.giorgosbatzios.com";
  let lastPreviewOk = false;
  let busy = "";
  const pending = new Map();    // "/assets/img/x.webp" -> data URL of a new picture made in this session
  const sent = new Set();       // pictures already saved to the preview
  const openItems = new WeakSet();
  const newItems = new WeakSet();
  let tab = "home";
  try { tab = sessionStorage.getItem("gb-tab") || "home"; } catch {}

  const $ = (s) => document.querySelector(s);
  const TABS = [
    ["home", "Home", "/"],
    ["theater", "Theater", "/theater/"],
    ["studio", "Studio", "/studio/"],
    ["music", "Music", "/music/"],
    ["tech", "Music Tech", "/music-technology/"],
    ["academic", "Academic", "/academic-portfolio/"],
    ["cv", "CV", "/curriculum-vitae/"],
    ["contact", "Contact", "/contact/"],
    ["texts", "All texts", "/"],
  ];
  const PAGES = [
    ["/", "Home"], ["/theater/", "Theater"], ["/studio/", "Studio"], ["/music/", "Music"],
    ["/music-technology/", "Music Technology"], ["/max4live-devices/", "Max for Live devices"],
    ["/arduino-projects/", "Arduino projects"], ["/daw-plugins/", "DAW plugins"],
    ["/curriculum-vitae/", "CV"], ["/academic-portfolio/", "Academic portfolio"], ["/contact/", "Contact"],
  ];

  // ------------------------------------------------------------------ tiny DOM helper
  function h(tag, props, ...kids) {
    const el = document.createElement(tag);
    for (const [k, v] of Object.entries(props || {})) {
      if (v == null || v === false) continue;
      if (k === "class") el.className = v;
      else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
      else if (["value", "checked", "disabled", "hidden", "selected", "multiple"].includes(k)) el[k] = v;
      else el.setAttribute(k, v === true ? "" : v);
    }
    for (const kid of kids.flat(Infinity)) {
      if (kid == null || kid === false) continue;
      el.append(kid instanceof Node ? kid : document.createTextNode(String(kid)));
    }
    return el;
  }
  const bi = (en = "", el = "") => ({ en, el });
  const L = (x) => (x && typeof x === "object" ? x.en || x.el || "" : x || "");

  // ------------------------------------------------------------------ dialogs and toasts
  function dialog({ title, body = [], buttons = [{ label: "OK", value: true, primary: true }], progress = false }) {
    return new Promise((resolve) => {
      const ov = $("#overlay");
      $("#dlg-title").textContent = title;
      const b = $("#dlg-body");
      b.replaceChildren(...[].concat(body).map((x) => (typeof x === "string" ? h("p", {}, x) : x)));
      if (progress) b.append(h("div", { class: "progress" }, h("span")));
      const acts = $("#dlg-actions");
      acts.replaceChildren(...buttons.map((btn) =>
        btn.href
          ? h("a", { class: "btn" + (btn.primary ? " primary" : ""), href: btn.href, target: "_blank", rel: "noopener", onclick: () => { close(); resolve(btn.value); } }, btn.label)
          : h("button", { type: "button", class: "btn" + (btn.primary ? " primary" : "") + (btn.danger ? " danger" : ""), onclick: () => { close(); resolve(btn.value); } }, btn.label)));
      ov.hidden = false;
      const first = acts.querySelector(".primary") || acts.querySelector("button,a");
      if (first) first.focus();
      function close() { ov.hidden = true; }
      dialog.close = () => { close(); resolve(undefined); };
    });
  }
  dialog.close = () => {};
  const confirmBox = (title, text, yes = "Yes", danger = false) =>
    dialog({ title, body: text, buttons: [{ label: "Cancel", value: false }, { label: yes, value: true, primary: !danger, danger }] });

  let toastTimer;
  function toast(msg, err = false) {
    const t = $("#toast");
    t.textContent = msg;
    t.className = "toast" + (err ? " err" : "");
    t.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => (t.hidden = true), err ? 6000 : 3000);
  }

  // ------------------------------------------------------------------ server
  let relogin = null;
  async function call(path, body, method) {
    for (let attempt = 0; attempt < 2; attempt++) {
      const res = await fetch("/api/" + path, {
        method: method || (body ? "POST" : "GET"),
        credentials: "same-origin",
        headers: body ? { "Content-Type": "application/json", "X-GB": "1" } : {},
        body: body ? JSON.stringify(body) : undefined,
      });
      let data = {};
      try { data = await res.json(); } catch {}
      if (res.status === 401 && data.error === "login" && attempt === 0) {
        await askLogin(true);
        continue;
      }
      if (!res.ok) {
        const e = new Error(data.message || data.error || "Error " + res.status);
        e.code = data.error;
        e.status = res.status;
        throw e;
      }
      return data;
    }
  }

  function askLogin(again) {
    if (relogin) return relogin;
    relogin = new Promise((resolve) => {
      $("#boot").hidden = true;
      $("#shell").hidden = true;
      $("#login").hidden = false;
      $("#login-msg").textContent = again ? "You were logged out after a while. Enter the password again — your changes are kept." : "";
      $("#pw").value = "";
      $("#pw").focus();
      $("#login-form").onsubmit = async (ev) => {
        ev.preventDefault();
        const btn = ev.target.querySelector("button");
        btn.disabled = true;
        $("#login-msg").textContent = "";
        try {
          const res = await fetch("/api/login", { method: "POST", credentials: "same-origin", headers: { "Content-Type": "application/json", "X-GB": "1" }, body: JSON.stringify({ password: $("#pw").value }) });
          const data = await res.json().catch(() => ({}));
          if (res.ok) {
            $("#login").hidden = true;
            if (C) $("#shell").hidden = false;
            relogin = null;
            resolve();
          } else if (data.error === "setup") {
            $("#login-msg").textContent = data.message;
          } else {
            $("#login-msg").textContent = "Wrong password.";
            $("#pw").select();
          }
        } catch {
          $("#login-msg").textContent = "No connection. Try again.";
        }
        btn.disabled = false;
      };
    });
    return relogin;
  }

  // ------------------------------------------------------------------ start
  async function start() {
    try {
      const r = await fetch("/api/content", { credentials: "same-origin" });
      const data = await r.json().catch(() => ({}));
      if (r.status === 503 && data.error === "setup") {
        $("#boot-msg").textContent = data.message;
        return;
      }
      if (r.status === 401) {
        await askLogin(false);
        $("#login").hidden = true;
        $("#boot").hidden = false;
        $("#boot-msg").textContent = "Loading…";
        return start();
      }
      if (!r.ok) throw new Error(data.message || "Error " + r.status);
      load(data);
    } catch (err) {
      $("#boot-msg").textContent = "Could not load the site content: " + err.message;
      $("#boot").append(h("button", { class: "btn", type: "button", onclick: () => location.reload() }, "Try again"));
    }
  }

  function load(data) {
    C = data.content;
    saved = JSON.stringify(C);
    head = data.head;
    unpublished = !!data.unpublished;
    PREVIEW_URL = data.previewUrl || PREVIEW_URL;
    LIVE_URL = data.liveUrl || LIVE_URL;
    $("#open-live").href = LIVE_URL;
    $("#open-preview").href = PREVIEW_URL;
    $("#boot").hidden = true;
    $("#login").hidden = true;
    $("#shell").hidden = false;
    renderTabs();
    render();
    status();
    offerDraft();
  }

  // ------------------------------------------------------------------ draft safety net (survives closing the tab)
  const DRAFT = "gb-editor-draft";
  let draftTimer;
  function keepDraft() {
    clearTimeout(draftTimer);
    draftTimer = setTimeout(() => {
      try {
        if (!isDirty()) { localStorage.removeItem(DRAFT); return; }
        const imgs = {};
        const txt = JSON.stringify(C);
        for (const [p, d] of pending) if (!sent.has(p) && txt.includes(p.replace(/-sm(\.\w+)$/, "$1"))) imgs[p] = d;
        try {
          localStorage.setItem(DRAFT, JSON.stringify({ base: head, content: C, images: imgs, at: Date.now() }));
        } catch {
          localStorage.setItem(DRAFT, JSON.stringify({ base: head, content: C, images: {}, at: Date.now() }));
        }
      } catch {}
    }, 800);
  }
  async function offerDraft() {
    let d = null;
    try { d = JSON.parse(localStorage.getItem(DRAFT) || "null"); } catch {}
    if (!d || !d.content) return;
    if ((d.base !== head && d.base !== "*") || JSON.stringify(d.content) === saved) {
      try { localStorage.removeItem(DRAFT); } catch {}
      return;
    }
    const when = new Date(d.at).toLocaleString();
    const ok = await confirmBox("Unsaved changes found", "You had changes from " + when + " that were never previewed. Bring them back?", "Bring them back");
    if (ok) {
      C = d.content;
      for (const [p, u] of Object.entries(d.images || {})) pending.set(p, u);
      render();
      status();
    } else {
      try { localStorage.removeItem(DRAFT); } catch {}
    }
  }

  // ------------------------------------------------------------------ status bar
  const isDirty = () => JSON.stringify(C) !== saved;
  let statusTimer;
  function changed() {
    clearTimeout(statusTimer);
    statusTimer = setTimeout(status, 150);
    keepDraft();
  }
  function status() {
    const s = $("#status");
    const dirty = C && isDirty();
    let cls = "status ", msg;
    if (busy) { cls += "busy"; msg = busy; }
    else if (dirty) { cls += "dirty"; msg = "Unsaved changes — press Preview to see them"; }
    else if (unpublished) { cls += "dirty"; msg = "Changes are in the preview, not live yet — press Push to publish"; }
    else { cls += "ok"; msg = "Everything is live"; }
    s.className = cls;
    s.replaceChildren(h("span", { class: "dot" }), msg);
    $("#discard").hidden = !dirty || !!busy;
    $("#preview").disabled = !!busy;
    $("#push").disabled = !!busy;
  }
  window.addEventListener("beforeunload", (e) => {
    if (C && isDirty()) { e.preventDefault(); e.returnValue = ""; }
  });

  // ------------------------------------------------------------------ tabs
  function renderTabs() {
    $("#tabs").replaceChildren(...TABS.map(([id, label]) =>
      h("button", { type: "button", "aria-current": id === tab ? "true" : "false", onclick: () => { tab = id; try { sessionStorage.setItem("gb-tab", id); } catch {} renderTabs(); render(); window.scrollTo(0, 0); } }, label)));
  }
  function render() {
    const y = window.scrollY;
    const fn = { home: tabHome, theater: tabTheater, studio: tabStudio, music: tabMusic, tech: tabTech, academic: tabAcademic, cv: tabCV, contact: tabContact, texts: tabTexts }[tab] || tabHome;
    $("#main").replaceChildren(...[].concat(fn()));
    window.scrollTo(0, y);
  }

  // ------------------------------------------------------------------ fields
  function field(label, input, hint) {
    return h("label", { class: "field" }, h("span", { class: "lbl" }, h("span", {}, label), hint ? h("span", { class: "hint" }, hint) : null), input);
  }

  // A text in English + Greek. obj[key] is {en, el}.
  function biField(obj, key, label, opts = {}) {
    if (!obj[key] || typeof obj[key] !== "object") obj[key] = bi();
    const val = obj[key];
    const mk = (lang) => {
      const props = {
        value: val[lang] || "", lang, rows: opts.rows || 3,
        placeholder: opts.placeholder ? opts.placeholder[lang] : "",
        oninput: (e) => { val[lang] = e.target.value; changed(); },
      };
      return h("div", { class: "lang-in" }, opts.multi ? h("textarea", props) : h("input", { ...props, type: "text" }), h("span", {}, lang === "en" ? "EN" : "ΕΛ"));
    };
    const ph = /\{(n|from|to)\}/.test((val.en || "") + (val.el || "")) ? "keep {n} {from} {to} as they are — they become numbers" : opts.hint;
    return h("div", { class: "field" }, h("span", { class: "lbl" }, h("span", {}, label), ph ? h("span", { class: "hint" }, ph) : null),
      h("div", { class: "bi" }, mk("en"), mk("el")));
  }

  // A plain text (same in both languages).
  function textField(obj, key, label, opts = {}) {
    const props = {
      value: obj[key] == null ? "" : String(obj[key]),
      type: opts.type || "text",
      placeholder: opts.placeholder || "",
      oninput: (e) => {
        let v = e.target.value;
        if (opts.type === "number") v = v === "" ? "" : Number(v);
        obj[key] = v;
        if (opts.onchange) opts.onchange(v);
        changed();
      },
    };
    return field(label, opts.multi ? h("textarea", props) : h("input", props), opts.hint);
  }

  // ------------------------------------------------------------------ images
  function imgSrc(path) {
    if (!path) return "";
    if (pending.has(path)) return pending.get(path);
    return /^https?:/.test(path) ? path : path;
  }
  function imgEl(path, cls, alt = "") {
    const img = h("img", { class: cls, alt, loading: "lazy", src: imgSrc(path) || "data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==" });
    let tries = 0;
    img.addEventListener("error", () => {
      if (!path || /^data:|^https?:/.test(path)) return;
      tries++;
      if (tries === 1) img.src = PREVIEW_URL + path;
      else if (tries === 2) img.src = LIVE_URL + path;
    });
    return img;
  }

  let webpOK = null;
  function canWebp() {
    if (webpOK === null) {
      const c = document.createElement("canvas");
      c.width = c.height = 2;
      webpOK = c.toDataURL("image/webp").startsWith("data:image/webp");
    }
    return webpOK;
  }
  function loadImage(file) {
    return new Promise((resolve, reject) => {
      const url = URL.createObjectURL(file);
      const img = new Image();
      img.onload = () => resolve(img);
      img.onerror = () => reject(new Error("This file is not a picture the browser can open. Try a JPG or PNG."));
      img.src = url;
    });
  }
  function encode(img, max) {
    const w0 = img.naturalWidth, h0 = img.naturalHeight;
    const s = Math.min(1, max / Math.max(w0, h0));
    const c = document.createElement("canvas");
    c.width = Math.max(1, Math.round(w0 * s));
    c.height = Math.max(1, Math.round(h0 * s));
    const ctx = c.getContext("2d");
    ctx.imageSmoothingQuality = "high";
    ctx.drawImage(img, 0, 0, c.width, c.height);
    return canWebp() ? c.toDataURL("image/webp", 0.84) : c.toDataURL("image/jpeg", 0.86);
  }
  async function addImage(file, hint) {
    const img = await loadImage(file);
    const ext = canWebp() ? "webp" : "jpg";
    const base = (slug(hint || file.name.replace(/\.[^.]+$/, "")) || "image").slice(0, 40) + "-" + Date.now().toString(36).slice(-5);
    const path = "/assets/img/" + base + "." + ext;
    pending.set(path, encode(img, 1800));
    pending.set("/assets/img/" + base + "-sm." + ext, encode(img, 700));
    return path;
  }

  // obj[key] is an image path. hintFn gives a name for the new file.
  function imgField(obj, key, label, hintFn, opts = {}) {
    const pic = imgEl(obj[key], "", label);
    const fileIn = h("input", { type: "file", accept: "image/*" });
    const btn = h("button", { type: "button", class: "btn small", onclick: () => fileIn.click() }, obj[key] ? "Change picture" : "Add picture");
    const msg = h("span", { class: "note" }, opts.note || "");
    fileIn.addEventListener("change", async () => {
      const f = fileIn.files[0];
      if (!f) return;
      btn.disabled = true;
      msg.textContent = "Preparing picture…";
      try {
        obj[key] = await addImage(f, hintFn ? hintFn() : "");
        pic.src = imgSrc(obj[key]);
        btn.textContent = "Change picture";
        msg.textContent = "New picture ready ✓";
        changed();
        fileIn.dispatchEvent(new Event("input", { bubbles: true }));
        if (opts.onchange) opts.onchange();
      } catch (err) {
        msg.textContent = err.message;
      }
      btn.disabled = false;
      fileIn.value = "";
    });
    const kids = [pic, h("div", { class: "img-btns" }, btn, msg, fileIn)];
    if (opts.removable && obj[key]) kids[1].append(h("button", { type: "button", class: "btn small ghost danger", onclick: () => { obj[key] = ""; changed(); render(); } }, "Remove picture"));
    return h("div", { class: "field" }, h("span", { class: "lbl" }, label), h("div", { class: "img-field" }, kids));
  }

  // ------------------------------------------------------------------ YouTube / SoundCloud
  function ytId(s) {
    s = (s || "").trim();
    if (/^[\w-]{11}$/.test(s)) return s;
    const m = s.match(/(?:youtube\.com\/(?:watch\?(?:.*&)?v=|embed\/|shorts\/|live\/|v\/)|youtu\.be\/|youtube-nocookie\.com\/embed\/)([\w-]{11})/);
    return m ? m[1] : "";
  }
  function ytCheck(id, out) {
    out.replaceChildren();
    if (!id) return;
    const img = h("img", { src: "https://i.ytimg.com/vi/" + id + "/mqdefault.jpg", alt: "", style: "width:160px;height:90px;object-fit:cover;border-radius:8px;border:1px solid var(--line)" });
    const note = h("span", { class: "note" }, "Checking video…");
    const bad = () => { note.className = "warn"; note.textContent = "⚠ This video can't be found on YouTube (removed or private). Check the link."; };
    img.onload = () => {
      if (img.naturalWidth <= 120) bad();
      else { note.className = "note"; note.textContent = "Video found ✓"; }
    };
    img.onerror = bad;
    out.append(h("div", { class: "img-field" }, img, note));
  }
  function ytField(obj, key, label, opts = {}) {
    const out = h("div");
    const warn = h("span", { class: "warn" });
    const input = h("input", {
      type: "url", placeholder: "Paste the YouTube link", value: obj[key] ? "https://youtu.be/" + obj[key] : "",
      oninput: (e) => {
        const id = ytId(e.target.value);
        warn.textContent = e.target.value.trim() && !id ? "That doesn't look like a YouTube link." : "";
        if (id && id !== obj[key]) {
          const old = obj[key];
          obj[key] = id;
          if (opts.onchange) opts.onchange(id, old);
          changed();
          ytCheck(id, out);
        }
      },
    });
    ytCheck(obj[key], out);
    return h("div", { class: "field" }, h("span", { class: "lbl" }, label), input, warn, out);
  }

  // Music items: {type: "yt"|"sc", id}
  function mediaField(m) {
    const out = h("div");
    const warn = h("span", { class: "warn" });
    const shown = m.type === "sc" ? (/^\d+$/.test(m.id) ? "https://api.soundcloud.com/tracks/" + m.id : m.id) : m.id ? "https://youtu.be/" + m.id : "";
    const input = h("input", {
      type: "url", placeholder: "Paste a YouTube or SoundCloud link", value: shown,
      oninput: (e) => {
        const v = e.target.value.trim();
        warn.textContent = "";
        out.replaceChildren();
        const y = ytId(v);
        if (y) { m.type = "yt"; m.id = y; ytCheck(y, out); changed(); return; }
        const t = v.match(/api\.soundcloud\.com\/tracks\/(\d+)/);
        if (t) { m.type = "sc"; m.id = t[1]; scNote(out); changed(); return; }
        if (/^https?:\/\/(on\.)?soundcloud\.com\//.test(v)) {
          if (/on\.soundcloud\.com/.test(v)) { warn.textContent = "Use the full soundcloud.com/… link: open the short link in the browser and copy the address from there."; return; }
          m.type = "sc"; m.id = v.split("?")[0]; scNote(out); changed(); return;
        }
        if (v) warn.textContent = "Paste a YouTube or SoundCloud link.";
      },
    });
    if (m.type === "yt") ytCheck(m.id, out); else if (m.id) scNote(out);
    return h("div", { class: "field" }, h("span", { class: "lbl" }, "Video or song link"), input, warn, out);
  }
  function scNote(out) { out.replaceChildren(h("span", { class: "note" }, "SoundCloud song ✓ — it shows as a SoundCloud player.")); }

  // ------------------------------------------------------------------ roles (chips in both languages)
  function knownRoles() {
    const map = new Map();
    const add = (r) => { if (r && r.en && !map.has(r.en.toLowerCase())) map.set(r.en.toLowerCase(), r); };
    (C.theater || []).forEach((t) => (t.roles || []).forEach(add));
    (C.music || []).forEach((t) => (t.roles || []).forEach(add));
    return map;
  }
  let dlCount = 0;
  function rolesField(arr, label) {
    const chips = h("div", { class: "chips" });
    const draw = () => chips.replaceChildren(...arr.map((r, i) =>
      h("span", { class: "chip" }, r.en, r.el && r.el !== r.en ? h("span", { class: "el" }, " / " + r.el) : null,
        h("button", { type: "button", title: "Remove", "aria-label": "Remove " + r.en, onclick: () => { arr.splice(i, 1); draw(); changed(); } }, "×"))));
    draw();
    const known = knownRoles();
    const id = "roles-" + ++dlCount;
    const dl = h("datalist", { id }, [...known.values()].map((r) => h("option", { value: r.en })));
    const en = h("input", { type: "text", placeholder: "Role in English", list: id, lang: "en" });
    const el = h("input", { type: "text", placeholder: "Ρόλος στα ελληνικά", lang: "el" });
    en.addEventListener("input", () => { const k = known.get(en.value.trim().toLowerCase()); if (k) el.value = k.el; });
    const add = () => {
      const e = en.value.trim(), g = el.value.trim();
      if (!e && !g) return;
      if (!e || !g) { toast("Write the role in both English and Greek", true); return; }
      arr.push({ en: e, el: g });
      en.value = el.value = "";
      draw();
      changed();
      en.focus();
    };
    [en, el].forEach((i) => i.addEventListener("keydown", (ev) => { if (ev.key === "Enter") { ev.preventDefault(); add(); } }));
    return h("div", { class: "field" }, h("span", { class: "lbl" }, h("span", {}, label), h("span", { class: "hint" }, "pick a known role and the Greek fills in")),
      chips, h("div", { class: "role-add" }, en, el, h("button", { type: "button", class: "btn small", onclick: add }, "Add role")), dl);
  }

  // ------------------------------------------------------------------ lists
  const ICON = { up: "↑", down: "↓", del: "✕", star: "★" };
  function list(o) {
    // o: {arr, title, head(it)->{title, sub, thumb, wide, badge}, body(it)->nodes, make()->obj, addLabel, addAtTop, note, extraTools(it)}
    const wrap = h("div", { class: "list" });
    o.arr.forEach((it, i) => wrap.append(itemEl(o, it, i)));
    const add = o.make ? h("button", {
      type: "button", class: "btn small", onclick: () => {
        const it = o.make();
        if (o.addAtTop === false) o.arr.push(it); else o.arr.unshift(it);
        openItems.add(it);
        newItems.add(it);
        changed();
        render();
        requestAnimationFrame(() => {
          const el = document.querySelector(".item.new.open");
          if (el) { el.scrollIntoView({ block: "center", behavior: "smooth" }); const f = el.querySelector(".item-body input, .item-body textarea"); if (f) f.focus({ preventScroll: true }); }
        });
      },
    }, "+ " + (o.addLabel || "Add")) : null;
    return h("section", { class: "group" },
      h("h2", {}, h("span", {}, o.title + " (" + o.arr.length + ")"), add),
      o.note ? h("p", { class: "note", style: "margin:-4px 0 12px" }, o.note) : null,
      wrap);
  }
  function itemEl(o, it, i) {
    const box = h("div", { class: "item" + (openItems.has(it) ? " open" : "") + (newItems.has(it) ? " new" : "") });
    const headBox = h("div", { class: "item-head", role: "button", tabindex: "0", "aria-expanded": openItems.has(it) ? "true" : "false" });
    const fillHead = () => {
      const d = o.head(it);
      const tools = h("div", { class: "tools" },
        o.extraTools ? o.extraTools(it) : null,
        h("button", { type: "button", class: "icon-btn", title: "Move up", "aria-label": "Move up", disabled: i === 0, onclick: (e) => { e.stopPropagation(); move(o.arr, i, -1); } }, ICON.up),
        h("button", { type: "button", class: "icon-btn", title: "Move down", "aria-label": "Move down", disabled: i === o.arr.length - 1, onclick: (e) => { e.stopPropagation(); move(o.arr, i, 1); } }, ICON.down),
        o.noDelete ? null : h("button", { type: "button", class: "icon-btn danger", title: "Delete", "aria-label": "Delete", onclick: async (e) => {
          e.stopPropagation();
          if (await confirmBox("Delete this?", "“" + (d.title || "Untitled") + "” will be removed from the site (after Preview and Push).", "Delete", true)) {
            o.arr.splice(i, 1); changed(); render();
          }
        } }, ICON.del));
      headBox.replaceChildren(...[
        d.thumb !== undefined ? (d.thumbEl || imgEl(d.thumb, "thumb" + (d.wide ? " wide" : ""))) : null,
        h("div", { class: "txt" }, h("div", { class: "t" }, d.title || h("span", { class: "muted" }, "Untitled"), d.badge ? h("span", { class: "badge" }, d.badge) : null), d.sub ? h("div", { class: "s" }, d.sub) : null),
        tools, h("span", { class: "chev", "aria-hidden": "true" }, "›")].filter(Boolean));
    };
    fillHead();
    box.append(headBox);
    let body = null;
    const openBody = () => {
      body = h("div", { class: "item-body" }, o.body(it));
      body.addEventListener("input", () => setTimeout(fillHead, 0));
      body.addEventListener("change", () => setTimeout(fillHead, 0));
      box.append(body);
    };
    if (openItems.has(it)) openBody();
    const toggle = () => {
      if (openItems.has(it)) { openItems.delete(it); box.classList.remove("open"); if (body) body.remove(); body = null; headBox.setAttribute("aria-expanded", "false"); }
      else { openItems.add(it); box.classList.add("open"); openBody(); headBox.setAttribute("aria-expanded", "true"); }
    };
    headBox.addEventListener("click", toggle);
    headBox.addEventListener("keydown", (e) => { if ((e.key === "Enter" || e.key === " ") && e.target === headBox) { e.preventDefault(); toggle(); } });
    return box;
  }
  function move(arr, i, d) {
    const j = i + d;
    if (j < 0 || j >= arr.length) return;
    [arr[i], arr[j]] = [arr[j], arr[i]];
    changed();
    render();
  }

  // Simple rows (no open/close): bilingual lines or name/org pairs
  function rows(o) {
    // o: {arr, title, cols:[{key,label,bi}], make, addLabel}
    const wrap = h("div", { class: "panel" });
    o.arr.forEach((it, i) => {
      const cells = o.cols.map((c) => c.bi
        ? h("div", { class: "bi" }, ["en", "el"].map((lang) => h("div", { class: "lang-in" },
          h("input", { type: "text", lang, value: (it[lang] || ""), placeholder: c.label, oninput: (e) => { it[lang] = e.target.value; changed(); } }), h("span", {}, lang === "en" ? "EN" : "ΕΛ"))))
        : h("input", { type: "text", value: it[c.key] || "", placeholder: c.label, oninput: (e) => { it[c.key] = e.target.value; changed(); } }));
      wrap.append(h("div", { style: "display:flex;gap:8px;align-items:center" },
        h("div", { style: "flex:1;min-width:0;display:grid;gap:8px;grid-template-columns:" + (o.cols.length > 1 ? "1fr 1fr" : "1fr") }, cells),
        h("button", { type: "button", class: "icon-btn", title: "Move up", "aria-label": "Move up", disabled: i === 0, onclick: () => move(o.arr, i, -1) }, ICON.up),
        h("button", { type: "button", class: "icon-btn danger", title: "Delete", "aria-label": "Delete", onclick: async () => {
          if (await confirmBox("Delete this line?", "“" + (L(it) || it.name || "") + "” will be removed.", "Delete", true)) { o.arr.splice(i, 1); changed(); render(); }
        } }, ICON.del)));
    });
    if (!o.arr.length) wrap.append(h("p", { class: "note" }, "Nothing here yet."));
    return h("section", { class: "group" },
      h("h2", {}, h("span", {}, o.title), h("button", { type: "button", class: "btn small", onclick: () => { o.arr.push(o.make()); changed(); render(); } }, "+ " + o.addLabel)),
      wrap);
  }

  // ------------------------------------------------------------------ helpers for sections
  const GR = { α: "a", ά: "a", β: "v", γ: "g", δ: "d", ε: "e", έ: "e", ζ: "z", η: "i", ή: "i", θ: "th", ι: "i", ί: "i", ϊ: "i", ΐ: "i", κ: "k", λ: "l", μ: "m", ν: "n", ξ: "x", ο: "o", ό: "o", π: "p", ρ: "r", σ: "s", ς: "s", τ: "t", υ: "y", ύ: "y", ϋ: "y", ΰ: "y", φ: "f", χ: "ch", ψ: "ps", ω: "o", ώ: "o" };
  function slug(s) {
    return String(s || "").toLowerCase().split("").map((c) => GR[c] ?? c).join("")
      .normalize("NFKD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 60);
  }
  function page(title, intro, ...kids) {
    return [h("div", { class: "sec-head" }, h("h1", { class: "dotted" }, title)), intro ? h("p", { class: "sec-intro" }, intro) : null, ...kids];
  }
  function group(title, ...kids) {
    return h("section", { class: "group" }, h("h2", {}, h("span", {}, title)), h("div", { class: "panel" }, kids));
  }
  const T = (key, label, opts) => biField(C.text, key, label, opts);

  // ------------------------------------------------------------------ HOME
  function tabHome() {
    C.selected = C.selected || [];
    return page("Home", "The first page of the site.",
      group("Top of the page",
        h("div", { class: "bi" }, textField(C.site, "name", "Your name (English)"), textField(C.site, "name_el", "Your name (Greek)")),
        biField(C.site, "role", "Line under your name"),
        imgField(C.images, "home1", "Top photo (cut as a rounded square)", () => "home-top"),
        T("home_photo1_alt", "Top photo description (for Google / blind visitors)")),
      h("section", { class: "group" }, h("h2", {}, h("span", {}, "Second photo and your fields")),
        h("div", { class: "panel" }, imgField(C.images, "home2", "Second photo (octagon shape)", () => "home-second"),
          T("home_photo2_alt", "Second photo description"))),
      rows({ arr: C.site.fields, title: "Fields next to the second photo", cols: [{ bi: true, label: "Field" }], make: () => bi(), addLabel: "Add field" }),
      list({
        arr: C.selected, title: "Selected work cards", addLabel: "Add card", addAtTop: false,
        note: "The site shows these cards in this order. Three look best.",
        head: (s) => ({ title: s.title, sub: L(s.kicker), thumb: s.image, wide: true }),
        make: () => ({ title: "", kicker: bi(), line: bi(), link: "/theater/", image: "" }),
        body: (s) => [
          textField(s, "title", "Title (same in both languages)"),
          biField(s, "kicker", "Small line above the title", { placeholder: { en: "Theater · Venue, 2025", el: "Θέατρο · Χώρος, 2025" } }),
          biField(s, "line", "Short description"),
          field("Opens page", h("select", { onchange: (e) => { s.link = e.target.value; changed(); } }, PAGES.map(([p, n]) => h("option", { value: p, selected: s.link === p }, n)))),
          imgField(s, "image", "Picture", () => "selected-" + slug(s.title)),
        ],
      }),
      group("Search engines (Google)",
        T("site_title", "Site title in Google"),
        T("home_desc", "Site description in Google", { multi: true })),
      group("Numbers on the section list at the bottom",
        T("home_meta_theater", "Theater"), T("home_meta_studio", "Studio"), T("home_meta_music", "Music"),
        T("home_meta_tech", "Music Technology"), T("home_meta_cv", "CV"), T("home_meta_academic", "Academic")));
  }

  // ------------------------------------------------------------------ THEATER
  function tabTheater() {
    return page("Theater", "Every show sits on the Theater page, grouped by year (newest first).",
      group("Page texts", T("theater_lede", "Intro text", { multi: true }), T("theater_genre", "Small label")),
      list({
        arr: C.theater, title: "Shows", addLabel: "Add show",
        head: (t) => ({ title: t.title, sub: [t.year, L(t.venue), (t.roles || []).map(L).join(" · ")].filter(Boolean).join(" — "), thumb: t.poster }),
        make: () => ({ year: new Date().getFullYear(), title: "", venue: bi(), roles: [], link: "", poster: "" }),
        body: (t) => [
          h("div", { class: "row", style: "grid-template-columns:120px 1fr" },
            textField(t, "year", "Year", { type: "number" }),
            textField(t, "title", "Show title (as written on the poster)")),
          biField(t, "venue", "Theater / venue"),
          rolesField(t.roles, "What you did"),
          textField(t, "link", "Link (tickets or info page) — optional", { type: "url", placeholder: "https://…" }),
          imgField(t, "poster", "Poster", () => "theater-" + slug(t.title)),
        ],
      }));
  }

  // ------------------------------------------------------------------ STUDIO
  function tabStudio() {
    const catName = (id) => { const c = C.studio_cats.find((x) => x.id === id); return c ? c.en : id; };
    return page("Studio", "Studio videos. The one with the ★ is shown big at the top of the page.",
      group("Page texts", T("studio_kicker", "Small label"), T("studio_lede", "Intro text", { multi: true }),
        imgField(C.images, "studio", "Page picture", () => "studio")),
      list({
        arr: C.studio, title: "Videos", addLabel: "Add video",
        head: (s) => ({ title: s.title, sub: [(s.date || "").slice(0, 4), (s.cats || []).map(catName).join(" · ")].filter(Boolean).join(" — "),
          thumbEl: h("img", { class: "thumb wide", alt: "", loading: "lazy", src: s.youtube ? "https://i.ytimg.com/vi/" + s.youtube + "/mqdefault.jpg" : "data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==" }),
          thumb: "", badge: s.youtube && s.youtube === C.featured_studio ? "Featured" : "" }),
        extraTools: (s) => h("button", { type: "button", class: "icon-btn", title: "Show big at the top", "aria-label": "Make featured",
          style: s.youtube && s.youtube === C.featured_studio ? "color:var(--accent);border-color:var(--accent)" : "",
          onclick: (e) => { e.stopPropagation(); if (!s.youtube) { toast("Add the YouTube link first", true); return; } C.featured_studio = s.youtube; changed(); render(); } }, ICON.star),
        make: () => ({ title: "", date: new Date().toISOString().slice(0, 10), cats: [], youtube: "", note: bi() }),
        body: (s) => [
          h("div", { class: "row", style: "grid-template-columns:1fr 170px" },
            textField(s, "title", "Title (Song – Artist)"),
            textField(s, "date", "Date", { type: "date" })),
          ytField(s, "youtube", "YouTube video", { onchange: (id, old) => { if (old && C.featured_studio === old) C.featured_studio = id; } }),
          h("div", { class: "field" }, h("span", { class: "lbl" }, "What you did"),
            h("div", { class: "checks" }, C.studio_cats.map((c) => h("label", { class: "check" },
              h("input", { type: "checkbox", checked: (s.cats || []).includes(c.id), onchange: (e) => {
                s.cats = s.cats || [];
                if (e.target.checked) { if (!s.cats.includes(c.id)) s.cats.push(c.id); s.cats.sort((a, b) => C.studio_cats.findIndex((x) => x.id === a) - C.studio_cats.findIndex((x) => x.id === b)); }
                else s.cats = s.cats.filter((x) => x !== c.id);
                changed();
              } }), c.en)))),
          biField(s, "note", "Note about the work — optional", { multi: true }),
        ],
      }),
      h("section", { class: "group" }, h("h2", {}, h("span", {}, "Filter buttons (categories)"),
        h("button", { type: "button", class: "btn small", onclick: () => { C.studio_cats.push({ id: "", en: "", el: "" }); changed(); render(); } }, "+ Add category")),
        h("div", { class: "panel" }, C.studio_cats.map((c, i) => {
          const used = C.studio.filter((s) => (s.cats || []).includes(c.id)).length;
          return h("div", { style: "display:flex;gap:8px;align-items:center" },
            h("div", { class: "bi", style: "flex:1" }, ["en", "el"].map((lang) => h("div", { class: "lang-in" },
              h("input", { type: "text", lang, value: c[lang] || "", oninput: (e) => {
                c[lang] = e.target.value;
                if (lang === "en" && !used) c.id = e.target.value.trim();
                changed();
              } }), h("span", {}, lang === "en" ? "EN" : "ΕΛ")))),
            h("span", { class: "note", style: "width:70px;text-align:right" }, used + " videos"),
            h("button", { type: "button", class: "icon-btn danger", title: "Delete", "aria-label": "Delete category", onclick: async () => {
              if (await confirmBox("Delete category?", used ? "It is used by " + used + " videos; they will lose this label." : "“" + c.en + "” will be removed.", "Delete", true)) {
                C.studio.forEach((s) => (s.cats = (s.cats || []).filter((x) => x !== c.id)));
                C.studio_cats.splice(i, 1); changed(); render();
              }
            } }, ICON.del));
        }))));
  }

  // ------------------------------------------------------------------ MUSIC
  function tabMusic() {
    return page("Music", "Your own songs and collaborations. YouTube videos or SoundCloud songs.",
      group("Page texts", T("music_kicker", "Small label"), T("music_lede", "Intro text", { multi: true }),
        imgField(C.images, "music", "Page picture", () => "music")),
      list({
        arr: C.music, title: "Songs", addLabel: "Add song",
        head: (m) => ({ title: m.title, sub: (m.type === "sc" ? "SoundCloud — " : "YouTube — ") + (m.roles || []).map(L).join(" · "),
          thumbEl: h("img", { class: "thumb wide", alt: "", loading: "lazy", src: m.type === "yt" && m.id ? "https://i.ytimg.com/vi/" + m.id + "/mqdefault.jpg" : "data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==" }), thumb: "" }),
        make: () => ({ title: "", roles: [], type: "yt", id: "", note: bi() }),
        body: (m) => [
          textField(m, "title", "Title (Artist – Song)"),
          mediaField(m),
          rolesField(m.roles, "What you did"),
          biField(m, "note", "Note — optional", { multi: true }),
        ],
      }));
  }

  // ------------------------------------------------------------------ MUSIC TECHNOLOGY (projects with their own pages)
  const TECH = [["m4l", "Max for Live devices", "/max4live-devices/"], ["arduino", "Arduino projects", "/arduino-projects/"], ["plugins", "DAW plugins", "/daw-plugins/"]];
  let techSub = "m4l";
  function tabTech() {
    const sub = h("div", { class: "tabs", style: "padding:0;margin:0 0 8px" }, TECH.map(([k, n]) =>
      h("button", { type: "button", "aria-current": k === techSub ? "true" : "false", onclick: () => { techSub = k; render(); } }, n)));
    const [key, name, path] = TECH.find((t) => t[0] === techSub);
    const sec = C.tech[key];
    const taken = () => new Set(TECH.flatMap(([k]) => C.tech[k].items.map((p) => p.slug)));
    return page("Music Technology", "Each project gets its own page with text, pictures and videos.",
      group("Overview page texts", T("tech_kicker", "Small label"), T("tech_lede", "Intro text", { multi: true })),
      h("section", { class: "group" }, sub, h("div", { class: "panel" }, biField(sec, "lede", name + " — intro text", { multi: true }))),
      list({
        arr: sec.items, title: name, addLabel: "Add project",
        head: (p) => ({ title: p.title, sub: L(p.summary) || "giorgosbatzios.com" + path + (p.slug || "…") + "/", thumb: p.cover }),
        make: () => ({ slug: "", title: "", cover: "", summary: bi(), download: { url: "", label: bi("Download", "Λήψη") }, blocks: [{ type: "p", text: bi() }] }),
        body: (p) => {
          const addr = h("span", { class: "note" }, "Page address: giorgosbatzios.com" + path + (p.slug || "…") + "/");
          const fixed = !!p.old; // pages that already exist keep their address
          return [
            textField(p, "title", "Project name", { onchange: (v) => {
              if (fixed) return;
              let s = slug(v) || "project", n = 2;
              const used = taken(); used.delete(p.slug);
              const base = s;
              while (used.has(s)) s = base + "-" + n++;
              p.slug = s;
              addr.textContent = "Page address: giorgosbatzios.com" + path + s + "/";
            } }),
            addr,
            biField(p, "summary", "Short description (on the card)"),
            imgField(p, "cover", "Cover picture", () => "project-" + (p.slug || slug(p.title))),
            p.download ? h("div", { class: "panel", style: "background:var(--paper)" },
              textField(p.download, "url", "Download / link button — address (optional)", { type: "url", placeholder: "https://…" }),
              biField(p.download, "label", "Button text")) : null,
            blocksEditor(p),
          ];
        },
      }));
  }

  const BLOCKS = [["p", "Paragraph"], ["h", "Heading"], ["ul", "Bullet list"], ["img", "Picture"], ["yt", "YouTube video"], ["link", "Link"], ["mono", "Code / technical text"]];
  function blocksEditor(p) {
    p.blocks = p.blocks || [];
    const wrap = h("div", { class: "blocks" });
    const draw = () => {
      wrap.replaceChildren(...p.blocks.map((b, i) => {
        const tools = h("span", { style: "display:flex;gap:6px" },
          h("button", { type: "button", class: "icon-btn", title: "Move up", "aria-label": "Move up", disabled: i === 0, onclick: () => { [p.blocks[i - 1], p.blocks[i]] = [p.blocks[i], p.blocks[i - 1]]; changed(); draw(); } }, ICON.up),
          h("button", { type: "button", class: "icon-btn", title: "Move down", "aria-label": "Move down", disabled: i === p.blocks.length - 1, onclick: () => { [p.blocks[i + 1], p.blocks[i]] = [p.blocks[i], p.blocks[i + 1]]; changed(); draw(); } }, ICON.down),
          h("button", { type: "button", class: "icon-btn danger", title: "Delete", "aria-label": "Delete", onclick: async () => { if (await confirmBox("Delete this part?", "It will be removed from the project page.", "Delete", true)) { p.blocks.splice(i, 1); changed(); draw(); } } }, ICON.del));
        const label = (BLOCKS.find((x) => x[0] === b.type) || [, b.type])[1];
        let inner;
        if (b.type === "p") inner = biField(b, "text", "", { multi: true, rows: 4 });
        else if (b.type === "h") inner = biField(b, "text", "");
        else if (b.type === "ul") {
          b.items = b.items || [];
          inner = h("div", { style: "display:grid;gap:8px" },
            b.items.map((it, j) => h("div", { style: "display:flex;gap:8px;align-items:center" },
              h("div", { class: "bi", style: "flex:1" }, ["en", "el"].map((lang) => h("div", { class: "lang-in" },
                h("input", { type: "text", lang, value: it[lang] || "", oninput: (e) => { it[lang] = e.target.value; changed(); } }), h("span", {}, lang === "en" ? "EN" : "ΕΛ")))),
              h("button", { type: "button", class: "icon-btn danger", title: "Delete point", "aria-label": "Delete point", onclick: () => { b.items.splice(j, 1); changed(); draw(); } }, ICON.del))),
            h("div", {}, h("button", { type: "button", class: "btn small", onclick: () => { b.items.push(bi()); changed(); draw(); } }, "+ Add point")));
        } else if (b.type === "img") inner = h("div", { style: "display:grid;gap:10px" }, imgField(b, "src", "", () => (p.slug || "project") + "-pic"), biField(b, "caption", "Caption — optional"));
        else if (b.type === "yt") inner = ytField(b, "id", "");
        else if (b.type === "link") inner = h("div", { style: "display:grid;gap:10px" }, textField(b, "url", "Address", { type: "url", placeholder: "https://…" }), biField(b, "label", "Link text"));
        else if (b.type === "mono") inner = textField(b, "text", "", { multi: true });
        else inner = h("p", { class: "note" }, "This part can't be edited here.");
        return h("div", { class: "block" }, h("div", { class: "block-head" }, h("span", {}, label), tools), inner);
      }));
    };
    draw();
    const make = { p: () => ({ type: "p", text: bi() }), h: () => ({ type: "h", text: bi() }), ul: () => ({ type: "ul", items: [bi()] }), img: () => ({ type: "img", src: "", caption: bi() }), yt: () => ({ type: "yt", id: "" }), link: () => ({ type: "link", url: "", label: bi() }), mono: () => ({ type: "mono", text: "" }) };
    return h("div", { class: "field" }, h("span", { class: "lbl" }, "Page content (top to bottom)"), wrap,
      h("div", { class: "add-row" }, h("span", { class: "note", style: "align-self:center;margin-right:4px" }, "Add:"),
        BLOCKS.map(([k, n]) => h("button", { type: "button", class: "btn small", onclick: () => { p.blocks.push(make[k]()); changed(); draw(); } }, n))));
  }

  // ------------------------------------------------------------------ ACADEMIC
  function tabAcademic() {
    return page("Academic portfolio", "University projects.",
      group("Page texts", T("academic_kicker", "Small label"), T("academic_card_kicker", "Label on each card"), T("academic_lede", "Intro text", { multi: true })),
      list({
        arr: C.academic, title: "Projects", addLabel: "Add project",
        head: (a) => ({ title: L(a.title), sub: L(a.inst), thumb: a.thumb }),
        make: () => ({ title: bi(), inst: bi(), video: "", reports: [], thumb: "" }),
        body: (a) => [
          biField(a, "title", "Title"),
          biField(a, "inst", "School / college"),
          textField(a, "video", "Video or files link (YouTube, Google Drive…)", { type: "url", placeholder: "https://…" }),
          imgField(a, "thumb", "Picture", () => "academic-" + slug(L(a.title))),
          reportsEditor(a),
        ],
      }));
  }

  function reportsEditor(a) {
    a.reports = a.reports || [];
    const wrap = h("div", { style: "display:grid;gap:10px" });
    const draw = () => wrap.replaceChildren(...a.reports.map((r, i) => h("div", { class: "block" },
      h("div", { class: "block-head" }, h("span", {}, "Link " + (i + 1)),
        h("button", { type: "button", class: "icon-btn danger", title: "Delete", "aria-label": "Delete link", onclick: () => { a.reports.splice(i, 1); changed(); draw(); } }, ICON.del)),
      biField(r, "label", "Link text"), textField(r, "url", "Address", { type: "url", placeholder: "https://…" }))),
      h("div", {}, h("button", { type: "button", class: "btn small", onclick: () => { a.reports.push({ label: bi("Report PDF", "Αναφορά PDF"), url: "" }); changed(); draw(); } }, "+ Add link")));
    draw();
    return h("div", { class: "field" }, h("span", { class: "lbl" }, "Extra links (reports, PDFs) — optional"), wrap);
  }

  // ------------------------------------------------------------------ CV
  function cvEntry(x) {
    return [
      biField(x, "title", "Title / place of work"),
      biField(x, "kind", "Type (e.g. Theater venue, BA) — optional"),
      biField(x, "org", "Company / organisation"),
      biField(x, "place", "City"),
      biField(x, "when", "When", { placeholder: { en: "May 2025 – Today", el: "Μάιος 2025 – Σήμερα" } }),
      biField(x, "desc", "What you did", { multi: true, rows: 4 }),
    ];
  }
  function tabCV() {
    const cv = C.cv;
    const mk = () => ({ title: bi(), kind: bi(), org: bi(), place: bi("Athens", "Αθήνα"), when: bi(), desc: bi() });
    return page("CV", "New experience goes on top.",
      group("About", biField(cv, "objective", "Professional objective", { multi: true, rows: 4 }), T("cv_kicker", "Small label"), T("cv_desc", "Description for Google", { multi: true })),
      list({ arr: cv.work, title: "Work experience", addLabel: "Add experience", head: (x) => ({ title: L(x.title), sub: [L(x.when), L(x.org)].filter(Boolean).join(" — ") }), make: mk, body: cvEntry }),
      list({ arr: cv.education, title: "Education", addLabel: "Add education", head: (x) => ({ title: L(x.title), sub: [L(x.when), L(x.org)].filter(Boolean).join(" — ") }), make: mk, body: cvEntry }),
      rows({ arr: cv.skills, title: "Skills", cols: [{ bi: true, label: "Skill" }], make: () => bi(), addLabel: "Add skill" }),
      rows({ arr: cv.software, title: "Software", cols: [{ key: "name", label: "Name" }, { key: "org", label: "Company" }], make: () => ({ name: "", org: "" }), addLabel: "Add software" }),
      rows({ arr: cv.mixers, title: "Mixing consoles", cols: [{ key: "name", label: "Brand" }, { key: "org", label: "Series" }], make: () => ({ name: "", org: "" }), addLabel: "Add console" }),
      rows({ arr: cv.certifications, title: "Certifications", cols: [{ key: "name", label: "Certificate" }, { key: "org", label: "From" }], make: () => ({ name: "", org: "" }), addLabel: "Add certificate" }));
  }

  // ------------------------------------------------------------------ CONTACT
  const SOCIALS = ["Instagram", "YouTube", "Facebook", "LinkedIn", "Linktree"];
  function tabContact() {
    return page("Contact", "Contact page, footer links and the details on your CV.",
      group("Details",
        textField(C.site, "email", "Email", { type: "email" }),
        textField(C.site, "phone", "Phone"),
        T("contact_lede", "Contact page text", { multi: true }),
        T("contact_desc", "Description for Google", { multi: true }),
        imgField(C.images, "contact", "Contact photo", () => "contact")),
      h("section", { class: "group" }, h("h2", {}, h("span", {}, "Social links (icons in the footer)"),
        h("button", { type: "button", class: "btn small", onclick: () => { C.social.push({ name: "", url: "" }); changed(); render(); } }, "+ Add link")),
        h("div", { class: "panel" }, C.social.map((s, i) => h("div", { style: "display:flex;gap:8px;align-items:center" },
          h("input", { type: "text", value: s.name, list: "social-names", placeholder: "Name", style: "width:160px", oninput: (e) => { s.name = e.target.value.trim(); changed(); } }),
          h("input", { type: "url", value: s.url, placeholder: "https://…", style: "flex:1", oninput: (e) => { s.url = e.target.value.trim(); changed(); } }),
          h("button", { type: "button", class: "icon-btn", title: "Move up", "aria-label": "Move up", disabled: i === 0, onclick: () => move(C.social, i, -1) }, ICON.up),
          h("button", { type: "button", class: "icon-btn danger", title: "Delete", "aria-label": "Delete", onclick: async () => { if (await confirmBox("Delete link?", "“" + s.name + "” will be removed.", "Delete", true)) { C.social.splice(i, 1); changed(); render(); } } }, ICON.del))),
          h("datalist", { id: "social-names" }, SOCIALS.map((n) => h("option", { value: n }))),
          h("p", { class: "note" }, "Instagram, YouTube, Facebook, LinkedIn and Linktree get their own icon; any other name gets a link icon."))),
      group("Contact form", textField(C.site, "form_key", "Web3Forms access key", { hint: "only change if you make a new Web3Forms key" })));
  }

  // ------------------------------------------------------------------ ALL TEXTS
  const TEXT_LABELS = {
    site_title: "Site title in Google", home_desc: "Site description in Google", home_photo1_alt: "Home top photo description", home_photo2_alt: "Home second photo description",
    home_meta_theater: "Home list — Theater", home_meta_studio: "Home list — Studio", home_meta_music: "Home list — Music", home_meta_tech: "Home list — Music Technology",
    home_meta_cv: "Home list — CV", home_meta_academic: "Home list — Academic", theater_lede: "Theater intro", theater_genre: "Theater label",
    studio_lede: "Studio intro", studio_kicker: "Studio label", music_lede: "Music intro", music_kicker: "Music label", tech_lede: "Music Technology intro",
    tech_kicker: "Music Technology label", academic_lede: "Academic intro", academic_kicker: "Academic label", academic_card_kicker: "Academic card label",
    cv_kicker: "CV label", cv_desc: "CV description in Google", contact_lede: "Contact text", contact_desc: "Contact description in Google",
  };
  function tabTexts() {
    const long = (v) => ((v.en || "").length > 70 || (v.el || "").length > 70);
    return page("All texts", "Every text of the site in one place. Menu names, buttons and labels are at the bottom.",
      group("Page texts", Object.keys(C.text).map((k) => biField(C.text, k, TEXT_LABELS[k] || k.replace(/_/g, " "), { multi: long(C.text[k]) }))),
      group("Menu, buttons and labels", Object.keys(C.ui).map((k) => biField(C.ui, k, (C.ui[k].en || k), { multi: long(C.ui[k]) }))));
  }

  // ------------------------------------------------------------------ checks before saving
  function problems() {
    const out = [];
    C.theater.forEach((t) => {
      if (!String(t.title || "").trim()) out.push("Theater: a show has no title.");
      if (!/^\d{4}$/.test(String(t.year))) out.push("Theater: “" + (t.title || "a show") + "” needs a year like 2025.");
      if (!t.poster) out.push("Theater: “" + (t.title || "a show") + "” has no poster.");
    });
    C.studio.forEach((s) => {
      if (!String(s.title || "").trim()) out.push("Studio: a video has no title.");
      if (!s.youtube) out.push("Studio: “" + (s.title || "a video") + "” has no YouTube link.");
      if (!/^\d{4}-\d{2}-\d{2}$/.test(s.date || "")) out.push("Studio: “" + (s.title || "a video") + "” needs a date.");
    });
    C.music.forEach((m) => {
      if (!String(m.title || "").trim()) out.push("Music: a song has no title.");
      if (!m.id) out.push("Music: “" + (m.title || "a song") + "” has no YouTube or SoundCloud link.");
    });
    TECH.forEach(([k, n]) => C.tech[k].items.forEach((p) => {
      if (!String(p.title || "").trim() || !p.slug) out.push(n + ": a project has no name.");
      if (!p.cover) out.push(n + ": “" + (p.title || "a project") + "” has no cover picture.");
      (p.blocks || []).forEach((b) => { if (b.type === "yt" && !b.id) out.push(n + ": “" + p.title + "” has an empty YouTube part."); if (b.type === "img" && !b.src) out.push(n + ": “" + p.title + "” has an empty picture part."); });
    }));
    C.academic.forEach((a) => { if (!L(a.title)) out.push("Academic: a project has no title."); if (!a.thumb) out.push("Academic: “" + L(a.title) + "” has no picture."); });
    ["work", "education"].forEach((k) => C.cv[k].forEach((x) => { if (!L(x.title)) out.push("CV: an entry has no title — fill it in or delete it."); }));
    C.selected.forEach((s) => { if (!s.title || !s.image) out.push("Home: a selected work card needs a title and a picture."); });
    C.studio_cats.forEach((c) => { if (!c.id || !c.en) out.push("Studio: a category has no English name."); });
    const half = [];
    const walk = (x, where) => {
      if (Array.isArray(x)) x.forEach((y) => walk(y, where));
      else if (x && typeof x === "object") {
        const keys = Object.keys(x);
        if (keys.includes("en") && keys.includes("el") && typeof x.en === "string" && typeof x.el === "string") {
          if (x.en.trim() && !x.el.trim()) half.push("“" + x.en.slice(0, 40) + "” has no Greek version.");
          else if (!x.en.trim() && x.el.trim()) half.push("“" + x.el.slice(0, 40) + "” has no English version.");
        } else keys.forEach((k) => walk(x[k], where));
      }
    };
    walk(C);
    return { errors: [...new Set(out)], half: [...new Set(half)] };
  }

  // ------------------------------------------------------------------ save / preview / push
  async function save() {
    const txt = JSON.stringify(C);
    const images = [];
    for (const [p, d] of pending) {
      if (sent.has(p) || !txt.includes(p.replace(/-sm(\.\w+)$/, "$1"))) continue;
      images.push({ path: "source" + p, data: d.split(",")[1] });
    }
    const res = await call("save", { content: C, images, base: head, message: "Edit from GB EDITOR" });
    head = res.head;
    saved = txt;
    unpublished = true;
    for (const im of images) sent.add(im.path.slice(6));
    try { localStorage.removeItem(DRAFT); } catch {}
  }

  async function checkFirst() {
    const { errors, half } = problems();
    if (errors.length) {
      await dialog({ title: "Fix these first", body: [h("ul", {}, errors.slice(0, 12).map((x) => h("li", {}, x)))], buttons: [{ label: "OK", value: true, primary: true }] });
      return false;
    }
    if (half.length) {
      return confirmBox("Missing translations", [h("ul", {}, half.slice(0, 8).map((x) => h("li", {}, x))), "The site will show the other language there. Continue anyway?"], "Continue");
    }
    return true;
  }

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  async function waitFor(target, commit, onTick) {
    const t0 = Date.now();
    while (Date.now() - t0 < 6 * 60 * 1000) {
      try {
        const s = await call("status?target=" + target + "&commit=" + encodeURIComponent(commit));
        if (s.ready) return { ok: true };
        if (s.failed) return { ok: false, failed: true, link: s.link };
      } catch (e) { if (e.status === 401) throw e; }
      if (onTick) onTick(Math.round((Date.now() - t0) / 1000));
      await sleep(5000);
    }
    return { ok: false, timeout: true };
  }

  function waitingPage(w, text) {
    try {
      w.document.write('<!doctype html><title>Preview — GB EDITOR</title><meta name="viewport" content="width=device-width,initial-scale=1"><body style="margin:0;background:#0d0d0e;color:#f3f3f4;font:16px/1.5 system-ui,sans-serif;display:grid;place-items:center;min-height:100vh;text-align:center"><div><p style="font-weight:650;letter-spacing:.08em">GB EDITOR<span style="color:#b9472f">●</span></p><p id="m" style="color:#9d9da3">' + text + "</p></div></body>");
      w.document.close();
    } catch {}
  }

  function buildTrouble(r, where) {
    const body = r.failed
      ? ["Cloudflare could not build the " + where + ". Nothing changed on the live site.", "Open Cloudflare and look at the build, or press “Retry build” there. If it fails again, ask Claude."]
      : ["The " + where + " is taking longer than usual (more than 6 minutes).", "Cloudflare is sometimes stuck at “Initializing”: open Cloudflare → Workers → giorgosbatzios → Deployments and press “Retry build”."];
    return dialog({ title: "Something is slow", body, buttons: [{ label: "Open Cloudflare", href: r.link || "https://dash.cloudflare.com/?to=/:account/workers-and-pages", value: true }, { label: "OK", value: true, primary: true }] });
  }

  async function doPreview() {
    if (busy) return;
    if (!(await checkFirst())) return;
    const path = (TABS.find((t) => t[0] === tab) || [, , "/"])[2];
    const w = window.open("", "gb-preview");
    if (w) waitingPage(w, "Preparing your preview… this takes about a minute.");
    try {
      if (isDirty()) {
        busy = "Saving…"; status();
        await save();
      }
      busy = "Building the preview… (about a minute)"; status();
      const r = await waitFor("preview", head, (s) => { busy = "Building the preview… " + s + "s"; status(); });
      busy = ""; status();
      if (!r.ok) { if (w) w.close(); await buildTrouble(r, "preview"); return; }
      lastPreviewOk = true;
      const url = PREVIEW_URL + path + "?v=" + head.slice(0, 7);
      $("#open-preview").href = url;
      if (w && !w.closed) { w.location.href = url; w.focus(); }
      else await dialog({ title: "Preview is ready", body: "Your changes are on the preview site. If you like them, press Push.", buttons: [{ label: "Close", value: true }, { label: "Open preview ↗", href: url, primary: true, value: true }] });
      toast("Preview ready — Greek version: add /el/ after the address");
    } catch (err) {
      busy = ""; status();
      if (w) w.close();
      if (err.code === "conflict") {
        await dialog({ title: "The site changed somewhere else", body: "Someone (probably Claude) changed the site while you were editing. Your changes are kept on this computer. Reload the editor and they will be offered back to you.", buttons: [{ label: "Reload", value: true, primary: true }] });
        keepDraftNow(true);
        location.reload();
        return;
      }
      toast("Could not save: " + err.message, true);
    }
  }

  function keepDraftNow(sameBaseless) {
    try {
      localStorage.setItem(DRAFT, JSON.stringify({ base: sameBaseless ? "*" : head, content: C, images: Object.fromEntries(pending), at: Date.now() }));
    } catch {}
  }

  async function doPush() {
    if (busy) return;
    if (!isDirty() && !unpublished) { toast("Nothing new to publish — everything is already live"); return; }
    if (!(await checkFirst())) return;
    const msg = isDirty()
      ? ["You have changes you haven't previewed yet. They will go straight to giorgosbatzios.com.", "Publish everything now?"]
      : ["Everything you saw in the preview will go live on giorgosbatzios.com.", "Publish now?"];
    if (!(await confirmBox("Push to the live site?", msg, "Push live"))) return;
    try {
      if (isDirty()) { busy = "Saving…"; status(); await save(); }
      busy = "Publishing…"; status();
      const r = await call("publish", {});
      if (r.head) head = r.head;
      busy = "Putting it live… (about a minute)"; status();
      const w = await waitFor("live", r.commit, (s) => { busy = "Putting it live… " + s + "s"; status(); });
      busy = ""; status();
      if (!w.ok) { await buildTrouble(w, "live site"); return; }
      unpublished = false;
      status();
      await dialog({ title: "It's live", body: "Your changes are now on giorgosbatzios.com. (If you still see the old version, refresh the page.)", buttons: [{ label: "Close", value: true }, { label: "Open the site ↗", href: LIVE_URL + ((TABS.find((t) => t[0] === tab) || [, , "/"])[2]), primary: true, value: true }] });
    } catch (err) {
      busy = ""; status();
      if (err.code === "conflict") { keepDraftNow(true); toast("The site changed somewhere else — reload the editor", true); return; }
      toast("Could not publish: " + err.message, true);
    }
  }

  async function doDiscard() {
    if (!(await confirmBox("Discard changes?", "All changes since the last Preview will be lost.", "Discard", true))) return;
    C = JSON.parse(saved);
    for (const p of [...pending.keys()]) if (!sent.has(p)) pending.delete(p);
    try { localStorage.removeItem(DRAFT); } catch {}
    render();
    status();
  }

  async function doReset() {
    if (busy) return;
    if (!(await confirmBox("Throw away everything that is not live?", ["The preview and this editor go back to exactly what is on giorgosbatzios.com now.", "This can't be undone."], "Throw away", true))) return;
    try {
      busy = "Resetting…"; status();
      await call("reset", {});
      busy = "";
      try { localStorage.removeItem(DRAFT); } catch {}
      window.onbeforeunload = null;
      saved = JSON.stringify(C);
      location.reload();
    } catch (err) {
      busy = ""; status();
      toast("Could not reset: " + err.message, true);
    }
  }

  // ------------------------------------------------------------------ wire up
  $("#preview").addEventListener("click", doPreview);
  $("#push").addEventListener("click", doPush);
  $("#discard").addEventListener("click", doDiscard);
  $("#logout").addEventListener("click", async () => {
    if (C && isDirty() && !(await confirmBox("Log out?", "You have changes that are not previewed yet. They stay saved on this computer only.", "Log out"))) return;
    if (C && isDirty()) keepDraftNow(false);
    await fetch("/api/logout", { method: "POST", headers: { "X-GB": "1" }, credentials: "same-origin" }).catch(() => {});
    saved = JSON.stringify(C);
    location.reload();
  });
  const reset = $("#reset");
  if (reset) reset.addEventListener("click", doReset);
  document.addEventListener("click", (e) => { const m = document.querySelector(".more[open]"); if (m && !m.contains(e.target)) m.open = false; });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !$("#overlay").hidden) dialog.close();
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "s") { e.preventDefault(); doPreview(); }
  });
  start();
})();
