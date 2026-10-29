"""Builds the bilingual static site into ../site from content.json.  Run: python3 source/build.py
English lives at /, Greek at /el/. content.json is edited by GB EDITOR (editor.giorgosbatzios.com) or by hand."""
import html, json, os, re, shutil, subprocess
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "site")
with open(os.path.join(HERE, "content.json"), encoding="utf-8") as _f:
    D = json.load(_f)


def _clean(x):
    """Texts typed in the editor are plain text: no HTML can sneak into the pages."""
    if isinstance(x, dict):
        return {k: _clean(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_clean(v) for v in x]
    if isinstance(x, str):
        return x.replace("<", "‹").replace(">", "›").replace('"', "”").strip()
    return x


D = _clean(D)

try:  # share-card images need Pillow; the site still builds without it
    import ogcard
except Exception as _err:  # pragma: no cover
    ogcard = None
    print("share cards skipped:", _err)

e = html.escape
LANGS = ("en", "el")
PREFIX = {"en": "", "el": "/el"}

SITE = D["site"]
SOCIAL = [(s["name"], s["url"]) for s in D["social"]]
IMG = D["images"]
FORM_KEY = SITE.get("form_key", "")
UI = D["ui"]
TX = D["text"]
THEATER = D["theater"]
STUDIO = D["studio"]
STUDIO_CATS = [c["id"] for c in D["studio_cats"]]
CAT_NAME = {c["id"]: c for c in D["studio_cats"]}
FEATURED_STUDIO = D["featured_studio"]
MUSIC = D["music"]
SELECTED = D["selected"]
ACADEMIC = D["academic"]
CV = D["cv"]
NAME = {"en": SITE["name"], "el": SITE.get("name_el") or SITE["name"]}
GREEK = re.compile(r"[\u0370-\u03ff\u1f00-\u1fff]")


def L(x, lang):
    """Pick the language version of a text (plain strings are the same in both)."""
    if x is None:
        return ""
    if isinstance(x, dict):
        return x.get(lang) or x.get("en") or ""
    return x


def U(lang, path):
    return PREFIX[lang] + path


def u(key, lang):
    return L(UI[key], lang)


def tx(key, lang, **kw):
    s = L(TX[key], lang)
    for k, v in kw.items():
        s = s.replace("{" + k + "}", str(v))
    return s


def lang_of(text):
    return "el" if GREEK.search(text or "") else "en"


def sq(url, w=1000):
    """Images live in /assets/img as <name>.webp plus a lighter <name>-sm.webp for thumbnails."""
    if not url:
        return ""
    if w <= 800 and url.startswith("/assets/img/"):
        root, ext = os.path.splitext(url)
        if not root.endswith("-sm"):
            small = root + "-sm" + ext
            if os.path.exists(os.path.join(HERE, small.lstrip("/"))):
                return small
    return url


def yt(vid, title, lang):
    return (f'<div class="yt" data-id="{vid}" data-title="{e(title)}"><button type="button" aria-label="{u("play", lang)}: {e(title)}">'
            f'<img src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" alt="{e(title)} — {u("video", lang)}" loading="lazy" decoding="async">'
            f'<span class="play"></span></button></div>')


ARROW = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'

# Simple outline icons for the social links (same size and stroke for all)
_S = 'fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"'
ICONS = {
    "Instagram": f'<rect x="3" y="3" width="18" height="18" rx="5" {_S}/><circle cx="12" cy="12" r="4" {_S}/><circle cx="17.2" cy="6.8" r="1.1" fill="currentColor"/>',
    "YouTube": f'<rect x="2.5" y="5.5" width="19" height="13" rx="4" {_S}/><path d="M10.2 9.3v5.4l4.6-2.7z" fill="currentColor"/>',
    "Facebook": f'<circle cx="12" cy="12" r="9.5" {_S}/><path d="M13.2 21.4V12.5h2.6M13.2 21.4V9.3c0-1.3.7-2 2-2h1.3M10.4 12.5h2.8" {_S}/>',
    "LinkedIn": f'<rect x="3" y="3" width="18" height="18" rx="3.5" {_S}/><path d="M8 10.5V17M11.6 17v-6.5M11.6 13.4c0-1.7 1.1-2.9 2.6-2.9s2.4 1.1 2.4 2.9V17" {_S}/><circle cx="8" cy="7.5" r="1.1" fill="currentColor"/>',
    "Linktree": f'<path d="M12 21.5V13M5 9.5h14M7 4.5l5 5 5-5M7 14.5l5-5 5 5" {_S}/>',
    "_link": f'<path d="M10 14a4.5 4.5 0 0 0 6.4 0l3-3a4.5 4.5 0 0 0-6.4-6.4l-1 1M14 10a4.5 4.5 0 0 0-6.4 0l-3 3a4.5 4.5 0 0 0 6.4 6.4l1-1" {_S}/>',
}


def socials_html(extra_class=""):
    items = "".join(f'<li><a href="{url}" target="_blank" rel="noopener" aria-label="{e(n)}" title="{e(n)}">'
                    f'<svg viewBox="0 0 24 24" aria-hidden="true">{ICONS.get(n, ICONS["_link"])}</svg></a></li>' for n, url in SOCIAL)
    return f'<ul class="socials {extra_class}">{items}</ul>'


def sc(track):
    """SoundCloud player: track is either the numeric track id or the normal soundcloud.com link."""
    from urllib.parse import quote
    src = f"https%3A//api.soundcloud.com/tracks/{track}" if str(track).isdigit() else quote(str(track), safe="")
    return (f'<div class="sc"><iframe loading="lazy" title="SoundCloud player" allow="autoplay" '
            f'src="https://w.soundcloud.com/player/?url={src}&color=%23b9472f&visual=true&show_artwork=true"></iframe></div>')


NAV = [("/theater/", "theater"), ("/studio/", "studio"), ("/music/", "music"), ("MT", "tech"),
       ("/curriculum-vitae/", "cv"), ("/academic-portfolio/", "academic"), ("/contact/", "contact")]
MT = [("/music-technology/", "overview"), ("/max4live-devices/", "m4l"), ("/arduino-projects/", "arduino"), ("/daw-plugins/", "plugins")]


def nav(cur, lang):
    out = []
    for href, key in NAV:
        if href == "MT":
            curmt = any(cur.startswith(h) for h, _ in MT)
            subs = "".join(f'<a href="{U(lang, h)}"{" aria-current=page" if cur == h else ""}>{u(k, lang)}</a>' for h, k in MT)
            out.append(f'<details class="{"is-current" if curmt else ""}"><summary>{u(key, lang)}</summary><div class="sub">{subs}</div></details>')
        else:
            ac = ' aria-current="page"' if cur.startswith(href) else ""
            out.append(f'<a href="{U(lang, href)}"{ac}>{u(key, lang)}</a>')
    return "".join(out)


PAGES = {}


def person_ld():
    return {
        "@type": "Person", "@id": SITE["url"] + "/#person", "name": SITE["name"],
        "alternateName": [NAME["el"], "Georgios Batzios", "George Batzios"], "url": SITE["url"] + "/",
        "image": SITE["url"] + sq(IMG["home1"], 1500), "jobTitle": "Sound Engineer",
        "description": "Audio and sound engineer and musician in Athens: theater sound, live mixing, studio recording, mixing, composing and music technology.",
        "email": "mailto:" + SITE["email"],
        "address": {"@type": "PostalAddress", "addressLocality": "Athens", "addressCountry": "GR"},
        "alumniOf": [{"@type": "CollegeOrUniversity", "name": "Metropolitan College"},
                     {"@type": "EducationalOrganization", "name": "IEK AKMI"}],
        "knowsAbout": ["Sound engineering", "Live sound mixing", "Theater sound", "Qlab", "Ableton Live", "Max for Live", "Arduino", "Music production"],
        "sameAs": [s[1] for s in SOCIAL],
    }


def crumb_ld(lang, crumbs):
    items = [{"@type": "ListItem", "position": 1, "name": NAME[lang], "item": SITE["url"] + U(lang, "/")}]
    for i, (n, p) in enumerate(crumbs, 2):
        items.append({"@type": "ListItem", "position": i, "name": n, "item": SITE["url"] + U(lang, p)})
    return {"@type": "BreadcrumbList", "itemListElement": items}


def page(path, lang, title, desc, body, og=None, ld=None, kicker="", crumbs=None):
    """path is the language-neutral path, e.g. /theater/. ld: list of schema.org objects."""
    if title:
        full = f"{title} — {NAME[lang]}"
    elif lang == "el":
        full = f"{NAME['el']} ({NAME['en']}) — {L(SITE['role'], lang)}"
    else:
        full = f"{NAME['en']} — {L(SITE['role'], lang)}"
    other = "el" if lang == "en" else "en"
    url = SITE["url"] + U(lang, path)
    # share preview card for this page
    full_path0 = U(lang, path)
    slug = full_path0.strip("/").replace("/", "-") or "home"
    card = f"/og/{slug}.png" if path != "/404/" else "/og/home.png"
    if path != "/404/" and ogcard:
        ogcard.make(os.path.join(OUT, card.lstrip("/")), title or NAME[lang], kicker,
                    NAME[lang] if title else "giorgosbatzios.com", L(SITE["role"], lang))
    graph = list(ld or [])
    if path not in ("/", "/404/"):
        graph.append(crumb_ld(lang, crumbs if crumbs is not None else [(title, path)]))
    ldtag = ""
    if graph:
        ldtag = '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False) + "</script>\n"
    copy = f"© {date.today().year} {NAME[lang]}" + (f" · {NAME['en']}" if lang == "el" else "")
    doc = f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="dark">
<meta name="theme-color" content="#0d0d0e">
<title>{e(full)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="en" href="{SITE['url']}{U('en', path)}">
<link rel="alternate" hreflang="el" href="{SITE['url']}{U('el', path)}">
<link rel="alternate" hreflang="x-default" href="{SITE['url']}{U('en', path)}">
<meta property="og:type" content="website">
<meta property="og:locale" content="{'en_US' if lang == 'en' else 'el_GR'}">
<meta property="og:title" content="{e(full)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="{NAME[lang]}">
<meta property="og:image" content="{SITE['url']}{card}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(full)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{SITE['url']}{card}">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/geist-var.woff" as="font" type="font/woff" crossorigin>
<link rel="stylesheet" href="/assets/style.css">
{ldtag}</head>
<body data-lang="{lang}">
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs><clipPath id="m-squircle" clipPathUnits="objectBoundingBox"><path d="M0.5,0 C0.768,0,0.894,0.056,0.919,0.081 C0.944,0.106,1,0.242,1,0.505 C1,0.768,0.947,0.891,0.919,0.919 C0.891,0.947,0.768,1,0.5,1 C0.202,1,0.11,0.948,0.081,0.919 C0.052,0.89,0,0.768,0,0.5 C0,0.232,0.053,0.109,0.081,0.081 C0.109,0.053,0.232,0,0.5,0"/></clipPath><clipPath id="m-octagon" clipPathUnits="objectBoundingBox"><path d="M0.5,0 L0.957,0.065,1,0.5,0.957,0.935 L0.5,1,0.043,0.935,0,0.5,0.043,0.065,0.5,0"/></clipPath></defs></svg>
<a class="skip" href="#main">{u('skip', lang)}</a>
<header class="site-head"><div class="wrap head-row">
<a class="mark dotted" href="{U(lang, '/')}">{e(NAME['en'])}</a>
<div class="head-right">
<nav class="nav" id="nav" aria-label="Main">{nav(path, lang)}</nav>
<a class="lang" href="{U(other, path)}" hreflang="{other}" lang="{other}" title="{u('switch', lang)}">{other.upper()}</a>
<button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav" data-open="{u('menu', lang)}" data-close="{u('close', lang)}">{u('menu', lang)}</button>
</div>
</div></header>
<main id="main">
{body}
</main>
<footer class="site-foot"><div class="wrap foot-row">
{socials_html()}
<span class="copy">{copy}</span>
</div></footer>
<script src="/assets/site.js" defer></script>
</body>
</html>
"""
    full_path = U(lang, path)
    depth = len([p for p in full_path.strip("/").split("/") if p])
    rel = "../" * depth or "./"
    if path != "/404/":  # the 404 page is shown at any address, so it keeps root links
        doc = doc.replace('href="/', f'href="{rel}').replace('src="/assets', f'src="{rel}assets')
    d = os.path.join(OUT, full_path.strip("/"))
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
        f.write(doc)
    PAGES[full_path] = doc


def head(title, eyebrow, lede=""):
    l = f'<p class="lede">{lede}</p>' if lede else ""
    return f'<header class="wrap page-head"><p class="kicker">{eyebrow}</p><h1 class="dotted">{title}</h1>{l}</header>'


def el(text):  # titles that are written in Greek
    return f'<span lang="el">{e(text)}</span>'


# ------------------------------------------------------------------ Home
def build_home(lang):
    years = sorted({int(t["year"]) for t in THEATER}) or [date.today().year]
    n_tech = sum(len(D["tech"][k]["items"]) for k in ("m4l", "arduino", "plugins"))
    rows = [
        ("/theater/", u("theater", lang), tx("home_meta_theater", lang, n=len(THEATER), **{"from": years[0], "to": years[-1]})),
        ("/studio/", u("studio", lang), tx("home_meta_studio", lang, n=len(STUDIO))),
        ("/music/", u("music", lang), tx("home_meta_music", lang, n=len(MUSIC))),
        ("/music-technology/", u("tech_long", lang), tx("home_meta_tech", lang, n=n_tech)),
        ("/curriculum-vitae/", u("cv_long", lang), tx("home_meta_cv", lang)),
        ("/academic-portfolio/", u("academic_long", lang), tx("home_meta_academic", lang, n=len(ACADEMIC))),
    ]
    idx = "".join(f'<a href="{U(lang, h)}"><span class="name">{n}</span><span class="meta">{m}</span></a>' for h, n, m in rows)
    fields = "".join(f"<li>{L(f, lang)}</li>" for f in SITE["fields"])
    sel = "".join(
        f'<a class="sel" href="{U(lang, s["link"])}"><div class="thumb"><img src="{sq(s["image"], 800)}" alt="{e(s["title"])}" loading="lazy" decoding="async" width="800" height="600"></div>'
        f'<div><p class="kicker">{L(s["kicker"], lang)}</p><h3 lang="{lang_of(s["title"])}">{e(s["title"])}</h3><p class="line">{L(s["line"], lang)}</p></div></a>'
        for s in SELECTED)
    first, _, last = NAME["en"].partition(" ")
    body = f"""
<div class="wrap">
  <section class="hero">
    <div>
      <h1 class="intro"><span class="ln"><span>{e(first)}</span></span><span class="ln"><span class="dotted">{e(last)}</span></span></h1>
      <p class="role">{L(SITE['role'], lang)}</p>
    </div>
    <img class="hero-img mask-squircle" src="{sq(IMG['home1'], 1200)}" alt="{NAME[lang]} — {tx('home_photo1_alt', lang)}" width="1200" height="1200" fetchpriority="high">
  </section>
  <div class="wave-wrap" aria-hidden="true"><canvas class="wave"></canvas></div>
  <section class="split">
    <img class="split-img mask-octagon" src="{sq(IMG['home2'], 1200)}" alt="{NAME[lang]} — {tx('home_photo2_alt', lang)}" loading="lazy" decoding="async" width="1000" height="1200">
    <ul class="fields">{fields}</ul>
  </section>
  <section class="selected"><div class="sec-title"><h2>{u('selected', lang)}</h2></div><div class="sel-grid">{sel}</div></section>
  <nav class="index" aria-label="Sections">{idx}</nav>
</div>"""
    website = {"@type": "WebSite", "name": NAME[lang], "url": SITE["url"] + U(lang, "/"), "inLanguage": lang,
               "alternateName": [NAME["en"], NAME["el"]]}
    page("/", lang, "", tx("home_desc", lang), body, ld=[person_ld(), website])


# ------------------------------------------------------------------ Theater
def roles_text(roles, lang):
    return " · ".join(L(r, lang) for r in roles)


def build_theater(lang):
    shows = sorted(THEATER, key=lambda t: -int(t["year"]))  # stable: keeps the editor's order inside a year
    rows, last = [], None
    for t in shows:
        if t["year"] != last:
            rows.append(f'<h2 class="year">{t["year"]}</h2>')
            last = t["year"]
        link = t.get("link") or ""
        if link:
            open_tag, close_tag, go = f'<a class="show" href="{e(link)}" target="_blank" rel="noopener">', "</a>", f'<span class="go">{ARROW}</span>'
        else:
            open_tag, close_tag, go = '<div class="show">', "</div>", "<span></span>"
        rows.append(f'''{open_tag}
  <img src="{sq(t["poster"], 300)}" alt="{u('poster', lang)}: {e(t["title"])}" loading="lazy" decoding="async" width="76" height="76">
  <div><h3 lang="{lang_of(t["title"])}">{e(t["title"])}</h3><p class="venue">{e(L(t["venue"], lang))}</p></div>
  <p class="roles">{e(roles_text(t["roles"], lang))}</p>
  {go}
{close_tag}''')
    lede = tx("theater_lede", lang)
    kick = f"{len(THEATER)} {u('productions', lang)}"
    body = head(u("theater", lang), kick, lede) + f'<div class="wrap">{"".join(rows)}</div>'
    works = []
    for i, t in enumerate(shows, 1):
        item = {"@type": "CreativeWork", "name": t["title"], "genre": tx("theater_genre", lang), "dateCreated": str(t["year"])}
        if t.get("link"):
            item["url"] = t["link"]
        item.update({"image": SITE["url"] + sq(t["poster"], 1500), "locationCreated": L(t["venue"], lang),
                     "contributor": {"@id": SITE["url"] + "/#person"}, "description": ", ".join(L(r, lang) for r in t["roles"])})
        works.append({"@type": "ListItem", "position": i, "item": item})
    page("/theater/", lang, u("theater", lang), lede, body, kicker=kick,
         ld=[{"@type": "ItemList", "name": u("theater", lang), "itemListElement": works}])


# ------------------------------------------------------------------ Studio
def build_studio(lang):
    def cat(c):
        return L(CAT_NAME[c], lang) if c in CAT_NAME else c

    counts = {c: sum(c in s["cats"] for s in STUDIO) for c in STUDIO_CATS}
    btns = f'<button type="button" data-cat="all" aria-pressed="true">{u("all", lang)}<span class="n">{len(STUDIO)}</span></button>' + "".join(
        f'<button type="button" data-cat="{e(c)}" aria-pressed="false">{e(cat(c))}<span class="n">{counts[c]}</span></button>' for c in STUDIO_CATS if counts[c])
    first = next((s for s in STUDIO if s["youtube"] == FEATURED_STUDIO), STUDIO[0] if STUDIO else None)
    rest = [s for s in STUDIO if s is not first]
    feat = ""
    if first:
        note_txt = L(first.get("note"), lang)
        note = f'<p class="note">{e(note_txt)}</p>' if note_txt else ""
        feat = (f'<article class="featured" data-cats="{"|".join(first["cats"])}">\n'
                f'  {yt(first["youtube"], first["title"], lang)}\n'
                f'  <div><p class="kicker">{u("featured", lang)}</p><h3 style="margin-top:10px"><span lang="{lang_of(first["title"])}">{e(first["title"])}</span></h3>{note}'
                f'<p class="meta">{" · ".join(cat(c) for c in first["cats"])}</p></div>\n</article>')
    cards = "".join(
        f'<article class="card" data-cats="{"|".join(s["cats"])}">\n'
        f'  {yt(s["youtube"], s["title"], lang)}\n'
        f'  <div><h3><span lang="{lang_of(s["title"])}">{e(s["title"])}</span></h3><p class="meta">{" · ".join(cat(c) for c in s["cats"])} — {s["date"][:4]}</p></div>\n</article>'
        for s in rest)
    yrs = sorted(s["date"][:4] for s in STUDIO) or [str(date.today().year)]
    lede = tx("studio_lede", lang)
    kick = tx("studio_kicker", lang, n=len(STUDIO), **{"from": yrs[0], "to": yrs[-1]})
    body = head(u("studio", lang), kick, lede) + (
        '\n<div class="wrap">\n'
        f'  <div class="filters" role="group" aria-label="{u("filter", lang)}">{btns}</div>\n'
        f'  {feat}\n'
        f'  <div class="grid">{cards}</div>\n</div>')
    vids = [{"@type": "ListItem", "position": i, "item": {
        "@type": "VideoObject", "name": st["title"], "uploadDate": st["date"],
        "description": " · ".join(cat(c) for c in st["cats"]) + " — " + NAME[lang],
        "thumbnailUrl": f"https://i.ytimg.com/vi/{st['youtube']}/hqdefault.jpg",
        "embedUrl": f"https://www.youtube.com/embed/{st['youtube']}", "contentUrl": f"https://www.youtube.com/watch?v={st['youtube']}",
        "contributor": {"@id": SITE["url"] + "/#person"}}} for i, st in enumerate(([first] if first else []) + rest, 1)]
    page("/studio/", lang, u("studio", lang), lede, body, kicker=f"{len(STUDIO)} {u('projects', lang)}",
         ld=[{"@type": "ItemList", "name": u("studio", lang), "itemListElement": vids}])


# ------------------------------------------------------------------ Music
def build_music(lang):
    items = []
    for m in MUSIC:
        media = sc(m["id"]) if m["type"] == "sc" else yt(m["id"], m["title"], lang)
        note = L(m.get("note"), lang)
        n = f'<p class="note">{e(note)}</p>' if note else ""
        items.append(f'<article class="track">{media}<div class="text"><h2><span lang="{lang_of(m["title"])}">{e(m["title"])}</span></h2>'
                     f'<p class="roles">{e(roles_text(m["roles"], lang))}</p>{n}</div></article>')
    lede = tx("music_lede", lang)
    body = head(u("music", lang), tx("music_kicker", lang), lede) + f'<div class="wrap">{"".join(items)}</div>'
    page("/music/", lang, u("music", lang), lede, body, kicker=tx("music_kicker", lang))


# ------------------------------------------------------------------ Music technology
SECTIONS = [("/max4live-devices/", "m4l"), ("/arduino-projects/", "arduino"), ("/daw-plugins/", "plugins")]


def cards_for(base, items, lang):
    out = []
    for p in items:
        summ = f'<p>{e(L(p["summary"], lang))}</p>' if L(p.get("summary"), lang) else ""
        out.append(f'<a class="proj" href="{U(lang, base + p["slug"] + "/")}"><div class="thumb"><img src="{sq(p["cover"], 800)}" alt="{e(p["title"])}" loading="lazy" decoding="async" width="800" height="600"></div>'
                   f'<div><h3>{e(p["title"])}</h3>{summ}</div></a>')
    return "".join(out)


def build_tech(lang):
    secs = "".join(f'<section><div class="sec-title"><h2><a href="{U(lang, b)}">{u(k, lang)}</a></h2><a class="small muted" href="{U(lang, b)}">{u("view_all", lang)} →</a></div>'
                   f'<div class="proj-grid">{cards_for(b, D["tech"][k]["items"], lang)}</div></section>' for b, k in SECTIONS if D["tech"][k]["items"])
    lede = tx("tech_lede", lang)
    body = head(u("tech_long", lang), tx("tech_kicker", lang), lede) + f'<div class="wrap">{secs}</div>'
    page("/music-technology/", lang, u("tech_long", lang), lede, body, kicker=tx("tech_kicker", lang))

    for base, key in SECTIONS:
        items = D["tech"][key]["items"]
        sect_lede = L(D["tech"][key]["lede"], lang)
        title = u(key, lang)
        body = head(title, u("tech_long", lang), sect_lede) + f'<div class="wrap"><div class="proj-grid">{cards_for(base, items, lang)}</div></div>'
        page(base, lang, title, f"{title} — {NAME[lang]}. {sect_lede}", body, kicker=u("tech_long", lang),
             crumbs=[(u("tech_long", lang), "/music-technology/"), (title, base)])
        for i in range(len(items)):
            build_project(base, title, items, i, lang)


def block(b, title, lang):
    k = b["type"]
    if k == "p":
        return f"<p>{e(L(b['text'], lang))}</p>"
    if k == "h":
        return f"<h2>{e(L(b['text'], lang))}</h2>"
    if k == "ul":
        return "<ul>" + "".join(f"<li>{e(L(x, lang))}</li>" for x in b["items"]) + "</ul>"
    if k == "img":
        cap = L(b.get("caption"), lang)
        fc = f"<figcaption>{e(cap)}</figcaption>" if cap else ""
        alt = cap or f"{title} — {u('photo', lang)}"
        return f'<figure class="zoomable"><img src="{sq(b["src"], 1500)}" alt="{e(alt)}" loading="lazy" decoding="async">{fc}</figure>'
    if k == "yt":
        return yt(b["id"], title, lang)
    if k == "link":
        return f'<a class="ext" href="{e(b["url"])}" target="_blank" rel="noopener">{e(L(b["label"], lang))}{ARROW}</a>'
    if k == "mono":
        return f'<div class="mono">{e(b["text"])}</div>'
    return ""


def build_project(base, sect, items, i, lang):
    p = items[i]
    d = p.get("download")
    dl = f'<a class="btn" href="{e(d["url"])}" target="_blank" rel="noopener">{e(L(d["label"], lang))}{ARROW}</a>' if d and d.get("url") else ""
    blocks = "".join(block(b, p["title"], lang) for b in p["blocks"])
    prev_ = items[i - 1] if i > 0 else None
    next_ = items[i + 1] if i < len(items) - 1 else None
    left = (f'<a href="{U(lang, base + prev_["slug"] + "/")}"><span>← {u("prev", lang)}</span><strong>{e(prev_["title"])}</strong></a>' if prev_
            else f'<a href="{U(lang, base)}"><span>← {u("back", lang)}</span><strong>{sect}</strong></a>')
    right = (f'<a href="{U(lang, base + next_["slug"] + "/")}"><span>{u("next", lang)} →</span><strong>{e(next_["title"])}</strong></a>' if next_
             else f'<a href="{U(lang, base)}"><span>{u("back", lang)}</span><strong>{sect}</strong></a>')
    summ = L(p.get("summary"), lang)
    summary = f'<p class="lede">{e(summ)}</p>' if summ else ""
    cover = f'<figure class="cover zoomable"><img src="{sq(p["cover"], 1500)}" alt="{e(p["title"])}"></figure>' if p.get("cover") else ""
    body = (f'<header class="wrap page-head"><p class="kicker"><a href="{U(lang, base)}">← {sect}</a></p><h1 class="dotted">{e(p["title"])}</h1>{summary}</header>'
            f'<div class="wrap"><div class="article">'
            f'{cover}'
            f'{dl}{blocks}</div><nav class="pager" aria-label="{u("projects", lang)}">{left}{right}</nav></div>')
    path = base + p["slug"] + "/"
    image = {"image": SITE["url"] + sq(p["cover"], 1500)} if p.get("cover") else {}
    if base == "/arduino-projects/":
        item = {"@type": "CreativeWork", "name": p["title"], "description": summ or sect, **image,
                "author": {"@id": SITE["url"] + "/#person"}, "url": SITE["url"] + U(lang, path), "inLanguage": lang}
    else:
        item = {"@type": "SoftwareApplication", "name": p["title"], "description": summ or sect,
                "applicationCategory": "MultimediaApplication",
                "applicationSubCategory": "Max for Live device" if base == "/max4live-devices/" else "Audio plugin",
                "operatingSystem": "Ableton Live (Max for Live)" if base == "/max4live-devices/" else "Windows, macOS",
                **image, "author": {"@id": SITE["url"] + "/#person"}, "url": SITE["url"] + U(lang, path),
                "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"}}
        if d and d.get("url"):
            item["downloadUrl"] = d["url"]
    page(path, lang, p["title"], f"{p['title']} — {summ or sect} · {NAME[lang]}", body, kicker=sect, ld=[item],
         crumbs=[(u("tech_long", lang), "/music-technology/"), (sect, base), (p["title"], path)])


# ------------------------------------------------------------------ Academic
def build_academic(lang):
    cards = []
    for a in ACADEMIC:
        t, video, reports = L(a["title"], lang), a.get("video"), a.get("reports") or []
        links = []
        if video:
            links.append(f'<a class="ext" href="{e(video)}" target="_blank" rel="noopener">{u("watch", lang) if "youtu" in video else u("files", lang)}{ARROW}</a>')
        links += [f'<a class="ext" href="{e(r["url"])}" target="_blank" rel="noopener">{e(L(r["label"], lang))}{ARROW}</a>' for r in reports]
        main = video or (reports[0]["url"] if reports else "#")
        cards.append(f'<article class="acad"><a class="thumb" href="{e(main)}" target="_blank" rel="noopener" tabindex="-1"><img src="{sq(a["thumb"], 800)}" alt="{e(t)}" loading="lazy" decoding="async" width="800" height="450"></a>'
                     f'<div><p class="kicker">{e(L(a["inst"], lang))}</p><h3 style="margin-top:4px">{e(t)}</h3></div><div class="links">{"".join(links)}</div></article>')
    lede = tx("academic_lede", lang)
    body = head(u("academic_long", lang), tx("academic_kicker", lang), lede) + f'<div class="wrap"><div class="grid">{"".join(cards)}</div></div>'
    page("/academic-portfolio/", lang, u("academic_long", lang), lede, body, kicker=tx("academic_card_kicker", lang))


# ------------------------------------------------------------------ CV
def build_cv(lang):
    def entries(items):
        out = []
        for x in items:
            kind = L(x.get("kind"), lang)
            k = f' <span class="muted" style="font-weight:400">· {e(kind)}</span>' if kind else ""
            out.append(f'<div class="entry"><span class="when">{e(L(x["when"], lang))}</span><div><h3>{e(L(x["title"], lang))}{k}</h3>'
                       f'<p class="org">{e(L(x["org"], lang))}, {e(L(x["place"], lang))}</p><p>{e(L(x["desc"], lang))}</p></div></div>')
        return "".join(out)

    def li(xs):
        return "<ul>" + "".join(f"<li>{e(x['name'])}<span>{e(x['org'])}</span></li>" for x in xs) + "</ul>"

    skills = "".join(f"<li>{e(L(s, lang))}</li>" for s in CV["skills"])
    linkedin = next((s_url for n, s_url in SOCIAL if n == "LinkedIn"), "")
    li_row = ""
    if linkedin:
        handle = linkedin.rstrip("/").split("/")[-1].rsplit("-", 1)[0]
        li_row = f'<div><dt>LinkedIn</dt><dd><a class="text-link" href="{linkedin}" target="_blank" rel="noopener">{e(handle)}</a></dd></div>'
    body = head(u("cv_long", lang), tx("cv_kicker", lang)) + f'''
<div class="wrap cv">
  <div>
    <p class="objective">{e(L(CV['objective'], lang))}</p>
    <section><h2 class="h">{u('work', lang)}</h2>{entries(CV['work'])}</section>
    <section><h2 class="h">{u('education', lang)}</h2>{entries(CV['education'])}</section>
  </div>
  <aside class="side">
    <div><h2 class="h">{u('contact', lang)}</h2><dl>
      <div><dt>{u('based', lang)}</dt><dd>{u('athens_gr', lang)}</dd></div>
      <div><dt>{u('phone', lang)}</dt><dd>{SITE['phone']}</dd></div>
      <div><dt>Email</dt><dd><a class="text-link" href="mailto:{SITE['email']}">{SITE['email']}</a></dd></div>
      {li_row}
    </dl></div>
    <div><h2 class="h">{u('skills', lang)}</h2><ul>{skills}</ul></div>
    <div><h2 class="h">{u('software', lang)}</h2>{li(CV['software'])}</div>
    <div><h2 class="h">{u('mixers', lang)}</h2>{li(CV['mixers'])}</div>
    <div><h2 class="h">{u('certs', lang)}</h2>{li(CV['certifications'])}</div>
  </aside>
</div>'''
    page("/curriculum-vitae/", lang, u("cv_long", lang), tx("cv_desc", lang), body, kicker=tx("cv_kicker", lang),
         ld=[{"@type": "ProfilePage", "name": u("cv_long", lang), "inLanguage": lang, "mainEntity": person_ld()}])


# ------------------------------------------------------------------ Contact
def build_contact(lang):
    live = bool(FORM_KEY)
    btn = u("send", lang) if live else u("write", lang)
    hint = "" if live else f'<p class="hint">{u("hint_mail", lang)}</p>'
    lede = tx("contact_lede", lang)
    body = head(u("contact", lang), u("athens_gr", lang), lede) + f'''
<div class="wrap contact">
  <div>
    <a class="big-mail" href="mailto:{SITE['email']}">{SITE['email']}</a>
    <form class="form" id="contact-form" data-to="{SITE['email']}" data-key="{FORM_KEY}"
      data-sending="{e(u('sending', lang))}" data-sent="{e(u('sent', lang))}" data-failed="{e(u('failed', lang))}">
      <label for="f-name">{u('name', lang)}<input id="f-name" name="name" required autocomplete="name"></label>
      <label for="f-email">{u('your_email', lang)}<input id="f-email" name="email" type="email" required autocomplete="email"></label>
      <label for="f-msg">{u('message', lang)}<textarea id="f-msg" name="message" required></textarea></label>
      <input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
      <button class="btn" type="submit">{btn}</button>
      {hint}
      <p class="form-status" role="status" aria-live="polite"></p>
    </form>
    <div style="margin-top:44px">{socials_html()}</div>
  </div>
  <img class="photo mask-squircle" src="{sq(IMG['contact'], 1000)}" alt="{NAME[lang]}" loading="lazy" decoding="async" width="750" height="1123">
</div>'''
    desc = tx("contact_desc", lang)
    page("/contact/", lang, u("contact", lang), desc, body, kicker=u("athens_gr", lang),
         ld=[{"@type": "ContactPage", "name": u("contact", lang), "inLanguage": lang, "about": {"@id": SITE["url"] + "/#person"}}])


# ------------------------------------------------------------------ extras
def build_extras():
    body404 = (
        '<section class="wrap nf">'
        '<p class="kicker">Error 404</p>'
        '<h1 class="dotted">No signal</h1>'
        '<div class="flat" aria-hidden="true"><span></span></div>'
        f'<p class="lede">{u("notfound", "en")}<br><span lang="el">{u("notfound", "el")}</span></p>'
        f'<p class="nf-links"><a class="btn" href="/">{u("home", "en")}</a> <a class="btn ghost" href="/el/" lang="el">{u("home", "el")}</a></p>'
        '</section>')
    page("/404/", "en", "Page not found", "Page not found.", body404)
    shutil.move(os.path.join(OUT, "404", "index.html"), os.path.join(OUT, "404.html"))
    os.rmdir(os.path.join(OUT, "404"))
    # Redirects from old Squarespace addresses
    lines = [f"/studio/v/{s['old']}  /studio/  301" for s in STUDIO if s.get("old")] + ["/studio/v/*  /studio/  301"]
    for base, key in SECTIONS:
        for p in D["tech"][key]["items"]:
            if p.get("old") and p["old"] != p["slug"]:
                lines.append(f"{base.rstrip('/')}/{p['old']}  {base}{p['slug']}/  301")
    lines += ["/studio/recording  /studio/  301", "/studio/mixing  /studio/  301", "/studio/production  /studio/  301",
              "/studio/video-edit  /studio/  301", "/studio/custom-sound-library  /studio/  301", "/cart  /  301"]
    open(os.path.join(OUT, "_redirects"), "w").write("\n".join(lines) + "\n")
    # Sitemap with both languages linked to each other
    urls = []
    for p in PAGES:
        if p in ("/404/",) or p.startswith("/el/"):
            continue
        en, gr = SITE["url"] + p, SITE["url"] + "/el" + p
        alt = (f'<xhtml:link rel="alternate" hreflang="en" href="{en}"/>'
               f'<xhtml:link rel="alternate" hreflang="el" href="{gr}"/>')
        urls.append(f"<url><loc>{en}</loc>{alt}</url><url><loc>{gr}</loc>{alt}</url>")
    open(os.path.join(OUT, "sitemap.xml"), "w").write(
        '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        f'xmlns:xhtml="http://www.w3.org/1999/xhtml">{"".join(urls)}</urlset>\n')
    open(os.path.join(OUT, "_headers"), "w").write(
        "/assets/img/*\n  Cache-Control: public, max-age=31536000, immutable\n"
        "/assets/fonts/*\n  Cache-Control: public, max-age=31536000, immutable\n"
        "/og/*\n  Cache-Control: public, max-age=604800\n"
        "/assets/*.css\n  Cache-Control: public, max-age=3600\n"
        "/assets/*.js\n  Cache-Control: public, max-age=3600\n"
        "/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n")
    open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nDisallow: /editor/\nSitemap: {SITE['url']}/sitemap.xml\n")
    # which commit this build came from (GB EDITOR checks it to know when the preview / live site is ready)
    sha = os.environ.get("WORKERS_CI_COMMIT_SHA", "")
    if not sha:
        try:
            sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=HERE, capture_output=True, text=True).stdout.strip()
        except Exception:
            sha = ""
    open(os.path.join(OUT, "version.txt"), "w").write(sha + "\n")


if __name__ == "__main__":
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(os.path.join(HERE, "assets"), os.path.join(OUT, "assets"))
    if os.path.isdir(os.path.join(HERE, "editor")):
        shutil.copytree(os.path.join(HERE, "editor"), os.path.join(OUT, "editor"))
    for lang in LANGS:
        build_home(lang); build_theater(lang); build_studio(lang); build_music(lang); build_tech(lang)
        build_academic(lang); build_cv(lang); build_contact(lang)
    build_extras()
    print(len(PAGES), "pages")
