"""Final Vestige Dispatch — strictly GET-only, PII-free, non-sending visitor DOM probe.

Usage: python signedout_probe.py --fixture (local six cases, zero HTTP)
       python signedout_probe.py --live   (two approved first-party GET pages only)

Never enters addresses, submits forms, sends email, subscribes or changes CMS.
A visible form is *not* proof that a subscriber confirmed or received email.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

ROOT = 'https://finalvestige.com'
PAGES = {'dispatch': ROOT + '/dispatch/', 'focus': ROOT + '/focus/'}
TRUSTED_HOSTS = ('finalvestige.com', 'www.finalvestige.com', 'wordpress.com',
                 'wp.com', 'jetpack.com', 'gravatar.com')


def permitted_get(url: str, method: str) -> bool:
    """Allow GET-only published page and static dependencies; never a write."""
    if method.upper() != 'GET':
        return False
    parsed = urlparse(url)
    if parsed.scheme in {'data', 'about', 'blob'}:
        return True
    if parsed.scheme != 'https' or not parsed.hostname:
        return False
    host = parsed.hostname.lower()
    return any(host == h or host.endswith('.' + h) for h in TRUSTED_HOSTS)


def snapshot(page, key: str) -> dict:
    """Aggregate DOM facts only; no input values, emails, names or page text."""
    return page.evaluate("""(key) => {
      const blocks=[...document.querySelectorAll('.wp-block-jetpack-subscriptions')];
      const isVisible=e=>{if(!e)return false;const s=getComputedStyle(e),r=e.getBoundingClientRect();
        return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0};
      const inputs=blocks.flatMap(b=>[...b.querySelectorAll('input[type=email]')]);
      const forms=blocks.flatMap(b=>[...b.querySelectorAll('form')]);
      const labels=inputs.map(e=>!!(e.labels?.length||e.getAttribute('aria-label')||e.getAttribute('aria-labelledby')));
      const anchors=blocks.flatMap(b=>[...b.querySelectorAll('a[href]')]);
      const base=location.protocol==='about:'?'https://finalvestige.com/'+(key==='focus'||key==='hidden_email'?'focus':'dispatch')+'/':location.href;
      const same=anchors.filter(a=>{try{const u=new URL(a.getAttribute('href'),base);
        return u.origin===new URL(base).origin && (u.pathname===new URL(base).pathname || u.searchParams.get('p')===(key==='focus'?'1579':'523'));}
        catch(_){return false}});
      const safeButtons=blocks.flatMap(b=>[...b.querySelectorAll('button[type=button]')]);
      return {page:key,block_count:blocks.length,forms:forms.length,
        email_inputs:inputs.length,visible_email_inputs:inputs.filter(isVisible).length,
        labeled_visible_inputs:inputs.filter((e,i)=>isVisible(e)&&labels[i]).length,
        same_site_anchors:anchors.filter(a=>{try{return new URL(a.getAttribute('href'),base).origin===new URL(base).origin}catch(_){return false}}).length,
        same_page_anchors:same.length, safe_modal_button_candidates:safeButtons.length,
        form_submit_attempts:0, real_subscription_verified:false, welcome_receipt_verified:false};
    }""", key)


def classify(before: dict, after: dict | None = None) -> str:
    evidence = after or before
    if evidence['visible_email_inputs'] and evidence['labeled_visible_inputs']:
        return 'VISIBLE_LABELED_FORM_NOT_SIGNUP_PROOF' if not after else 'VISIBLE_FORM_AFTER_SAFE_MODAL_ACTION_NOT_SIGNUP_PROOF'
    if evidence['visible_email_inputs'] and not evidence['labeled_visible_inputs']:
        return 'VISIBLE_UNLABELED_INPUT_ACCESSIBILITY_BLOCKER'
    if before['same_page_anchors'] and not before['visible_email_inputs']:
        return 'SAME_PAGE_ANCHOR_ONLY_PENDING_NATIVE_VALIDATION'
    if before['block_count'] == 0:
        return 'NO_SUBSCRIBE_BLOCK_DETECTED'
    return 'NO_VISIBLE_SIGNUP_FORM_VERIFIED'


def inspect_page(page, key: str) -> dict:
    before = snapshot(page, key)
    after = None
    # Only a type=button is safe to click. No submit buttons or links are clicked.
    safe = page.locator('.wp-block-jetpack-subscriptions button[type="button"]')
    if before['visible_email_inputs'] == 0 and safe.count():
        try:
            safe.first.click(timeout=1200)
            page.wait_for_timeout(250)
            after = snapshot(page, key)
        except Exception:
            pass
    return {'page': key, 'status': classify(before, after), 'initial': before,
            'after_safe_button': after, 'source': 'BROWSER_DOM_NOT_PROVIDER_CONSENT',
            'confirmed_signup': None, 'email_eligible': None, 'email_delivered': None}


FIXTURES = {
  'visible_labeled': '<div class="wp-block-jetpack-subscriptions"><form><label>Email<input type="email" /></label><button type="submit">Subscribe</button></form></div>',
  'same_page_only': '<div class="wp-block-jetpack-subscriptions"><a href="/dispatch/">Subscribe</a></div>',
  'safe_modal': '<div class="wp-block-jetpack-subscriptions"><button type="button" onclick="document.getElementById(\'modal\').hidden=false">Show form</button><div id="modal" hidden><label>Email<input type="email"></label></div></div>',
  'no_op_button': '<div class="wp-block-jetpack-subscriptions"><button type="button">Subscribe</button></div>',
  'hidden_email': '<div class="wp-block-jetpack-subscriptions"><form hidden><label>Email<input type="email"></label></form><a href="/focus/">Subscribe</a></div>',
  'no_block': '<main><h1>Subscribe to The Dispatch</h1></main>',
}


def run_fixture() -> dict:
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        try:
            for key, html in FIXTURES.items():
                context = browser.new_context(viewport={'width':390,'height':844}, java_script_enabled=True)
                page = context.new_page()
                page.set_content(html)
                results.append(inspect_page(page, key))
                context.close()
        finally:
            browser.close()
    return {'mode':'OFFLINE_SYNTHETIC_FIXTURE','cases':results, 'live_visitor_verified':False,
            'actual_received_email_verified':False}


def run_live() -> dict:
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        try:
            for key, url in PAGES.items():
                context = browser.new_context(viewport={'width':390,'height':844},
                                              storage_state={'cookies':[],'origins':[]})
                page = context.new_page()
                blocked = {'non_get':0, 'other_host':0}
                def restrict(route):
                    request = route.request
                    if not permitted_get(request.url, request.method):
                        blocked['non_get' if request.method.upper()!='GET' else 'other_host'] += 1
                        route.abort()
                    else:
                        route.continue_()
                page.route('**/*', restrict)
                try:
                    response = page.goto(url,wait_until='domcontentloaded',timeout=15000)
                    code = response.status if response is not None else None
                    if code is None or not (200 <= code < 400):
                        results.append({'page':key,'status':'HTTP_NOT_OK',
                                        'http_status':code,'live_signed_out_dom_observed':False,
                                        'blocked_requests':blocked,'confirmed_signup':None})
                        context.close()
                        continue
                    page.wait_for_timeout(1000)
                    result = inspect_page(page,key)
                    result['http_status'] = code
                    result['live_signed_out_dom_observed'] = True
                    result['blocked_requests'] = blocked
                    results.append(result)
                except Exception as exc:
                    results.append({'page':key,'status':'NOT_TESTED_LIVE',
                                    'reason':type(exc).__name__, 'live_signed_out_dom_observed':False,
                                    'blocked_requests':blocked,'confirmed_signup':None})
                context.close()
        finally:
            browser.close()
    return {'mode':'LIVE_SIGNED_OUT_GET_ONLY','cases':results,
            'submissions':0, 'welcome_messages_sent':0,
            'native_subscription_status_verified':False,
            'actual_received_email_verified':False}


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    mode=ap.add_mutually_exclusive_group(required=True)
    mode.add_argument('--fixture',action='store_true')
    mode.add_argument('--live',action='store_true')
    args=ap.parse_args()
    print(json.dumps(run_fixture() if args.fixture else run_live(),indent=2,sort_keys=True))
