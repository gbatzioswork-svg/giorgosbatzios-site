// Sends visitors of giorgosbatzios.com to www.giorgosbatzios.com (one address for Google),
// everything else is served from the ./site folder.
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.hostname === "giorgosbatzios.com") {
      url.hostname = "www.giorgosbatzios.com";
      return Response.redirect(url.toString(), 301);
    }
    return env.ASSETS.fetch(request);
  },
};
