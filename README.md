# giorgosbatzios.com

- `site/` is the published website (served by Cloudflare Workers, see `wrangler.jsonc`; no build command).
- `source/` holds the content and build script. Edit `source/content.py`, then run `python3 source/build.py` (it rewrites `site/`).
