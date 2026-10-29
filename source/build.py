"""Builds the bilingual static site into ../site from content.py.  Run: python3 build.py
English lives at /, Greek at /el/."""
import html, json, os, shutil
from datetime import date
from content import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "site")
e = html.escape
LANGS = ("en", "el")
PREFIX = {"en": "", "el": "/el"}


def L(x, lang):
    """Pick the language version of a text (plain strings are the same in both)."""
    if x is None:
        return ""
    if isinstance(x, dict):
        return x[lang]
    return x


def U(lang, path):
    return PREFIX[lang] + path


UI = {
    "theater": T("Theater", "Θέατρο"), "studio": T("Studio", "Studio"), "music": T("Music", "Μουσική"),
    "tech": T("Music Tech", "Τεχνολογία"), "tech_long": T("Music Technology", "Μουσική Τεχνολογία"),
    "overview": T("Overview", "Επισκόπηση"), "m4l": T("Max4Live Devices", "Max4Live Devices"),
    "arduino": T("Arduino Projects", "Arduino Projects"), "plugins": T("DAW Plugins", "DAW Plugins"),
    "cv": T("CV", "Βιογραφικό"), "cv_long": T("Curriculum Vitae", "Βιογραφικό"),
    "academic": T("Academic", "Ακαδημαϊκά"), "academic_long": T("Academic Portfolio", "Ακαδημαϊκό Portfolio"),
    "contact": T("Contact", "Επικοινωνία"), "menu": T("Menu", "Μενού"), "close": T("Close", "Κλείσιμο"),
    "skip": T("Skip to content", "Μετάβαση στο περιεχόμενο"), "switch": T("Ελληνικά", "English"),
    "selected": T("Selected work", "Επιλεγμένα έργα"), "all": T("All", "Όλα"), "featured": T("Featured", "Προτεινόμενο"),
    "view_all": T("View all", "Όλα τα έργα"), "prev": T("Previous", "Προηγούμενο"), "next": T("Next", "Επόμενο"),
    "back": T("Back to", "Πίσω στα"), "watch": T("Watch video", "Δείτε το βίντεο"), "files": T("Project files", "Αρχεία project"),
    "play": T("Play", "Αναπαραγωγή"), "filter": T("Filter by work", "Φίλτρο ανά εργασία"),
    "productions": T("productions", "παραγωγές"), "projects": T("projects", "έργα"),
    "work": T("Work experience", "Επαγγελματική εμπειρία"), "education": T("Education", "Σπουδές"),
    "skills": T("Skills", "Δεξιότητες"), "software": T("Software", "Λογισμικό"),
    "mixers": T("Audio mixers I've used", "Κονσόλες ήχου που έχω χρησιμοποιήσει"), "certs": T("Certifications", "Πιστοποιήσεις"),
    "based": T("Based in", "Τοποθεσία"), "athens_gr": T("Athens, Greece", "Αθήνα, Ελλάδα"), "phone": T("Phone", "Τηλέφωνο"),
    "name": T("Name", "Όνομα"), "your_email": T("Your email", "Το email σας"), "message": T("Message", "Μήνυμα"),
    "send": T("Send message", "Αποστολή"), "write": T("Write email", "Γράψτε email"),
    "hint_mail": T("This opens your email app with your message ready to send.", "Ανοίγει την εφαρμογή email σας με το μήνυμα έτοιμο για αποστολή."),
    "sending": T("Sending…", "Αποστολή…"), "sent": T("Thank you. Your message was sent and I'll reply soon.", "Ευχαριστώ! Το μήνυμά σας στάλθηκε και θα απαντήσω σύντομα."),
    "failed": T("The message couldn't be sent. Please email me directly at", "Το μήνυμα δεν στάλθηκε. Στείλτε μου απευθείας email στο"),
    "notfound": T("This page doesn't exist.", "Αυτή η σελίδα δεν υπάρχει."), "home": T("Go to the home page", "Αρχική σελίδα"),
}


def u(key, lang):
    return UI[key][lang]


def sq(url, w=1000):
    """Map an original Squarespace image address to our own copy in /assets/img.
    Small sizes (thumbnails) use the lighter -sm version."""
    if "squarespace-cdn" not in url:
        return url
    key = url.split("67b51908870e605d6a390286/")[1].split("/")[0][:13].lower()
    return f"/assets/img/{key}{'-sm' if w <= 800 else ''}.webp"


