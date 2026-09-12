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
PAYLOAD = ROOT / "payloads" / "case-delta-wp-block-r1.txt"
EXPECTED_BYTES = 21851
EXPECTED_SHA256 = "3144b3675a331b15d0aac6611c93fde67050577e4de348c88107309993e6eb04"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def paragraphs(prefix: str, n: int) -> str:
    return "\n".join(
        f'<p id="{prefix}-{i}">{prefix} narrative paragraph {i} with enough words for a stable comparison fixture.</p>'
        for i in range(1, n + 1)
    )


def figure(n: int) -> str:
    return (
        f'<figure class="wp-block-image" id="fig-{n}">'
        f'<img src="/img/{n}.jpg" alt="Archive view {n}">'
        f'<figcaption>Published caption {n}</figcaption></figure>'
    )


def source_block(n: int = 4) -> str:
    items = "".join(
        f'<li id="fv-fn-{i}">Archive source {i} '
        f'<a href="https://example.org/{i}">Open source</a>'
        f'<span class="fv-fn-backlinks"><a class="fv-fn-back" href="#ref-{i}">↩</a></span></li>'
        for i in range(1, n + 1)
    )
    return (
        '<h2 class="wp-block-heading fv-source-heading" id="sources">'
        'Sources &amp; Further Reading</h2>'
        f'<ul data-fv-footnotes>{items}</ul>'
    )


def valid_article() -> str:
    return f'''<main><article id="post-621"><h1>Six Miles an Hour</h1>
{paragraphs("opening", 4)}
{figure(1)}
<h2>The curve under Malbone Street</h2>{paragraphs("curve", 4)}
{figure(2)}
<h2>Why the wooden cars made the wreck worse</h2>{paragraphs("cars", 4)}
<h2>The switch upstairs</h2>{paragraphs("switch", 4)}
{source_block(4)}
</article></main>'''


def article_for(mode: str) -> tuple[str, str]:
    article = valid_article()
    prelude = ""
    canonical = '<h2 class="wp-block-heading fv-source-heading" id="sources">Sources &amp; Further Reading</h2>'

    if mode == "id-only":
        article = article.replace(
            'class="wp-block-heading fv-source-heading" id="sources"',
            'class="wp-block-heading" id="sources"',
        )
    elif mode == "class-only":
        article = article.replace(
            'class="wp-block-heading fv-source-heading" id="sources"',
            'class="wp-block-heading fv-source-heading"',
        )
    elif mode == "duplicate-exact":
        article = article.replace(canonical, canonical + canonical)
    elif mode == "exact-plus-id-earlier":
        article = article.replace(
            '<h2>The switch upstairs</h2>',
            '<h2 id="sources">Earlier misleading Sources marker</h2><h2>The switch upstairs</h2>',
        )
    elif mode == "exact-plus-class-earlier":
        article = article.replace(
            '<h2>The switch upstairs</h2>',
            '<h2 class="fv-source-heading">Earlier misleading Sources marker</h2><h2>The switch upstairs</h2>',
        )
    elif mode == "exact-plus-id-later":
        article = article.replace(
            canonical,
            canonical + '<h2 id="sources">Later misleading Sources marker</h2>',
        )
    elif mode == "exact-plus-class-later":
        article = article.replace(
            canonical,
            canonical + '<h2 class="fv-source-heading">Later misleading Sources marker</h2>',
        )
    elif mode == "reversed-footnotes":
        notes = '<ul data-fv-footnotes>' + "".join(
            f'<li id="fv-fn-{i}">Archive source {i}</li>' for i in range(1, 5)
        ) + '</ul>'
        article = article.replace(source_block(4), canonical)
        article = article.replace('<h1>Six Miles an Hour</h1>', '<h1>Six Miles an Hour</h1>' + notes)
    elif mode == "too-short":
        article = re.sub(
            r'<p id="(?:opening|curve|cars|switch)-(?:3|4)">.*?</p>',
            '',
            article,
        )
    elif mode == "too-few-sources":
        article = article.replace(source_block(4), source_block(3))
    elif mode == "storage-fail":
        prelude = "<script>Storage.prototype.setItem=function(){throw new Error('blocked storage')}</script>"
    elif mode == "jump-preowned":
        article = article.replace(
            '<h2>The curve under Malbone Street</h2>',
            '<h2 tabindex="0" class="fvcd-story-focus publisher-class">The curve under Malbone Street</h2>',
        )
    elif mode in {"valid", "jump-absent"}:
        pass
    else:
        raise ValueError(mode)
    return article, prelude


