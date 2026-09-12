from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import tempfile
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "payloads" / "evidence-desk-wp-block-r2.txt"
EXPECTED_BYTES = 16373
EXPECTED_SHA256 = "739d5776c86db4ee706f6a73b04ff4c6770492a9d1524405a0492deb35930079"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def fixture(payload: str, mode: str, origin: str) -> str:
    para = (
        "A documented paragraph in a long investigation keeps the reader inside the published narrative while "
        "preserving enough text to satisfy the longform qualification threshold. " * 2
    )
    story = "".join(f"<p>{para}{i}</p>" for i in range(12))
    figures = "".join(
        f'<figure class="wp-block-image"><img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw==" '
        f'alt="Figure {i} alt"><figcaption>Published figure {i} caption.</figcaption></figure>'
        for i in range(1, 3)
    )
    note_rows = []
    for i in range(1, 5):
        attrs = ' class="publisher-owned marker-x" tabindex="-7"' if i == 2 else ""
        backlink = f'<span class="fv-fn-backlinks"><a href="#fv-fnref-{i}-1">↩</a></span>'
        relative_internal = f'<a href="/internal-source-{i}">Internal relative</a>'
        absolute_internal = f'<a href="{origin}/internal-source-{i}">Internal absolute</a>'
        aliases = (
            f'<a href="https://www.finalvestige.com/source-{i}">FV alias</a>'
            f'<a href="https://labs.finalvestige.com/source-{i}">FV subdomain</a>'
        )
        external = f'<a href="https://example.org/source-{i}">External published source</a>'
        links = backlink + relative_internal + absolute_internal + aliases
        if not (mode == "internalonly" and i == 1):
            links += external
        note_rows.append(f'<li id="fv-fn-{i}"{attrs}>Published source note {i} with context {links}</li>')
    notes = '<ul class="wp-block-list fv-source-list" data-fv-footnotes>' + "".join(note_rows) + "</ul>"
    heading = '<h2 class="wp-block-heading fv-source-heading" id="sources">Sources &amp; Further Reading</h2>'
    if mode in ("valid", "internalonly"):
        boundary = heading + notes
    elif mode == "missing":
        boundary = notes
    elif mode == "reversed":
        boundary = notes + heading
    else:
        raise ValueError(mode)

    assertions = r'''
<script>
const runEvidenceDeskFixture=()=>{
  const fail=m=>{document.body.dataset.fvTest='fail';document.body.dataset.fvReason=m};
  try{
    const launch=document.querySelector('[data-fv-evidence-desk-launcher]');
    if(MODE==='missing'||MODE==='reversed'){
      if(launch)return fail('fail-closed qualification did not hold');
      document.body.dataset.fvTest='pass';return;
    }
    if(!launch)return fail('launcher missing');
    const open=launch.querySelector('.fved-open');open.click();
    const desk=document.querySelector('[data-fv-evidence-desk]');
    if(!desk||desk.hidden)return fail('desk did not open');
    if(open.getAttribute('aria-expanded')!=='true')return fail('launcher expanded state missing');
    let buttons=[...document.querySelectorAll('.fved-pin')];
    if(buttons.length!==6)return fail('expected six pin controls');
    const initialImages=document.querySelectorAll('figure.wp-block-image img').length;
    buttons.slice(0,4).forEach(b=>b.click());
    if(desk.querySelectorAll('.fved-card').length!==4)return fail('four-card working set failed');
    buttons=[...document.querySelectorAll('.fved-pin')];
    if(!buttons[4].disabled||!buttons[5].disabled)return fail('four-item cap not enforced');

    const sourceOne=desk.querySelector('.fved-card[data-key="source-1"]');
    if(!sourceOne)return fail('source-one card missing');
    const sourceOneLinks=[...sourceOne.querySelectorAll('a[href]')];
    if(MODE==='valid'){
      if(sourceOneLinks.length!==1||sourceOneLinks[0].href!=='https://example.org/source-1')return fail('controlled host family was not rejected before genuine external source');
    }else if(MODE==='internalonly'){
      if(sourceOneLinks.length!==0)return fail('alias/subdomain-only note exposed Open source');
      if(!desk.querySelector('.fved-card[data-key="source-2"] a[href="https://example.org/source-2"]'))return fail('later genuine external source lost');
    }
    if(desk.querySelector('a[href*="finalvestige.com"]'))return fail('controlled Final Vestige host leaked into Open source');
    if(desk.querySelector('.fved-card a[href*="/internal-source-"]'))return fail('same-origin/internal link leaked');

    if(MODE==='valid'){
      const t1=document.getElementById('fv-fn-1');
      const t2=document.getElementById('fv-fn-2');
      const v1=sourceOne.querySelector('[data-action="view"]');
      if(t1.hasAttribute('class')||t1.hasAttribute('tabindex'))return fail('fixture source1 should begin attribute-free');
      v1.click();window.__fvFlushTimers(0);
      if(document.activeElement!==t1)return fail('successful jump did not focus source1');
      if(!t1.classList.contains('fved-arrived')||t1.getAttribute('tabindex')!=='-1')return fail('temporary jump state missing');
      window.__fvFlushTimers(1200);
      if(t1.hasAttribute('class')||t1.hasAttribute('tabindex'))return fail('absent publisher attributes were not restored to absent');

      const v2=desk.querySelector('.fved-card[data-key="source-2"] [data-action="view"]');
      v2.click();window.__fvFlushTimers(0);window.__fvFlushTimers(1200);
      if(t2.getAttribute('class')!=='publisher-owned marker-x'||t2.getAttribute('tabindex')!=='-7')return fail('pre-owned class/tabindex were not restored exactly');

      v1.click();window.__fvFlushTimers(0);v1.click();window.__fvFlushTimers(0);window.__fvFlushTimers(1200);
      if(t1.hasAttribute('class')||t1.hasAttribute('tabindex'))return fail('repeat jump drifted absent publisher state');

      const realScroll=t1.scrollIntoView.bind(t1);
      t1.scrollIntoView=()=>{throw new Error('forced scroll failure')};
      v1.focus();v1.click();
      if(t1.hasAttribute('class')||t1.hasAttribute('tabindex'))return fail('scroll failure mutated publisher state');
      if(document.activeElement!==v1)return fail('scroll failure did not recover feature-owned focus');
      t1.scrollIntoView=realScroll;

      const realFocus=t1.focus.bind(t1);
      t1.focus=()=>{throw new Error('forced focus failure')};
      v1.click();window.__fvFlushTimers(0);
      if(t1.hasAttribute('class')||t1.hasAttribute('tabindex'))return fail('focus failure did not restore publisher state');
      if(document.activeElement!==v1)return fail('focus failure did not recover feature-owned focus');
      t1.focus=realFocus;

      v1.click();window.__fvFlushTimers(0);desk.querySelector('.fved-close').click();
      if(t1.hasAttribute('class')||t1.hasAttribute('tabindex'))return fail('close during active jump did not restore publisher state');
      if(document.activeElement!==open)return fail('close did not restore launcher focus');
      open.click();if(desk.hidden)return fail('repeat open failed');
    }

    const firstRemove=desk.querySelector('.fved-card [data-action="remove"]');firstRemove.click();
    buttons=[...document.querySelectorAll('.fved-pin')];
    if(buttons[4].disabled)return fail('capacity did not reopen');
    buttons[4].click();
    if(desk.querySelectorAll('.fved-card').length!==4)return fail('replacement pin failed');
    if(document.querySelectorAll('figure.wp-block-image img').length!==initialImages)return fail('figure images were duplicated');
    const externalLinks=[...desk.querySelectorAll('.fved-card a[href^="https://example.org/"]')];
    if(!externalLinks.length||externalLinks.some(a=>a.rel!=='noopener'))return fail('external link safety contract failed');
    desk.querySelector('.fved-clear').click();
    if(desk.querySelectorAll('.fved-card').length!==0)return fail('clear failed');
    if(!desk.querySelector('.fved-status strong').textContent.startsWith('0 of 4'))return fail('status did not reset');
    const spacer=document.querySelector('[data-fv-evidence-desk-spacer]');
    if(!spacer||!desk.dataset.layout)return fail('adaptive layout/spacer contract missing');
    desk.querySelector('.fved-close').click();
    if(!desk.hidden||document.querySelectorAll('.fved-pin').length!==0)return fail('close cleanup failed');
    open.click();const p=[...document.querySelectorAll('.fved-pin')][0];p.focus();
    document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));
    if(!desk.hidden||document.activeElement!==open)return fail('Escape/focus-return failed');
    document.body.dataset.fvTest='pass';
  }catch(e){fail(e&&e.message?e.message:String(e))}
};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',runEvidenceDeskFixture,{once:true});else runEvidenceDeskFixture();
</script>
'''.replace("MODE", repr(mode))

    timer_harness = r'''<script>
let __fvTimerId=0;const __fvTimers=new Map();
window.setTimeout=(fn,ms)=>{const id=++__fvTimerId;__fvTimers.set(id,{fn,ms});return id};
window.clearTimeout=id=>__fvTimers.delete(id);
window.__fvFlushTimers=max=>{let progressed=true;while(progressed){progressed=false;for(const [id,t] of [...__fvTimers]){if(t.ms<=max){__fvTimers.delete(id);t.fn();progressed=true}}}};
window.requestAnimationFrame=fn=>{fn();return 1};window.cancelAnimationFrame=()=>{};
window.matchMedia=q=>({matches:q.includes('prefers-reduced-motion'),addListener(){},removeListener(){},addEventListener(){},removeEventListener(){}});
try{delete window.ResizeObserver}catch(e){window.ResizeObserver=undefined}
</script>'''
    return (
        '<!doctype html><html><head><meta charset="utf-8"><style>body{margin:0}main{max-width:760px;margin:auto}</style></head>'
        f'<body class="single-post">{timer_harness}<main><article><div class="entry-content">{story}'
        f'<h2 class="wp-block-heading">First turn</h2>{figures}{boundary}</div></article></main>{payload}{assertions}</body></html>'
    )


