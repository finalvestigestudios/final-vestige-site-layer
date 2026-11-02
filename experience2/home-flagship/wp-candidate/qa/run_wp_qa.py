#!/usr/bin/env python3
"""Real-browser QA of the integrated candidate running in the isolated local WordPress.

  python run_wp_qa.py --url http://127.0.0.1:9400/ --axe <axe.min.js> --out <dir> [--chrome-channel chrome]

Everything here runs in real Chromium against the real WordPress+Assembler render (not an inlined
fixture). Results go to <out>/wp_qa_results.json; screenshots to <out>/shots/.
Outgoing POSTs to finalvestige.com / wordpress.com are aborted (the preserved Jetpack form).
"""
import argparse
import json
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

WIDTHS = [320, 360, 390, 768, 1024, 1440, 1920]
WCAG = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]


def summarize_axe(res):
    def pack(items):
        out = []
        for r in items:
            inside = sum(1 for n in r["nodes"] if any(".fv-hf" in t or "fv-hf" in str(t) for t in n.get("target", [])))
            out.append({"id": r["id"], "impact": r.get("impact"), "nodes": len(r["nodes"]),
                        "nodes_in_flagship": inside,
                        "targets": [n["target"][-1] if n["target"] else "" for n in r["nodes"][:4]],
                        "help": r["help"]})
        return out
    return {"violations": pack(res["violations"]), "incomplete": pack(res["incomplete"]),
            "passes": len(res["passes"])}


def page_state(pg):
    return pg.evaluate("""()=>({
      scrollW:document.documentElement.scrollWidth, innerW:window.innerWidth,
      margins:document.querySelectorAll('.fv-margin-strip__item').length,
      flagship:document.querySelectorAll('[data-fv-home-flagship]').length,
      mains:document.querySelectorAll('main').length,
      headers:document.querySelectorAll('header').length,
      footers:document.querySelectorAll('footer').length,
      h1:[...document.querySelectorAll('h1')].map(h=>h.textContent.trim().replace(/\\s+/g,' ')),
      devBanner:!!document.querySelector('.fv-hf__studio, [data-fv-direction]'),
      candidateText:/DESIGN CANDIDATE|NOT LIVE|Direction switcher/i.test(document.body.innerText),
      jetpackForm:document.querySelectorAll('form#subscribe-blog').length,
      focusLinks:[...document.querySelectorAll('a[href*="/focus/"]')].length,
      ids:(()=>{const s={},d=[];document.querySelectorAll('[id]').forEach(e=>{if(s[e.id])d.push(e.id);s[e.id]=1});return d})(),
    })""")