def yt(vid, title, lang):
    return (f'<div class="yt" data-id="{vid}" data-title="{e(title)}"><button type="button" aria-label="{u("play", lang)}: {e(title)}">'
            f'<img src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" alt="" loading="lazy">'
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
}


def socials_html(extra_class=""):
    items = "".join(f'<li><a href="{url}" target="_blank" rel="noopener" aria-label="{n}" title="{n}">'
                    f'<svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[n]}</svg></a></li>' for n, url in SOCIAL)
    return f'<ul class="socials {extra_class}">{items}</ul>'


def sc(track):
    return (f'<div class="sc"><iframe loading="lazy" title="SoundCloud player" allow="autoplay" '
            f'src="https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/{track}&color=%23b9472f&visual=true&show_artwork=true"></iframe></div>')


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
    return json.dumps({
        "@context": "https://schema.org", "@type": "Person", "name": SITE["name"],
        "alternateName": ["Georgios Batzios", "George Batzios"], "url": SITE["url"] + "/",
        "image": SITE["url"] + sq(IMG["home1"], 1500), "jobTitle": "Sound Engineer",
        "description": "Audio and sound engineer and musician in Athens: theater sound, live mixing, studio recording, mixing, composing and music technology.",
        "email": "mailto:" + SITE["email"],
        "address": {"@type": "PostalAddress", "addressLocality": "Athens", "addressCountry": "GR"},
        "alumniOf": [{"@type": "CollegeOrUniversity", "name": "Metropolitan College"},
                     {"@type": "EducationalOrganization", "name": "IEK AKMI"}],
        "knowsAbout": ["Sound engineering", "Live sound mixing", "Theater sound", "Qlab", "Ableton Live", "Max for Live", "Arduino", "Music production"],
        "sameAs": [s[1] for s in SOCIAL],
    }, ensure_ascii=False)


def page(path, lang, title, desc, body, og=None, ld=None):
    """path is the language-neutral path, e.g. /theater/."""
    full = f"{title} — {SITE['name']}" if title else f"{SITE['name']} — {L(SITE['role'], lang)}"
    og = og or IMG["home1"]
    other = "el" if lang == "en" else "en"
    url = SITE["url"] + U(lang, path)
    ldtag = f'<script type="application/ld+json">{ld}</script>\n' if ld else ""
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
<meta property="og:image" content="{SITE['url']}{sq(og, 1500)}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;550;600;650&family=Geist+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="/assets/style.css">
{ldtag}</head>
<body data-lang="{lang}">
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs><clipPath id="m-squircle" clipPathUnits="objectBoundingBox"><path d="M0.5,0 C0.768,0,0.894,0.056,0.919,0.081 C0.944,0.106,1,0.242,1,0.505 C1,0.768,0.947,0.891,0.919,0.919 C0.891,0.947,0.768,1,0.5,1 C0.202,1,0.11,0.948,0.081,0.919 C0.052,0.89,0,0.768,0,0.5 C0,0.232,0.053,0.109,0.081,0.081 C0.109,0.053,0.232,0,0.5,0"/></clipPath><clipPath id="m-octagon" clipPathUnits="objectBoundingBox"><path d="M0.5,0 L0.957,0.065,1,0.5,0.957,0.935 L0.5,1,0.043,0.935,0,0.5,0.043,0.065,0.5,0"/></clipPath></defs></svg>
<a class="skip" href="#main">{u('skip', lang)}</a>
<header class="site-head"><div class="wrap head-row">
<a class="mark dotted" href="{U(lang, '/')}">Giorgos Batzios</a>
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
<span class="copy">© {date.today().year} Giorgos Batzios</span>
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
    years = sorted({t[0] for t in THEATER})
    n_tech = len(MAX4LIVE) + len(ARDUINO) + len(PLUGINS)
    rows = [
        ("/theater/", u("theater", lang), L(T(f"{len(THEATER)} productions, {years[0]}–{years[-1]}", f"{len(THEATER)} παραγωγές, {years[0]}–{years[-1]}"), lang)),
        ("/studio/", "Studio", L(T(f"{len(STUDIO)} recordings, mixes and videos", f"{len(STUDIO)} ηχογραφήσεις, μίξεις και βίντεο"), lang)),
        ("/music/", u("music", lang), L(T(f"{len(MUSIC)} songs and sessions", f"{len(MUSIC)} τραγούδια και sessions"), lang)),
        ("/music-technology/", u("tech_long", lang), L(T(f"{n_tech} projects: Max4Live, Arduino, plugins", f"{n_tech} έργα: Max4Live, Arduino, plugins"), lang)),
        ("/curriculum-vitae/", u("cv_long", lang), L(T("Experience, education and skills", "Εμπειρία, σπουδές και δεξιότητες"), lang)),
        ("/academic-portfolio/", u("academic_long", lang), L(T(f"{len(ACADEMIC)} projects", f"{len(ACADEMIC)} έργα"), lang)),
    ]
    idx = "".join(f'<a href="{U(lang, h)}"><span class="name">{n}</span><span class="meta">{m}</span></a>' for h, n, m in rows)
    fields = "".join(f"<li>{L(f, lang)}</li>" for f in SITE["fields"])
    sel = "".join(
        f'<a class="sel" href="{U(lang, link)}"><div class="thumb"><img src="{sq(img, 800)}" alt="" loading="lazy" width="800" height="600"></div>'
        f'<div><p class="kicker">{L(k, lang)}</p><h3 lang="{"el" if title == "Αντιγόνη" else "en"}">{e(title)}</h3><p class="line">{L(line, lang)}</p></div></a>'
        for title, k, line, link, img in SELECTED)
    body = f"""
<div class="wrap">
  <section class="hero">
    <div>
      <h1 class="dotted">Giorgos<br>Batzios</h1>
      <p class="role">{L(SITE['role'], lang)}</p>
    </div>
    <img class="hero-img mask-squircle" src="{sq(IMG['home1'], 1200)}" alt="Giorgos Batzios" width="1200" height="1200">
  </section>
  <hr class="divider">
  <section class="split">
    <img class="split-img mask-octagon" src="{sq(IMG['home2'], 1200)}" alt="Giorgos Batzios" loading="lazy" width="1000" height="1200">
    <ul class="fields">{fields}</ul>
  </section>
  <section class="selected"><div class="sec-title"><h2>{u('selected', lang)}</h2></div><div class="sel-grid">{sel}</div></section>
  <nav class="index" aria-label="Sections">{idx}</nav>
</div>"""
    desc = L(T("Giorgos Batzios — audio and sound engineer, musician. Theater, live sound, studio recording, mixing and composing in Athens, Greece.",
               "Γιώργος Μπάτζιος — ηχολήπτης και μουσικός. Θέατρο, live ήχος, ηχογράφηση, μίξη και σύνθεση στην Αθήνα."), lang)
    page("/", lang, "", desc, body, ld=person_ld())


