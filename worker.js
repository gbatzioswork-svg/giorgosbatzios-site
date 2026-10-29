// giorgosbatzios.com — Cloudflare Worker in front of the static site.
//  * giorgosbatzios.com            → 301 to www.giorgosbatzios.com (one address for Google)
//  * editor.giorgosbatzios.com     → GB EDITOR (files in ./site/editor)
//  * /api/*                        → GB EDITOR backend (password protected)
//  * everything else               → the static site in ./site
//
// Secrets (Cloudflare → Workers & Pages → giorgosbatzios → Settings → Variables and Secrets):
//   EDITOR_PASSWORD  the password for GB EDITOR
//   GITHUB_TOKEN     fine-grained GitHub token with "Contents: Read and write" on the site repository

const OWNER = "gbatzioswork-svg";
const REPO = "giorgosbatzios-site";
const CONTENT_PATH = "source/content.json";
const PREVIEW_BRANCH = "preview";
const LIVE_BRANCH = "main";
const PREVIEW_URL = "https://preview-giorgosbatzios.gbatzios-work.workers.dev";
const LIVE_URL = "https://www.giorgosbatzios.com";
const SESSION_HOURS = 12;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.hostname === "giorgosbatzios.com") {
      url.hostname = "www.giorgosbatzios.com";
      return Response.redirect(url.toString(), 301);
    }
    if (url.pathname.startsWith("/api/")) {
      try {
        return await api(request, env, url);
      } catch (err) {
        return json({ error: "server", message: String(err && err.message || err) }, 500);
      }
    }
    const editorHost = url.hostname.startsWith("editor.");
    const editorPath = url.pathname === "/editor" || url.pathname.startsWith("/editor/");
    if (editorHost || editorPath) {
      if (editorHost && !url.pathname.startsWith("/assets/") && !editorPath) {
        url.pathname = "/editor" + url.pathname;
      }
      const res = await env.ASSETS.fetch(new Request(url.toString(), request));
      const out = new Response(res.body, res);
      out.headers.set("X-Robots-Tag", "noindex, nofollow");
      if (!url.pathname.startsWith("/assets/")) out.headers.set("Cache-Control", "no-store");
      return out;
    }
    return env.ASSETS.fetch(request);
  },
};

// ------------------------------------------------------------------ helpers
function json(data, status = 200, headers = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store", ...headers },
  });
}

const enc = new TextEncoder();

