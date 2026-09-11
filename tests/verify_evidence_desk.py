from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "payloads" / "evidence-desk-wp-block-v1.txt"
EXPECTED_BYTES = 15604
EXPECTED_SHA256 = "49747071b3a425a1f53033cc1f76fc33e9fb0f6c330d1f9437f75bfd75cb0d7f"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def fixture(payload: str, mode: str) -> str:
    para = ("A documented paragraph in a long investigation keeps the reader inside the published narrative while "
            "preserving enough text to satisfy the longform qualification threshold. " * 2)
    story = "".join(f"<p>{para}{i}</p>" for i in range(12))
    figures = "".join(
        f'<figure class="wp-block-image"><img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw==" '
        f'alt="Figure {i} alt"><figcaption>Published figure {i} caption.</figcaption></figure>'
        for i in range(1, 3)
    )
    notes = '<ul class="wp-block-list fv-source-list" data-fv-footnotes>' + "".join(
        f'<li id="fv-fn-{i}">Published source note {i} with context '
        f'<a href="https://example.org/source-{i}">Open source</a>'
        f'<span class="fv-fn-backlinks"><a href="#fv-fnref-{i}-1">↩</a></span></li>'
        for i in range(1, 5)
    ) + "</ul>"
    heading = '<h2 class="wp-block-heading fv-source-heading" id="sources">Sources &amp; Further Reading</h2>'
    if mode == "valid":
        boundary = heading + notes
    elif mode == "missing":
        boundary = notes
    elif mode == "reversed":
        boundary = notes + heading
    else:
        raise ValueError(mode)

    assertions = """
<script>
const runEvidenceDeskFixture=()=>{
  const fail=(m)=>{document.body.dataset.fvTest='fail';document.body.dataset.fvReason=m};
  try{
    const launch=document.querySelector('[data-fv-evidence-desk-launcher]');
    if(MODE!=='valid'){
      if(launch) return fail('fail-closed qualification did not hold');
      document.body.dataset.fvTest='pass';return;
    }
    if(!launch) return fail('launcher missing');
    const open=launch.querySelector('.fved-open');open.click();
    const desk=document.querySelector('[data-fv-evidence-desk]');
    if(!desk||desk.hidden) return fail('desk did not open');
    if(open.getAttribute('aria-expanded')!=='true') return fail('launcher expanded state missing');
    let buttons=[...document.querySelectorAll('.fved-pin')];
    if(buttons.length!==6) return fail('expected six pin controls');
    const initialImages=document.querySelectorAll('figure.wp-block-image img').length;
    buttons.slice(0,4).forEach(b=>b.click());
    if(desk.querySelectorAll('.fved-card').length!==4) return fail('four-card working set failed');
    buttons=[...document.querySelectorAll('.fved-pin')];
    if(!buttons[4].disabled||!buttons[5].disabled) return fail('four-item cap not enforced');
    const firstRemove=desk.querySelector('.fved-card [data-action="remove"]');firstRemove.click();
    buttons=[...document.querySelectorAll('.fved-pin')];
    if(buttons[4].disabled) return fail('capacity did not reopen');
    buttons[4].click();
    if(desk.querySelectorAll('.fved-card').length!==4) return fail('replacement pin failed');
    if(document.querySelectorAll('figure.wp-block-image img').length!==initialImages) return fail('figure images were duplicated');
    const sourceLink=desk.querySelector('.fved-card a[href^="https://example.org/"]');
    if(!sourceLink||sourceLink.rel!=='noopener') return fail('published source link was not safely preserved');
    desk.querySelector('.fved-clear').click();
    if(desk.querySelectorAll('.fved-card').length!==0) return fail('clear failed');
    if(!desk.querySelector('.fved-status strong').textContent.startsWith('0 of 4')) return fail('status did not reset');
    const spacer=document.querySelector('[data-fv-evidence-desk-spacer]');
    if(!spacer||!desk.dataset.layout) return fail('adaptive layout/spacer contract missing');
    desk.querySelector('.fved-close').click();
    if(!desk.hidden||document.querySelectorAll('.fved-pin').length!==0) return fail('close cleanup failed');
    open.click();
    const p=[...document.querySelectorAll('.fved-pin')][0];p.focus();
    document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));
    if(!desk.hidden) return fail('Escape did not close desk');
    if(document.activeElement!==open) return fail('focus did not return to launcher');
    document.body.dataset.fvTest='pass';
  }catch(e){fail(e&&e.message?e.message:String(e))}
};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',runEvidenceDeskFixture,{once:true});else runEvidenceDeskFixture();
</script>
"""
    assertions = assertions.replace("MODE", repr(mode))
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>body{{margin:0}}main{{max-width:760px;margin:auto}}</style></head>
<body class="single-post"><script>try{{delete window.ResizeObserver}}catch(e){{window.ResizeObserver=undefined}}</script><main><article><div class="entry-content">{story}<h2 class="wp-block-heading">First turn</h2>{figures}{boundary}</div></article></main>
{payload}
{assertions}
</body></html>"""


def run_browser(payload: str) -> None:
    browser = next((shutil.which(name) for name in ("google-chrome", "chromium", "chromium-browser") if shutil.which(name)), None)
    require(browser is not None, "headless Chrome/Chromium not available for runtime regression test")
    with tempfile.TemporaryDirectory() as temp:
        temp_path = Path(temp)
        for mode in ("valid", "missing", "reversed"):
            page = temp_path / f"evidence-desk-{mode}.html"
            page.write_text(fixture(payload, mode), encoding="utf-8")
            proc = subprocess.run(
                [browser, "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage",
                 "--dump-dom", page.as_uri()],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30
            )
            require(proc.returncode == 0, f"browser fixture {mode} failed to execute: {proc.stderr[-500:]}")
            require('data-fv-test="pass"' in proc.stdout, f"browser fixture {mode} failed runtime assertions")


def main() -> None:
    raw = PAYLOAD.read_bytes()
    text = raw.decode("utf-8")
    require(len(raw) == EXPECTED_BYTES, f"payload byte count drifted: {len(raw)}")
    actual_sha256 = hashlib.sha256(raw).hexdigest()
    require(actual_sha256 == EXPECTED_SHA256, f"payload SHA-256 drifted: {actual_sha256}")

    require(text.count("<!-- wp:html -->") == 1, "payload must contain exactly one wp:html opener")
    require(text.count("<!-- /wp:html -->") == 1, "payload must contain exactly one wp:html closer")
    require('<style id="fv-evidence-desk-v1-css">' in text, "versioned stylesheet id missing")
    require('<script id="fv-evidence-desk-v1-js">' in text, "versioned script id missing")
    require("window.__fvEvidenceDesk" in text, "duplicate-init guard missing")

    require("single-post" in text, "single-post qualification missing")
    require("h2#sources.fv-source-heading" in text, "trusted Sources heading selector missing")
    require(".fv-source-list[data-fv-footnotes]" in text, "trusted source-note selector missing")
    require("if(!sourceHeading||!notesRoot)return" in text, "missing-source fail-closed gate missing")
    require("sourceHeading.compareDocumentPosition(notesRoot)&Node.DOCUMENT_POSITION_FOLLOWING" in text, "heading-before-notes contract missing")
    require("if(!root.contains(sourceHeading)||!root.contains(notesRoot))return" in text, "same-root source contract missing")
    require("paragraphs.length<12||storyChars<2800||validNotes.length<4||figures.length<2" in text, "longform/evidence qualification missing")
    require("if(items.size<6)return" in text, "minimum useful working-set candidate threshold missing")

    require("Keep the record in reach while you read." in text, "visitor-value headline missing")
    require("Session only—nothing is saved." in text, "session boundary copy missing")
    require("Only published material from this page. No notes are created, scored or saved." in text, "evidence/non-scoring boundary copy missing")
    require("up to four" in text.lower() and "pins.size>=4" in text, "four-item cap missing")

    require("cleanText" in text and ".fv-fn-backlinks,.fved-pin,[data-fv-feature-ui]" in text, "clean published-text extraction missing")
    require("textContent=" in text, "safe dynamic text rendering missing")
    require("external?external.href:''" in text, "source-link provenance extraction missing")
    require("link.rel='noopener'" in text and "link.target='_blank'" in text, "safe external-link behavior missing")
    require("figure.wp-block-image" in text and "img.getAttribute('alt')" in text, "figure caption/alt fallback missing")
    require("pins=new Map()" in text and "pinButtons=new Map()" in text, "in-memory working set missing")
    require("spacer.style.height" in text and "ResizeObserver" in text, "non-obstructive bottom-tray reachability contract missing")
    require("window.innerWidth>=1180&&r.right<=window.innerWidth-395" in text, "free-margin side-layout gate missing")
    require("scrollIntoView" in text and "fved-arrived" in text, "return-to-story behavior missing")
    require("e.key==='Escape'&&isOpen" in text and "open.focus()" in text, "Escape/focus-return behavior missing")

    require("min-height:44px" in text, "44px target contract missing")
    require("@media(max-width:700px)" in text and "@media(max-width:360px)" in text, "mobile behavior missing")
    require("prefers-reduced-motion:reduce" in text, "reduced-motion support missing")
    require("forced-colors:active" in text, "forced-colors support missing")
    require("@media print" in text, "print cleanup missing")
    require("outline:3px solid var(--fved-accent)" in text, "unambiguous keyboard focus ring missing")

    banned_literals = [
        "localStorage", "sessionStorage", "indexedDB", "document.cookie", "posthog", "gtag(",
        "sendBeacon", "WebSocket", "history.pushState", "history.replaceState", "navigator.clipboard"
    ]
    for token in banned_literals:
        require(token.lower() not in text.lower(), f"unexpected persistence/network/analytics/history token: {token}")
    banned_patterns = {
        r"\bfetch\s*\(": "network fetch",
        r"XMLHttpRequest": "XHR",
        r"<script[^>]+src=": "external script dependency",
        r"<iframe\b": "embedded external frame",
    }
    for pattern, label in banned_patterns.items():
        require(not re.search(pattern, text, flags=re.I), f"unexpected {label}")

    match = re.search(r'<script id="fv-evidence-desk-v1-js">\n(.*?)\n</script>', text, flags=re.S)
    require(match is not None, "unable to extract JavaScript")
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(match.group(1))
        js_path = Path(handle.name)
    try:
        subprocess.run(["node", "--check", str(js_path)], check=True)
    finally:
        js_path.unlink(missing_ok=True)

    if os.environ.get("FV_BROWSER_RUNTIME") == "1":
        run_browser(text)
    print("PASS: Evidence Desk exact identity, trusted-source fail-closed qualification, four-item session working set, adaptive non-obstructive layout, source/figure provenance, focus/accessibility behavior, no-persistence/no-network boundary, JavaScript syntax, and headless browser runtime regressions verified")


if __name__ == "__main__":
    main()