# ------------------------------------------------------------------ Theater
def build_theater(lang):
    rows, last = [], None
    for yr, title, venue, roles, link, img in sorted(THEATER, key=lambda t: -t[0]):
        if yr != last:
            rows.append(f'<h2 class="year">{yr}</h2>')
            last = yr
        rl = " · ".join(r if lang == "en" else ROLES[r] for r in roles)
        rows.append(f'''<a class="show" href="{e(link)}" target="_blank" rel="noopener">
  <img src="{sq(img, 300)}" alt="" loading="lazy" width="76" height="76">
  <div><h3 lang="el">{e(title)}</h3><p class="venue">{e(L(venue, lang))}</p></div>
  <p class="roles">{e(rl)}</p>
  <span class="go">{ARROW}</span>
</a>''')
    lede = L(T("Sound mixing, lights and AV programming, and show operation for theater productions in Athens and on tour around Greece.",
               "Μίξη ήχου, προγραμματισμός φώτων και AV, και εκτέλεση παραστάσεων για θεατρικές παραγωγές στην Αθήνα και σε περιοδείες σε όλη την Ελλάδα."), lang)
    body = head(u("theater", lang), f"{len(THEATER)} {u('productions', lang)}", lede) + f'<div class="wrap">{"".join(rows)}</div>'
    page("/theater/", lang, u("theater", lang), lede, body)


