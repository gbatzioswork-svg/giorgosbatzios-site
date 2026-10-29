"""Builds the static site into ./dist from content.py.  Run: python3 build.py"""
import html, json, os, shutil
from datetime import date
from content import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "site")
e = html.escape


def sq(url, w=1000):
    """Squarespace CDN resize (ignored once images are local)."""
    return f"{url}?format={w}w" if "squarespace-cdn" in url else url


def yt(vid, title=""):
    return (f'<div class="yt" data-id="{vid}" data-title="{e(title)}"><button type="button" aria-label="Play {e(title)}">'
            f'<img src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" alt="" loading="lazy">'
            f'<span class="play"></span></button></div>')


def sc(track):
    return (f'<div class="sc tall"><iframe loading="lazy" title="SoundCloud player" allow="autoplay" '
            f'src="https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/{track}&color=%23cf3b20&visual=true&show_artwork=true"></iframe></div>')


NAV = [
    ("/theater/", "Theater"), ("/studio/", "Studio"), ("/music/", "Music"),
    ("MT", "Music Tech"), ("/curriculum-vitae/", "CV"), ("/academic-portfolio/", "Academic"), ("/contact/", "Contact"),
]
MT = [("/music-technology/", "Overview"), ("/max4live-devices/", "Max4Live Devices"),
      ("/arduino-projects/", "Arduino Projects"), ("/daw-plugins/", "DAW Plugins")]


def nav(cur):
    out = []
    for href, label in NAV:
        if href == "MT":
            curmt = any(cur.startswith(h) for h, _ in MT)
            subs = "".join(f'<a href="{h}"{" aria-current=page" if cur == h else ""}>{l}</a>' for h, l in MT)
            out.append(f'<details class="{"is-current" if curmt else ""}"><summary>{label}</summary><div class="sub">{subs}</div></details>')
        else:
            ac = ' aria-current="page"' if cur.startswith(href) else ""
            out.append(f'<a href="{href}"{ac}>{label}</a>')
    return "".join(out)


def page(path, title, desc, body, og=None):
    full = f"{title} — {SITE['name']}" if title else f"{SITE['name']} — Sound engineer & musician"
    og = og or IMG["home1"]
    socials = "".join(f'<li><a href="{u}" target="_blank" rel="noopener">{n}</a></li>' for n, u in SOCIAL)
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(full)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE['url']}{path}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(full)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{SITE['url']}{path}">
<meta property="og:image" content="{sq(og, 1500)}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;550;600;650&family=Geist+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs><clipPath id="m-squircle" clipPathUnits="objectBoundingBox"><path d="M0.5,0 C0.768,0,0.894,0.056,0.919,0.081 C0.944,0.106,1,0.242,1,0.505 C1,0.768,0.947,0.891,0.919,0.919 C0.891,0.947,0.768,1,0.5,1 C0.202,1,0.11,0.948,0.081,0.919 C0.052,0.89,0,0.768,0,0.5 C0,0.232,0.053,0.109,0.081,0.081 C0.109,0.053,0.232,0,0.5,0"/></clipPath><clipPath id="m-octagon" clipPathUnits="objectBoundingBox"><path d="M0.5,0 L0.957,0.065,1,0.5,0.957,0.935 L0.5,1,0.043,0.935,0,0.5,0.043,0.065,0.5,0"/></clipPath></defs></svg>
<a class="skip" href="#main">Skip to content</a>
<header class="site-head"><div class="wrap head-row">
<a class="mark" href="/">Giorgos Batzios</a>
<button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav">Menu</button>
<nav class="nav" id="nav" aria-label="Main">{nav(path)}</nav>
</div></header>
<main id="main">
{body}
</main>
<footer class="site-foot"><div class="wrap foot-row">
<ul class="socials">{socials}</ul>
<span class="copy">© {date.today().year} Giorgos Batzios</span>
</div></footer>
<script src="/assets/site.js" defer></script>
</body>
</html>
"""
    # Relative links, so the site also works when opened straight from a folder
    depth = len([p for p in path.strip("/").split("/") if p])
    rel = "../" * depth or "./"
    if path != "/404/":  # the 404 page is shown at any address, so it keeps root links
        doc = doc.replace('href="/', f'href="{rel}').replace('src="/assets', f'src="{rel}assets')
    d = os.path.join(OUT, path.strip("/"))
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
        f.write(doc)
    PAGES[path] = doc


PAGES = {}


def head(title, eyebrow, lede=""):
    l = f'<p class="lede">{lede}</p>' if lede else ""
    return f'<header class="wrap page-head"><p class="kicker">{eyebrow}</p><h1>{title}</h1>{l}</header>'


def el(text):  # Greek title element
    return f'<span lang="el">{e(text)}</span>'


# ------------------------------------------------------------------ Home
def build_home():
    years = sorted({t[0] for t in THEATER})
    n_tech = len(MAX4LIVE) + len(ARDUINO) + len(PLUGINS)
    rows = [
        ("/theater/", "Theater", f"{len(THEATER)} productions, {years[0]}–{years[-1]}"),
        ("/studio/", "Studio", f"{len(STUDIO)} recordings, mixes and videos"),
        ("/music/", "Music", f"{len(MUSIC)} songs and sessions"),
        ("/music-technology/", "Music Technology", f"{n_tech} projects: Max4Live, Arduino, plugins"),
        ("/curriculum-vitae/", "Curriculum Vitae", "Experience, education and skills"),
        ("/academic-portfolio/", "Academic Portfolio", f"{len(ACADEMIC)} projects"),
    ]
    idx = "".join(f'<a href="{h}"><span class="name">{n}</span><span class="meta">{m}</span></a>' for h, n, m in rows)
    fields = "".join(f"<li>{f.strip()}</li>" for f in SITE["fields"].split("–"))
    body = f"""
