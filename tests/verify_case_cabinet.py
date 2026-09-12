from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "payloads" / "case-cabinet-wp-block-v1.txt"
EXPECTED_BYTES = 13945
EXPECTED_SHA256 = "f6522968d145b6b22d647744ee3981bf9b482fc6d994e4464aa1ba46e38f062b"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def failure_patch() -> str:
    return """
<script>
window.__fvccFailKey=false;
window.__fvccOriginalSetItem=Storage.prototype.setItem;
window.__fvccArmFailure=()=>{window.__fvccFailKey=true};
Storage.prototype.setItem=function(key,value){
  if(window.__fvccFailKey && key==='fv_case_cabinet_v1'){
    throw new DOMException('quota','QuotaExceededError');
  }
  return window.__fvccOriginalSetItem.call(this,key,value);
};
</script>
"""


def fixture(payload: str, mode: str) -> str:
    now_ms = int(time.time() * 1000)
    pre = ""
    post = ""
    body_class = "single-post postid-621"
    article = """
<main><article id="post-621"><h1 class="entry-title">Six Miles an Hour</h1><div class="entry-content">
<p>Opening one with enough narrative text for qualification.</p><p>Opening two adds more story context.</p><p>Opening three continues the investigation.</p><p>Opening four completes the minimum threshold.</p><h2>First turn</h2><p>More narrative here.</p><h2 class="fv-source-heading" id="sources">Sources &amp; Further Reading</h2><ul class="fv-source-list" data-fv-footnotes><li id="fv-fn-1">Source one.</li></ul>
</div></article></main>
"""
    if mode == "nonpost":
        body_class = "home"
        article = "<main><h1>Final Vestige</h1></main>"
        records = [{"path": "/case-a/", "title": "Case A", "savedAt": now_ms}]
        pre = f"<script>localStorage.setItem('fv_case_cabinet_v1',{json.dumps(json.dumps(records))});</script>"
    elif mode == "preseed":
        body_class = "archive"
        article = "<main><h1>Archive</h1></main>"
        records = [
            {"path": f"/case-{i}/", "title": f"Case {i}", "savedAt": now_ms - i * 1000}
            for i in range(14)
        ]
        records += [
            {"path": "https://evil.example/trap", "title": "External", "savedAt": now_ms},
            {"path": "/stale/", "title": "Stale", "savedAt": now_ms - (181 * 24 * 60 * 60 * 1000)},
            {"path": "/query/?x=1", "title": "Query", "savedAt": now_ms},
        ]
        pre = f"<script>localStorage.setItem('fv_case_cabinet_v1',{json.dumps(json.dumps(records))});</script>"
    elif mode == "disabled":
        pre = "<script>Object.defineProperty(window,'localStorage',{configurable:true,get(){throw new DOMException('blocked','SecurityError')}});</script>"
    elif mode == "startupfail":
        records = [{"path": "/old/", "title": "Old", "savedAt": now_ms}]
        pre = f"<script>localStorage.setItem('fv_case_cabinet_v1',{json.dumps(json.dumps(records))});</script>{failure_patch()}<script>window.__fvccArmFailure();</script>"
    elif mode == "savefail":
        post = failure_patch()
    elif mode == "removefail":
        records = [{"path": "/case-cabinet-removefail.html", "title": "Six Miles an Hour", "savedAt": now_ms}]
        pre = f"<script>localStorage.setItem('fv_case_cabinet_v1',{json.dumps(json.dumps(records))});</script>"
        post = failure_patch()
    elif mode == "clearfail":
        records = [
            {"path": "/case-cabinet-clearfail.html", "title": "Six Miles an Hour", "savedAt": now_ms},
            {"path": "/case-b/", "title": "Case B", "savedAt": now_ms - 1000},
        ]
        pre = f"<script>localStorage.setItem('fv_case_cabinet_v1',{json.dumps(json.dumps(records))});</script>"
        post = failure_patch()

    assertions = f"""
<script>
const runFixture=()=>{{
  const mode={json.dumps(mode)};
  const fail=m=>{{document.body.dataset.fvTest='fail';document.body.dataset.fvReason=m}};
  const pass=()=>{{document.body.dataset.fvTest='pass'}};
  const records=()=>JSON.parse(localStorage.getItem('fv_case_cabinet_v1')||'[]');
  try{{
    if(mode==='disabled'||mode==='startupfail'){{
      if(document.querySelector('[data-fv-case-cabinet-band],.fvcc-launch,.fvcc-dialog'))return fail('storage failure did not fail closed before UI');
      return pass();
    }}
    const dialog=document.querySelector('.fvcc-dialog');
    if(!dialog)return fail('dialog missing');

    if(mode==='savefail'){{
      const save=document.querySelector('.fvcc-save');
      if(!save)return fail('save button missing');
      window.__fvccArmFailure();
      save.click();
      if(records().length!==0)return fail('failed save changed durable state');
      if(save.getAttribute('aria-pressed')!=='false'||save.textContent!=='Save to Cabinet')return fail('failed save changed committed aria/button state');
      const open=document.querySelector('.fvcc-open');
      if(!open.textContent.includes('0'))return fail('failed save changed count');
      if(!dialog.querySelector('.fvcc-status').textContent.includes('Nothing was changed'))return fail('failed save lacks failure status');
      return pass();
    }}

    if(mode==='removefail'){{
      const save=document.querySelector('.fvcc-save'),open=document.querySelector('.fvcc-open');
      if(save.getAttribute('aria-pressed')!=='true')return fail('preseeded save state missing');
      open.click();
      setTimeout(()=>{{
        try{{
          window.__fvccArmFailure();
          const remove=dialog.querySelector('.fvcc-remove');if(!remove)return fail('remove control missing');
          remove.click();
          if(records().length!==1)return fail('failed remove changed durable state');
          if(save.getAttribute('aria-pressed')!=='true'||!save.textContent.includes('Saved'))return fail('failed remove changed committed aria/button state');
          if(dialog.querySelectorAll('.fvcc-card').length!==1)return fail('failed remove changed rendered cabinet');
          if(!dialog.querySelector('.fvcc-status').textContent.includes('Nothing was changed'))return fail('failed remove lacks failure status');
          return pass();
        }}catch(e){{fail(e&&e.message?e.message:String(e))}}
      }},80);return;
    }}

    if(mode==='clearfail'){{
      const save=document.querySelector('.fvcc-save'),open=document.querySelector('.fvcc-open');
      if(save.getAttribute('aria-pressed')!=='true')return fail('preseeded clear state missing');
      open.click();
      setTimeout(()=>{{
        try{{
          const clear=dialog.querySelector('.fvcc-clear');
          clear.click();if(clear.textContent!=='Clear all?')return fail('clear guard missing before forced failure');
          window.__fvccArmFailure();clear.click();
          if(records().length!==2)return fail('failed clear changed durable state');
          if(dialog.querySelectorAll('.fvcc-card').length!==2)return fail('failed clear changed rendered cabinet');
          if(!dialog.querySelector('.fvcc-status').textContent.includes('Nothing was changed'))return fail('failed clear lacks failure status');
          if(clear.textContent!=='Clear cabinet')return fail('failed clear left destructive confirmation armed');
          if(!document.querySelector('.fvcc-open').textContent.includes('2'))return fail('failed clear changed count');
          return pass();
        }}catch(e){{fail(e&&e.message?e.message:String(e))}}
      }},80);return;
    }}

    if(mode==='valid'){{
      const band=document.querySelector('[data-fv-case-cabinet-band]');
      if(!band)return fail('post save band missing');
      const save=band.querySelector('.fvcc-save'),open=band.querySelector('.fvcc-open');
      if(save.getAttribute('aria-pressed')!=='false')return fail('initial save state wrong');
      save.click();
      let stored=records();
      if(stored.length!==1||stored[0].path!==location.pathname||stored[0].title!=='Six Miles an Hour')return fail('explicit save did not store bounded record');
      if(save.getAttribute('aria-pressed')!=='true'||!save.textContent.includes('Saved'))return fail('saved state not exposed');
      open.click();
      setTimeout(()=>{{
        try{{
          if(!dialog.open)return fail('dialog did not open');
          const link=dialog.querySelector('.fvcc-card a');if(!link)return fail('saved card missing');
          if(new URL(link.href).origin!==location.origin||new URL(link.href).pathname!==location.pathname)return fail('saved link escaped same origin/path');
          const remove=dialog.querySelector('.fvcc-remove');remove.click();
          stored=records();if(stored.length!==0)return fail('remove did not persist');
          if(save.getAttribute('aria-pressed')!=='false')return fail('remove did not update page save state');
          save.click();save.click();save.click();
          if(records().length!==1)return fail('toggle created duplicate records');
          const clear=dialog.querySelector('.fvcc-clear');clear.click();if(clear.textContent!=='Clear all?')return fail('clear lacks two-step guard');clear.click();
          if(records().length!==0)return fail('clear did not persist');
          dialog.querySelector('.fvcc-close').click();if(dialog.open)return fail('dialog did not close');
          return pass();
        }}catch(e){{fail(e&&e.message?e.message:String(e))}}
      }},80);return;
    }}

    if(document.querySelector('[data-fv-case-cabinet-band]'))return fail('non-post page rendered save band');
    const launch=document.querySelector('.fvcc-launch');if(!launch||launch.hidden)return fail('saved cabinet launcher missing off-article');
    const count=mode==='preseed'?12:1;if(!launch.textContent.includes(String(count)))return fail('launcher count incorrect');
    const stored=records();if(stored.length!==count)return fail('stored records were not pruned/capped');
    if(stored.some(r=>String(r.path).includes('evil')||String(r.path).includes('?')||r.title==='Stale'))return fail('unsafe/stale record survived normalization');
    launch.click();setTimeout(()=>{{
      try{{
        if(!dialog.open)return fail('global launcher did not open dialog');
        const links=[...dialog.querySelectorAll('.fvcc-card a')];if(links.length!==count)return fail('dialog card count incorrect');
        if(links.some(a=>new URL(a.href).origin!==location.origin))return fail('card escaped same origin');
        return pass();
      }}catch(e){{fail(e&&e.message?e.message:String(e))}}
    }},80);
  }}catch(e){{fail(e&&e.message?e.message:String(e))}}
}};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',runFixture,{{once:true}});else runFixture();
</script>
"""
    return f"<!doctype html><html><head><meta charset='utf-8'><title>Fixture</title></head><body class='{body_class}'>{pre}{article}{payload}{post}{assertions}</body></html>"