# ------------------------------------------------------------------ Studio
def build_studio(lang):
    cat = (lambda c: c) if lang == "en" else (lambda c: CATS_EL[c])
    counts = {c: sum(c in s[2] for s in STUDIO) for c in STUDIO_CATS}
    btns = f'<button type="button" data-cat="all" aria-pressed="true">{u("all", lang)}<span class="n">{len(STUDIO)}</span></button>' + "".join(
        f'<button type="button" data-cat="{c}" aria-pressed="false">{cat(c)}<span class="n">{counts[c]}</span></button>' for c in STUDIO_CATS)
    first = next(s for s in STUDIO if s[3] == FEATURED_STUDIO)
    rest = [s for s in STUDIO if s is not first]
    note = f'<p class="note">{e(L(first[4], lang))}</p>' if first[4] else ""
    feat = f'''<article class="featured" data-cats="{"|".join(first[2])}">
  {yt(first[3], first[0], lang)}
  <div><p class="kicker">{u("featured", lang)}</p><h3 style="margin-top:10px">{el(first[0])}</h3>{note}<p class="meta">{" · ".join(cat(c) for c in first[2])}</p></div>
</article>'''
    cards = "".join(f'''<article class="card" data-cats="{"|".join(s[2])}">
  {yt(s[3], s[0], lang)}
  <div><h3>{el(s[0])}</h3><p class="meta">{" · ".join(cat(c) for c in s[2])} — {s[1][:4]}</p></div>
</article>''' for s in rest)
    lede = L(T("Recording, mixing, production and video editing for artists and bands.",
               "Ηχογράφηση, μίξη, παραγωγή και μοντάζ βίντεο για καλλιτέχνες και συγκροτήματα."), lang)
    body = head("Studio", f"{len(STUDIO)} {u('projects', lang)}, 2020–2025", lede) + f'''
<div class="wrap">
  <div class="filters" role="group" aria-label="{u('filter', lang)}">{btns}</div>
  {feat}
  <div class="grid">{cards}</div>
</div>'''
    page("/studio/", lang, "Studio", lede, body, IMG["studio"])


# ------------------------------------------------------------------ Music
def build_music(lang):
    items = []
    for t, roles, kind, mid, note in MUSIC:
        media = sc(mid) if kind == "sc" else yt(mid, t, lang)
        n = f'<p class="note">{e(L(note, lang))}</p>' if note else ""
        rl = " · ".join(r if lang == "en" else MUSIC_ROLES[r] for r in roles)
        items.append(f'<article class="track">{media}<div class="text"><h2>{el(t)}</h2><p class="roles">{e(rl)}</p>{n}</div></article>')
    lede = L(T("Songs and sessions I wrote, played on or produced.", "Τραγούδια και sessions που έγραψα, έπαιξα ή έκανα την παραγωγή τους."), lang)
    body = head(u("music", lang), L(T("Composing, playing, producing", "Σύνθεση, εκτέλεση, παραγωγή"), lang), lede) + \
        f'<div class="wrap">{"".join(items)}</div>'
    page("/music/", lang, u("music", lang), lede, body, IMG["music"])


# ------------------------------------------------------------------ Music technology
SECTIONS = [
    ("/max4live-devices/", "m4l", T("Free devices for Ableton Live, built in Max.", "Δωρεάν devices για το Ableton Live, φτιαγμένα σε Max."), MAX4LIVE),
    ("/arduino-projects/", "arduino", T("Hardware controllers and sensor systems for live performance and shows.",
                                        "Hardware controllers και συστήματα με σένσορες για live performance και παραστάσεις."), ARDUINO),
    ("/daw-plugins/", "plugins", T("Audio plugins for mixing and spatial sound.", "Audio plugins για μίξη και χωρικό ήχο."), PLUGINS),
]


def cards_for(base, items, lang):
    out = []
    for p in items:
        summ = f'<p>{e(L(p["summary"], lang))}</p>' if p["summary"] else ""
        out.append(f'<a class="proj" href="{U(lang, base + p["slug"] + "/")}"><div class="thumb"><img src="{sq(p["cover"], 800)}" alt="" loading="lazy" width="800" height="600"></div>'
                   f'<div><h3>{e(p["title"])}</h3>{summ}</div></a>')
    return "".join(out)


def build_tech(lang):
    secs = "".join(f'<section><div class="sec-title"><h2><a href="{U(lang, b)}">{u(k, lang)}</a></h2><a class="small muted" href="{U(lang, b)}">{u("view_all", lang)} →</a></div>'
                   f'<div class="proj-grid">{cards_for(b, items, lang)}</div></section>' for b, k, _, items in SECTIONS)
    lede = L(T("Tools I build for Ableton Live, for the stage and for the mix.", "Εργαλεία που φτιάχνω για το Ableton Live, για τη σκηνή και για τη μίξη."), lang)
    body = head(u("tech_long", lang), "Max4Live, Arduino, plugins", lede) + f'<div class="wrap">{secs}</div>'
    page("/music-technology/", lang, u("tech_long", lang), lede, body)

    for base, key, lede, items in SECTIONS:
        title = u(key, lang)
        body = head(title, u("tech_long", lang), L(lede, lang)) + f'<div class="wrap"><div class="proj-grid">{cards_for(base, items, lang)}</div></div>'
        page(base, lang, title, f"{title} — Giorgos Batzios. {L(lede, lang)}", body)
        for i in range(len(items)):
            build_project(base, title, items, i, lang)


