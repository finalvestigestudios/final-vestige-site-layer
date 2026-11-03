import sys, io, json, threading, http.server, socketserver, collections
from playwright.sync_api import sync_playwright
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
S = r"C:\Users\brhod\AppData\Local\Temp\claude\C--Users-brhod-OneDrive-Desktop-Projects\6eab5688-8a27-4625-bcfa-cfc59d65ee88\scratchpad"
HTML = open(S + r"\live_home_new.html", encoding="utf-8").read()
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        b = HTML.encode("utf-8"); self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def log_message(self, *a): pass
srv = socketserver.TCPServer(("127.0.0.1", 0), H); PORT = srv.server_address[1]; threading.Thread(target=srv.serve_forever, daemon=True).start()
OBS = """(() => { window.__e = []; new PerformanceObserver(l => { for (const e of l.getEntries()) window.__e.push({t: Math.round(e.startTime), tag: e.element ? e.element.tagName + '.' + String(e.element.className).slice(0, 36) : '?', url: (e.url || '').slice(-50), size: e.size, rt: Math.round(e.renderTime), lt: Math.round(e.loadTime)}); }).observe({type: 'largest-contentful-paint', buffered: true});
  window.__fonts = []; document.fonts.addEventListener('loadingdone', () => window.__fonts.push(Math.round(performance.now()))); })()"""
NOP = ("collect", "/e/?", "/i/v0/e", "g.gif", "posthog.com/s/", "ahrefs.com/api", "/decide/", "pixel.wp.com", "stats.wp.com/g.gif")
with sync_playwright() as pw:
    b = pw.chromium.launch(channel="msedge", headless=True)
    for run in range(12):
        ctx = b.new_context(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True); pg = ctx.new_page(); cdp = ctx.new_cdp_session(pg)
        cdp.send("Network.enable"); cdp.send("Network.setCacheDisabled", {"cacheDisabled": True}); cdp.send("Emulation.setCPUThrottlingRate", {"rate": 4})
        cdp.send("Network.emulateNetworkConditions", {"offline": False, "latency": 150, "downloadThroughput": 1.6 * 1024 * 1024 / 8, "uploadThroughput": 750 * 1024 / 8})
        BLK = sys.argv[1].split(",") if len(sys.argv) > 1 else []
        pg.route("**/*", lambda route, request: route.abort() if (any(p in request.url for p in NOP) or any(p in request.url for p in BLK)) and "127.0.0.1" not in request.url else route.continue_())
        pg.add_init_script(OBS); pg.goto(f"http://127.0.0.1:{PORT}/", wait_until="load", timeout=120000); pg.wait_for_timeout(3000)
        e = pg.evaluate("window.__e"); fonts = pg.evaluate("window.__fonts")
        print(run, " | ".join(f"{x['t']}ms {x['tag']}" + (f" img:{x['url']}" if x['url'] else "") for x in e), "| fonts loaded at", fonts)
        ctx.close()
    b.close()