function b64url(bytes) {
  let s = "";
  for (const b of new Uint8Array(bytes)) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

async function sha256(text) {
  return new Uint8Array(await crypto.subtle.digest("SHA-256", enc.encode(text)));
}

async function hmacKey(env) {
  const material = await sha256("gb-editor|" + env.EDITOR_PASSWORD + "|" + env.GITHUB_TOKEN);
  return crypto.subtle.importKey("raw", material, { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
}

async function makeSession(env) {
  const exp = String(Date.now() + SESSION_HOURS * 3600 * 1000);
  const sig = await crypto.subtle.sign("HMAC", await hmacKey(env), enc.encode(exp));
  return exp + "." + b64url(sig);
}

function equalBytes(a, b) {
  if (a.length !== b.length) return false;
  if (crypto.subtle.timingSafeEqual) return crypto.subtle.timingSafeEqual(a, b);
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a[i] ^ b[i];
  return d === 0;
}

async function checkSession(request, env) {
  const cookie = request.headers.get("Cookie") || "";
  const m = cookie.match(/(?:^|;\s*)gbsess=([^;]+)/);
  if (!m) return false;
  const [exp, sig] = m[1].split(".");
  if (!exp || !sig || Number(exp) < Date.now()) return false;
  const good = b64url(await crypto.subtle.sign("HMAC", await hmacKey(env), enc.encode(exp)));
  return equalBytes(enc.encode(good), enc.encode(sig));
}

function cookieHeader(value, maxAge) {
  return `gbsess=${value}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=${maxAge}`;
}

async function gh(env, path, opts = {}) {
  const res = await fetch("https://api.github.com/repos/" + OWNER + "/" + REPO + path, {
    method: opts.method || "GET",
    headers: {
      Authorization: "Bearer " + env.GITHUB_TOKEN,
      Accept: opts.accept || "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "gb-editor",
      ...(opts.body ? { "Content-Type": "application/json" } : {}),
    },
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  if (opts.raw) return res;
  const text = await res.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch { data = text; }
  if (!res.ok && !(opts.ok || []).includes(res.status)) {
    const msg = (data && data.message) || res.statusText;
    const e = new Error("GitHub " + res.status + ": " + msg);
    e.status = res.status;
    throw e;
  }
  return { status: res.status, data };
}

async function headSha(env, branch) {
  return (await gh(env, "/git/ref/heads/" + branch)).data.object.sha;
}

// Bring the preview branch up to date with the live branch (e.g. after changes made outside the editor).
async function syncPreview(env) {
  const cmp = (await gh(env, "/compare/" + LIVE_BRANCH + "..." + PREVIEW_BRANCH)).data;
  if (cmp.status === "behind") {
    // preview has nothing of its own: just move it forward to the live version
    await gh(env, "/git/refs/heads/" + PREVIEW_BRANCH, { method: "PATCH", body: { sha: await headSha(env, LIVE_BRANCH), force: false } });
  } else if (cmp.status === "diverged") {
    await gh(env, "/merges", {
      method: "POST",
      body: { base: PREVIEW_BRANCH, head: LIVE_BRANCH, commit_message: "Bring preview up to date with the live site" },
      ok: [204],
    });
  }
}

// Does the preview contain changes that are not live? (compares files, not commits)
async function hasUnpublished(env) {
  const cmp = (await gh(env, "/compare/" + LIVE_BRANCH + "..." + PREVIEW_BRANCH)).data;
  return (cmp.ahead_by || 0) > 0 && (cmp.files || []).length > 0;
}

// Which commit the files of THIS deployment were built from (a Worker can't fetch its own workers.dev / custom domains).
async function ownVersion(env) {
  try {
    const r = await env.ASSETS.fetch(new Request("https://assets.local/version.txt"));
    return r.ok ? (await r.text()).trim() : "";
  } catch {
    return "";
  }
}

// ------------------------------------------------------------------ API
async function api(request, env, url) {
  const route = url.pathname.replace(/^\/api\//, "");
  if (!env.EDITOR_PASSWORD || !env.GITHUB_TOKEN) {
    return json({ error: "setup", message: "GB EDITOR is not set up yet: the EDITOR_PASSWORD and GITHUB_TOKEN secrets are missing in Cloudflare." }, 503);
  }
  if (request.method === "POST" && request.headers.get("X-GB") !== "1") {
    return json({ error: "forbidden" }, 403);
  }

  if (route === "login" && request.method === "POST") {
    const body = await request.json().catch(() => ({}));
    const ok = equalBytes(await sha256(String(body.password || "")), await sha256(env.EDITOR_PASSWORD));
    if (!ok) {
      await new Promise((r) => setTimeout(r, 900));
      return json({ error: "wrong_password" }, 401);
    }
    return json({ ok: true }, 200, { "Set-Cookie": cookieHeader(await makeSession(env), SESSION_HOURS * 3600) });
  }
  if (route === "logout") {
    return json({ ok: true }, 200, { "Set-Cookie": cookieHeader("", 0) });
  }
  if (!(await checkSession(request, env))) return json({ error: "login" }, 401);

  // ---- read the content (from the preview branch, which always contains the latest saved draft)
  if (route === "content" && request.method === "GET") {
    await syncPreview(env);
    const head = await headSha(env, PREVIEW_BRANCH);
    const live = await headSha(env, LIVE_BRANCH);
    const res = await gh(env, "/contents/" + CONTENT_PATH + "?ref=" + head, { accept: "application/vnd.github.raw+json", raw: true });
    if (!res.ok) throw new Error("Could not read the content file (" + res.status + ")");
    const content = JSON.parse(await res.text());
    return json({ content, head, live, unpublished: await hasUnpublished(env), previewUrl: PREVIEW_URL, liveUrl: LIVE_URL });
  }

  // ---- save the draft (content + new images) as one commit on the preview branch
  if (route === "save" && request.method === "POST") {
    const body = await request.json();
    if (!body || typeof body.content !== "object") return json({ error: "bad_request" }, 400);
    const head = await headSha(env, PREVIEW_BRANCH);
    if (body.base && body.base !== head) {
      return json({ error: "conflict", message: "The site was changed somewhere else in the meantime. Reload the editor to continue." }, 409);
    }
    const baseTree = (await gh(env, "/git/commits/" + head)).data.tree.sha;
    const tree = [];
    for (const img of body.images || []) {
      if (!/^source\/assets\/img\/[a-z0-9._-]+\.(webp|jpg|jpeg|png)$/i.test(img.path)) continue;
      const blob = await gh(env, "/git/blobs", { method: "POST", body: { content: img.data, encoding: "base64" } });
      tree.push({ path: img.path, mode: "100644", type: "blob", sha: blob.data.sha });
    }
    const text = JSON.stringify(body.content, null, 1) + "\n";
    const blob = await gh(env, "/git/blobs", { method: "POST", body: { content: text, encoding: "utf-8" } });
    tree.push({ path: CONTENT_PATH, mode: "100644", type: "blob", sha: blob.data.sha });
    const newTree = await gh(env, "/git/trees", { method: "POST", body: { base_tree: baseTree, tree } });
    const commit = await gh(env, "/git/commits", {
      method: "POST",
      body: { message: (body.message || "Edit from GB EDITOR").slice(0, 200), tree: newTree.data.sha, parents: [head] },
    });
    await gh(env, "/git/refs/heads/" + PREVIEW_BRANCH, { method: "PATCH", body: { sha: commit.data.sha } });
    return json({ ok: true, head: commit.data.sha });
  }

  // ---- publish: bring everything from preview into the live site
  if (route === "publish" && request.method === "POST") {
    const r = await gh(env, "/merges", {
      method: "POST",
      body: { base: LIVE_BRANCH, head: PREVIEW_BRANCH, commit_message: "Publish from GB EDITOR" },
      ok: [204],
    });
    const live = r.status === 204 ? await headSha(env, LIVE_BRANCH) : r.data.sha;
    // keep preview identical to live afterwards (fast-forward, never loses anything)
    let head = await headSha(env, PREVIEW_BRANCH);
    if (r.status !== 204) {
      try {
        await gh(env, "/git/refs/heads/" + PREVIEW_BRANCH, { method: "PATCH", body: { sha: live, force: false } });
        head = live;
      } catch { /* preview moved meanwhile; the next load merges it */ }
    }
    return json({ ok: true, nothing: r.status === 204, commit: live, head });
  }

  // ---- throw away everything on preview that is not live
  if (route === "reset" && request.method === "POST") {
    const live = await headSha(env, LIVE_BRANCH);
    await gh(env, "/git/refs/heads/" + PREVIEW_BRANCH, { method: "PATCH", body: { sha: live, force: true } });
    return json({ ok: true, head: live });
  }

  // ---- is the preview / live site built from this commit yet?
  // Live: this Worker's own files tell us. Preview: Cloudflare reports each build back to GitHub as a check run.
  if (route === "status" && request.method === "GET") {
    const target = url.searchParams.get("target") === "live" ? "live" : "preview";
    const commit = url.searchParams.get("commit") || "";
    if (!commit) return json({ ready: false, failed: false });
    if (target === "live" && (await ownVersion(env)) === commit) return json({ ready: true });
    let runs = [];
    try {
      runs = (await gh(env, "/commits/" + commit + "/check-runs?per_page=50")).data.check_runs || [];
    } catch { /* not reported yet */ }
    const mine = runs.filter((r) => (target === "preview") === (r.details_url || "").includes("/previews/"));
    const bad = mine.find((r) => r.status === "completed" && r.conclusion && !["success", "neutral", "skipped"].includes(r.conclusion));
    if (bad) return json({ ready: false, failed: true, link: bad.details_url || "" });
    const ok = mine.find((r) => r.status === "completed" && r.conclusion === "success");
    if (ok) {
      // give the new files a few seconds to reach every Cloudflare location
      const done = Date.parse(ok.completed_at || "") || 0;
      return json({ ready: Date.now() - done > (target === "preview" ? 8000 : 45000) });
    }
    return json({ ready: false, failed: false });
  }

  return json({ error: "not_found" }, 404);
}