<div class="wrap">
  <section class="hero">
    <div>
      <h1>Giorgos<br>Batzios</h1>
      <p class="role">{e(SITE['role'])}</p>
    </div>
    <img class="hero-img mask-squircle" src="{sq(IMG['home1'], 1200)}" alt="Giorgos Batzios at the piano" width="1200" height="1200">
  </section>
  <section class="split">
    <img class="split-img mask-octagon" src="{sq(IMG['home2'], 1200)}" alt="Giorgos Batzios at the mixing desk" loading="lazy" width="1000" height="1200">
    <ul class="fields">{fields}</ul>
  </section>
  <nav class="index" aria-label="Sections">{idx}</nav>
</div>"""
    page("/", "", "Giorgos Batzios — audio and sound engineer, musician. Theater, live sound, studio recording, mixing and composing in Athens, Greece.", body)


# ------------------------------------------------------------------ Theater
def build_theater():
    rows, last = [], None
    for yr, title, venue, roles, link, img in sorted(THEATER, key=lambda t: -t[0]):
        if yr != last:
            rows.append(f'<h2 class="year">{yr}</h2>')
            last = yr
        rows.append(f'''<a class="show" href="{e(link)}" target="_blank" rel="noopener">
  <img src="{sq(img, 300)}" alt="" loading="lazy" width="76" height="76">
  <div><h3 lang="el">{e(title)}</h3><p class="venue" lang="el">{e(venue)}</p></div>
  <p class="roles">{e(" · ".join(roles))}</p>
  <span class="go" aria-hidden="true">↗</span>
</a>''')
    body = head("Theater", f"{len(THEATER)} productions", "Sound mixing, lights and AV programming, and show operation for theater productions in Athens and on tour around Greece.") + \
        f'<div class="wrap">{"".join(rows)}</div>'
    page("/theater/", "Theater", "Theater productions: sound mixing, lights programming, Qlab and AV programming and show operation.", body)


# ------------------------------------------------------------------ Studio
def build_studio():
    counts = {c: sum(c in s[2] for s in STUDIO) for c in STUDIO_CATS}
    btns = f'<button type="button" data-cat="all" aria-pressed="true">All<span class="n">{len(STUDIO)}</span></button>' + "".join(
        f'<button type="button" data-cat="{c}" aria-pressed="false">{c}<span class="n">{counts[c]}</span></button>' for c in STUDIO_CATS)
    first, rest = STUDIO[0], STUDIO[1:]
    feat = f'''<article class="featured" data-cats="{"|".join(first[2])}">
  {yt(first[3], first[0])}
  <div><p class="kicker">Featured</p><h3 style="margin-top:10px">{e(first[0])}</h3><p class="note">{e(first[4])}</p><p class="meta">{" · ".join(first[2])}</p></div>
</article>'''
    cards = "".join(f'''<article class="card" data-cats="{"|".join(s[2])}">
  {yt(s[3], s[0])}
  <div><h3>{el(s[0])}</h3><p class="meta">{" · ".join(s[2])} — {s[1][:4]}</p></div>
</article>''' for s in rest)
    body = head("Studio", f"{len(STUDIO)} projects, 2020–2025", "Recording, mixing, production and video editing for artists and bands.") + f'''
<div class="wrap">
  <div class="filters" role="group" aria-label="Filter by work">{btns}</div>
  {feat}
  <div class="grid">{cards}</div>
</div>'''
    page("/studio/", "Studio", "Studio work: recording, mixing, production and video editing for music videos and sessions.", body, IMG["studio"])


# ------------------------------------------------------------------ Music
def build_music():
    items = []
    for t, roles, kind, mid, note in MUSIC:
        media = sc(mid) if kind == "sc" else yt(mid, t)
        n = f'<p class="note">{e(note)}</p>' if note else ""
        items.append(f'''<article class="track">{media}
<div class="text"><h2>{el(t)}</h2><p class="roles">{e(roles.replace(" – ", " · "))}</p>{n}</div></article>''')
    body = head("Music", "Composing, playing, producing", "Songs and sessions I wrote, played on or produced.") + \
        f'<div class="wrap">{"".join(items)}</div>'
    page("/music/", "Music", "Original music, swing sessions and productions by Giorgos Batzios.", body, IMG["music"])


# ------------------------------------------------------------------ Music technology
SECTIONS = [
    ("/max4live-devices/", "Max4Live Devices", "Free devices for Ableton Live, built in Max.", MAX4LIVE),
    ("/arduino-projects/", "Arduino Projects", "Hardware controllers and sensor systems for live performance and shows.", ARDUINO),
    ("/daw-plugins/", "DAW Plugins", "Audio plugins for mixing and spatial sound.", PLUGINS),
]


def cards_for(base, items):
    out = []
    for p in items:
        summ = f'<p lang="el">{e(p["summary"])}</p>' if p["summary"] else ""
        out.append(f'<a class="proj" href="{base}{p["slug"]}/"><div class="thumb"><img src="{sq(p["cover"], 800)}" alt="" loading="lazy" width="800" height="600"></div>'
                   f'<div><h3>{e(p["title"])}</h3>{summ}</div></a>')
    return "".join(out)


def build_tech():
    secs = "".join(f'<section><div class="sec-title"><h2><a href="{b}">{t}</a></h2><a class="small muted" href="{b}">View all →</a></div>'
                   f'<div class="proj-grid">{cards_for(b, items)}</div></section>' for b, t, _, items in SECTIONS)
    body = head("Music Technology", "Max4Live, Arduino, plugins", "Tools I build for Ableton Live, for the stage and for the mix.") + f'<div class="wrap">{secs}</div>'
    page("/music-technology/", "Music Technology", "Max4Live devices, Arduino projects and DAW plugins by Giorgos Batzios.", body)

    for base, title, lede, items in SECTIONS:
        body = head(title, "Music Technology", lede) + \
            f'<div class="wrap"><div class="proj-grid">{cards_for(base, items)}</div></div>'
        page(base, title, f"{title} by Giorgos Batzios. {lede}", body)
        for i, p in enumerate(items):
            build_project(base, title, items, i)


def block(b, title):
    k = b[0]
    if k == "p":
        return f"<p>{e(b[1])}</p>"
    if k == "h":
        return f"<h2>{e(b[1])}</h2>"
    if k == "ul":
        return "<ul>" + "".join(f"<li>{e(x)}</li>" for x in b[1]) + "</ul>"
    if k == "img":
        cap = f"<figcaption>{e(b[2])}</figcaption>" if b[2] else ""
        return f'<figure><img src="{sq(b[1], 1500)}" alt="{e(b[2])}" loading="lazy">{cap}</figure>'
    if k == "yt":
        return yt(b[1], title)
    if k == "link":
        return f'<a class="ext" href="{e(b[1])}" target="_blank" rel="noopener">{e(b[2])}</a>'
    if k == "mono":
        return f'<div class="mono">{e(b[1])}</div>'
    raise ValueError(k)


def build_project(base, sect, items, i):
    p = items[i]
    lang = "en" if base == "/daw-plugins/" else "el"
    dl = f'<a class="btn" href="{e(p["download"][0])}" target="_blank" rel="noopener">{e(p["download"][1])} ↗</a>' if p.get("download") else ""
    blocks = "".join(block(b, p["title"]) for b in p["blocks"])
    prev_ = items[i - 1] if i > 0 else None
    next_ = items[i + 1] if i < len(items) - 1 else None
    left = (f'<a href="{base}{prev_["slug"]}/"><span>← Previous</span><strong>{e(prev_["title"])}</strong></a>' if prev_
            else f'<a href="{base}"><span>← Back to</span><strong>{sect}</strong></a>')
    right = (f'<a href="{base}{next_["slug"]}/"><span>Next →</span><strong>{e(next_["title"])}</strong></a>' if next_
             else f'<a href="{base}"><span>Back to</span><strong>{sect}</strong></a>')
    summary = f'<p class="lede" lang="{lang}">{e(p["summary"])}</p>' if p["summary"] else ""
    body = (f'<header class="wrap page-head"><p class="kicker"><a href="{base}">← {sect}</a></p><h1>{e(p["title"])}</h1>{summary}</header>'
            f'<div class="wrap"><div class="article" lang="{lang}">'
            f'<figure class="cover"><img src="{sq(p["cover"], 1500)}" alt="{e(p["title"])}"></figure>'
            f'{dl}{blocks}</div><nav class="pager" aria-label="More projects">{left}{right}</nav></div>')
    page(f"{base}{p['slug']}/", p["title"], f"{p['title']} — {p['summary'] or sect} · Giorgos Batzios", body, p["cover"])


# ------------------------------------------------------------------ Academic
def build_academic():
    cards = []
    for t, inst, video, reports, thumb in ACADEMIC:
        links = []
        if video:
            links.append(f'<a class="ext" href="{e(video)}" target="_blank" rel="noopener">{"Watch video" if "youtube" in video else "Project files"}</a>')
        links += [f'<a class="ext" href="{e(u)}" target="_blank" rel="noopener">{e(l)}</a>' for l, u in reports]
        main = video or (reports[0][1] if reports else "#")
        cards.append(f'<article class="acad"><a class="thumb" href="{e(main)}" target="_blank" rel="noopener" tabindex="-1"><img src="{sq(thumb, 800)}" alt="" loading="lazy" width="800" height="450"></a>'
                     f'<div><p class="kicker">{e(inst)}</p><h3 style="margin-top:4px">{el(t)}</h3></div><div class="links">{"".join(links)}</div></article>')
    body = head("Academic Portfolio", "Metropolitan College, AKMI Institution", "Coursework, live performances and final projects from my studies.") + \
        f'<div class="wrap"><div class="grid">{"".join(cards)}</div></div>'
    page("/academic-portfolio/", "Academic Portfolio", "Academic projects from Metropolitan College and AKMI: live performance systems, foley and a Kontakt library thesis.", body)


# ------------------------------------------------------------------ CV
def build_cv():
    def entries(items):
        out = []
        for t, kind, org, place, when, d in items:
            k = f' <span class="muted" style="font-weight:400">· {e(kind)}</span>' if kind else ""
            out.append(f'<div class="entry"><span class="when">{when}</span><div><h3>{e(t)}{k}</h3><p class="org">{e(org)}, {e(place)}</p><p>{e(d)}</p></div></div>')
        return "".join(out)

    def li(xs):
        return "<ul>" + "".join(f"<li>{e(a)}<span>{e(b)}</span></li>" for a, b in xs) + "</ul>"
    skills = "".join(f"<li>{e(s)}</li>" for s in CV["skills"])
    body = head("Curriculum Vitae", "Sound / audio engineer") + f'''
<div class="wrap cv">
  <div>
    <p class="objective">{e(CV['objective'])}</p>
    <section><h2 class="h">Work experience</h2>{entries(CV['work'])}</section>
    <section><h2 class="h">Education</h2>{entries(CV['education'])}</section>
  </div>
  <aside class="side">
    <div><h2 class="h">Contact</h2><dl>
      <div><dt>Based in</dt><dd>Athens, Greece</dd></div>
      <div><dt>Phone</dt><dd>{SITE['phone']}</dd></div>
      <div><dt>Email</dt><dd><a class="text-link" href="mailto:{SITE['email']}">{SITE['email']}</a></dd></div>
      <div><dt>LinkedIn</dt><dd><a class="text-link" href="{SOCIAL[3][1]}" target="_blank" rel="noopener">giorgos-batzios</a></dd></div>
    </dl></div>
    <div><h2 class="h">Skills</h2><ul>{skills}</ul></div>
    <div><h2 class="h">Software</h2>{li(CV['software'])}</div>
    <div><h2 class="h">Audio mixers I've used</h2>{li(CV['mixers'])}</div>
    <div><h2 class="h">Certifications</h2>{li(CV['certifications'])}</div>
  </aside>
</div>'''
    page("/curriculum-vitae/", "Curriculum Vitae", "CV of Giorgos Batzios, sound and audio engineer: theater, live and studio experience, education and certifications.", body)


# ------------------------------------------------------------------ Contact
def build_contact():
    socials = "".join(f'<li><a href="{u}" target="_blank" rel="noopener">{n} ↗</a></li>' for n, u in SOCIAL)
    body = head("Contact", "Athens, Greece", "Get in touch using the form, by email, or through the links below.") + f'''
<div class="wrap contact">
  <div>
    <a class="big-mail" href="mailto:{SITE['email']}">{SITE['email']}</a>
    <form class="form" id="contact-form" data-to="{SITE['email']}">
      <label for="f-name">Name<input id="f-name" name="name" required autocomplete="name"></label>
      <label for="f-email">Your email<input id="f-email" name="email" type="email" required autocomplete="email"></label>
      <label for="f-msg">Message<textarea id="f-msg" name="message" required></textarea></label>
      <button class="btn" type="submit">Write email</button>
      <p class="hint">This opens your email app with your message ready to send.</p>
    </form>
    <ul class="socials" style="margin-top:44px">{socials}</ul>
  </div>
  <img class="photo mask-squircle" src="{sq(IMG['contact'], 1000)}" alt="Giorgos Batzios" loading="lazy" width="1000" height="1000">
</div>'''
    page("/contact/", "Contact", "Contact Giorgos Batzios for theater sound, live sound, recording and mixing.", body, IMG["contact"])


# ------------------------------------------------------------------ extras
def build_extras():
    # 404
    page("/404/", "Page not found", "Page not found.",
         head("Not found", "Error 404", 'This page doesn’t exist. <a href="/">Go to the home page</a>.'))
    shutil.move(os.path.join(OUT, "404", "index.html"), os.path.join(OUT, "404.html"))
    os.rmdir(os.path.join(OUT, "404"))
    # Redirects from old Squarespace addresses (Cloudflare Pages / Netlify format)
    lines = ["/studio/v/*  /studio/  301"]
    for s in STUDIO:
        lines.insert(0, f"/studio/v/{s[5]}  /studio/  301")
    for base, _, _, items in SECTIONS:
        for p in items:
            if p["old"] != p["slug"]:
                lines.append(f"{base.rstrip('/')}/{p['old']}  {base}{p['slug']}/  301")
    lines += ["/studio/recording  /studio/  301", "/studio/mixing  /studio/  301", "/studio/production  /studio/  301",
              "/studio/video-edit  /studio/  301", "/studio/custom-sound-library  /studio/  301", "/cart  /  301"]
    open(os.path.join(OUT, "_redirects"), "w").write("\n".join(lines) + "\n")
    # sitemap + robots
    urls = "".join(f"<url><loc>{SITE['url']}{p}</loc></url>" for p in PAGES if p != "/404/")
    open(os.path.join(OUT, "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE['url']}/sitemap.xml\n")


if __name__ == "__main__":
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(os.path.join(os.path.dirname(__file__), "assets"), os.path.join(OUT, "assets"))
    build_home(); build_theater(); build_studio(); build_music(); build_tech()
    build_academic(); build_cv(); build_contact(); build_extras()
    json.dump(PAGES, open(os.path.join(os.path.dirname(__file__), "pages.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print(len(PAGES), "pages")
