# giorgosbatzios.com — how this site works

Personal site of Giorgos Batzios (sound engineer, musician, Athens). The owner is not a developer:
he asks for changes in plain words (often with a poster, photo or YouTube link) and says **"push"**.
Make the change, rebuild, check, commit and push. Keep replies short and non-technical.

## Structure
- `source/content.json` — ALL content. Edit this for almost every request (keep it valid JSON, UTF-8, `indent=1`).
  The owner also edits it himself through **GB EDITOR** (see below), so always start from the latest `preview` branch.
  - Texts that differ by language are `{"en": "...", "el": "..."}`. Always write both.
  - Show titles and song titles stay in their original language (plain strings).
  - Keys: `site` (name, role, fields, email, phone, form_key), `social`, `images` (page photos), `ui` (menu/buttons),
    `text` (page intros, Google descriptions; `{n}` `{from}` `{to}` are filled in by build.py), `theater`,
    `studio_cats` + `studio` (+ `featured_studio` = YouTube id), `music` (`type` "yt" or "sc"; `id` = YouTube id,
    SoundCloud track number or soundcloud.com link), `tech` (`m4l`/`arduino`/`plugins`, each project has `slug`,
    `cover`, `summary`, `download`, `blocks` of type p/h/ul/img/yt/link/mono), `selected` (home cards), `academic`, `cv`.
  - Roles are `{en, el}` pairs inside each item; reuse the same wording as existing items.
- `source/render.mjs` — ALL page templates (pure JS, runs in Node and in the browser). English at `/`, Greek at `/el/`.
  Don't change design unless asked. GB EDITOR uses this same file for its instant preview, so preview = real site.
- `source/build.py` → runs `node source/build.mjs` (writes `site/` from render.mjs) and then draws share cards with `ogcard.py`.
  Always build with `python3 source/build.py`. Don't put page HTML in Python.
- `source/assets/style.css`, `site.js`, `favicon.svg` — design and behaviour.
- `source/assets/img/` — all images, self-hosted as WebP: `<key>.webp` (max 1800px) and `<key>-sm.webp` (max 700px, thumbnails).
  For NEW images: convert to WebP in both sizes with Pillow, save under `source/assets/img/<short-name>.webp` and
  `<short-name>-sm.webp`, and reference them in content.json as `"/assets/img/<short-name>.webp"`
  (build.py automatically uses the `-sm` file for thumbnails when it exists).
- `site/` — the built output. Never edit by hand. Cloudflare regenerates it on every build
  (build command `pip install -q pillow; python3 source/build.py`, set in both Production and Preview build settings),
  so commits that only change content.json (like GB EDITOR's) still update the site. `site/version.txt` = commit of the build.
- `wrangler.jsonc` — Cloudflare Workers config (serves `./site`, custom domains giorgosbatzios.com, www and editor).
- `worker.js` — Worker in front of the files: 301-redirects giorgosbatzios.com → www.giorgosbatzios.com
  (one address for Google; canonical/sitemap use www), serves GB EDITOR on editor.giorgosbatzios.com and its `/api/*`, then serves `./site`.
- `source/ogcard.py` + `source/og-fonts/` — build.py draws a 1200×630 share-preview card per page into `site/og/`.
- `source/assets/fonts/` — self-hosted Geist (Latin) + Inter (Greek letters), OFL licensed. No Google Fonts.
- Name: English pages use "Giorgos Batzios", Greek pages "Γιώργος Μπάτζιος" (`NAME` in build.py).
- Every page has schema.org data (Person, WebSite, BreadcrumbList, VideoObject list for Studio, CreativeWork list for Theater,
  SoftwareApplication for devices/plugins). Every `<img>` needs a descriptive `alt` in the page's language.

## GB EDITOR (editor.giorgosbatzios.com)
The owner's own editing app, same look as the site. Files: `source/editor/` (index.html, editor.css, editor.js; copied to `site/editor/`).
- Password login → signed cookie. Secrets in Cloudflare (Worker → Settings → Variables and Secrets):
  `EDITOR_PASSWORD` (only the owner knows it) and `GITHUB_TOKEN` (fine-grained, Contents read/write on this repo only).
- API in worker.js: `GET /api/content` (syncs preview with main, returns content.json from preview), `POST /api/save`
  (one commit on `preview` with content.json + new images in `source/assets/img/`), `POST /api/publish` (merges preview → main,
  then fast-forwards preview), `POST /api/reset` (preview = main), `GET /api/status` (compares `version.txt` with a commit).
- Preview button = instant: renders all pages in the browser with render.mjs into a cache that `sw.js` (service worker,
  scope `/preview/` on the editor host) serves; then saves to `preview` in the background. Push = save + publish + wait for the live build.
- The editor commits to the same `preview` branch Claude uses: always `git pull` first, and never force-push `preview` or `main`.
- If you add a new kind of content to content.json, also add fields for it in editor.js so the owner can edit it.

## Workflow (preview first, then publish)
The owner wants to SEE changes before they go live.
1. Work on the `preview` branch (`git checkout preview && git merge main` to bring it up to date).
2. `git pull` (GB EDITOR may have committed), edit `source/content.json` (and images if any), then
   `python3 source/build.py` (rewrites `site/`, ~39 pages).
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