def block(b, title, lang):
    k = b[0]
    if k == "p":
        return f"<p>{e(L(b[1], lang))}</p>"
    if k == "h":
        return f"<h2>{e(L(b[1], lang))}</h2>"
    if k == "ul":
        return "<ul>" + "".join(f"<li>{e(L(x, lang))}</li>" for x in b[1]) + "</ul>"
    if k == "img":
        cap = L(b[2], lang)
        fc = f"<figcaption>{e(cap)}</figcaption>" if cap else ""
        return f'<figure><img src="{sq(b[1], 1500)}" alt="{e(cap)}" loading="lazy">{fc}</figure>'
    if k == "yt":
        return yt(b[1], title, lang)
    if k == "link":
        return f'<a class="ext" href="{e(b[1])}" target="_blank" rel="noopener">{e(L(b[2], lang))}{ARROW}</a>'
    if k == "mono":
        return f'<div class="mono">{e(b[1])}</div>'
    raise ValueError(k)


def build_project(base, sect, items, i, lang):
    p = items[i]
    dl = f'<a class="btn" href="{e(p["download"][0])}" target="_blank" rel="noopener">{e(L(p["download"][1], lang))}{ARROW}</a>' if p.get("download") else ""
    blocks = "".join(block(b, p["title"], lang) for b in p["blocks"])
    prev_ = items[i - 1] if i > 0 else None
    next_ = items[i + 1] if i < len(items) - 1 else None
    left = (f'<a href="{U(lang, base + prev_["slug"] + "/")}"><span>← {u("prev", lang)}</span><strong>{e(prev_["title"])}</strong></a>' if prev_
            else f'<a href="{U(lang, base)}"><span>← {u("back", lang)}</span><strong>{sect}</strong></a>')
    right = (f'<a href="{U(lang, base + next_["slug"] + "/")}"><span>{u("next", lang)} →</span><strong>{e(next_["title"])}</strong></a>' if next_
             else f'<a href="{U(lang, base)}"><span>{u("back", lang)}</span><strong>{sect}</strong></a>')
    summ = L(p["summary"], lang)
    summary = f'<p class="lede">{e(summ)}</p>' if summ else ""
    body = (f'<header class="wrap page-head"><p class="kicker"><a href="{U(lang, base)}">← {sect}</a></p><h1 class="dotted">{e(p["title"])}</h1>{summary}</header>'
            f'<div class="wrap"><div class="article">'
            f'<figure class="cover"><img src="{sq(p["cover"], 1500)}" alt="{e(p["title"])}"></figure>'
            f'{dl}{blocks}</div><nav class="pager" aria-label="{u("projects", lang)}">{left}{right}</nav></div>')
    page(base + p["slug"] + "/", lang, p["title"], f"{p['title']} — {summ or sect} · Giorgos Batzios", body, p["cover"])


# ------------------------------------------------------------------ Academic
def build_academic(lang):
    cards = []
    for t, inst, video, reports, thumb in ACADEMIC:
        links = []
        if video:
            links.append(f'<a class="ext" href="{e(video)}" target="_blank" rel="noopener">{u("watch", lang) if "youtube" in video else u("files", lang)}{ARROW}</a>')
        links += [f'<a class="ext" href="{e(l_url)}" target="_blank" rel="noopener">{e(L(lbl, lang))}{ARROW}</a>' for lbl, l_url in reports]
        main = video or (reports[0][1] if reports else "#")
        cards.append(f'<article class="acad"><a class="thumb" href="{e(main)}" target="_blank" rel="noopener" tabindex="-1"><img src="{sq(thumb, 800)}" alt="" loading="lazy" width="800" height="450"></a>'
                     f'<div><p class="kicker">{e(L(inst, lang))}</p><h3 style="margin-top:4px">{e(L(t, lang))}</h3></div><div class="links">{"".join(links)}</div></article>')
    lede = L(T("Coursework, live performances and final projects from my studies.", "Εργασίες, live performances και τελικά projects από τις σπουδές μου."), lang)
    body = head(u("academic_long", lang), L(T("Metropolitan College, AKMI Institution", "Μητροπολιτικό Κολλέγιο, ΙΕΚ ΑΚΜΗ"), lang), lede) + \
        f'<div class="wrap"><div class="grid">{"".join(cards)}</div></div>'
    page("/academic-portfolio/", lang, u("academic_long", lang), lede, body)


