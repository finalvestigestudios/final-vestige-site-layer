"""LCP bimodality harness (local copy of live homepage HTML, throttled mobile, analytics collection aborted).

Method (identical to perf-2026-11-02): Playwright + Edge (msedge channel), 390x844 mobile, CDP CPU 4x,
150 ms RTT, 1.6 Mbps down / 750 kbps up, HTTP cache disabled, analytics *collection* requests aborted.
Every run is a fresh browser context. Variants are served from 127.0.0.1 under /<variant>; order alternates per round.

usage: python harness.py --html base.html --variants base,x --runs 30 --mode light|rich --out out.jsonl
       [--variant-file variants.py] [--cpu 4] [--cache cold|warm] [--block substr,substr]
Variant transforms live in VARIANTS (pure string -> string functions, applied to the saved HTML only).
"""
import sys, io, json, threading, http.server, socketserver, time, argparse
from playwright.sync_api import sync_playwright
try:
    import psutil
except Exception:
    psutil = None
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

NOP = ("collect", "/e/?", "/i/v0/e", "g.gif", "posthog.com/s/", "ahrefs.com/api", "/decide/", "pixel.wp.com", "stats.wp.com/g.gif")

LIGHT = r"""(() => {
  const W = window.__w = {lcp: [], lt: [], ls: [], paint: [], fonts: [], marks: {}};
  const r = Math.round;
  const desc = e => e ? e.tagName + '.' + String(e.className).slice(0, 40) : '?';
  new PerformanceObserver(l => { for (const e of l.getEntries()) W.lcp.push({t: r(e.startTime), rt: r(e.renderTime), lt: r(e.loadTime), size: e.size, el: desc(e.element), url: (e.url||'').slice(-40)}); }).observe({type: 'largest-contentful-paint', buffered: true});
  new PerformanceObserver(l => { for (const e of l.getEntries()) W.lt.push([r(e.startTime), r(e.duration)]); }).observe({type: 'longtask', buffered: true});
  new PerformanceObserver(l => { for (const e of l.getEntries()) W.ls.push({t: r(e.startTime), v: e.value, src: (e.sources||[]).map(s => desc(s.node))}); }).observe({type: 'layout-shift', buffered: true});
  new PerformanceObserver(l => { for (const e of l.getEntries()) W.paint.push([e.name, r(e.startTime)]); }).observe({type: 'paint', buffered: true});
  try { document.fonts.addEventListener('loading', () => W.fonts.push(['loading', r(performance.now())])); document.fonts.addEventListener('loadingdone', e => W.fonts.push(['done', r(performance.now()), (e.fontfaces||[]).map(f => f.family + ' ' + f.style + ' ' + f.status).join(',')])); document.fonts.addEventListener('loadingerror', e => W.fonts.push(['error', r(performance.now())])); } catch (e) {}
  document.addEventListener('DOMContentLoaded', () => W.marks.dcl = r(performance.now()));
  addEventListener('load', () => W.marks.load = r(performance.now()));
})()"""

# rich: rAF sampler of the dek + mutation log. Perturbs timing slightly; never used for the distributions.
RICH = LIGHT + r"""
;(() => {
  const W = window.__w; W.dek = []; W.mut = []; const r = Math.round;
  const q = () => document.querySelector('.fv-hf__opening-dek');
  let last = '';
  const tick = () => {
    const d = q();
    if (d) {
      const cs = getComputedStyle(d), rc = d.getBoundingClientRect(), h1 = document.querySelector('#fv-hf-title');
      const s = [cs.opacity, cs.visibility, cs.display, cs.contentVisibility, cs.fontFamily.slice(0, 30), cs.fontSize, r(rc.width), r(rc.height), r(rc.top), document.fonts.check('17px Inter') ? 1 : 0, h1 ? r(h1.getBoundingClientRect().height) : -1].join('|');
      if (s !== last) { W.dek.push([r(performance.now()), s]); last = s; }
    } else if (last !== 'none') { W.dek.push([r(performance.now()), 'none']); last = 'none'; }
    if (performance.now() < 8000) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
  new MutationObserver(ms => { for (const m of ms) { const t = m.target; W.mut.push([r(performance.now()), m.type, t.nodeType === 1 ? (t.tagName + '.' + String(t.className).slice(0, 40)) : '#', m.attributeName || '', (m.attributeName && t.getAttribute) ? String(t.getAttribute(m.attributeName)).slice(0, 60) : '']); } }).observe(document, {subtree: true, attributes: true, childList: true, attributeFilter: ['class', 'style', 'hidden', 'aria-hidden']});
})()"""


def ident(h):
    return h


def _rep(h, a, b, count=1):
    assert a in h, "pattern not found: " + a[:60]
    return h.replace(a, b, count)


VARIANTS = {"base": ident, "ctl": ident}   # 'ctl' = identical copy at a different URL (A/A control)


