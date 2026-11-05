#!/usr/bin/env python3
"""Read-only actual-visitor Focus signup gate. NO email entry, submission, cookies, CMS writes.

This is a separate guest-render gate, not the WordPress editor's preview gate.
Synthetic fixture success is NOT live signup or email-delivery verification.
"""
from __future__ import annotations
import argparse, json, shutil
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright

LANDING = 'https://finalvestige.com/focus/'
WIDTHS = (320, 390, 768, 1440)


def examine(page):
    """Check the rendered DOM, never collect visitor information."""
    return page.evaluate('''() => {
      const root=document.querySelector('.fv-focus');
      const block=root && root.querySelector('.wp-block-jetpack-subscriptions');
      const email=block && block.querySelector('input[type="email"]');
      const form=email && email.closest('form');
      const submit=form && form.querySelector('button[type="submit"], input[type="submit"]');
      const er=email && email.getBoundingClientRect();
      const sr=submit && submit.getBoundingClientRect();
      const style=el=>el && getComputedStyle(el);
      const displayed=el=>!!el && !!el.getClientRects().length &&
        !el.hidden && !el.closest('[hidden], [inert]') &&
        style(el).visibility!=='hidden' && +style(el).opacity>0;
      const links=block?[...block.querySelectorAll('a[href]')]:[];
      const selfLink=links.some(a=>{try {
         const url=new URL(a.href,location.href);
         return url.origin===location.origin && (url.pathname==='/focus/' ||
                url.searchParams.get('p')==='1579');
      } catch(e){return false;}});
      const missingForm=!!block && !form;
      const hasForm=!!form && displayed(email) && displayed(submit);
      const hasLabel=!!email && (email.labels.length>0 || !!email.getAttribute('aria-label') ||
         !!email.getAttribute('aria-labelledby'));
      return {focus_root:!!root, jetpack_block:!!block, guest_email_form:hasForm,
        email_label:hasLabel, email_height:er?er.height:0, submit_height:sr?sr.height:0,
        missing_form:missingForm, fallback_self_link:selfLink,
        no_horizontal_overflow:document.documentElement.scrollWidth<=innerWidth+1,
        email_is_empty:email?email.value==='':null};
    }''')


def grade(m):
    """Fail closed for a *rendered* guest form, never infer subscriber delivery."""
    rules = {
      'focus_root': m['focus_root'],
      'jetpack_block': m['jetpack_block'],
      'guest_email_form': m['guest_email_form'],
      'labelled_email': m['email_label'],
      'email_touch_height_44px': m['email_height'] >= 44,
      'submit_touch_height_44px': m['submit_height'] >= 44,
      'no_self_link_only_fallback': not (m['missing_form'] and m['fallback_self_link']),
      'no_horizontal_overflow': m['no_horizontal_overflow'],
      'no_existing_email_data': m['email_is_empty'] is True,
    }
    return {k:bool(v) for k,v in rules.items()}


def run(url, output, offline_html=None, widths=WIDTHS):
    output=Path(output); output.mkdir(parents=True,exist_ok=True)
    if offline_html is None:
        parts=urlsplit(url)
        if parts.scheme!='https' or parts.netloc!='finalvestige.com' or parts.path!='/focus/' or parts.query or parts.fragment:
            raise ValueError('Only read-only exact public Focus URL allowed')
    results=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=shutil.which('chromium') or None,args=['--no-sandbox'])
        for width in widths:
            context=browser.new_context(viewport={'width':width,'height':900},
                                        reduced_motion='reduce',service_workers='block')
            page=context.new_page()
            try:
                if offline_html is not None:
                    page.route('**/*',lambda route:route.abort())
                    page.set_content(offline_html,wait_until='domcontentloaded')
                else:
                    response=page.goto(url,wait_until='networkidle',timeout=30000)
                    if response is None or response.status != 200:
                        raise RuntimeError('Landing did not return HTTP 200')
                m=examine(page); checks=grade(m)
                if width in (390,1440):
                    page.screenshot(path=str(output/f'guest-focus-{width}.png'),full_page=False)
                results.append({'width':width,'checks':checks,'pass':all(checks.values()),
                                'markers':m})
            except Exception as exc:
                results.append({'width':width,'checks':{},'pass':False,
                                'error':type(exc).__name__+': '+str(exc)[:180]})
            finally:
                context.close()
        browser.close()
    (output/'result.json').write_text(json.dumps({
        'scope':'read-only Focus guest visual gate; no signup attempt',
        'url':'offline synthetic fixture' if offline_html else url,
        'results':results},indent=2))
    return results


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live-guest',action='store_true',
                        help='Opt in to READ-ONLY public Focus check; never submit a form')
    parser.add_argument('--fixture-file',type=Path)
    parser.add_argument('--output',type=Path,default=Path('/tmp/fv-focus-guest-gate'))
    args=parser.parse_args()
    if args.live_guest==bool(args.fixture_file):
        parser.error('Choose exactly one of --live-guest or --fixture-file')
    html=args.fixture_file.read_text() if args.fixture_file else None
    results=run(LANDING,args.output,offline_html=html)
    for r in results:
        print(r['width'],'PASS' if r['pass'] else 'FAIL',
              [k for k,v in r['checks'].items() if not v],r.get('error',''))
    raise SystemExit(0 if all(r['pass'] for r in results) else 1)

if __name__=='__main__':
    main()