# ------------------------------------------------------------------ CV
def build_cv(lang):
    def entries(items):
        out = []
        for t, kind, org, place, when, d in items:
            k = f' <span class="muted" style="font-weight:400">· {e(L(kind, lang))}</span>' if kind else ""
            out.append(f'<div class="entry"><span class="when">{e(L(when, lang))}</span><div><h3>{e(L(t, lang))}{k}</h3>'
                       f'<p class="org">{e(L(org, lang))}, {e(L(place, lang))}</p><p>{e(L(d, lang))}</p></div></div>')
        return "".join(out)

    def li(xs):
        return "<ul>" + "".join(f"<li>{e(a)}<span>{e(b)}</span></li>" for a, b in xs) + "</ul>"
    skills = "".join(f"<li>{e(L(s, lang))}</li>" for s in CV["skills"])
    body = head(u("cv_long", lang), L(T("Sound / audio engineer", "Ηχολήπτης / sound engineer"), lang)) + f'''
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
      <div><dt>LinkedIn</dt><dd><a class="text-link" href="{SOCIAL[3][1]}" target="_blank" rel="noopener">giorgos-batzios</a></dd></div>
    </dl></div>
    <div><h2 class="h">{u('skills', lang)}</h2><ul>{skills}</ul></div>
    <div><h2 class="h">{u('software', lang)}</h2>{li(CV['software'])}</div>
    <div><h2 class="h">{u('mixers', lang)}</h2>{li(CV['mixers'])}</div>
    <div><h2 class="h">{u('certs', lang)}</h2>{li(CV['certifications'])}</div>
  </aside>
</div>'''
    desc = L(T("CV of Giorgos Batzios, sound and audio engineer: theater, live and studio experience, education and certifications.",
               "Βιογραφικό του Γιώργου Μπάτζιου, ηχολήπτη: εμπειρία σε θέατρο, live και στούντιο, σπουδές και πιστοποιήσεις."), lang)
    page("/curriculum-vitae/", lang, u("cv_long", lang), desc, body)


# ------------------------------------------------------------------ Contact
def build_contact(lang):
    live = bool(FORM_KEY)
    btn = u("send", lang) if live else u("write", lang)
    hint = "" if live else f'<p class="hint">{u("hint_mail", lang)}</p>'
    lede = L(T("Get in touch using the form, by email, or through the links below.",
               "Επικοινωνήστε μαζί μου μέσω της φόρμας, με email ή από τους παρακάτω συνδέσμους."), lang)
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
  <img class="photo mask-squircle" src="{sq(IMG['contact'], 1000)}" alt="Giorgos Batzios" loading="lazy" width="750" height="1123">
</div>'''
    desc = L(T("Contact Giorgos Batzios for theater sound, live sound, recording and mixing.",
               "Επικοινωνήστε με τον Γιώργο Μπάτζιο για ήχο θεάτρου, live, ηχογράφηση και μίξη."), lang)
    page("/contact/", lang, u("contact", lang), desc, body, IMG["contact"])


# ------------------------------------------------------------------ extras
def build_extras():
    page("/404/", "en", "Page not found", "Page not found.",
         head("Not found", "Error 404", f'{u("notfound", "en")} <a href="/">{u("home", "en")}</a> · <a href="/el/">{u("home", "el")}</a>'))
    shutil.move(os.path.join(OUT, "404", "index.html"), os.path.join(OUT, "404.html"))
    os.rmdir(os.path.join(OUT, "404"))
    # Redirects from old Squarespace addresses
    lines = [f"/studio/v/{s[5]}  /studio/  301" for s in STUDIO] + ["/studio/v/*  /studio/  301"]
    for base, _, _, items in SECTIONS:
        for p in items:
            if p["old"] != p["slug"]:
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
    open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE['url']}/sitemap.xml\n")


if __name__ == "__main__":
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(os.path.join(HERE, "assets"), os.path.join(OUT, "assets"))
    for lang in LANGS:
        build_home(lang); build_theater(lang); build_studio(lang); build_music(lang); build_tech(lang)
        build_academic(lang); build_cv(lang); build_contact(lang)
    build_extras()
    print(len(PAGES), "pages")