def load_variants_from_file(path):
    g = {"_rep": _rep}
    exec(open(path, encoding="utf-8").read(), g)
    VARIANTS.update(g["VARIANTS"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", required=True)
    ap.add_argument("--variants", default="base")
    ap.add_argument("--runs", type=int, default=30)
    ap.add_argument("--mode", default="light")
    ap.add_argument("--out", required=True)
    ap.add_argument("--cpu", type=float, default=4)
    ap.add_argument("--cache", default="cold")
    ap.add_argument("--block", default="")
    ap.add_argument("--variant-file", default="")
    ap.add_argument("--net", default="1.6")
    ap.add_argument("--rtt", type=int, default=150)
    ap.add_argument("--wait", type=int, default=3000)
    ap.add_argument("--enc", default="none", help="none|gzip: Content-Encoding the local server uses (live serves br, ~89 KB vs 406 KB identity)")
    ap.add_argument("--live", default="", help="URL: variant named 'live' navigates to this real URL instead of the local copy")
    a = ap.parse_args()
    if a.variant_file:
        load_variants_from_file(a.variant_file)
    base = open(a.html, encoding="utf-8").read()
    names = a.variants.split(",")
    import gzip
    pages = {n: VARIANTS[n](base).encode("utf-8") for n in names if n != "live"}
    if a.enc == "gzip":
        pages = {n: gzip.compress(b, 6) for n, b in pages.items()}

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            k = self.path.strip("/").split("?")[0]
            if k not in pages:
                self.send_response(404); self.end_headers(); return
            b = pages[k]
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(b)))
            if a.enc == "gzip":
                self.send_header("Content-Encoding", "gzip")
            self.send_header("Cache-Control", "max-age=0" if a.cache == "cold" else "max-age=600"); self.end_headers(); self.wfile.write(b)

        def log_message(self, *x):
            pass

    srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), H)
    srv.daemon_threads = True
    PORT = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    blk = [x for x in a.block.split(",") if x]
    init = RICH if a.mode == "rich" else LIGHT
    out = open(a.out, "a", encoding="utf-8")
    with sync_playwright() as pw:
        b = pw.chromium.launch(channel="msedge", headless=True)
        for rnd in range(a.runs):
            order = names if rnd % 2 == 0 else list(reversed(names))
            for k in order:
                ctx = b.new_context(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True)
                pg = ctx.new_page()
                cdp = ctx.new_cdp_session(pg)
                ev = {}
                cdp.send("Network.enable")
                cdp.send("Network.setCacheDisabled", {"cacheDisabled": a.cache == "cold"})
                cdp.send("Emulation.setCPUThrottlingRate", {"rate": a.cpu})
                cdp.send("Network.emulateNetworkConditions", {"offline": False, "latency": a.rtt, "downloadThroughput": float(a.net) * 1024 * 1024 / 8, "uploadThroughput": 750 * 1024 / 8})
                if a.mode == "rich":
                    cdp.on("Network.requestWillBeSent", lambda p: ev.setdefault(p["requestId"], {}).update(url=p["request"]["url"][-90:], t0=p["timestamp"], prio=p["request"].get("initialPriority"), type=p.get("type")))
                    cdp.on("Network.responseReceived", lambda p: ev.setdefault(p["requestId"], {}).update(t1=p["timestamp"], status=p["response"]["status"], fromcache=p["response"].get("fromDiskCache", False), mime=p["response"].get("mimeType")))
                    cdp.on("Network.loadingFinished", lambda p: ev.setdefault(p["requestId"], {}).update(t2=p["timestamp"], bytes=p.get("encodedDataLength")))
                    cdp.on("Network.loadingFailed", lambda p: ev.setdefault(p["requestId"], {}).update(t2=p["timestamp"], failed=p.get("errorText")))
                pg.route("**/*", lambda route, request: route.abort() if (any(p in request.url for p in NOP) or any(p in request.url for p in blk)) and "127.0.0.1" not in request.url else route.continue_())
                pg.add_init_script(init)
                if psutil:
                    psutil.cpu_percent(interval=None)
                t_wall = time.time()
                if a.cache == "warm":   # prime the HTTP cache with an untimed load, then measure a second navigation
                    pg.goto(f"http://127.0.0.1:{PORT}/{k}?prime", wait_until="load", timeout=120000)
                    pg.wait_for_timeout(1500)
                    pg.goto("about:blank")
                    ev.clear()
                pg.goto(a.live if k == "live" else f"http://127.0.0.1:{PORT}/{k}", wait_until="load", timeout=120000)
                pg.wait_for_timeout(a.wait)
                hostcpu = psutil.cpu_percent(interval=None) if psutil else None
                w = pg.evaluate("window.__w")
                res = pg.evaluate("performance.getEntriesByType('resource').map(e => [e.name.slice(-80), Math.round(e.startTime), Math.round(e.responseEnd), e.transferSize, e.initiatorType, e.renderBlockingStatus || ''])")
                nav = pg.evaluate("(() => { const n = performance.getEntriesByType('navigation')[0]; return [Math.round(n.responseEnd), Math.round(n.domContentLoadedEventEnd), Math.round(n.loadEventEnd)]; })()")
                rec = {"variant": k, "round": rnd, "mode": a.mode, "cache": a.cache, "cpu": a.cpu, "enc": a.enc, "ts": round(t_wall, 1), "hostcpu": hostcpu, "w": w, "res": res, "nav": nav}
                if a.mode == "rich":
                    rec["net"] = sorted([v for v in ev.values() if "t0" in v], key=lambda v: v["t0"])
                out.write(json.dumps(rec) + "\n")
                out.flush()
                lcp = w["lcp"][-1] if w["lcp"] else {}
                fcp = next((p[1] for p in w["paint"] if p[0] == "first-contentful-paint"), None)
                print(f"{rnd:3d} {k:10s} FCP {fcp} LCP {lcp.get('t')} {lcp.get('el')} n={len(w['lcp'])} fonts={[f[:2] for f in w['fonts']]} cpu={hostcpu}", flush=True)
                ctx.close()
        b.close()


if __name__ == "__main__":
    main()
