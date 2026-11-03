import sys, io, re, json, statistics, threading, http.server, socketserver
from playwright.sync_api import sync_playwright
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
S = r"C:\Users\brhod\AppData\Local\Temp\claude\C--Users-brhod-OneDrive-Desktop-Projects\6eab5688-8a27-4625-bcfa-cfc59d65ee88\scratchpad"
BASE = open(S + r"\live_home.html", encoding="utf-8").read()
PRE = re.compile(r'<link rel="preload" href="https://finalvestige\.com/wp-content/themes/assembler/assets/fonts/inter/InterVariable\.woff2"[^>]*>')
assert PRE.search(BASE), "font preload not found"
IMG = re.compile(r'(<img\b[^>]*\bwp-post-image\b[^>]*>)')
def lazy_thumbs(h):
    def f(m):
        t = m.group(1).replace(' fetchpriority="high"', '')
        return t if 'loading=' in t else t.replace('<img ', '<img loading="lazy" ', 1)
    return IMG.sub(f, h)
VARIANTS = {
    "v0": ("baseline (saved live HTML, unchanged)", lambda h: h),
    "v1": ("remove the Inter preload link only (font still loads on demand)", lambda h: PRE.sub("", h)),
    "v2": ("lazy-load the query-loop thumbnails, drop fetchpriority=high", lazy_thumbs),
    "v3": ("v1 + v2", lambda h: lazy_thumbs(PRE.sub("", h))),
}
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        k = self.path.strip("/").split("?")[0]
        if k not in VARIANTS: self.send_response(404); self.end_headers(); return
        body = VARIANTS[k][1](BASE).encode("utf-8")
        self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
    def log_message(self, *a): pass
srv = socketserver.TCPServer(("127.0.0.1", 0), H); PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
OBS = """(() => { window.__m = {lcp: 0, lcpTag: '', cls: 0}; new PerformanceObserver(l => { for (const e of l.getEntries()) { window.__m.lcp = Math.round(e.startTime); window.__m.lcpTag = e.element ? e.element.tagName + '.' + String(e.element.className).slice(0, 30) : ''; } }).observe({type: 'largest-contentful-paint', buffered: true});
  new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__m.cls += e.value; }).observe({type: 'layout-shift', buffered: true}); })()"""
NOPOLLUTE = ("collect", "/e/?", "/i/v0/e", "g.gif", "posthog.com/s/", "ahrefs.com/api", "/decide/", "pixel.wp.com", "stats.wp.com/g.gif")
RUNS = int(sys.argv[1]) if len(sys.argv) > 1 else 8
KEYS = sys.argv[2].split(",") if len(sys.argv) > 2 else list(VARIANTS)
res = {k: {"fcp": [], "lcp": [], "cls": [], "font": []} for k in KEYS}
with sync_playwright() as pw:
    b = pw.chromium.launch(channel="msedge", headless=True)
    for run in range(RUNS):
        for k in (KEYS if run % 2 == 0 else list(reversed(KEYS))):   # alternate order to cancel drift
            ctx = b.new_context(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True); pg = ctx.new_page(); cdp = ctx.new_cdp_session(pg)
            cdp.send("Network.enable"); cdp.send("Network.setCacheDisabled", {"cacheDisabled": True}); cdp.send("Emulation.setCPUThrottlingRate", {"rate": 4})
            cdp.send("Network.emulateNetworkConditions", {"offline": False, "latency": 150, "downloadThroughput": 1.6 * 1024 * 1024 / 8, "uploadThroughput": 750 * 1024 / 8})
            def handler(route, request):
                u = request.url
                if any(p in u for p in NOPOLLUTE) and request.method in ("POST", "GET") and "127.0.0.1" not in u: return route.abort()
                return route.continue_()
            pg.route("**/*", handler)
            pg.add_init_script(OBS)
            pg.goto(f"http://127.0.0.1:{PORT}/{k}", wait_until="load", timeout=120000); pg.wait_for_timeout(2500)
            res[k]["fcp"].append(round(pg.evaluate("(performance.getEntriesByName('first-contentful-paint')[0] || {}).startTime || 0")))
            m = pg.evaluate("window.__m"); res[k]["lcp"].append(m["lcp"]); res[k]["cls"].append(round(m["cls"], 4))
            res[k]["font"].append(pg.evaluate("[...document.fonts].filter(f => f.family.includes('Inter') && f.status==='loaded').length")); ctx.close()
    b.close()
print(f"mobile throttled (390x844, CPU 4x, 150 ms RTT, 1.6 Mbps, cache off), {RUNS} runs each, alternating order, local copy of the live HTML")
for k in KEYS:
    r = res[k]
    print(f"{k} {VARIANTS[k][0]:68s} FCP med {int(statistics.median(r['fcp'])):5d} [{min(r['fcp'])}-{max(r['fcp'])}] LCP med {int(statistics.median(r['lcp'])):5d} [{min(r['lcp'])}-{max(r['lcp'])}] CLS max {max(r['cls'])} Inter loaded in {sum(1 for x in r['font'] if x)}/{RUNS}")
json.dump(res, open(S + r"\whatif_result.json", "w"))