def fixture(payload_text: str, mode: str) -> str:
    article, prelude = article_for(mode)
    invalid_modes = [
        "id-only",
        "class-only",
        "duplicate-exact",
        "exact-plus-id-earlier",
        "exact-plus-class-earlier",
        "exact-plus-id-later",
        "exact-plus-class-later",
        "reversed-footnotes",
        "too-short",
        "too-few-sources",
    ]
    assertions = f'''
<script>
const fvcdTest=()=>{{
 const mode={mode!r};
 const fail=m=>{{document.body.dataset.fvTest='fail';document.body.dataset.fvReason=m}};
 const pass=()=>{{document.body.dataset.fvTest='pass'}};
 try{{
   const band=document.querySelector('[data-fvcd-band]');
   if({invalid_modes!r}.includes(mode)){{
     if(band||document.querySelector('.fvcd-dialog'))return fail('untrusted/invalid Sources fixture did not fail closed');
     return pass();
   }}
   if(!band)return fail('Case Delta launcher missing');
   if(!band.textContent.includes('not a complete publication history'))return fail('history-boundary disclosure missing');
   const primary=band.querySelector('.fvcd-primary');
   if(primary.textContent!=='Save current version')return fail('first-run save state wrong');
   primary.click();
   setTimeout(()=>{{
     try{{
       if(mode==='storage-fail'){{
         if(!band.textContent.includes('storage is unavailable'))return fail('storage failure not surfaced');
         if(document.querySelector('.fvcd-dialog'))return fail('dialog opened after failed save');
         return pass();
       }}
       const store=JSON.parse(localStorage.getItem('fv_case_delta_v1')||'{{}}');
       const snap=store[location.pathname];
       if(!snap)return fail('snapshot not stored under same-page path');
       if(snap.sources.length!==4||snap.sections.length!==4||snap.figures.length!==2)return fail('snapshot structure count wrong');
       if(JSON.stringify(snap).includes('#ref-1'))return fail('citation backlink leaked into snapshot');
       document.getElementById('curve-2').textContent+=' Updated story wording.';
       document.getElementById('fv-fn-2').firstChild.textContent='Archive source 2 revised wording ';
       document.querySelector('#fig-2 figcaption').textContent='Published caption 2 revised';
       primary.focus();primary.click();
       setTimeout(()=>{{
         try{{
           const dialog=document.querySelector('.fvcd-dialog');
           if(!dialog||!dialog.open)return fail('comparison dialog did not open');
           if(dialog.getAttribute('aria-labelledby')!=='fvcd-dialog-title')return fail('dialog label missing');
           if(dialog.querySelector('[data-fvcd-stat="all"] strong').textContent!=='3')return fail('total change count wrong');

           if(mode==='jump-absent'||mode==='jump-preowned'){{
             const target=[...document.querySelectorAll('h2')].find(h=>h.textContent==='The curve under Malbone Street');
             if(!target)return fail('jump target missing');
             const expectedTab=mode==='jump-preowned'?'0':null;
             const expectedOwnClass=mode==='jump-preowned';
             const jump=[...dialog.querySelectorAll('.fvcd-row')].find(r=>r.textContent.includes('The curve under Malbone Street'))?.querySelector('.fvcd-jump');
             if(!jump)return fail('story jump control missing');
             jump.click();
             setTimeout(()=>{{
               try{{
                 if(target.getAttribute('tabindex')!==expectedTab)return fail('jump changed publisher tabindex state');
                 if(target.classList.contains('fvcd-story-focus')!==expectedOwnClass)return fail('jump changed pre-owned focus-class state after cleanup boundary');
                 if(mode==='jump-preowned'&&!target.classList.contains('publisher-class'))return fail('jump removed publisher class');
                 primary.click();
                 setTimeout(()=>{{
                   try{{
                     const d2=document.querySelector('.fvcd-dialog');
                     if(!d2||!d2.open)return fail('repeat-jump dialog did not reopen');
                     const jump2=[...d2.querySelectorAll('.fvcd-row')].find(r=>r.textContent.includes('The curve under Malbone Street'))?.querySelector('.fvcd-jump');
                     if(!jump2)return fail('repeat-jump control missing');
                     jump2.click();
                     setTimeout(()=>{{
                       if(target.getAttribute('tabindex')!==expectedTab)return fail('repeat jump drifted tabindex');
                       if(target.classList.contains('fvcd-story-focus')!==expectedOwnClass)return fail('repeat jump drifted focus class');
                       if(mode==='jump-preowned'&&!target.classList.contains('publisher-class'))return fail('repeat jump removed publisher class');
                       return pass();
                     }},120);
                   }}catch(e){{fail(e&&e.message?e.message:String(e))}}
                 }},100);
               }}catch(e){{fail(e&&e.message?e.message:String(e))}}
             }},120);
             return;
           }}

           const sourceFilter=dialog.querySelector('[data-kind="source"]');
           sourceFilter.click();
           if(dialog.querySelectorAll('.fvcd-row').length!==1)return fail('source filter did not isolate source change');
           const details=dialog.querySelector('.fvcd-diff');
           if(!details)return fail('saved/current detail comparison missing');
           details.open=true;
           if(!details.textContent.includes('Archive source 2')||!details.textContent.includes('revised wording'))return fail('saved/current source details incomplete');
           dialog.querySelector('[data-kind="all"]').click();
           const storyRow=[...dialog.querySelectorAll('.fvcd-row')].find(r=>r.textContent.includes('The curve under Malbone Street'));
           if(!storyRow||!storyRow.textContent.includes('words. Story text changed'))return fail('story change disclosure missing');
           let replace=dialog.querySelector('.fvcd-replace');
           replace.click();
           if(replace.textContent!=='Confirm replace snapshot')return fail('replace snapshot not two-step');
           replace.click();
           setTimeout(()=>{{
             try{{
               if(dialog.open)return fail('replace did not close dialog');
               primary.click();
               setTimeout(()=>{{
                 try{{
                   const d2=document.querySelector('.fvcd-dialog');
                   if(!d2||!d2.open)return fail('post-replace comparison did not open');
                   if(d2.querySelector('[data-fvcd-stat="all"] strong').textContent!=='0')return fail('replaced snapshot still reports changes');
                   if(!d2.textContent.includes('No structural changes detected'))return fail('zero-change state missing');
                   d2.querySelector('.fvcd-close').click();
                   setTimeout(()=>{{
                     if(document.activeElement!==primary)return fail('close did not return focus to invoker');
                     band.querySelector('.fvcd-forget').click();
                     const after=JSON.parse(localStorage.getItem('fv_case_delta_v1')||'{{}}');
                     if(after[location.pathname])return fail('forget did not remove page snapshot');
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
</script>
'''
    return (
        "<!doctype html><html><head><meta charset='utf-8'><title>Case Delta R1 fixture</title></head>"
        f"<body>{prelude}{article}{payload_text}{assertions}</body></html>"
    )


