"""Draws the 1200x630 preview images shown when a page is shared (WhatsApp, Facebook, LinkedIn…)."""
import math, os, unicodedata
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(HERE, "og-fonts")
W, H = 1200, 630
BG, INK, MUTED, ACCENT = (13, 13, 14), (243, 243, 244), (157, 157, 163), (185, 71, 47)

_cache = {}


def _font(kind, size):
    """kind: 'bold' or 'reg'. Geist for Latin, Inter for Greek (Geist has no Greek letters)."""
    key = (kind, size)
    if key not in _cache:
        geist = "Geist-SemiBold.ttf" if kind == "bold" else "Geist-Regular.ttf"
        inter = "Inter-SemiBold.otf" if kind == "bold" else "Inter-Regular.otf"
        _cache[key] = (ImageFont.truetype(os.path.join(F, geist), size), ImageFont.truetype(os.path.join(F, inter), size))
    return _cache[key]


def _is_greek(ch):
    o = ord(ch)
    return 0x370 <= o <= 0x3FF or 0x1F00 <= o <= 0x1FFF


def _runs(text):
    out, cur, g = [], "", None
    for ch in text:
        gg = _is_greek(ch) if ch.strip() else g
        if g is None or gg == g:
            cur += ch
        else:
            out.append((cur, g)); cur = ch
        g = gg
    if cur:
        out.append((cur, g))
    return out


def _width(text, kind, size, track=0.0):
    latin, greek = _font(kind, size)
    return sum((greek if g else latin).getlength(t) for t, g in _runs(text)) + track * size * max(len(text) - 1, 0)


def _draw(d, xy, text, kind, size, fill, track=0.0):
    latin, greek = _font(kind, size)
    x, y = xy
    for t, g in _runs(text):
        f = greek if g else latin
        if track:
            for ch in t:
                d.text((x, y), ch, font=f, fill=fill)
                x += f.getlength(ch) + track * size
        else:
            d.text((x, y), t, font=f, fill=fill)
            x += f.getlength(t)
    return x


def _wrap(text, kind, size, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if _width(test, kind, size, -0.03) <= max_w or not cur:
            cur = test
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def caps(text):
    """Uppercase without accents (Greek capitals are written without tonos)."""
    t = unicodedata.normalize("NFD", text.upper())
    return unicodedata.normalize("NFC", "".join(c for c in t if unicodedata.category(c) != "Mn"))


def make(path, title, kicker, footer_name, tagline):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # faint dot grid, stronger towards the right
    for gx in range(30, W, 30):
        for gy in range(30, H, 30):
            a = max(0.0, (gx - 420) / 780) * 0.22
            if a > 0.01:
                c = tuple(int(BG[i] + (255 - BG[i]) * a * 0.5) for i in range(3))
                d.ellipse((gx - 1.1, gy - 1.1, gx + 1.1, gy + 1.1), fill=c)
    # the sound-wave line
    mid = 185
    pts = []
    for i in range(0, 801):
        x = i / 800
        env = math.sin(math.pi * x)
        y = math.sin(x * 38) * 0.55 + math.sin(x * 91 + 1.2) * 0.3 + math.sin(x * 13 + 0.4) * 0.4
        pts.append((380 + x * 760, mid + y / 1.25 * env * 34))
    for i in range(len(pts) - 1):
        x = (pts[i][0] - 380) / 760
        fade = min(1.0, min(x, 1 - x) / 0.18)
        c = tuple(int(BG[k] + (200 - BG[k]) * fade * 0.55) for k in range(3))
        d.line([pts[i], pts[i + 1]], fill=c, width=2)
    # top: name + red dot, small
    nx = _draw(d, (72, 64), caps(footer_name), "bold", 26, INK, track=0.08)
    d.ellipse((nx + 3, 64 + 19, nx + 10, 64 + 26), fill=ACCENT)
    # title (big, up to 2 lines) + red dot
    size = 108
    lines = _wrap(title, "bold", size, 1056)
    while len(lines) > 2 and size > 60:
        size -= 8
        lines = _wrap(title, "bold", size, 1056)
    lines = lines[:2]
    y = H - 72 - size * 1.02 * len(lines) - 54
    if kicker:
        _draw(d, (72, y - 50), kicker, "reg", 30, MUTED)
    for i, ln in enumerate(lines):
        end = _draw(d, (68, y + i * size * 1.02), ln, "bold", size, INK, track=-0.03)
    r = max(6, size * 0.075)
    by = y + (len(lines) - 1) * size * 1.02 + size * 0.86
    d.ellipse((end + size * 0.05, by - r * 2, end + size * 0.05 + r * 2, by), fill=ACCENT)
    # tagline at the bottom
    _draw(d, (72, H - 72 - 30), tagline, "reg", 30, MUTED)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, "PNG", optimize=True)
