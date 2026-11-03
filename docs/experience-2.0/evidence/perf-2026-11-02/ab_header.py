import sys, io, re, json, statistics, threading, http.server, socketserver, urllib.request, time
from playwright.sync_api import sync_playwright
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
S = r"C:\Users\brhod\AppData\Local\Temp\claude\C--Users-brhod-OneDrive-Desktop-Projects\6eab5688-8a27-4625-bcfa-cfc59d65ee88\scratchpad"
OLD = open(S + r"\live_home.html", encoding="utf-8").read()
NEW = urllib.request.urlopen(urllib.request.Request("https://finalvestige.com/?fvcb=%d" % int(time.time()), headers={"User-Agent": "Mozilla/5.0 (compatible; fv-ab)"}), timeout=60).read().decode("utf-8", "replace")
open(S + r"\live_home_new.html", "w", encoding="utf-8").write(NEW)
print("old bytes", len(OLD), "new bytes", len(NEW))
V = {"old": OLD, "new": NEW}
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        k = self.path.strip("/").split("?")[0]
        if k not in V: self.send_response(404); self.end_headers(); return
        body = V[k].encode("utf-8"); self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
    def log_message(self, *a): pass
srv = socketserver.TCPServer(("127.0.0.1", 0), H); PORT = srv.server_address[1]; threading.Thread(target=srv.serve_forever, daemon=True).start()
OBS = """(() => { window.__m = {lcp: 0, cls: 0}; new PerformanceObserver(l => { for (const e of l.getEntries()) window.__m.lcp = Math.round(e.startTime); }).observe({type: 'largest-contentful-paint', buffered: true});
  new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__m.cls += e.value; }).observe({type: 'layout-shift', buffered: true}); })()"""
NOP = ("collect", "/e/?", "/i/v0/e", "g.gif", "posthog.com/s/", "ahrefs.com/api", "/decide/", "pixel.wp.com", "stats.wp.com/g.gif")
RUNS = 10; res = {k: {"fcp": [], "lcp": [], "cls": []} for k in V}
with sync_playwright() as pw:
    b = pw.chromium.launch(channel="msedge", headless=True)
    for run in range(RUNS):
        for k in (list(V) if run % 2 == 0 else list(reversed(list(V)))):
            ctx = b.new_context(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True); pg = ctx.new_page(); cdp = ctx.new_cdp_session(pg)
            cdp.send("Network.enable"); cdp.send("Network.setCacheDisabled", {"cacheDisabled": True}); cdp.send("Emulation.setCPUThrottlingRate", {"rate": 4})
            cdp.send("Network.emulateNetworkConditions", {"offline": False, "latency": 150, "downloadThroughput": 1.6 * 1024 * 1024 / 8, "uploadThroughput": 750 * 1024 / 8})
            pg.route("**/*", lambda route, request: route.abort() if any(p in request.url for p in NOP) and "127.0.0.1" not in request.url else route.continue_())
            pg.add_init_script(OBS); pg.goto(f"http://127.0.0.1:{PORT}/{k}", wait_until="load", timeout=120000); pg.wait_for_timeout(2500)
            res[k]["fcp"].append(round(pg.evaluate("(performance.getEntriesByName('first-contentful-paint')[0] || {}).startTime || 0"))); m = pg.evaluate("window.__m")
            res[k]["lcp"].append(m["lcp"]); res[k]["cls"].append(round(m["cls"], 4)); ctx.close()
    b.close()
for k in V:
    r = res[k]; print(f"{k}: FCP med {int(statistics.median(r['fcp']))} [{min(r['fcp'])}-{max(r['fcp'])}] | LCP med {int(statistics.median(r['lcp']))} [{min(r['lcp'])}-{max(r['lcp'])}] | CLS max {max(r['cls'])}")
json.dump(res, open(S + r"\ab_header_result.json", "w"))
