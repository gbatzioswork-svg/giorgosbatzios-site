# giorgosbatzios.com — how this site works

Personal site of Giorgos Batzios (sound engineer, musician, Athens). The owner is not a developer:
he asks for changes in plain words (often with a poster, photo or YouTube link) and says **"push"**.
Make the change, rebuild, check, commit and push. Keep replies short and non-technical.

## Structure
- `source/content.py` — ALL content. Edit this for almost every request.
  - Texts that differ by language use `T("English", "Ελληνικά")`. Always write both.
  - Show titles and song titles stay in their original language in both versions (plain strings).
  - Lists: `THEATER`, `STUDIO` (+ `FEATURED_STUDIO`), `MUSIC`, `MAX4LIVE`, `ARDUINO`, `PLUGINS`,
    `ACADEMIC`, `CV`, `SELECTED` (3 cards on the home page), `SOCIAL`, `SITE`, `FORM_KEY` (Web3Forms, public).
  - Theater roles are translated through `ROLES`; studio categories through `CATS_EL`; music roles through `MUSIC_ROLES`.
    Add new terms there when needed.
- `source/build.py` — generates the static site. English at `/`, Greek at `/el/`. Don't change design unless asked.
- `source/assets/style.css`, `site.js`, `favicon.svg` — design and behaviour.
- `source/assets/img/` — all images, self-hosted as WebP: `<key>.webp` (max 1800px) and `<key>-sm.webp` (max 700px, thumbnails).
  Old entries reference Squarespace URLs only as IDs; `sq()` in build.py maps them to `/assets/img/<first 13 chars of the id, lowercase>`.
  For NEW images: convert to WebP in both sizes with Pillow, save under `source/assets/img/<short-name>.webp` and
  `<short-name>-sm.webp`, and reference them in content.py as `"/assets/img/<short-name>.webp"`
  (paths that don't contain `squarespace-cdn` are used as-is; use the `-sm` file for thumbnails where needed).
- `site/` — the built output that Cloudflare serves. Never edit by hand; it is regenerated.
- `wrangler.jsonc` — Cloudflare Workers config (serves `./site`, custom domains giorgosbatzios.com + www).
- `worker.js` — tiny Worker in front of the files: 301-redirects giorgosbatzios.com → www.giorgosbatzios.com
  (one address for Google; canonical/sitemap use www), then serves `./site`.
- `source/ogcard.py` + `source/og-fonts/` — build.py draws a 1200×630 share-preview card per page into `site/og/`.
- `source/assets/fonts/` — self-hosted Geist (Latin) + Inter (Greek letters), OFL licensed. No Google Fonts.
- Name: English pages use "Giorgos Batzios", Greek pages "Γιώργος Μπάτζιος" (`NAME` in build.py).
- Every page has schema.org data (Person, WebSite, BreadcrumbList, VideoObject list for Studio, CreativeWork list for Theater,
  SoftwareApplication for devices/plugins). Every `<img>` needs a descriptive `alt` in the page's language.

## Workflow (preview first, then publish)
The owner wants to SEE changes before they go live.
1. Work on the `preview` branch (`git checkout preview && git merge main` to bring it up to date).
2. Edit `source/content.py` (and images if any), then `python3 source/build.py` (rewrites `site/`, ~38 pages).
3. Check: every relative `href`/`src` in `site/**/*.html` resolves to a file; no Python `None` text in pages.
4. Commit and push `preview`. Cloudflare builds a draft copy in ~1 minute at
   **https://preview-giorgosbatzios.gbatzios-work.workers.dev** (Greek: `/el/`). Send the owner that link.
5. Only when the owner says **"push"** (or "publish"/"ok, live"): merge `preview` into `main` and push `main`.
   That deploys to giorgosbatzios.com. If he explicitly says to push straight away, skip the preview.
6. Confirm it's live. If a build hangs/fails at "Initializing", it's Cloudflare's side: tell the owner to click **Retry build**.
   Preview builds need `"previews": {}` in wrangler.jsonc (already there).

## Design (agreed with the owner — keep it)
- Always dark, minimal, one typeface (Geist). Red accent `#b9472f` (the shirt in the home photo) used only for the small round dot after names/titles (`.dotted`) and hovers.
- Home photos use the original Squarespace masks: squircle (top photo, contact photo) and octagon (second photo).
- Bold arrow icons (`ARROW` svg), not the ↗ character.
- YouTube videos load only on click (thumbnail first). Check new YouTube IDs actually play (thumbnail must not be the 120×90 placeholder).

## Notes
- Some Daniel Se videos were removed from YouTube; the site uses the official audio uploads by "Danihl" instead.
- Contact form posts to Web3Forms with `FORM_KEY`; messages go to Gbatzios.work@gmail.com.
- Domain was registered at Squarespace and is being transferred to Cloudflare; DNS is already on Cloudflare.
