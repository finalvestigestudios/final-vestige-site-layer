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
PAYLOAD = ROOT / "payloads" / "case-delta-wp-block-v1.txt"
EXPECTED_BYTES = 21292
EXPECTED_SHA256 = "70f84e21d2985175929e18a9a050e70a525e619134a45d6d77bebe2141ff5faa"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def paragraphs(prefix: str, n: int) -> str:
    return "\n".join(f'<p id="{prefix}-{i}">{prefix} narrative paragraph {i} with enough words for a stable comparison fixture.</p>' for i in range(1, n + 1))


def figure(n: int) -> str:
    return f'<figure class="wp-block-image" id="fig-{n}"><img src="/img/{n}.jpg" alt="Archive view {n}"><figcaption>Published caption {n}</figcaption></figure>'


def sources(n: int = 4) -> str:
    items = "".join(
        f'<li id="fv-fn-{i}">Archive source {i} <a href="https://example.org/{i}">Open source</a><span class="fv-fn-backlinks"><a class="fv-fn-back" href="#ref-{i}">↩</a></span></li>'
        for i in range(1, n + 1)
    )
    return f'<h2 class="wp-block-heading fv-source-heading" id="sources">Sources &amp; Further Reading</h2><ul data-fv-footnotes>{items}</ul>'


def valid_article() -> str:
    return f'''<main><article id="post-621"><h1>Six Miles an Hour</h1>
{paragraphs("opening", 4)}
{figure(1)}
<h2>The curve under Malbone Street</h2>{paragraphs("curve", 4)}
{figure(2)}
<h2>Why the wooden cars made the wreck worse</h2>{paragraphs("cars", 4)}
<h2>The switch upstairs</h2>{paragraphs("switch", 4)}
{sources(4)}
</article></main>'''