def small_targets(pg, limit=24):
    return pg.evaluate("""(lim)=>[...document.querySelectorAll('.fv-hf a[href], .fv-hf button, .fv-hf summary')].filter(e=>{
        const r=e.getBoundingClientRect(); const cs=getComputedStyle(e);
        if(cs.display==='none'||cs.visibility==='hidden'||r.width===0) return false;
        if(cs.display==='inline' && e.tagName==='A' && e.closest('p,li')) return false; /* WCAG 2.5.8 inline exception */
        return r.height<lim||r.width<lim}).map(e=>[e.tagName,(e.className||'').toString().slice(0,40),Math.round(e.getBoundingClientRect().width),Math.round(e.getBoundingClientRect().height)]).slice(0,20)""", limit)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:9400/")
    ap.add_argument("--axe", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--chrome-channel", default="chrome")
    a = ap.parse_args()
    (a.out / "shots").mkdir(parents=True, exist_ok=True)
    R = {"url": a.url, "widths": {}, "interactions": {}, "nojs": {}, "reduced_motion": {}, "zoom": {}, "touch": {}, "keyboard": {}}

    def blocker(route, request):
        if request.method == "POST" and "localhost" not in request.url and "127.0.0.1" not in request.url:
            return route.abort()
        return route.continue_()

    with sync_playwright() as p:
        b = p.chromium.launch(channel=a.chrome_channel)

        def newpage(w, h=900, **kw):
            ctx = b.new_context(viewport={"width": w, "height": h}, **kw)
            ctx.route("**/*", blocker)
            pg = ctx.new_page()
            errs = []
            pg.on("console", lambda m: errs.append(m.text[:200]) if m.type == "error" else None)
            pg.on("pageerror", lambda e: errs.append("pageerror:" + str(e)[:200]))
            pg.on("requestfailed", lambda r: errs.append("reqfailed[" + str(r.failure) + "]:" + r.url[:110]))
            return ctx, pg, errs

        # ---- A. seven widths: structure, overflow, console, axe, screenshots
        for w in WIDTHS:
            ctx, pg, errs = newpage(w)
            pg.goto(a.url, wait_until="load")
            pg.wait_for_timeout(1800)
            pg.screenshot(path=str(a.out / "shots" / f"first-arrival-{w}.png"))
            # content-visibility:auto sections are not laid out until near the viewport, so axe,
            # target-size and full-page captures would see them as empty. Force them rendered for
            # the audit only; interactions below run with the real (skipped) behaviour.
            pg.add_style_tag(content=".fv-home-shell,.fv-enter-record{content-visibility:visible!important}")
            pg.wait_for_timeout(300)
            st = page_state(pg)
            st["horizontal_overflow"] = st["scrollW"] > st["innerW"]
            st["small_targets_lt24"] = small_targets(pg, 24)
            st["small_targets_lt44"] = len(small_targets(pg, 44))
            h = pg.evaluate("document.documentElement.scrollHeight")
            for y in range(0, h, 700):
                pg.evaluate(f"window.scrollTo(0,{y})")
                pg.wait_for_timeout(40)
            pg.evaluate("window.scrollTo(0,0)")
            pg.wait_for_timeout(400)
            pg.screenshot(path=str(a.out / "shots" / f"full-{w}.png"), full_page=True)
            pg.add_script_tag(path=str(a.axe))
            ax = pg.evaluate("""async(tags)=>{const r=await axe.run(document,{runOnly:{type:'tag',values:tags}});
                return {violations:r.violations.map(v=>({id:v.id,impact:v.impact,help:v.help,nodes:v.nodes.map(n=>({target:n.target}))})),
                        incomplete:r.incomplete.map(v=>({id:v.id,impact:v.impact,help:v.help,nodes:v.nodes.map(n=>({target:n.target}))})),
                        passes:r.passes.map(v=>v.id)}}""", WCAG + ["best-practice"])
            st["axe"] = summarize_axe(ax)
            st["console_errors"] = errs[:8]
            R["widths"][str(w)] = st
            ctx.close()

        # ---- B. interactions at desktop and mobile (touch)
        for label, kw, w in [("desktop", {}, 1440), ("mobile_touch", {"has_touch": True, "is_mobile": True}, 390)]:
            ctx, pg, errs = newpage(w, 844 if w < 500 else 900, **kw)
            pg.goto(a.url, wait_until="load")
            pg.wait_for_timeout(1500)
            I = {}
            click = (lambda sel: pg.tap(sel)) if kw.get("has_touch") else (lambda sel: pg.click(sel))
            # Franklin document switching (chronicle lens)
            fr = {}
            for v in ["original", "addition", "both"]:
                sel = f'[data-fv-chronicle-view="{v}"]'
                pg.locator(sel).scroll_into_view_if_needed()
                click(sel)
                pg.wait_for_timeout(250)
                fr[v] = pg.evaluate("""(v)=>({pressed:[...document.querySelectorAll('[data-fv-chronicle-view]')].map(b=>b.getAttribute('aria-pressed')),
                   root:(document.querySelector('[data-fv-chronicle-lens],[data-fv-chronicle]')||{}).dataset||null})""", v)
            fr["pressed_follows_clicks"] = (fr["original"]["pressed"] == ["true", "false", "false"]
                                            and fr["addition"]["pressed"] == ["false", "true", "false"]
                                            and fr["both"]["pressed"] == ["false", "false", "true"])
            I["franklin_switch"] = fr
            # Historical investigation chooser
            ch = {}
            for c in ["franklin", "malbone", "apollo"]:
                sel = f'[data-fv-case-button="{c}"]'
                pg.locator(sel).scroll_into_view_if_needed()
                click(sel)
                pg.wait_for_timeout(250)
                ch[c] = pg.evaluate("""()=>({pressed:[...document.querySelectorAll('[data-fv-case-button]')].map(b=>b.getAttribute('aria-pressed')),
                   visiblePanels:[...document.querySelectorAll('[data-fv-case]')].filter(e=>e.getBoundingClientRect().height>0&&!e.hidden).map(e=>e.dataset.fvCase),
                   status:((document.querySelector('[data-fv-case-status]')||{}).textContent||'').trim().slice(0,80)})""")
                ch[c]["only_selected_visible"] = ch[c]["visiblePanels"] == [c]
            I["case_chooser"] = ch
            # Inquiry accordion + native details
            pg.locator(".fv-hf__inquiry-record summary").nth(1).scroll_into_view_if_needed()
            before = pg.evaluate("[...document.querySelectorAll('.fv-hf__inquiry-record')].map(d=>d.open)")
            click(".fv-hf__inquiry-record >> nth=1 >> summary")
            pg.wait_for_timeout(250)
            after = pg.evaluate("[...document.querySelectorAll('.fv-hf__inquiry-record')].map(d=>d.open)")
            I["inquiry_toggle"] = {"before": before, "after": after, "changed": before != after}
            # Observer Lab
            pg.locator('[data-fv-observer-switch="b"]').scroll_into_view_if_needed()
            click('[data-fv-observer-switch="b"]')
            pg.wait_for_timeout(300)
            pb = pg.evaluate("[...document.querySelectorAll('[data-fv-observer-switch]')].map(b=>b.getAttribute('aria-pressed'))")
            click('[data-fv-observer-switch="a"]')
            pg.wait_for_timeout(300)
            pa = pg.evaluate("[...document.querySelectorAll('[data-fv-observer-switch]')].map(b=>b.getAttribute('aria-pressed'))")
            click("#fv-hf-observer-answer summary")
            pg.wait_for_timeout(200)
            I["observer_lab"] = {"after_b": pb, "after_a": pa, "toggles": pb == ["false", "true"] and pa == ["true", "false"],
                                  "answer_open": pg.evaluate("document.getElementById('fv-hf-observer-answer').open")}
            # Chapter navigation: target reaches viewport, hash updates
            nav = []
            for i, href in enumerate(pg.evaluate("[...document.querySelectorAll('.fv-hf__chapter-nav a')].map(a=>a.getAttribute('href'))")):
                pg.evaluate("window.scrollTo(0,0)")
                pg.wait_for_timeout(150)
                click(f'.fv-hf__chapter-nav a[href="{href}"]')
                # smooth scrolling can take ~2 s for long jumps: wait until scrollY stops changing
                last, stable = -1, 0
                for _ in range(60):
                    pg.wait_for_timeout(100)
                    y = pg.evaluate("window.scrollY")
                    stable = stable + 1 if y == last else 0
                    last = y
                    if stable >= 4:
                        break
                nav.append(pg.evaluate("""(h)=>{const t=document.querySelector(h);const r=t?t.getBoundingClientRect():null;
                    return {href:h,found:!!t,top:r?Math.round(r.top):null,inView:r?(r.top<innerHeight&&r.bottom>0):false,hash:location.hash,
                            underStickyHeader:r?r.top<60:null}}""", href))
            I["chapter_nav"] = nav
            I["console_errors"] = errs[:6]
            R["interactions"][label] = I
            if label == "mobile_touch":
                R["touch"]["targets_lt24"] = small_targets(pg, 24)
                R["touch"]["targets_lt44_count"] = len(small_targets(pg, 44))
            ctx.close()

        # ---- B2. fragment navigation into content-visibility-skipped preserved sections (#dispatch is the
        # target of the site header's "Dispatch" link) must land with the target in view
        ctx, pg, errs = newpage(1440)
        pg.goto(a.url + "#dispatch", wait_until="load")
        last, stable = -1, 0
        for _ in range(60):
            pg.wait_for_timeout(100)
            y = pg.evaluate("window.scrollY"); stable = stable + 1 if y == last else 0; last = y
            if stable >= 4: break
        R["dispatch_anchor"] = pg.evaluate("""()=>{const t=document.getElementById('dispatch');const r=t?t.getBoundingClientRect():null;
            return {found:!!t,top:r?Math.round(r.top):null,height:r?Math.round(r.height):null,inView:!!r&&r.top<innerHeight&&r.bottom>0,formVisible:!!document.querySelector('#dispatch form#subscribe-blog')&&document.querySelector('#dispatch form#subscribe-blog').getBoundingClientRect().height>0}}""")
        ctx.close()

        # ---- C. keyboard: visible focus, skip link, tab order sample
        ctx, pg, errs = newpage(1440)
        pg.goto(a.url, wait_until="load")
        pg.wait_for_timeout(1200)
        stops = []
        for i in range(40):
            pg.keyboard.press("Tab")
            stops.append(pg.evaluate("""()=>{const e=document.activeElement;if(!e)return null;const cs=getComputedStyle(e);const r=e.getBoundingClientRect();
                return {tag:e.tagName,txt:(e.textContent||e.getAttribute('aria-label')||'').trim().slice(0,30),
                        outline:cs.outlineStyle+' '+cs.outlineWidth,shadow:cs.boxShadow!=='none',visible:r.width>0&&r.height>0&&r.bottom>0&&r.top<innerHeight,
                        inFlagship:!!e.closest('.fv-hf')}}"""))
        R["keyboard"]["first_40_stops"] = stops
        R["keyboard"]["stops_without_visible_indicator"] = [s for s in stops if s and s["visible"] and s["outline"].startswith("none") and not s["shadow"]]
        # chapter-nav keyboard activation moves focus into the target region
        pg.goto(a.url + "#fv-hf-method-title", wait_until="load")
        pg.wait_for_timeout(500)
        ctx.close()

        # ---- D. JavaScript disabled: evidence readable
        ctx, pg, errs = newpage(1440, java_script_enabled=False)
        pg.goto(a.url, wait_until="load")
        pg.wait_for_timeout(3500)
        R["nojs"] = pg.evaluate("""()=>{const t=document.body.innerText;const vis=s=>[...document.querySelectorAll(s)].filter(e=>e.getBoundingClientRect().height>0).length;
          return {margins:document.querySelectorAll('.fv-margin-strip__item').length,
                  caseButtonsHidden:[...document.querySelectorAll('[data-fv-case-button]')].filter(e=>e.getBoundingClientRect().height>0).length,
                  hasApollo:/hatch opened inward/i.test(t),hasFranklin:/All well/i.test(t)&&/Terror and Erebus/i.test(t),hasMalbone:/Malbone/i.test(t)&&/1903/.test(t),
                  hasObserver:/unreliable/i.test(t), sourceLinks:document.querySelectorAll('.fv-hf a[href^="http"]').length,
                  detailsCount:document.querySelectorAll('.fv-hf details').length, focus:document.querySelectorAll('a[href*="/focus/"]').length,
                  jetpackForm:document.querySelectorAll('form#subscribe-blog').length,
                  casePhotosLoaded:[...document.querySelectorAll('.fv-hf__case img')].filter(i=>i.complete&&i.naturalWidth>0).length}}""")
        pg.screenshot(path=str(a.out / "shots" / "nojs-full-1440.png"), full_page=True)
        ctx.close()

        # ---- E. reduced motion: no running animations/transitions from flagship
        ctx, pg, errs = newpage(1440, reduced_motion="reduce")
        pg.goto(a.url, wait_until="load")
        pg.wait_for_timeout(1500)
        R["reduced_motion"] = pg.evaluate("""()=>{const an=document.getAnimations().filter(a=>a.effect&&a.effect.target&&a.effect.target.closest&&a.effect.target.closest('.fv-hf'));
          return {mediaMatches:matchMedia('(prefers-reduced-motion: reduce)').matches,runningFlagshipAnimations:an.filter(a=>a.playState==='running').map(a=>a.animationName||a.transitionProperty||'?').slice(0,8),
                  scrollBehavior:getComputedStyle(document.documentElement).scrollBehavior}}""")
        ctx.close()

        # ---- F. zoom/reflow: 200% of 1280 = 640 CSS px; 400% of 1280 = 320 CSS px
        for name, w in [("200pct_640css", 640), ("400pct_320css", 320)]:
            ctx, pg, errs = newpage(w, 700)
            pg.goto(a.url, wait_until="load")
            pg.wait_for_timeout(1200)
            st = page_state(pg)
            R["zoom"][name] = {"scrollW": st["scrollW"], "innerW": st["innerW"], "overflow": st["scrollW"] > st["innerW"]}
            pg.screenshot(path=str(a.out / "shots" / f"zoom-{name}.png"))
            ctx.close()
        b.close()
    (a.out / "wp_qa_results.json").write_text(json.dumps(R, indent=2), encoding="utf-8")
    # compact console report
    for w, s in R["widths"].items():
        print(w, "overflow" if s["horizontal_overflow"] else "ok", "margins", s["margins"], "main", s["mains"],
              "axe viol", [(v["id"], v["nodes"]) for v in s["axe"]["violations"]], "incomplete", len(s["axe"]["incomplete"]))


if __name__ == "__main__":
    main()
