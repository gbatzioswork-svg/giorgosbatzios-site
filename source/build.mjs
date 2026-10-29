// Writes the whole site into ../site from content.json (pages come from render.mjs, shared with GB EDITOR's instant preview).
// Normally run through `python3 source/build.py`, which also draws the share-preview cards.
//   node source/build.mjs [--cards cards.json]
import fs from "node:fs";
import path from "node:path";
import { execSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { render } from "./render.mjs";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(HERE, "..", "site");

const content = JSON.parse(fs.readFileSync(path.join(HERE, "content.json"), "utf8"));
const out = render(content, { exists: (p) => fs.existsSync(path.join(HERE, p)) });

fs.rmSync(OUT, { recursive: true, force: true });
fs.mkdirSync(OUT, { recursive: true });
fs.cpSync(path.join(HERE, "assets"), path.join(OUT, "assets"), { recursive: true });
if (fs.existsSync(path.join(HERE, "editor"))) {
  fs.cpSync(path.join(HERE, "editor"), path.join(OUT, "editor"), { recursive: true });
  fs.copyFileSync(path.join(HERE, "render.mjs"), path.join(OUT, "editor", "render.mjs"));
}
for (const [p, text] of Object.entries(out.files)) {
  const f = path.join(OUT, p);
  fs.mkdirSync(path.dirname(f), { recursive: true });
  fs.writeFileSync(f, text);
}

// which commit this build came from (GB EDITOR checks it to know when the live site is ready)
let sha = process.env.WORKERS_CI_COMMIT_SHA || "";
if (!sha) {
  try { sha = execSync("git rev-parse HEAD", { cwd: HERE, stdio: ["ignore", "pipe", "ignore"] }).toString().trim(); } catch { sha = ""; }
}
fs.writeFileSync(path.join(OUT, "version.txt"), sha + "\n");

const i = process.argv.indexOf("--cards");
if (i > 0) fs.writeFileSync(process.argv[i + 1], JSON.stringify(out.cards));
console.log(out.pages + " pages");
