import sys, io, statistics
from playwright.sync_api import sync_playwright
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
URL = "https://finalvestige.com/"
OBS = """(() => { window.__m = {lcp: 0}; new PerformanceObserver(l => { for (const e of l.getEntries()) window.__m.lcp = Math.round(e.startTime); }).observe({type: 'largest-contentful-paint', buffered: true}); })()"""
LEVERS = {
    "A baseline": [],
    "B drop 2 minor blocking CSS (jetpack related-posts, gravatar patterns)": ["related-posts.css", "patterns-view.css"],
    "C drop both Inter font files (750 KB)": ["InterVariable.woff2", "InterVariable-Italic.woff2"],
    "D drop 3 eager thumbnails (~200 KB)": ["edit-017-v01-mal", "News03a.jpg", "archivalidaho432"],
    "E drop third-party analytics/scripts (gtag x2, posthog, ahrefs, bilmur, stats.wp)": ["googletagmanager.com", "posthog.com", "ahrefs.com", "bilmur", "stats.wp.com"],
    "F B+C+D together": ["related-posts.css", "patterns-view.css", "InterVariable.woff2", "InterVariable-Italic.woff2", "edit-017-v01-mal", "News03a.jpg", "archivalidaho432"],
    "G everything above": ["related-posts.css", "patterns-view.css", "InterVariable.woff2", "InterVariable-Italic.woff2", "edit-017-v01-mal", "News03a.jpg", "archivalidaho432", "googletagmanager.com", "posthog.com", "ahrefs.com", "bilmur", "stats.wp.com"],
}
RUNS = 4
with sync_playwright() as pw:
    b = pw.chromium.launch(channel="msedge", headless=True)
    for name, blocked in LEVERS.items():
        fcps, lcps = [], []
        for run in range(RUNS):
            ctx = b.new_context(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True); pg = ctx.new_page(); cdp = ctx.new_cdp_session(pg)
            cdp.send("Network.enable"); cdp.send("Network.setCacheDisabled", {"cacheDisabled": True}); cdp.send("Emulation.setCPUThrottlingRate", {"rate": 4})
            cdp.send("Network.emulateNetworkConditions", {"offline": False, "latency": 150, "downloadThroughput": 1.6 * 1024 * 1024 / 8, "uploadThroughput": 750 * 1024 / 8})
            if blocked:
                def make(bl):
                    return lambda route, request: route.abort() if any(s in request.url for s in bl) else route.continue_()
                pg.route("**/*", make(blocked))
            pg.add_init_script(OBS)
            pg.goto(URL, wait_until="load", timeout=120000); pg.wait_for_timeout(2500)
            fcps.append(round(pg.evaluate("(performance.getEntriesByName('first-contentful-paint')[0] || {}).startTime || 0")))
            lcps.append(pg.evaluate("window.__m.lcp")); ctx.close()
        print(f"{name:82s} FCP median {int(statistics.median(fcps)):5d} ms {sorted(fcps)} | LCP median {int(statistics.median(lcps)):5d} ms")
    b.close()