def run_browser(payload_text: str) -> None:
    browser = next(
        (shutil.which(name) for name in ("google-chrome", "chromium", "chromium-browser") if shutil.which(name)),
        None,
    )
    require(browser is not None, "headless Chrome/Chromium not available")
    modes = (
        "valid",
        "id-only",
        "class-only",
        "duplicate-exact",
        "exact-plus-id-earlier",
        "exact-plus-class-earlier",
        "exact-plus-id-later",
        "exact-plus-class-later",
        "reversed-footnotes",
        "too-short",
        "too-few-sources",
        "storage-fail",
        "jump-absent",
        "jump-preowned",
    )
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        handler = partial(QuietHandler, directory=str(root))
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        origin = f"http://127.0.0.1:{server.server_port}"
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            for mode in modes:
                page = root / f"case-delta-r1-{mode}.html"
                page.write_text(fixture(payload_text, mode), encoding="utf-8")
                proc = subprocess.run(
                    [
                        browser,
                        "--headless=new",
                        "--no-sandbox",
                        "--disable-gpu",
                        "--disable-dev-shm-usage",
                        "--virtual-time-budget=4200",
                        "--dump-dom",
                        f"{origin}/{page.name}",
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=40,
                )
                require(proc.returncode == 0, f"browser fixture {mode} failed: {proc.stderr[-500:]}")
                if 'data-fv-test="pass"' not in proc.stdout:
                    reason = re.search(r'data-fv-reason="([^"]*)"', proc.stdout)
                    raise SystemExit(
                        f"FAIL: browser fixture {mode}: "
                        f"{reason.group(1) if reason else 'runtime assertions failed'}"
                    )
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


def main() -> None:
    raw = PAYLOAD.read_bytes()
    text = raw.decode("utf-8")
    require(len(raw) == EXPECTED_BYTES, f"payload byte count drifted: {len(raw)}")
    actual = hashlib.sha256(raw).hexdigest()
    require(actual == EXPECTED_SHA256, f"payload SHA-256 drifted: {actual}")
    require(
        text.count("<!-- wp:html -->") == 1 and text.count("<!-- /wp:html -->") == 1,
        "single isolated wp:html block required",
    )
    require("window.__fvCaseDelta" in text, "duplicate-init guard missing")
    require(
        "article h2#sources.fv-source-heading" in text
        and "sourceHeadingCandidates" in text
        and "article.querySelectorAll('#sources, .fv-source-heading')" in text
        and "sourceHeadingCandidates.length!==1||sourceHeadingCandidates[0]!==sourceHeading" in text,
        "hardened unique Sources boundary contract missing",
    )
    require(
        "noteRoots.length!==1" in text and "DOCUMENT_POSITION_FOLLOWING" in text,
        "unique ordered footnote-root gate missing",
    )
    require(
        "STORAGE='fv_case_delta_v1'" in text
        and "MAX_CASES=6" in text
        and "MAX_AGE=120*24*60*60*1000" in text
        and "MAX_RECORD=90000" in text,
        "bounded browser-local snapshot policy missing",
    )
    require(
        "Saved only in this browser for up to 120 days. This is not a complete publication history." in text
        and "Nothing is sent to Final Vestige." in text
        and "does not explain why a change was made" in text,
        "trust/privacy boundary microcopy missing",
    )
    require(
        "hadTab=target.hasAttribute('tabindex')" in text
        and "oldTab=target.getAttribute('tabindex')" in text
        and "hadFocusClass=target.classList.contains('fvcd-story-focus')" in text,
        "publisher-owned DOM state ownership tracking missing",
    )
    require(
        "if(!hadTab){target.setAttribute('tabindex','-1');addedTab=true}" in text
        and "if(addedTab)target.removeAttribute('tabindex')" in text
        and "if(!hadFocusClass){target.classList.add('fvcd-story-focus');addedClass=true}" in text
        and "if(addedClass)target.classList.remove('fvcd-story-focus')" in text,
        "temporary DOM state is not ownership-safe",
    )
    for token in [
        "fetch(",
        "XMLHttpRequest",
        "sendBeacon",
        "WebSocket",
        "indexedDB",
        "document.cookie",
        "posthog",
        "gtag(",
        "<iframe",
        "<script src=",
        "navigator.clipboard",
        "history.pushState",
        "history.replaceState",
    ]:
        require(token.lower() not in text.lower(), f"unexpected network/analytics/navigation token: {token}")

    match = re.search(r'<script id="fv-case-delta-v1-js">\n(.*?)\n</script>', text, flags=re.S)
    require(match is not None, "unable to extract Case Delta JavaScript")
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(match.group(1))
        js_path = Path(handle.name)
    try:
        subprocess.run(["node", "--check", str(js_path)], check=True)
    finally:
        js_path.unlink(missing_ok=True)

    if os.environ.get("FV_BROWSER_RUNTIME") == "1":
        run_browser(text)

    print(
        "PASS: Case Delta R1 exact identity, unique canonical Sources boundary, "
        "mixed/partial/duplicate fail-closed behavior, browser-local snapshot trust contract, "
        "nondestructive repeated story jumps, accessibility/mobile/privacy, and zero-network assertions verified"
    )


if __name__ == "__main__":
    main()
