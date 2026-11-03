import sys, io, json, time
from playwright.sync_api import sync_playwright
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
OUT = sys.argv[1]; AXE = r"C:\Users\brhod\OneDrive\Desktop\Projects\fv-ex2-living-archive\experience-2.0\tools\.cache\axe-4.10.2.min.js"
ts = int(time.time()); R = {}
JS = """() => { const hd = document.querySelector('.fv-site-header'); const q = s => hd && hd.querySelector(s); const vis = e => e && e.getBoundingClientRect().width > 0 && getComputedStyle(e).display !== 'none' && getComputedStyle(e).visibility !== 'hidden';
  const pill = q('.fv-nav-free-ebook a'), strip = q('.fv-ebook-strip a'); const el = vis(pill) ? pill : (vis(strip) ? strip : null);
  const r = el && el.getBoundingClientRect(); const cs = el && getComputedStyle(el);
  return {headerH: hd && Math.round(hd.getBoundingClientRect().height), hscroll: document.documentElement.scrollWidth > innerWidth, kind: el === pill ? 'nav-pill' : (el === strip ? 'strip' : 'none'),
          href: el && el.getAttribute('href'), text: el && el.textContent.trim().replace(/\\s+/g, ' '), box: r && [Math.round(r.left), Math.round(r.right), Math.round(r.top), Math.round(r.width), Math.round(r.height)], color: cs && cs.color, bg: cs && cs.backgroundColor,
          navItemsInOneRow: (() => { const lis = [...document.querySelectorAll('.fv-primary-nav .wp-block-navigation__container > li')].filter(l => l.getBoundingClientRect().width > 0); if (!lis.length) return null; const tops = new Set(lis.map(l => Math.round(l.getBoundingClientRect().top / 10))); return tops.size === 1; })()}; }"""
with sync_playwright() as pw:
    b = pw.chromium.launch(channel="msedge", headless=True)
    for w, h in [(360, 740), (390, 844), (768, 1024), (1024, 768), (1279, 800), (1280, 800), (1440, 900), (1920, 1080)]:
        ctx = b.new_context(viewport={"width": w, "height": h}, is_mobile=w < 700, has_touch=w < 700); pg = ctx.new_page()
        pg.goto(f"https://finalvestige.com/?fvcb={ts}", wait_until="load", timeout=90000); pg.wait_for_timeout(1200)
        R[f"home@{w}"] = pg.evaluate(JS)
        pg.screenshot(path=f"{OUT}-{w}.png", clip={"x": 0, "y": 0, "width": w, "height": min(h, 240)})
        ctx.close()
    # /focus/: neither the strip nor the pill may show
    ctx = b.new_context(viewport={"width": 1440, "height": 900}); pg = ctx.new_page(); pg.goto(f"https://finalvestige.com/focus/?fvcb={ts}", wait_until="load", timeout=90000); pg.wait_for_timeout(1000)
    R["focus@1440"] = pg.evaluate(JS); ctx.close()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True); pg = ctx.new_page(); pg.goto(f"https://finalvestige.com/focus/?fvcb={ts}", wait_until="load", timeout=90000); pg.wait_for_timeout(1000)
    R["focus@390"] = pg.evaluate(JS); ctx.close()
    # a post page, mobile + desktop
    for w, h, mob in [(390, 844, True), (1440, 900, False)]:
        ctx = b.new_context(viewport={"width": w, "height": h}, is_mobile=mob, has_touch=mob); pg = ctx.new_page()
        pg.goto("https://finalvestige.com/2026/11/02/mesmerism/", wait_until="load", timeout=90000); pg.wait_for_timeout(1200)
        R[f"post@{w}"] = pg.evaluate(JS); ctx.close()
    # mobile overlay: open menu, find Free Ebook, click through
    ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True); pg = ctx.new_page(); pg.goto(f"https://finalvestige.com/?fvcb={ts}", wait_until="load", timeout=90000); pg.wait_for_timeout(1000)
    pg.locator(".fv-primary-nav .wp-block-navigation__responsive-container-open").first.click(); pg.wait_for_timeout(800)
    a = pg.locator(".fv-overlay-primary a", has_text="Free Ebook"); R["overlay"] = {"count": a.count(), "visible": a.first.is_visible() if a.count() else None, "href": a.first.get_attribute("href") if a.count() else None}
    pg.screenshot(path=f"{OUT}-overlay-390.png")
    if a.count(): a.first.click(); pg.wait_for_load_state("load"); pg.wait_for_timeout(800); R["overlay"]["landed"] = pg.url; R["overlay"]["h1"] = pg.locator("h1").first.inner_text()[:70] if pg.locator("h1").count() else None
    ctx.close()
    # keyboard: tab to the desktop pill, check focus ring + click through; axe on header
    ctx = b.new_context(viewport={"width": 1440, "height": 900}); pg = ctx.new_page(); pg.goto(f"https://finalvestige.com/?fvcb={ts}", wait_until="load", timeout=90000); pg.wait_for_timeout(1200)
    got = None
    for i in range(30):
        pg.keyboard.press("Tab"); pg.wait_for_timeout(80)
        t = pg.evaluate("(() => { const e = document.activeElement; return e && e.closest('.fv-nav-free-ebook') ? {tag: e.tagName, text: e.textContent.trim(), outline: getComputedStyle(e).outlineStyle + ' ' + getComputedStyle(e).outlineWidth, bg: getComputedStyle(e).backgroundColor} : null })()")
        if t: got = {"tabs": i + 1, **t}; break
    R["kbd_pill"] = got
    pg.add_script_tag(path=AXE); ax = pg.evaluate("axe.run('.fv-site-header', {runOnly: ['wcag2a','wcag2aa','wcag22aa']}).then(r => ({violations: r.violations.map(v => [v.id, v.impact, v.nodes.length, v.nodes[0].target.join(' ').slice(0,80)]), passes: r.passes.length}))")
    R["axe_header_1440"] = ax; ctx.close()
    b.close()
for k, v in R.items(): print(k, json.dumps(v, ensure_ascii=False))