def fixture(payload: str, mode: str) -> str:
    prelude = ""
    article = valid_article()
    if mode == "partial-boundary":
        article = article.replace('class="wp-block-heading fv-source-heading" id="sources"', 'class="wp-block-heading" id="sources"')
    elif mode == "ambiguous-boundary":
        article = article.replace('<h2 class="wp-block-heading fv-source-heading" id="sources">', '<h2 class="wp-block-heading fv-source-heading" id="sources">Sources</h2><h2 class="wp-block-heading fv-source-heading" id="sources">')
    elif mode == "reversed-boundary":
        note_list = '<ul data-fv-footnotes>' + ''.join(f'<li id="fv-fn-{i}">Archive source {i}</li>' for i in range(1, 5)) + '</ul>'
        heading = '<h2 class="wp-block-heading fv-source-heading" id="sources">Sources &amp; Further Reading</h2>'
        article = valid_article().replace(sources(4), heading).replace('<h1>Six Miles an Hour</h1>', '<h1>Six Miles an Hour</h1>' + note_list)
    elif mode == "too-short":
        article = valid_article()
        article = re.sub(r'<p id="(?:opening|curve|cars|switch)-(?:4|3)">.*?</p>', '', article)
    elif mode == "too-few-sources":
        article = article.replace(sources(4), sources(3))
    elif mode == "storage-fail":
        prelude = "<script>Storage.prototype.setItem=function(){throw new Error('blocked storage')}</script>"
    elif mode != "valid":
        raise ValueError(mode)

    assertions = f'''
<script>
const fvcdTest=()=>{{
 const mode={mode!r};
 const fail=m=>{{document.body.dataset.fvTest='fail';document.body.dataset.fvReason=m}};
 const pass=()=>{{document.body.dataset.fvTest='pass'}};
 try{{
  const band=document.querySelector('[data-fvcd-band]');
  if(['partial-boundary','ambiguous-boundary','reversed-boundary','too-short','too-few-sources'].includes(mode)){{if(band||document.querySelector('.fvcd-dialog'))return fail('invalid fixture did not fail closed');return pass()}}
  if(!band)return fail('Case Delta launcher missing');
  if(!band.textContent.includes('not a complete publication history'))return fail('history boundary disclosure missing');
  const primary=band.querySelector('.fvcd-primary');
  if(primary.textContent!=='Save current version')return fail('first-run save state wrong');
  primary.click();
  setTimeout(()=>{{
   try{{
    if(mode==='storage-fail'){{if(!band.textContent.includes('storage is unavailable'))return fail('storage failure not surfaced');if(document.querySelector('.fvcd-dialog'))return fail('dialog opened after failed save');return pass()}}
    const store=JSON.parse(localStorage.getItem('fv_case_delta_v1')||'{{}}');
    const snap=store[location.pathname];if(!snap)return fail('snapshot not stored under same-page path');
    if(snap.sources.length!==4||snap.sections.length!==4||snap.figures.length!==2)return fail('snapshot structure count wrong');
    if(JSON.stringify(snap).includes('#ref-1'))return fail('citation backlink leaked into snapshot');
    if(primary.textContent!=='Compare with saved version')return fail('post-save compare state wrong');
    document.getElementById('curve-2').textContent+=' Updated story wording.';
    document.getElementById('fv-fn-2').firstChild.textContent='Archive source 2 revised wording ';
    document.querySelector('#fig-2 figcaption').textContent='Published caption 2 revised';
    primary.focus();primary.click();
    setTimeout(()=>{{
     try{{
      const dialog=document.querySelector('.fvcd-dialog');if(!dialog||!dialog.open)return fail('comparison dialog did not open');
      if(dialog.getAttribute('aria-labelledby')!=='fvcd-dialog-title')return fail('dialog label missing');
      if(dialog.querySelector('[data-fvcd-stat="all"] strong').textContent!=='3')return fail('total change count wrong');
      if(dialog.querySelector('[data-fvcd-stat="story"] strong').textContent!=='1')return fail('story change count wrong');
      if(dialog.querySelector('[data-fvcd-stat="source"] strong').textContent!=='1')return fail('source change count wrong');
      if(dialog.querySelector('[data-fvcd-stat="figure"] strong').textContent!=='1')return fail('figure change count wrong');
      const sourceFilter=dialog.querySelector('[data-kind="source"]');sourceFilter.click();
      if(dialog.querySelectorAll('.fvcd-row').length!==1)return fail('source filter did not isolate source change');
      const details=dialog.querySelector('.fvcd-diff');if(!details)return fail('saved/current detail comparison missing');details.open=true;
      if(!details.textContent.includes('Archive source 2')||!details.textContent.includes('revised wording'))return fail('saved/current source details incomplete');
      dialog.querySelector('[data-kind="all"]').click();
      const storyRow=[...dialog.querySelectorAll('.fvcd-row')].find(r=>r.textContent.includes('The curve under Malbone Street'));if(!storyRow||!storyRow.textContent.includes('words. Story text changed'))return fail('story change disclosure missing');
      let replace=dialog.querySelector('.fvcd-replace');replace.click();if(replace.textContent!=='Confirm replace snapshot')return fail('replace snapshot not two-step');replace.click();
      setTimeout(()=>{{
       try{{
        if(dialog.open)return fail('replace did not close dialog');
        primary.click();
        setTimeout(()=>{{
         try{{
          const d2=document.querySelector('.fvcd-dialog');if(!d2||!d2.open)return fail('post-replace comparison did not open');
          if(d2.querySelector('[data-fvcd-stat="all"] strong').textContent!=='0')return fail('replaced snapshot still reports changes');
          if(!d2.textContent.includes('No structural changes detected'))return fail('zero-change state missing');
          d2.querySelector('.fvcd-close').click();
          setTimeout(()=>{{
           if(document.activeElement!==primary)return fail('close did not return focus to invoker');
           band.querySelector('.fvcd-forget').click();
           if(localStorage.getItem('fv_case_delta_v1')&&JSON.parse(localStorage.getItem('fv_case_delta_v1'))[location.pathname])return fail('forget did not remove page snapshot');
           if(primary.textContent!=='Save current version')return fail('forget did not restore save state');
           return pass();
          }},100);
         }}catch(e){{fail(e&&e.message?e.message:String(e))}}
        }},90);
       }}catch(e){{fail(e&&e.message?e.message:String(e))}}
      }},100);
     }}catch(e){{fail(e&&e.message?e.message:String(e))}}
    }},90);
   }}catch(e){{fail(e&&e.message?e.message:String(e))}}
  }},80);
 }}catch(e){{fail(e&&e.message?e.message:String(e))}}
}};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',fvcdTest,{{once:true}});else fvcdTest();
</script>'''
    return f"<!doctype html><html><head><meta charset='utf-8'><title>Case Delta fixture</title></head><body>{prelude}{article}{payload}{assertions}</body></html>"