def run_browser(payload: str) -> None:
    browser = next((shutil.which(name) for name in ("google-chrome", "chromium", "chromium-browser") if shutil.which(name)), None)
    require(browser is not None, "headless Chrome/Chromium not available")
    with tempfile.TemporaryDirectory() as temp:
        temp_path = Path(temp)
        server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(temp_path)))
        origin = f"http://127.0.0.1:{server.server_port}"
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            for mode in ("valid", "internalonly", "missing", "reversed"):
                page = temp_path / f"evidence-desk-{mode}.html"
                page.write_text(fixture(payload, mode, origin), encoding="utf-8")
                proc = subprocess.run(
                    [browser, "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage", "--dump-dom", f"{origin}/{page.name}"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30,
                )
                require(proc.returncode == 0, f"browser fixture {mode} failed to execute: {proc.stderr[-500:]}")
                if 'data-fv-test="pass"' not in proc.stdout:
                    match = re.search(r'data-fv-reason="([^"]*)"', proc.stdout)
                    require(False, f"browser fixture {mode} failed: {match.group(1) if match else 'no reason'}")
        finally:
            server.shutdown();server.server_close();thread.join(timeout=5)


def main() -> None:
    raw = PAYLOAD.read_bytes()
    text = raw.decode("utf-8")
    require(len(raw) == EXPECTED_BYTES, f"payload byte count drifted: {len(raw)}")
    require(hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256, "payload SHA-256 drifted")
    checks = [
        ("window.__fvEvidenceDesk={version:'1.0.2'}", "R2 version guard missing"),
        ("controlledSiteHost", "controlled host helper missing"),
        ("h==='finalvestige.com'||h.endsWith('.finalvestige.com')", "Final Vestige host-family rule missing"),
        ("url.origin===location.origin||url.hostname===location.hostname||controlledSiteHost(url.hostname)", "combined same-origin/host-family rejection missing"),
        ("getAttribute('href')", "raw href inspection missing"),
        ("!a.closest('.fv-fn-backlinks')", "backlink exclusion missing"),
        ("clearActiveJump", "repeat-jump cleanup missing"),
        ("hadClass:target.hasAttribute('class')", "class state preservation missing"),
        ("hadTab:target.hasAttribute('tabindex')", "tabindex state preservation missing"),
        ("if(jump.hadClass)jump.target.setAttribute('class',jump.oldClass);else jump.target.removeAttribute('class')", "exact class restoration missing"),
        ("if(jump.hadTab)jump.target.setAttribute('tabindex',jump.oldTab);else jump.target.removeAttribute('tabindex')", "exact tabindex restoration missing"),
        ("try{target.scrollIntoView", "scroll-before-mutation transaction missing"),
        ("catch(_){restoreJump(jump);activeJump=null", "focus-failure restoration missing"),
        ("clearActiveJump();isOpen=false", "close cleanup missing"),
        ("min-height:44px", "44px target contract missing"),
        ("forced-colors:active", "forced-colors support missing"),
        ("prefers-reduced-motion:reduce", "reduced-motion support missing"),
        ("@media print", "print cleanup missing"),
    ]
    for needle, message in checks:
        require(needle in text, message)
    require(text.find("try{target.scrollIntoView") < text.find("target.classList.add('fved-story-target','fved-arrived')"), "scroll must occur before publisher DOM mutation")
    banned_literals = ["localStorage", "sessionStorage", "indexedDB", "document.cookie", "posthog", "gtag(", "sendBeacon", "WebSocket", "history.pushState", "history.replaceState", "navigator.clipboard"]
    for token in banned_literals:
        require(token.lower() not in text.lower(), f"unexpected persistence/network token: {token}")
    for pattern, label in {r"\bfetch\s*\(": "network fetch", r"XMLHttpRequest": "XHR", r"<script[^>]+src=": "external script dependency", r"<iframe\b": "embedded external frame"}.items():
        require(not re.search(pattern, text, flags=re.I), f"unexpected {label}")
    match = re.search(r'<script id="fv-evidence-desk-v1-js">\n(.*?)\n</script>', text, flags=re.S)
    require(match is not None, "unable to extract JavaScript")
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(match.group(1)); js_path = Path(handle.name)
    try:
        subprocess.run(["node", "--check", str(js_path)], check=True)
    finally:
        js_path.unlink(missing_ok=True)
    if os.environ.get("FV_BROWSER_RUNTIME") == "1":
        run_browser(text)
    print("PASS: Evidence Desk R2 host-family provenance, nondestructive DOM state, accessibility/privacy, and browser regressions verified")


if __name__ == "__main__":
    main()
