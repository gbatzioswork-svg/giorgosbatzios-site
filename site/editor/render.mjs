// Turns content.json into every page of giorgosbatzios.com.
// Used in two places, so both always look exactly the same:
//   * source/build.mjs   — writes the real site into ../site (run through: python3 source/build.py)
//   * GB EDITOR          — instant preview in the browser, before anything is saved
// render(content, { exists(path) → bool, year }) → { files: { "/theater/index.html": html, … }, cards: [...] }

const LANGS = ["en", "el"];
const PREFIX = { en: "", el: "/el" };
const GREEK = /[Ͱ-Ͽἀ-῿]/;

// html.escape(s, quote=True)
const e = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#x27;");

// json.dumps(x, ensure_ascii=False)
function pyjson(x) {
  if (x === null || x === undefined) return "null";
  if (Array.isArray(x)) return "[" + x.map(pyjson).join(", ") + "]";
  if (typeof x === "object") return "{" + Object.entries(x).map(([k, v]) => JSON.stringify(k) + ": " + pyjson(v)).join(", ") + "}";
  if (typeof x === "boolean") return x ? "true" : "false";
  return JSON.stringify(x);
}

// urllib.parse.quote(s, safe="")
const quote = (s) => encodeURIComponent(s).replace(/[!'()*]/g, (c) => "%" + c.charCodeAt(0).toString(16).toUpperCase());

// Texts typed in the editor are plain text: no HTML can sneak into the pages.
function clean(x) {
  if (Array.isArray(x)) return x.map(clean);
  if (x && typeof x === "object") return Object.fromEntries(Object.entries(x).map(([k, v]) => [k, clean(v)]));
  if (typeof x === "string") return x.replace(/</g, "‹").replace(/>/g, "›").replace(/"/g, "”").trim();
  return x;
}

const ARROW = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';
const _S = 'fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"';
const ICONS = {
  Instagram: `<rect x="3" y="3" width="18" height="18" rx="5" ${_S}/><circle cx="12" cy="12" r="4" ${_S}/><circle cx="17.2" cy="6.8" r="1.1" fill="currentColor"/>`,
  YouTube: `<rect x="2.5" y="5.5" width="19" height="13" rx="4" ${_S}/><path d="M10.2 9.3v5.4l4.6-2.7z" fill="currentColor"/>`,
  Facebook: `<circle cx="12" cy="12" r="9.5" ${_S}/><path d="M13.2 21.4V12.5h2.6M13.2 21.4V9.3c0-1.3.7-2 2-2h1.3M10.4 12.5h2.8" ${_S}/>`,
  LinkedIn: `<rect x="3" y="3" width="18" height="18" rx="3.5" ${_S}/><path d="M8 10.5V17M11.6 17v-6.5M11.6 13.4c0-1.7 1.1-2.9 2.6-2.9s2.4 1.1 2.4 2.9V17" ${_S}/><circle cx="8" cy="7.5" r="1.1" fill="currentColor"/>`,
  Linktree: `<path d="M12 21.5V13M5 9.5h14M7 4.5l5 5 5-5M7 14.5l5-5 5 5" ${_S}/>`,
  _link: `<path d="M10 14a4.5 4.5 0 0 0 6.4 0l3-3a4.5 4.5 0 0 0-6.4-6.4l-1 1M14 10a4.5 4.5 0 0 0-6.4 0l-3 3a4.5 4.5 0 0 0 6.4 6.4l1-1" ${_S}/>`,
};
const NAV = [["/theater/", "theater"], ["/studio/", "studio"], ["/music/", "music"], ["MT", "tech"],
  ["/curriculum-vitae/", "cv"], ["/academic-portfolio/", "academic"], ["/contact/", "contact"]];
const MT = [["/music-technology/", "overview"], ["/max4live-devices/", "m4l"], ["/arduino-projects/", "arduino"], ["/daw-plugins/", "plugins"]];
const SECTIONS = [["/max4live-devices/", "m4l"], ["/arduino-projects/", "arduino"], ["/daw-plugins/", "plugins"]];

export function render(content, opts = {}) {
  const exists = opts.exists || (() => false);
  const YEAR = opts.year || new Date().getFullYear();
  const D = clean(content);
  const SITE = D.site, IMG = D.images, UI = D.ui, TX = D.text, THEATER = D.theater, STUDIO = D.studio, MUSIC = D.music;
  const SOCIAL = D.social.map((s) => [s.name, s.url]);
  const FORM_KEY = SITE.form_key || "";
  const STUDIO_CATS = D.studio_cats.map((c) => c.id);
  const CAT_NAME = Object.fromEntries(D.studio_cats.map((c) => [c.id, c]));
  const FEATURED_STUDIO = D.featured_studio;
  const SELECTED = D.selected, ACADEMIC = D.academic, CV = D.cv;
  const NAME = { en: SITE.name, el: SITE.name_el || SITE.name };
  const files = {}, cards = [], PAGES = [];

  const L = (x, lang) => (x == null ? "" : typeof x === "object" ? x[lang] || x.en || "" : x);
  const U = (lang, path) => PREFIX[lang] + path;
  const u = (key, lang) => L(UI[key], lang);
  const tx = (key, lang, kw = {}) => {
    let s = L(TX[key], lang);
    for (const [k, v] of Object.entries(kw)) s = s.split("{" + k + "}").join(String(v));
    return s;
  };
  const lang_of = (text) => (GREEK.test(text || "") ? "el" : "en");

  function sq(url, w = 1000) {
    if (!url) return "";
    if (w <= 800 && url.startsWith("/assets/img/")) {
      const m = url.match(/^(.*?)(\.[^./]*)?$/);
      const root = m[1], ext = m[2] || "";
      if (!root.endsWith("-sm")) {
        const small = root + "-sm" + ext;
        if (exists(small)) return small;
      }
    }
    return url;
  }
  const yt = (vid, title, lang) =>
    `<div class="yt" data-id="${vid}" data-title="${e(title)}"><button type="button" aria-label="${u("play", lang)}: ${e(title)}">` +
    `<img src="https://i.ytimg.com/vi/${vid}/hqdefault.jpg" alt="${e(title)} — ${u("video", lang)}" loading="lazy" decoding="async">` +
    `<span class="play"></span></button></div>`;
  const socials_html = (extra = "") =>
    `<ul class="socials ${extra}">` + SOCIAL.map(([n, url]) => `<li><a href="${url}" target="_blank" rel="noopener" aria-label="${e(n)}" title="${e(n)}">` +
      `<svg viewBox="0 0 24 24" aria-hidden="true">${ICONS[n] || ICONS._link}</svg></a></li>`).join("") + "</ul>";
  function sc(track) {
    const t = String(track);
    const src = /^[0-9]+$/.test(t) ? `https%3A//api.soundcloud.com/tracks/${t}` : quote(t);
    return `<div class="sc"><iframe loading="lazy" title="SoundCloud player" allow="autoplay" ` +
      `src="https://w.soundcloud.com/player/?url=${src}&color=%23b9472f&visual=true&show_artwork=true"></iframe></div>`;
  }
  function nav(cur, lang) {
    return NAV.map(([href, key]) => {
      if (href === "MT") {
        const curmt = MT.some(([h]) => cur.startsWith(h));
        const subs = MT.map(([h, k]) => `<a href="${U(lang, h)}"${cur === h ? " aria-current=page" : ""}>${u(k, lang)}</a>`).join("");
        return `<details class="${curmt ? "is-current" : ""}"><summary>${u(key, lang)}</summary><div class="sub">${subs}</div></details>`;
      }
      const ac = cur.startsWith(href) ? ' aria-current="page"' : "";
      return `<a href="${U(lang, href)}"${ac}>${u(key, lang)}</a>`;
    }).join("");
  }
  const person_ld = () => ({
    "@type": "Person", "@id": SITE.url + "/#person", name: SITE.name,
    alternateName: [NAME.el, "Georgios Batzios", "George Batzios"], url: SITE.url + "/",
    image: SITE.url + sq(IMG.home1, 1500), jobTitle: "Sound Engineer",
    description: "Audio and sound engineer and musician in Athens: theater sound, live mixing, studio recording, mixing, composing and music technology.",
    email: "mailto:" + SITE.email,
    address: { "@type": "PostalAddress", addressLocality: "Athens", addressCountry: "GR" },
    alumniOf: [{ "@type": "CollegeOrUniversity", name: "Metropolitan College" }, { "@type": "EducationalOrganization", name: "IEK AKMI" }],
    knowsAbout: ["Sound engineering", "Live sound mixing", "Theater sound", "Qlab", "Ableton Live", "Max for Live", "Arduino", "Music production"],
    sameAs: SOCIAL.map((s) => s[1]),
  });
  const crumb_ld = (lang, crumbs) => ({
    "@type": "BreadcrumbList",
    itemListElement: [{ "@type": "ListItem", position: 1, name: NAME[lang], item: SITE.url + U(lang, "/") },
      ...crumbs.map(([n, p], i) => ({ "@type": "ListItem", position: i + 2, name: n, item: SITE.url + U(lang, p) }))],
  });

  function page(path, lang, title, desc, body, { ld = null, kicker = "", crumbs = null } = {}) {
    let full;
    if (title) full = `${title} — ${NAME[lang]}`;
    else if (lang === "el") full = `${NAME.el} (${NAME.en}) — ${L(SITE.role, lang)}`;
    else full = `${NAME.en} — ${L(SITE.role, lang)}`;
    const other = lang === "en" ? "el" : "en";
    const url = SITE.url + U(lang, path);
    const full_path = U(lang, path);
    const slug = full_path.replace(/^\/+|\/+$/g, "").split("/").join("-") || "home";
    const card = path !== "/404/" ? `/og/${slug}.png` : "/og/home.png";
    if (path !== "/404/") cards.push({ file: card, title: title || NAME[lang], kicker, footer: title ? NAME[lang] : "giorgosbatzios.com", tagline: L(SITE.role, lang) });
    const graph = [...(ld || [])];
    if (path !== "/" && path !== "/404/") graph.push(crumb_ld(lang, crumbs !== null ? crumbs : [[title, path]]));
    const ldtag = graph.length ? '<script type="application/ld+json">' + pyjson({ "@context": "https://schema.org", "@graph": graph }) + "</script>\n" : "";
    const copy = `© ${YEAR} ${NAME[lang]}` + (lang === "el" ? ` · ${NAME.en}` : "");
    let doc = `<!doctype html>
<html lang="${lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="dark">
<meta name="theme-color" content="#0d0d0e">
<title>${e(full)}</title>
<meta name="description" content="${e(desc)}">
<link rel="canonical" href="${url}">
<link rel="alternate" hreflang="en" href="${SITE.url}${U("en", path)}">
<link rel="alternate" hreflang="el" href="${SITE.url}${U("el", path)}">
<link rel="alternate" hreflang="x-default" href="${SITE.url}${U("en", path)}">
<meta property="og:type" content="website">
<meta property="og:locale" content="${lang === "en" ? "en_US" : "el_GR"}">
<meta property="og:title" content="${e(full)}">
<meta property="og:description" content="${e(desc)}">
<meta property="og:url" content="${url}">
<meta property="og:site_name" content="${NAME[lang]}">
<meta property="og:image" content="${SITE.url}${card}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="${e(full)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="${SITE.url}${card}">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/geist-var.woff" as="font" type="font/woff" crossorigin>
<link rel="stylesheet" href="/assets/style.css">
${ldtag}</head>
<body data-lang="${lang}">
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs><clipPath id="m-squircle" clipPathUnits="objectBoundingBox"><path d="M0.5,0 C0.768,0,0.894,0.056,0.919,0.081 C0.944,0.106,1,0.242,1,0.505 C1,0.768,0.947,0.891,0.919,0.919 C0.891,0.947,0.768,1,0.5,1 C0.202,1,0.11,0.948,0.081,0.919 C0.052,0.89,0,0.768,0,0.5 C0,0.232,0.053,0.109,0.081,0.081 C0.109,0.053,0.232,0,0.5,0"/></clipPath><clipPath id="m-octagon" clipPathUnits="objectBoundingBox"><path d="M0.5,0 L0.957,0.065,1,0.5,0.957,0.935 L0.5,1,0.043,0.935,0,0.5,0.043,0.065,0.5,0"/></clipPath></defs></svg>
<a class="skip" href="#main">${u("skip", lang)}</a>
<header class="site-head"><div class="wrap head-row">
<a class="mark dotted" href="${U(lang, "/")}">${e(NAME.en)}</a>
<div class="head-right">
<nav class="nav" id="nav" aria-label="Main">${nav(path, lang)}</nav>
<a class="lang" href="${U(other, path)}" hreflang="${other}" lang="${other}" title="${u("switch", lang)}">${other.toUpperCase()}</a>
<button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav" data-open="${u("menu", lang)}" data-close="${u("close", lang)}">${u("menu", lang)}</button>
</div>
</div></header>
<main id="main">
${body}
</main>
<footer class="site-foot"><div class="wrap foot-row">
${socials_html()}
<span class="copy">${copy}</span>
</div></footer>
<script src="/assets/site.js" defer></script>
</body>
</html>
`;
    const depth = full_path.split("/").filter(Boolean).length;
    const rel = "../".repeat(depth) || "./";
    if (path !== "/404/") doc = doc.split('href="/').join(`href="${rel}`).split('src="/assets').join(`src="${rel}assets`);
    if (path === "/404/") files["/404.html"] = doc;
    else files[full_path + "index.html"] = doc;
    PAGES.push(full_path);
  }

  const head = (title, eyebrow, lede = "") =>
    `<header class="wrap page-head"><p class="kicker">${eyebrow}</p><h1 class="dotted">${title}</h1>${lede ? `<p class="lede">${lede}</p>` : ""}</header>`;
  const roles_text = (roles, lang) => roles.map((r) => L(r, lang)).join(" · ");

  // ---------------------------------------------------------------- Home
  function build_home(lang) {
    const ys = [...new Set(THEATER.map((t) => parseInt(t.year, 10)))].sort((a, b) => a - b);
    const years = ys.length ? ys : [YEAR];
    const n_tech = ["m4l", "arduino", "plugins"].reduce((n, k) => n + D.tech[k].items.length, 0);
    const rows = [
      ["/theater/", u("theater", lang), tx("home_meta_theater", lang, { n: THEATER.length, from: years[0], to: years[years.length - 1] })],
      ["/studio/", u("studio", lang), tx("home_meta_studio", lang, { n: STUDIO.length })],
      ["/music/", u("music", lang), tx("home_meta_music", lang, { n: MUSIC.length })],
      ["/music-technology/", u("tech_long", lang), tx("home_meta_tech", lang, { n: n_tech })],
      ["/curriculum-vitae/", u("cv_long", lang), tx("home_meta_cv", lang)],
      ["/academic-portfolio/", u("academic_long", lang), tx("home_meta_academic", lang, { n: ACADEMIC.length })],
    ];
    const idx = rows.map(([h, n, m]) => `<a href="${U(lang, h)}"><span class="name">${n}</span><span class="meta">${m}</span></a>`).join("");
    const fields = SITE.fields.map((f) => `<li>${L(f, lang)}</li>`).join("");
    const sel = SELECTED.map((s) =>
      `<a class="sel" href="${U(lang, s.link)}"><div class="thumb"><img src="${sq(s.image, 800)}" alt="${e(s.title)}" loading="lazy" decoding="async" width="800" height="600"></div>` +
      `<div><p class="kicker">${L(s.kicker, lang)}</p><h3 lang="${lang_of(s.title)}">${e(s.title)}</h3><p class="line">${L(s.line, lang)}</p></div></a>`).join("");
    const sp = NAME.en.indexOf(" ");
    const first = sp < 0 ? NAME.en : NAME.en.slice(0, sp), last = sp < 0 ? "" : NAME.en.slice(sp + 1);
    const body = `
<div class="wrap">
  <section class="hero">
    <div>
      <h1 class="intro"><span class="ln"><span>${e(first)}</span></span><span class="ln"><span class="dotted">${e(last)}</span></span></h1>
      <p class="role">${L(SITE.role, lang)}</p>
    </div>
    <img class="hero-img mask-squircle" src="${sq(IMG.home1, 1200)}" alt="${NAME[lang]} — ${tx("home_photo1_alt", lang)}" width="1200" height="1200" fetchpriority="high">
  </section>
  <div class="wave-wrap" aria-hidden="true"><canvas class="wave"></canvas></div>
  <section class="split">
    <img class="split-img mask-octagon" src="${sq(IMG.home2, 1200)}" alt="${NAME[lang]} — ${tx("home_photo2_alt", lang)}" loading="lazy" decoding="async" width="1000" height="1200">
    <ul class="fields">${fields}</ul>
  </section>
  <section class="selected"><div class="sec-title"><h2>${u("selected", lang)}</h2></div><div class="sel-grid">${sel}</div></section>
  <nav class="index" aria-label="Sections">${idx}</nav>
</div>`;
    const website = { "@type": "WebSite", name: NAME[lang], url: SITE.url + U(lang, "/"), inLanguage: lang, alternateName: [NAME.en, NAME.el] };
    page("/", lang, "", tx("home_desc", lang), body, { ld: [person_ld(), website] });
  }

  // ---------------------------------------------------------------- Theater
  function build_theater(lang) {
    const shows = [...THEATER].sort((a, b) => parseInt(b.year, 10) - parseInt(a.year, 10));
    const rows = [];
    let last = null;
    for (const t of shows) {
      if (t.year !== last) { rows.push(`<h2 class="year">${t.year}</h2>`); last = t.year; }
      const link = t.link || "";
      let open_tag, close_tag, go;
      if (link) { open_tag = `<a class="show" href="${e(link)}" target="_blank" rel="noopener">`; close_tag = "</a>"; go = `<span class="go">${ARROW}</span>`; }
      else { open_tag = '<div class="show">'; close_tag = "</div>"; go = "<span></span>"; }
      rows.push(`${open_tag}
  <img src="${sq(t.poster, 300)}" alt="${u("poster", lang)}: ${e(t.title)}" loading="lazy" decoding="async" width="76" height="76">
  <div><h3 lang="${lang_of(t.title)}">${e(t.title)}</h3><p class="venue">${e(L(t.venue, lang))}</p></div>
  <p class="roles">${e(roles_text(t.roles, lang))}</p>
  ${go}
${close_tag}`);
    }
    const lede = tx("theater_lede", lang);
    const kick = `${THEATER.length} ${u("productions", lang)}`;
    const body = head(u("theater", lang), kick, lede) + `<div class="wrap">${rows.join("")}</div>`;
    const works = shows.map((t, i) => {
      const item = { "@type": "CreativeWork", name: t.title, genre: tx("theater_genre", lang), dateCreated: String(t.year) };
      if (t.link) item.url = t.link;
      Object.assign(item, { image: SITE.url + sq(t.poster, 1500), locationCreated: L(t.venue, lang),
        contributor: { "@id": SITE.url + "/#person" }, description: t.roles.map((r) => L(r, lang)).join(", ") });
      return { "@type": "ListItem", position: i + 1, item };
    });
    page("/theater/", lang, u("theater", lang), lede, body, { kicker: kick, ld: [{ "@type": "ItemList", name: u("theater", lang), itemListElement: works }] });
  }

  // ---------------------------------------------------------------- Studio
  function build_studio(lang) {
    const cat = (c) => (c in CAT_NAME ? L(CAT_NAME[c], lang) : c);
    const counts = Object.fromEntries(STUDIO_CATS.map((c) => [c, STUDIO.filter((s) => s.cats.includes(c)).length]));
    const btns = `<button type="button" data-cat="all" aria-pressed="true">${u("all", lang)}<span class="n">${STUDIO.length}</span></button>` +
      STUDIO_CATS.filter((c) => counts[c]).map((c) => `<button type="button" data-cat="${e(c)}" aria-pressed="false">${e(cat(c))}<span class="n">${counts[c]}</span></button>`).join("");
    const first = STUDIO.find((s) => s.youtube === FEATURED_STUDIO) || (STUDIO.length ? STUDIO[0] : null);
    const rest = STUDIO.filter((s) => s !== first);
    let feat = "";
    if (first) {
      const note_txt = L(first.note, lang);
      const note = note_txt ? `<p class="note">${e(note_txt)}</p>` : "";
      feat = `<article class="featured" data-cats="${first.cats.join("|")}">\n` +
        `  ${yt(first.youtube, first.title, lang)}\n` +
        `  <div><p class="kicker">${u("featured", lang)}</p><h3 style="margin-top:10px"><span lang="${lang_of(first.title)}">${e(first.title)}</span></h3>${note}` +
        `<p class="meta">${first.cats.map(cat).join(" · ")}</p></div>\n</article>`;
    }
    const cardsHtml = rest.map((s) =>
      `<article class="card" data-cats="${s.cats.join("|")}">\n` +
      `  ${yt(s.youtube, s.title, lang)}\n` +
      `  <div><h3><span lang="${lang_of(s.title)}">${e(s.title)}</span></h3><p class="meta">${s.cats.map(cat).join(" · ")} — ${String(s.date).slice(0, 4)}</p></div>\n</article>`).join("");
    const ys = STUDIO.map((s) => String(s.date).slice(0, 4)).sort();
    const yrs = ys.length ? ys : [String(YEAR)];
    const lede = tx("studio_lede", lang);
    const kick = tx("studio_kicker", lang, { n: STUDIO.length, from: yrs[0], to: yrs[yrs.length - 1] });
    const body = head(u("studio", lang), kick, lede) + (
      '\n<div class="wrap">\n' +
      `  <div class="filters" role="group" aria-label="${u("filter", lang)}">${btns}</div>\n` +
      `  ${feat}\n` +
      `  <div class="grid">${cardsHtml}</div>\n</div>`);
    const vids = [...(first ? [first] : []), ...rest].map((st, i) => ({ "@type": "ListItem", position: i + 1, item: {
      "@type": "VideoObject", name: st.title, uploadDate: st.date,
      description: st.cats.map(cat).join(" · ") + " — " + NAME[lang],
      thumbnailUrl: `https://i.ytimg.com/vi/${st.youtube}/hqdefault.jpg`,
      embedUrl: `https://www.youtube.com/embed/${st.youtube}`, contentUrl: `https://www.youtube.com/watch?v=${st.youtube}`,
      contributor: { "@id": SITE.url + "/#person" } } }));
    page("/studio/", lang, u("studio", lang), lede, body, { kicker: `${STUDIO.length} ${u("projects", lang)}`, ld: [{ "@type": "ItemList", name: u("studio", lang), itemListElement: vids }] });
  }

  // ---------------------------------------------------------------- Music
  function build_music(lang) {
    const items = MUSIC.map((m) => {
      const media = m.type === "sc" ? sc(m.id) : yt(m.id, m.title, lang);
      const note = L(m.note, lang);
      const n = note ? `<p class="note">${e(note)}</p>` : "";
      return `<article class="track">${media}<div class="text"><h2><span lang="${lang_of(m.title)}">${e(m.title)}</span></h2>` +
        `<p class="roles">${e(roles_text(m.roles, lang))}</p>${n}</div></article>`;
    });
    const lede = tx("music_lede", lang);
    const body = head(u("music", lang), tx("music_kicker", lang), lede) + `<div class="wrap">${items.join("")}</div>`;
    page("/music/", lang, u("music", lang), lede, body, { kicker: tx("music_kicker", lang) });
  }

  // ---------------------------------------------------------------- Music technology
  function cards_for(base, items, lang) {
    return items.map((p) => {
      const summ = L(p.summary, lang) ? `<p>${e(L(p.summary, lang))}</p>` : "";
      return `<a class="proj" href="${U(lang, base + p.slug + "/")}"><div class="thumb"><img src="${sq(p.cover, 800)}" alt="${e(p.title)}" loading="lazy" decoding="async" width="800" height="600"></div>` +
        `<div><h3>${e(p.title)}</h3>${summ}</div></a>`;
    }).join("");
  }
  function build_tech(lang) {
    const secs = SECTIONS.filter(([, k]) => D.tech[k].items.length).map(([b, k]) =>
      `<section><div class="sec-title"><h2><a href="${U(lang, b)}">${u(k, lang)}</a></h2><a class="small muted" href="${U(lang, b)}">${u("view_all", lang)} →</a></div>` +
      `<div class="proj-grid">${cards_for(b, D.tech[k].items, lang)}</div></section>`).join("");
    const lede = tx("tech_lede", lang);
    const body = head(u("tech_long", lang), tx("tech_kicker", lang), lede) + `<div class="wrap">${secs}</div>`;
    page("/music-technology/", lang, u("tech_long", lang), lede, body, { kicker: tx("tech_kicker", lang) });
    for (const [base, key] of SECTIONS) {
      const items = D.tech[key].items;
      const sect_lede = L(D.tech[key].lede, lang);
      const title = u(key, lang);
      const b = head(title, u("tech_long", lang), sect_lede) + `<div class="wrap"><div class="proj-grid">${cards_for(base, items, lang)}</div></div>`;
      page(base, lang, title, `${title} — ${NAME[lang]}. ${sect_lede}`, b, { kicker: u("tech_long", lang), crumbs: [[u("tech_long", lang), "/music-technology/"], [title, base]] });
      items.forEach((_, i) => build_project(base, title, items, i, lang));
    }
  }
  function block(b, title, lang) {
    const k = b.type;
    if (k === "p") return `<p>${e(L(b.text, lang))}</p>`;
    if (k === "h") return `<h2>${e(L(b.text, lang))}</h2>`;
    if (k === "ul") return "<ul>" + b.items.map((x) => `<li>${e(L(x, lang))}</li>`).join("") + "</ul>";
    if (k === "img") {
      const cap = L(b.caption, lang);
      const fc = cap ? `<figcaption>${e(cap)}</figcaption>` : "";
      const alt = cap || `${title} — ${u("photo", lang)}`;
      return `<figure class="zoomable"><img src="${sq(b.src, 1500)}" alt="${e(alt)}" loading="lazy" decoding="async">${fc}</figure>`;
    }
    if (k === "yt") return yt(b.id, title, lang);
    if (k === "link") return `<a class="ext" href="${e(b.url)}" target="_blank" rel="noopener">${e(L(b.label, lang))}${ARROW}</a>`;
    if (k === "mono") return `<div class="mono">${e(b.text)}</div>`;
    return "";
  }
  function build_project(base, sect, items, i, lang) {
    const p = items[i];
    const d = p.download;
    const dl = d && d.url ? `<a class="btn" href="${e(d.url)}" target="_blank" rel="noopener">${e(L(d.label, lang))}${ARROW}</a>` : "";
    const blocks = p.blocks.map((b) => block(b, p.title, lang)).join("");
    const prev_ = i > 0 ? items[i - 1] : null;
    const next_ = i < items.length - 1 ? items[i + 1] : null;
    const left = prev_ ? `<a href="${U(lang, base + prev_.slug + "/")}"><span>← ${u("prev", lang)}</span><strong>${e(prev_.title)}</strong></a>`
      : `<a href="${U(lang, base)}"><span>← ${u("back", lang)}</span><strong>${sect}</strong></a>`;
    const right = next_ ? `<a href="${U(lang, base + next_.slug + "/")}"><span>${u("next", lang)} →</span><strong>${e(next_.title)}</strong></a>`
      : `<a href="${U(lang, base)}"><span>${u("back", lang)}</span><strong>${sect}</strong></a>`;
    const summ = L(p.summary, lang);
    const summary = summ ? `<p class="lede">${e(summ)}</p>` : "";
    const cover = p.cover ? `<figure class="cover zoomable"><img src="${sq(p.cover, 1500)}" alt="${e(p.title)}"></figure>` : "";
    const body = `<header class="wrap page-head"><p class="kicker"><a href="${U(lang, base)}">← ${sect}</a></p><h1 class="dotted">${e(p.title)}</h1>${summary}</header>` +
      `<div class="wrap"><div class="article">` + cover + `${dl}${blocks}</div><nav class="pager" aria-label="${u("projects", lang)}">${left}${right}</nav></div>`;
    const path = base + p.slug + "/";
    const image = p.cover ? { image: SITE.url + sq(p.cover, 1500) } : {};
    let item;
    if (base === "/arduino-projects/") {
      item = { "@type": "CreativeWork", name: p.title, description: summ || sect, ...image,
        author: { "@id": SITE.url + "/#person" }, url: SITE.url + U(lang, path), inLanguage: lang };
    } else {
      item = { "@type": "SoftwareApplication", name: p.title, description: summ || sect,
        applicationCategory: "MultimediaApplication",
        applicationSubCategory: base === "/max4live-devices/" ? "Max for Live device" : "Audio plugin",
        operatingSystem: base === "/max4live-devices/" ? "Ableton Live (Max for Live)" : "Windows, macOS",
        ...image, author: { "@id": SITE.url + "/#person" }, url: SITE.url + U(lang, path),
        offers: { "@type": "Offer", price: "0", priceCurrency: "EUR" } };
      if (d && d.url) item.downloadUrl = d.url;
    }
    page(path, lang, p.title, `${p.title} — ${summ || sect} · ${NAME[lang]}`, body, { kicker: sect, ld: [item],
      crumbs: [[u("tech_long", lang), "/music-technology/"], [sect, base], [p.title, path]] });
  }

  // ---------------------------------------------------------------- Academic
  function build_academic(lang) {
    const cardsHtml = ACADEMIC.map((a) => {
      const t = L(a.title, lang), video = a.video, reports = a.reports || [];
      const links = [];
      if (video) links.push(`<a class="ext" href="${e(video)}" target="_blank" rel="noopener">${video.includes("youtu") ? u("watch", lang) : u("files", lang)}${ARROW}</a>`);
      for (const r of reports) links.push(`<a class="ext" href="${e(r.url)}" target="_blank" rel="noopener">${e(L(r.label, lang))}${ARROW}</a>`);
      const main = video || (reports.length ? reports[0].url : "#");
      return `<article class="acad"><a class="thumb" href="${e(main)}" target="_blank" rel="noopener" tabindex="-1"><img src="${sq(a.thumb, 800)}" alt="${e(t)}" loading="lazy" decoding="async" width="800" height="450"></a>` +
        `<div><p class="kicker">${e(L(a.inst, lang))}</p><h3 style="margin-top:4px">${e(t)}</h3></div><div class="links">${links.join("")}</div></article>`;
    });
    const lede = tx("academic_lede", lang);
    const body = head(u("academic_long", lang), tx("academic_kicker", lang), lede) + `<div class="wrap"><div class="grid">${cardsHtml.join("")}</div></div>`;
    page("/academic-portfolio/", lang, u("academic_long", lang), lede, body, { kicker: tx("academic_card_kicker", lang) });
  }

  // ---------------------------------------------------------------- CV
  function build_cv(lang) {
    const entries = (items) => items.map((x) => {
      const kind = L(x.kind, lang);
      const k = kind ? ` <span class="muted" style="font-weight:400">· ${e(kind)}</span>` : "";
      return `<div class="entry"><span class="when">${e(L(x.when, lang))}</span><div><h3>${e(L(x.title, lang))}${k}</h3>` +
        `<p class="org">${e(L(x.org, lang))}, ${e(L(x.place, lang))}</p><p>${e(L(x.desc, lang))}</p></div></div>`;
    }).join("");
    const li = (xs) => "<ul>" + xs.map((x) => `<li>${e(x.name)}<span>${e(x.org)}</span></li>`).join("") + "</ul>";
    const skills = CV.skills.map((s) => `<li>${e(L(s, lang))}</li>`).join("");
    const lk = SOCIAL.find(([n]) => n === "LinkedIn");
    const linkedin = lk ? lk[1] : "";
    let li_row = "";
    if (linkedin) {
      const lastPart = linkedin.replace(/\/+$/, "").split("/").pop();
      const dash = lastPart.lastIndexOf("-");
      const handle = dash < 0 ? lastPart : lastPart.slice(0, dash);
      li_row = `<div><dt>LinkedIn</dt><dd><a class="text-link" href="${linkedin}" target="_blank" rel="noopener">${e(handle)}</a></dd></div>`;
    }
    const body = head(u("cv_long", lang), tx("cv_kicker", lang)) + `
<div class="wrap cv">
  <div>
    <p class="objective">${e(L(CV.objective, lang))}</p>
    <section><h2 class="h">${u("work", lang)}</h2>${entries(CV.work)}</section>
    <section><h2 class="h">${u("education", lang)}</h2>${entries(CV.education)}</section>
  </div>
  <aside class="side">
    <div><h2 class="h">${u("contact", lang)}</h2><dl>
      <div><dt>${u("based", lang)}</dt><dd>${u("athens_gr", lang)}</dd></div>
      <div><dt>${u("phone", lang)}</dt><dd>${SITE.phone}</dd></div>
      <div><dt>Email</dt><dd><a class="text-link" href="mailto:${SITE.email}">${SITE.email}</a></dd></div>
      ${li_row}
    </dl></div>
    <div><h2 class="h">${u("skills", lang)}</h2><ul>${skills}</ul></div>
    <div><h2 class="h">${u("software", lang)}</h2>${li(CV.software)}</div>
    <div><h2 class="h">${u("mixers", lang)}</h2>${li(CV.mixers)}</div>
    <div><h2 class="h">${u("certs", lang)}</h2>${li(CV.certifications)}</div>
  </aside>
</div>`;
    page("/curriculum-vitae/", lang, u("cv_long", lang), tx("cv_desc", lang), body, { kicker: tx("cv_kicker", lang),
      ld: [{ "@type": "ProfilePage", name: u("cv_long", lang), inLanguage: lang, mainEntity: person_ld() }] });
  }

  // ---------------------------------------------------------------- Contact
  function build_contact(lang) {
    const live = !!FORM_KEY;
    const btn = live ? u("send", lang) : u("write", lang);
    const hint = live ? "" : `<p class="hint">${u("hint_mail", lang)}</p>`;
    const lede = tx("contact_lede", lang);
    const body = head(u("contact", lang), u("athens_gr", lang), lede) + `
<div class="wrap contact">
  <div>
    <a class="big-mail" href="mailto:${SITE.email}">${SITE.email}</a>
    <form class="form" id="contact-form" data-to="${SITE.email}" data-key="${FORM_KEY}"
      data-sending="${e(u("sending", lang))}" data-sent="${e(u("sent", lang))}" data-failed="${e(u("failed", lang))}">
      <label for="f-name">${u("name", lang)}<input id="f-name" name="name" required autocomplete="name"></label>
      <label for="f-email">${u("your_email", lang)}<input id="f-email" name="email" type="email" required autocomplete="email"></label>
      <label for="f-msg">${u("message", lang)}<textarea id="f-msg" name="message" required></textarea></label>
      <input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
      <button class="btn" type="submit">${btn}</button>
      ${hint}
      <p class="form-status" role="status" aria-live="polite"></p>
    </form>
    <div style="margin-top:44px">${socials_html()}</div>
  </div>
  <img class="photo mask-squircle" src="${sq(IMG.contact, 1000)}" alt="${NAME[lang]}" loading="lazy" decoding="async" width="750" height="1123">
</div>`;
    page("/contact/", lang, u("contact", lang), tx("contact_desc", lang), body, { kicker: u("athens_gr", lang),
      ld: [{ "@type": "ContactPage", name: u("contact", lang), inLanguage: lang, about: { "@id": SITE.url + "/#person" } }] });
  }

  for (const lang of LANGS) {
    build_home(lang); build_theater(lang); build_studio(lang); build_music(lang); build_tech(lang);
    build_academic(lang); build_cv(lang); build_contact(lang);
  }

  // ---------------------------------------------------------------- 404, redirects, sitemap, headers, robots
  const body404 = '<section class="wrap nf">' +
    '<p class="kicker">Error 404</p>' +
    '<h1 class="dotted">No signal</h1>' +
    '<div class="flat" aria-hidden="true"><span></span></div>' +
    `<p class="lede">${u("notfound", "en")}<br><span lang="el">${u("notfound", "el")}</span></p>` +
    `<p class="nf-links"><a class="btn" href="/">${u("home", "en")}</a> <a class="btn ghost" href="/el/" lang="el">${u("home", "el")}</a></p>` +
    "</section>";
  page("/404/", "en", "Page not found", "Page not found.", body404);

  const lines = [...STUDIO.filter((s) => s.old).map((s) => `/studio/v/${s.old}  /studio/  301`), "/studio/v/*  /studio/  301"];
  for (const [base, key] of SECTIONS) {
    for (const p of D.tech[key].items) if (p.old && p.old !== p.slug) lines.push(`${base.replace(/\/+$/, "")}/${p.old}  ${base}${p.slug}/  301`);
  }
  lines.push("/studio/recording  /studio/  301", "/studio/mixing  /studio/  301", "/studio/production  /studio/  301",
    "/studio/video-edit  /studio/  301", "/studio/custom-sound-library  /studio/  301", "/cart  /  301");
  files["/_redirects"] = lines.join("\n") + "\n";

  const urls = [];
  for (const p of PAGES) {
    if (p === "/404/" || p.startsWith("/el/")) continue;
    const en = SITE.url + p, gr = SITE.url + "/el" + p;
    const alt = `<xhtml:link rel="alternate" hreflang="en" href="${en}"/>` + `<xhtml:link rel="alternate" hreflang="el" href="${gr}"/>`;
    urls.push(`<url><loc>${en}</loc>${alt}</url><url><loc>${gr}</loc>${alt}</url>`);
  }
  files["/sitemap.xml"] = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" ' +
    `xmlns:xhtml="http://www.w3.org/1999/xhtml">${urls.join("")}</urlset>\n`;
  files["/_headers"] = "/assets/img/*\n  Cache-Control: public, max-age=31536000, immutable\n" +
    "/assets/fonts/*\n  Cache-Control: public, max-age=31536000, immutable\n" +
    "/og/*\n  Cache-Control: public, max-age=604800\n" +
    "/assets/*.css\n  Cache-Control: public, max-age=3600\n" +
    "/assets/*.js\n  Cache-Control: public, max-age=3600\n" +
    "/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n";
  files["/robots.txt"] = `User-agent: *\nAllow: /\nDisallow: /editor/\nSitemap: ${SITE.url}/sitemap.xml\n`;

  return { files, cards, pages: PAGES.length };
}