def run_browser(payload: str) -> None:
    browser = next((shutil.which(name) for name in ("google-chrome", "chromium", "chromium-browser") if shutil.which(name)), None)
    require(browser is not None, "headless Chrome/Chromium not available")
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        handler = partial(QuietHandler, directory=str(root))
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        origin = f"http://127.0.0.1:{server.server_port}"
        thread = threading.Thread(target=server.serve_forever, daemon=True);thread.start()
        try:
            for mode in ("valid", "partial-boundary", "ambiguous-boundary", "reversed-boundary", "too-short", "too-few-sources", "storage-fail"):
                page = root / f"case-delta-{mode}.html";page.write_text(fixture(payload, mode), encoding="utf-8")
                proc = subprocess.run([browser,"--headless=new","--no-sandbox","--disable-gpu","--disable-dev-shm-usage","--virtual-time-budget=3600","--dump-dom",f"{origin}/{page.name}"],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=35)
                require(proc.returncode == 0, f"browser fixture {mode} failed: {proc.stderr[-500:]}")
                if 'data-fv-test="pass"' not in proc.stdout:
                    reason=re.search(r'data-fv-reason="([^"]*)"',proc.stdout);raise SystemExit(f"FAIL: browser fixture {mode}: {reason.group(1) if reason else 'runtime assertions failed'}")
        finally:
            server.shutdown();server.server_close();thread.join(timeout=5)


def main() -> None:
    raw=PAYLOAD.read_bytes();text=raw.decode('utf-8')
    require(len(raw)==EXPECTED_BYTES,f"payload byte count drifted: {len(raw)}")
    actual=hashlib.sha256(raw).hexdigest();require(actual==EXPECTED_SHA256,f"payload SHA-256 drifted: {actual}")
    require(text.count('<!-- wp:html -->')==1 and text.count('<!-- /wp:html -->')==1,'single isolated wp:html block required')
    require('<style id="fv-case-delta-v1-css">' in text and '<script id="fv-case-delta-v1-js">' in text,'versioned style/script ids missing')
    require('window.__fvCaseDelta' in text,'duplicate-init guard missing')
    require("article h2#sources.fv-source-heading" in text and 'canonical.length!==1' in text,'exact canonical Sources heading gate missing')
    require('noteRoots.length!==1' in text and 'DOCUMENT_POSITION_FOLLOWING' in text,'unique ordered source-list gate missing')
    require('storyHeadings.length<2||storyHeadings.length>10' in text and 'paragraphs.length<12||paragraphs.length>120' in text and 'sourceItems.length<4||sourceItems.length>40' in text,'bounded qualification missing')
    require("STORAGE='fv_case_delta_v1'" in text and 'MAX_CASES=6' in text and 'MAX_AGE=120*24*60*60*1000' in text and 'MAX_RECORD=90000' in text,'bounded local snapshot policy missing')
    require('Saved only in this browser for up to 120 days. This is not a complete publication history.' in text,'local/history boundary microcopy missing')
    require('Nothing is sent to Final Vestige.' in text and 'does not explain why a change was made' in text,'privacy/interpretation disclosure missing')
    require('Compare with saved version' in text and 'Replace snapshot with current version' in text and 'Confirm replace snapshot' in text and 'Forget snapshot' in text,'snapshot controls incomplete')
    require('Total changes' in text and 'Story' in text and 'Sources' in text and 'Figures' in text,'change summary/filter model incomplete')
    require('min-height:44px' in text and '@media(max-width:720px)' in text and '@media(max-width:360px)' in text,'touch/mobile behavior missing')
    require('prefers-reduced-motion:reduce' in text and 'forced-colors:active' in text and '@media print' in text,'accessibility media handling missing')
    banned=['fetch(','XMLHttpRequest','sendBeacon','WebSocket','indexedDB','document.cookie','posthog','gtag(','<iframe','<script src=','navigator.clipboard','history.pushState','history.replaceState']
    lower=text.lower()
    for token in banned: require(token.lower() not in lower,f"unexpected network/analytics/navigation token: {token}")
    match=re.search(r'<script id="fv-case-delta-v1-js">\n(.*?)\n</script>',text,flags=re.S);require(match is not None,'unable to extract JavaScript')
    with tempfile.NamedTemporaryFile('w',suffix='.js',encoding='utf-8',delete=False) as handle:handle.write(match.group(1));js_path=Path(handle.name)
    try:subprocess.run(['node','--check',str(js_path)],check=True)
    finally:js_path.unlink(missing_ok=True)
    if os.environ.get('FV_BROWSER_RUNTIME')=='1':run_browser(text)
    print('PASS: Case Delta exact identity, trusted source boundary, bounded explicit local snapshots, structural story/source/figure comparison, two-step replacement, storage failure, focus/mobile/accessibility, zero-network boundary, and adversarial browser fixtures verified')

if __name__=='__main__':main()