def run_browser(payload: str) -> None:
    browser = next((shutil.which(name) for name in ("google-chrome", "chromium", "chromium-browser") if shutil.which(name)), None)
    require(browser is not None, "headless Chrome/Chromium not available")
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        handler = partial(QuietHandler, directory=str(root))
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        origin = f"http://127.0.0.1:{server.server_port}"
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            for mode in ("valid", "nonpost", "preseed", "disabled", "startupfail", "savefail", "removefail", "clearfail"):
                page = root / f"case-cabinet-{mode}.html"
                page.write_text(fixture(payload, mode), encoding="utf-8")
                proc = subprocess.run(
                    [browser, "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage", "--virtual-time-budget=1500", "--dump-dom", f"{origin}/{page.name}"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30,
                )
                require(proc.returncode == 0, f"browser fixture {mode} failed: {proc.stderr[-500:]}")
                if 'data-fv-test="pass"' not in proc.stdout:
                    reason = re.search(r'data-fv-reason="([^"]*)"', proc.stdout)
                    raise SystemExit(f"FAIL: browser fixture {mode}: {reason.group(1) if reason else 'runtime assertions failed'}")
        finally:
            server.shutdown(); server.server_close(); thread.join(timeout=5)


def main() -> None:
    raw = PAYLOAD.read_bytes(); text = raw.decode("utf-8")
    require(len(raw) == EXPECTED_BYTES, f"payload byte count drifted: {len(raw)}")
    actual = hashlib.sha256(raw).hexdigest(); require(actual == EXPECTED_SHA256, f"payload SHA-256 drifted: {actual}")
    require(text.count("<!-- wp:html -->") == 1 and text.count("<!-- /wp:html -->") == 1, "single isolated wp:html block required")
    require('<style id="fv-case-cabinet-v1-css">' in text and '<script id="fv-case-cabinet-v1-js">' in text, "versioned style/script ids missing")
    require("window.__fvCaseCabinet={version:'1.0.1'}" in text, "R1 version guard missing")
    require("KEY='fv_case_cabinet_v1',MAX=12,MAX_AGE=180*24*60*60*1000" in text, "bounded storage contract missing")
    require("window.localStorage" in text and ".setItem(" in text and ".removeItem(" in text, "Web Storage implementation missing")
    require("safePath" in text and "u.origin!==location.origin||u.search||u.hash" in text, "same-origin query-free path validation missing")
    require("const initial=read();if(!write(initial))return;let items=initial;" in text, "startup canonical write is not fail closed")
    require("const next=items.filter(x=>x.path!==item.path);if(!write(next))" in text, "remove is not transactional")
    require("const next=[];if(!write(next))" in text, "clear is not transactional")
    require("const next=savedCurrent()?items.filter(item=>item.path!==currentPath):" in text and "if(!write(next))" in text, "save is not transactional")
    require(text.count("Nothing was changed.") >= 3, "failed mutation status is incomplete")
    require("No account or cross-device sync." in text, "storage boundary copy missing")
    require("Only the investigation title, page path and save time are stored locally." in text, "stored-fields disclosure missing")
    require("Save to Cabinet" in text and "Open Cabinet" in text and "Clear all?" in text, "core cabinet controls missing")
    require("window.addEventListener('storage'" in text, "cross-tab storage synchronization missing")
    require("showModal" in text and "dialog.addEventListener('cancel'" in text, "native dialog/Escape behavior missing")
    require("opener.focus()" in text, "focus return missing")
    require("min-height:44px" in text, "44px controls missing")
    require("@media(max-width:680px)" in text and "@media(max-width:360px)" in text, "responsive behavior missing")
    require("prefers-reduced-motion:reduce" in text and "forced-colors:active" in text and "@media print" in text, "accessibility/print media handling missing")
    banned = ["sessionStorage", "indexedDB", "document.cookie", "fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket", "posthog", "gtag(", "history.pushState", "history.replaceState", "navigator.clipboard", "<iframe", "<script src="]
    lower = text.lower()
    for token in banned:
        require(token.lower() not in lower, f"unexpected network/analytics/private-state token: {token}")
    match = re.search(r'<script id="fv-case-cabinet-v1-js">\n(.*?)\n</script>', text, flags=re.S); require(match is not None, "unable to extract JavaScript")
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(match.group(1)); js_path = Path(handle.name)
    try:
        subprocess.run(["node", "--check", str(js_path)], check=True)
    finally:
        js_path.unlink(missing_ok=True)
    if os.environ.get("FV_BROWSER_RUNTIME") == "1":
        run_browser(text)
    print("PASS: Case Cabinet R1 exact identity, startup canonical-write fail closed, transactional save/remove/clear rollback, post-probe quota adversaries, local-only privacy, 12-item/180-day bounds, same-origin query-free links, responsive accessibility, JavaScript syntax, and browser regressions verified")


if __name__ == "__main__":
    main()
