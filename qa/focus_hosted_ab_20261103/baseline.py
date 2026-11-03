#!/usr/bin/env python3
"""Anonymous real-host Focus DOM QA. GET only: no subscriber action, edits or login."""
import argparse
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

URL = "https://finalvestige.com/focus/"
CASES = ((390, True), (390, False), (1440, True))

class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.blocks = 0
        self.anchors = 0
        self.target = False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "wp-block-jetpack-subscriptions" in (a.get("class") or "").split():
            self.blocks += 1
        if tag == "a" and a.get("href") == "#subscribe-blog":
            self.anchors += 1
        if a.get("id") == "subscribe-blog":
            self.target = True

def safe_request(req):
    if req.method != "GET":
        return False
    u = urlparse(req.url)
    if u.hostname in ("finalvestige.com", "www.finalvestige.com"):
        return u.scheme == "https" and not any(
            x in u.query.lower() for x in ("subscribe=", "email="))
    return u.scheme == "https"

def grade(results):
    if len(results) != len(CASES) or set((r.get("width"), r.get("js")) for r in results) != set(CASES):
        return ["incomplete_matrix"]
    failures = []
    for r in results:
        key = f"{r['width']}/js-{r['js']}"
        if (r.get("status") != 200 or r.get("host") != "finalvestige.com"
                or r.get("path") != "/focus/"):
            failures.append(key + ":public_http")
        if r.get("blocks") != 1:
            failures.append(key + ":jetpack_block_count")
        if r.get("links", 0) < 1:
            failures.append(key + ":missing_cta")
        if not r.get("target"):
            failures.append(key + ":broken_cta_fragment")
        if r["js"] and r.get("script") != "PASS":
            failures.append(key + ":gift_inline_syntax")
        if r["js"] and r.get("pageerrors"):
            failures.append(key + ":actual_browser_syntax_error")
        if r.get("overflow") is True:
            failures.append(key + ":horizontal_overflow")
    return failures

def run(out):
    from playwright.sync_api import sync_playwright
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            for width, js in CASES:
                ctx = browser.new_context(viewport={"width": width, "height": 850},
                                          device_scale_factor=1,
                                          java_script_enabled=js, service_workers="block",
                                          reduced_motion="reduce")
                try:
                    ctx.route("**/*", lambda route:
                              route.continue_() if safe_request(route.request) else route.abort())
                    page = ctx.new_page()
                    errors = []
                    page.on("pageerror", lambda error: errors.append(str(error)[:160]))
                    resp = None
                    row = {"width": width, "js": js}
                    try:
                        resp = page.goto(URL, wait_until="domcontentloaded", timeout=30000)
                        page.wait_for_timeout(1000)
                        parser = Tags()
                        parser.feed(page.content())
                        final = urlparse(page.url)
                        row.update(status=resp.status if resp else None, host=final.hostname,
                                   path=final.path, blocks=parser.blocks, links=parser.anchors,
                                   target=parser.target, script="NOT_RUN", pageerrors=[],
                                   overflow=None)
                        if js:
                            row.update(page.evaluate("""() => {
                                let scripts=[...document.querySelectorAll('script:not([src])')];
                                let s=scripts.find(x=>x.textContent.includes('fvf-gift')
                                    && x.textContent.includes('URLSearchParams'));
                                let status='MISSING';
                                if(s){try{new Function(s.textContent);status='PASS'}
                                    catch(e){status='FAIL:'+e.name}}
                                return {script:status,
                                  overflow:document.documentElement.scrollWidth>innerWidth+1};
                            }"""))
                            row["pageerrors"] = [s for s in errors if
                                "SyntaxError" in s or "unexpected" in s.lower() or "fvf-" in s.lower()]
                        page.screenshot(path=str(out / f"focus-{width}-js-{int(js)}.png"),
                                        full_page=False, timeout=12000)
                    except Exception as e:
                        row.update(status=resp.status if resp else None, error=type(e).__name__,
                                   pageerrors=["observation_failed"], script="NOT_OBSERVED")
                    rows.append(row)
                finally:
                    ctx.close()
        finally:
            browser.close()
    fails = grade(rows)
    data = {"release": "HOLD", "kind": "actual_logged_out_public_chromium",
            "subscriber_submission_count": 0, "confirmation_email": "NOT_TESTED",
            "welcome_email": "NOT_TESTED", "hosted_pdf": "NOT_TESTED",
            "wordpress_writes": 0, "cases": rows, "failures": fails}
    (out / "focus-hosted-dom.json").write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"focus_hosted_dom": "PASS" if not fails else "HOLD",
                      "failures": fails, "production_release": "HOLD"}))
    return 1 if fails else 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(run(args.out))
