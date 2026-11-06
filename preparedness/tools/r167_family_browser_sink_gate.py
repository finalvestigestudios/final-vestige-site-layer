#!/usr/bin/env python3
"""R167: fail-closed active browser privacy-sink preflight for unapproved Family Card.

The sandbox uses synthetic entries only. It detects classes of calls but neither claims
WordPress privacy nor qualifies an emergency instruction for publication. In-page JS
instrumentation is regression testing, NOT a hostile-code security boundary.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
from urllib.parse import urlsplit

SCHEMA = 'fv-preparedness-r167-browser-sink-gate-v1'
WIDTHS = (360, 390, 768, 1440)
SENTINEL = 'FV-SYNTHETIC-TEST-ONLY-167'
FIELDS = ('hhName', 'hhPhone', 'outName', 'outPhone', 'meet1', 'meet2',
          'school', 'schoolPlan', 'pickup', 'careName', 'carePhone', 'access', 'reviewed')
SENSITIVE = ('school', 'schoolPlan', 'pickup', 'careName', 'carePhone', 'access', 'meet2')

# This script runs at document initialization, before any page-owned scripts.
# No request URL, input value, header, contact detail or payload is logged.
PROBE_JS = r'''(() => {
  'use strict';
  const attempted = [];
  const track = (label) => { attempted.push(String(label)); };
  Object.defineProperty(window, '__fv_r167_snapshot', {
    configurable:false, writable:false,
    value:() => attempted.slice()
  });
  const denyCall = (name, host, property) => {
    try {
      const original = Object.getOwnPropertyDescriptor(host, property);
      if (original && !original.configurable && !original.writable) return;
      Object.defineProperty(host, property, {
        configurable:true, writable:true,
        value:function(...args){ track(name); throw new DOMException('Disabled by offline review probe','SecurityError'); }
      });
    } catch (e) { track('probe_install_error:' + name); }
  };
  for (const n of ['fetch','WebSocket','EventSource','XMLHttpRequest','Worker',
                   'SharedWorker','BroadcastChannel','RTCPeerConnection',
                   'webkitRTCPeerConnection']) denyCall(n, window, n);
  try { if (navigator.sendBeacon) denyCall('sendBeacon', Object.getPrototypeOf(navigator), 'sendBeacon'); }
  catch(e){ track('probe_install_error:sendBeacon'); }
  for (const n of ['localStorage','sessionStorage']) {
    try { Object.defineProperty(window,n,{ configurable:true,
      get:function(){track(n+'.access'); throw new DOMException('No browser storage in offline review','SecurityError');}
    }); } catch(e) {track('probe_install_error:'+n);} 
  }
  try { if (window.Storage) {
    for (const n of ['setItem','removeItem','clear']) denyCall('Storage.'+n, Storage.prototype, n);
  }} catch(e){track('probe_install_error:Storage');}
  try { if (window.indexedDB) for (const n of ['open','deleteDatabase']) denyCall('indexedDB.'+n, IDBFactory.prototype, n); }
  catch(e){track('probe_install_error:indexedDB');}
  try { if (window.HTMLFormElement) {
    for (const n of ['submit','requestSubmit']) denyCall('form.'+n, HTMLFormElement.prototype, n);
  }}catch(e){track('probe_install_error:form');}
  try { if (navigator.serviceWorker) denyCall('serviceWorker.register', ServiceWorkerContainer.prototype, 'register'); }
  catch(e){track('probe_install_error:serviceWorker');}
  try { if (navigator.clipboard) {
    for (const n of ['writeText','write']) denyCall('clipboard.'+n, Clipboard.prototype, n);
  }}catch(e){track('probe_install_error:clipboard');}
  try { if (window.URL && URL.createObjectURL) denyCall('URL.createObjectURL', URL, 'createObjectURL'); }
  catch(e){track('probe_install_error:objectURL');}
  try { const original = Object.getOwnPropertyDescriptor(Document.prototype, 'cookie');
    if (original && original.configurable) Object.defineProperty(Document.prototype,'cookie',{
      configurable:true, get:function(){return original.get ? original.get.call(this) : '';},
      set:function(_value){track('document.cookie');}
    });
  } catch(e){track('probe_install_error:cookie');}
})();'''


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def safe_summary(events: list[str]) -> dict:
    """Allow only bounded API names; never include contact or destination data."""
    require(isinstance(events, list), 'invalid event container')
    cleaned = []
    for event in events:
        require(isinstance(event, str), 'nontext event')
        require(bool(re.fullmatch(r'[A-Za-z_.:]{1,80}', event)), 'unsafe telemetry key')
        cleaned.append(event)
    return {'attempts': len(cleaned), 'kinds': sorted(set(cleaned))[:64]}


def document(html: str) -> str:
    require(isinstance(html, str) and len(html) > 200, 'invalid document')
    # The unmodified R165 generator is the source of the authentic HTML. This is
    # just a no-network local preview; citations remain editorial tokens.
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '</head><body><main class="pa-article"><div class="pa-shell">'
            '<div class="pa-body">' + html + '</div></div></main></body></html>')


def _snapshot(page) -> list[str]:
    got = page.evaluate('window.__fv_r167_snapshot && window.__fv_r167_snapshot()')
    require(isinstance(got, list), 'pre-document privacy sensor missing')
    return got


def _observe_one(page, width: int, external: list[str], socket: list[str], errors: list[str]) -> dict:
    # Check before interaction, during data entry, after minimal mode, after clear.
    require(not _snapshot(page), 'privacy/network sink at page initialization')
    require(page.locator('#rc-live').evaluate('(e) => !e.hidden'), 'card did not initialize')
    require(page.locator('#rc-reset').is_visible(), 'clear button unavailable')
    require(page.locator('#rc-print').is_visible(), 'print button unavailable')
    require(page.locator('#rc input[name]').count() == 0, 'named personal-data inputs')
    page.locator('#rc-outName').fill(SENTINEL)
    page.locator('#rc-school').fill('FV-FAKE-SCHOOL-167')
    page.locator('#rc-careName').fill('FV-FAKE-CARE-167')
    page.locator('#rc-meet2').fill('FV-FAKE-SECOND-167')
    require(SENTINEL in page.locator('#rc-preview').inner_text(), 'card preview not populated')
    require(not _snapshot(page), 'privacy/network sink during typing')
    page.locator('#rc-minimal').check()
    page.locator('#rc-copies').select_option('4')
    require(page.locator('#rc-sheet .pa-foldcard').count() == 4, 'print copies not generated')
    output = page.locator('#rc-sheet').inner_text() + page.locator('#rc-preview').inner_text()
    for secret in ('FV-FAKE-SCHOOL-167','FV-FAKE-CARE-167','FV-FAKE-SECOND-167'):
        require(secret not in output, 'minimal card still discloses sensitive field')
    require(not _snapshot(page), 'privacy/network sink during minimal mode')
    page.emulate_media(media='print')
    require(page.locator('#rc-sheet').evaluate('(e) => getComputedStyle(e).display') != 'none', 'print sheet invisible')
    require(page.locator('#rc').evaluate('(e) => getComputedStyle(e).display') == 'none', 'entry form visible in print')
    page.emulate_media(media='screen')
    page.locator('#rc-reset').click()
    for name in FIELDS:
        require(page.locator('#rc-'+name).input_value() == '', 'clear left personal data in '+name)
    require(SENTINEL not in page.locator('#rc-preview').inner_text()+page.locator('#rc-sheet').inner_text(), 'clear left visible data')
    require(not _snapshot(page), 'privacy/network sink during clear')
    require(page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), 'horizontal overflow')
    require(not external and not socket and not errors, 'external network/socket or script error')
    return {'width': width, 'status':'SYNTHETIC_OFFLINE_ONLY', 'sink_attempts':0,
            'external_attempts':0, 'socket_attempts':0}


def probe(html: str, *, widths=WIDTHS, action=None) -> dict:
    """Synthetic-only Chromium proof. Optional action is only for isolated tests."""
    require(tuple(widths) != (), 'no viewport checks')
    require(len(set(widths)) == len(tuple(widths)), 'duplicate viewport')
    require(all(type(w) is int and 240 <= w <= 2200 for w in widths), 'invalid viewport')
    preview = document(html)
    from playwright.sync_api import sync_playwright
    executable = shutil.which('chromium') or shutil.which('chromium-browser')
    require(bool(executable), 'local Chromium unavailable')
    results=[]
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=executable, args=['--no-sandbox'])
        try:
            for width in widths:
                ctx=browser.new_context(viewport={'width':width,'height':900},
                                        service_workers='block',accept_downloads=False)
                external, socket, errors=[],[],[]
                try:
                    ctx.add_init_script(script=PROBE_JS)
                    def route_handler(route):
                        scheme=urlsplit(route.request.url).scheme.lower()
                        if scheme not in ('file','data','about'):
                            external.append(scheme) # No URL or payload retained
                            route.abort()
                        else:
                            route.continue_()
                    ctx.route('**/*',route_handler)
                    page=ctx.new_page()
                    page.on('websocket',lambda ws:socket.append('websocket'))
                    page.on('pageerror',lambda e:errors.append(type(e).__name__))
                    page.set_content(preview,wait_until='load')
                    require(not errors, 'script exception on load')
                    if action:
                        action(page)
                    results.append(_observe_one(page,width,external,socket,errors))
                finally:
                    ctx.close()
        finally:
            browser.close()
    return {'schema':SCHEMA, 'state':'DRAFT_HARD_HOLD', 'fixture_test':action is not None,
            'checks':results,'wordPress_verified':False,'independent_qd_pass':False,
            'source_safety_approved':False,'paid_checkout_authorized':False,
            'publication_authorized':False}


def authentic(root: Path) -> dict:
    # Authenticated source custody is required before *any* authentic browser probe.
    import sys
    path=root/'preparedness'/'tools'
    sys.path.insert(0,str(path))
    import r166_family_browser_probe as r166
    import r165_inline_dependency_custody as r165
    prior=r166.authentic(root)  # Still DRAFT/HARD HOLD even if the previous probe passes.
    require(prior.get('state') == 'DRAFT_HARD_HOLD' and prior.get('complete_source_custody_checked'), 'R166 custody incomplete')
    original=r165.audit(root)
    require(original.get('state') == 'DRAFT_HARD_HOLD', 'R165 custody incomplete')
    scripts={n:(path/n).read_text(encoding='utf-8') for n in r165.EXPECTED}
    template=(root/r165.STAGED).read_text(encoding='utf-8')
    html, expanded=r165.expand_checked(template,scripts)
    require(expanded.get('expanded_sha256') == prior.get('r165_dependency_hash'), 'R165 expansion drift')
    r166.valid_card(html)
    return {**probe(html), 'source_chain_checked':True, 'r165_hash':expanded['expanded_sha256'],
            'previous_browser_checks':len(prior.get('local_chromium_preflight',[]))}


def main(argv=None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',type=Path,default=Path('.'))
    parser.add_argument('--report',type=Path,default=None)
    opts=parser.parse_args(argv)
    try:
        report=authentic(opts.repo.resolve(strict=True))
    except Exception as error:
        report={'schema':SCHEMA,'state':'INVALID_HARD_HOLD',
                'reason':type(error).__name__+': '+str(error)[:160],
                'publication_authorized':False,'independent_qd_pass':False}
    output=json.dumps(report,sort_keys=True)
    if opts.report:
        opts.report.write_text(output+'\n',encoding='utf-8')
    print(output)
    return 2  # explicit human approval cannot be granted by a local probe

if __name__=='__main__':
    raise SystemExit(main())
