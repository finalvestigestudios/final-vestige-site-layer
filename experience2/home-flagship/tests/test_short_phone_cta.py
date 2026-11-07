#!/usr/bin/env python3
"""Exact-source Chromium QA: a small phone must expose the main evidence action.

Non-production only. Does not fetch media, access WordPress, submit forms, or
measure Lighthouse / field CWV. Fails closed if Playwright/Chromium is absent.
Run: python experience2/home-flagship/tests/test_short_phone_cta.py
"""
from pathlib import Path
import os
import re

ROOT = Path(__file__).resolve().parents[1]
CSS = ("flagship.css", "chronicle.css", "chronicle-lens.css", "inquiry.css",
       "observer-lab.css", "reading-trail.css")
JS = ("flagship.js", "observer-lab.js", "chronicle-lens.js", "reading-trail.js")
MARKER = "EX2 conversion-first 320px short-screen composition"
SELECTOR = ".fv-hf__opening-actions a.fv-hf__button--gold"


def build_source():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    for name in CSS:
        tag = '<link rel="stylesheet" href="./' + name + '">'
        assert html.count(tag) == 1, name
        html = html.replace(tag, "<style>" + (ROOT/name).read_text(encoding="utf-8") + "</style>")
    for name in JS:
        tag = '<script src="./' + name + '" defer></script>'
        assert html.count(tag) == 1, name
        html = html.replace(tag, "<script>" + (ROOT/name).read_text(encoding="utf-8") + "</script>")
    assert html.count(MARKER) == 1, "missing or duplicate short-screen CSS"
    return html


def inspect(page):
    return page.evaluate("""selector => {
      const a=document.querySelector(selector);
      if(!a) throw Error('evidence CTA missing');
      const r=a.getBoundingClientRect(), x=r.left+r.width/2, y=r.top+r.height/2;
      return {
        top:r.top,bottom:r.bottom,height:r.height,href:a.getAttribute('href'),
        fullyVisible:r.top>=0 && r.bottom<=innerHeight,
        hit:y<innerHeight && (document.elementFromPoint(x,y)===a ||
             a.contains(document.elementFromPoint(x,y))),
        overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth,
        headlines:document.querySelectorAll('h1').length,
        chapters:document.querySelectorAll('.fv-hf__chapter-nav a').length,
        focusLinks:document.querySelectorAll('a[href="https://finalvestige.com/focus/"]').length,
        editorial:document.body.innerText.includes('EDITORIAL TYPESETTING')
      };
    }""", SELECTOR)


def run():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError("Playwright unavailable: QA FAIL-CLOSED") from exc
    html=build_source()
    shots=os.environ.get("FV_EVIDENCE_OUT")
    if shots:
        Path(shots).mkdir(parents=True, exist_ok=True)
    cases=((320,568),(360,640),(390,844),(768,1024),(1440,900),(1920,1080))
    with sync_playwright() as p:
        import shutil
        executable=shutil.which("chromium") or shutil.which("google-chrome")
        browser=p.chromium.launch(**({"executable_path":executable} if executable else {}),
                                  args=["--no-sandbox","--disable-dev-shm-usage"])
        count=0
        for js in (False, True):
            for w,h in cases:
                context=browser.new_context(viewport={"width":w,"height":h},
                                            java_script_enabled=js,reduced_motion="reduce")
                page=context.new_page()
                errors=[]
                page.on("pageerror",lambda e:errors.append(str(e)))
                page.set_content(html,wait_until="domcontentloaded")
                data=inspect(page)
                assert not errors, (w,h,js,errors)
                assert not data["overflow"], (w,h,js,"horizontal overflow")
                assert data["headlines"]==1 and data["chapters"]==7, data
                assert data["focusLinks"]>=2 and data["editorial"], data
                assert data["href"]=="#fv-hf-evidence" and data["height"]>=44, data
                if w<=360:
                    assert data["fullyVisible"] and data["hit"], (w,h,js,data)
                if shots and (w,h) in ((320,568),(390,844),(1440,900)):
                    page.screenshot(path=str(Path(shots) / f"{w}_{h}_js{int(js)}.png"))
                count+=1
                context.close()
        context=browser.new_context(viewport={"width":640,"height":900},
                                    java_script_enabled=False,reduced_motion="reduce")
        page=context.new_page()
        page.set_content(html,wait_until="domcontentloaded")
        assert not inspect(page)["overflow"], "640 CSS px (1280 physical at 200% proxy) overflow"
        context.close()
        browser.close()
    print(f"PASS {count} exact-source Chromium configurations + 640 CSS px zoom proxy; not WordPress staging")


if __name__=="__main__":
    run()
