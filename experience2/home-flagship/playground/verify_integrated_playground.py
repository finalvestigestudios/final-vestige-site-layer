#!/usr/bin/env python3
"""FV EX2 actual WordPress/Assembler gated visual and evidence admission.

Read-only. This does NOT install WordPress, mutate a CMS, submit a form, or
certify production hosting. A local isolated WordPress/Playground page URL is
required. Negative tests and fixture checks are NOT staging acceptance.
"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
from urllib.parse import urlparse
from verify_archival_provenance import classify_source, verify_receipt
from request_boundary import admit_request

CHAPTERS = ("fv-hf-title", "fv-hf-chronicle", "fv-hf-evidence",
            "fv-hf-inquiry", "fv-hf-method-title", "fv-hf-observer", "fv-hf-mind-title")
WIDTHS = ((320, 568), (360, 640), (390, 667), (390, 900),
          (768, 900), (1440, 900), (1920, 900))
IMAGES = {"s67-19766.webp": "WEBP", "Franklinexpeditionnote.jpg": "JPEG"}


def admit_url(url, authorized_host=None):
    """Refuse any production/FV host; allow explicit isolated target only."""
    p = urlparse(url)
    host = (p.hostname or "").lower().rstrip(".")
    forbidden = ("finalvestige.com", "www.finalvestige.com",
                 "vestigefinal-tezws.wpcomstaging.com")
    if not host or host in forbidden or host.endswith(".finalvestige.com"):
        raise ValueError("Refusing production or included production alias")
    if p.username or p.password or p.fragment or p.scheme not in ("http", "https"):
        raise ValueError("Invalid preview URL (auth, fragment or scheme)")
    if host in ("127.0.0.1", "localhost", "::1"):
        return url
    if not authorized_host or authorized_host.lower().rstrip(".") != host:
        raise ValueError("Unrecognized staging host: explicitly authorize exact host")
    if p.scheme != "https":
        raise ValueError("Remote isolated preview must use HTTPS")
    return url


def verify_image_bytes(body, expected):
    if len(body) < 1024:
        raise ValueError("Image response too small")
    fmt = ("WEBP" if body[:4] == b"RIFF" and body[8:12] == b"WEBP" else
           "JPEG" if body[:3] == b"\xff\xd8\xff" else None)
    if fmt != expected:
        raise ValueError("HTML, wrong image format, or error response")
    # Decode actual pixels; if PIL unavailable, FAIL rather than paper over it.
    from PIL import Image
    with Image.open(io.BytesIO(body)) as img:
        img.verify()
        dims = img.size
    if min(dims) < 150:
        raise ValueError("Tiny/invalid image dimensions")
    return {"format": fmt, "width": dims[0], "height": dims[1],
            "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest()}


def read_semantics(page):
    return page.evaluate("""() => {
      const root=document.querySelector('[data-fv-home-flagship]');
      const inSite=!!document.querySelector('.wp-site-blocks');
      const tabs=[...document.querySelectorAll('[data-fv-case-button]')];
      const items=[...document.querySelectorAll('.fv-margin-strip__item')];
      const f=[...document.querySelectorAll('a[href="https://finalvestige.com/focus/"]')];
      const img=[...document.querySelectorAll('[data-fv-archive-img]')];
      const ids=%s;
      // Actual first-screen CTA hit targets; read-only, no clicks or signup submissions.
      const focusFirstScreen=f.map(a=>{
        const r=a.getBoundingClientRect(), style=getComputedStyle(a);
        const visible=r.width>=24 && r.height>=24 && r.bottom>0 && r.top<innerHeight &&
          r.right>0 && r.left<innerWidth && style.visibility!=='hidden' &&
          style.display!=='none' && Number(style.opacity)>0 && style.pointerEvents!=='none';
        const x=Math.max(0,Math.min(innerWidth-1,r.left+r.width/2));
        const y=Math.max(0,Math.min(innerHeight-1,r.top+Math.min(r.height/2,22)));
        const hit=visible?document.elementFromPoint(x,y):null;
        return {in_first_screen:!!visible,hit_clear:!!(visible&&hit&&(hit===a||a.contains(hit))),
          width:r.width,height:r.height,label:(a.textContent||'').trim().slice(0,80)};
      });
      return {wordpress_shell:inSite,root:!!root,chapters:ids.map(id=>!!document.getElementById(id)),
        record_count:items.length,focus_links:f.length,focus_first_screen:focusFirstScreen,image_count:img.length,
        archive_sources:img.map(x=>({src:x.getAttribute('src'),current:x.currentSrc,alt:x.getAttribute('alt'),
          complete:x.complete,naturalWidth:x.naturalWidth,loading:x.loading})),
        overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth,
        source_actions:tabs.length,
        has_review_label:!!document.querySelector('.fv-hf__studio-note') && /NOT LIVE/.test(document.querySelector('.fv-hf__studio-note').textContent),
        static_visible:{cases:[...document.querySelectorAll('.fv-hf__case')].every(x=>x.getBoundingClientRect().height>0),
          chronicle:[...document.querySelectorAll('.fv-hf__chronicle-entry')].every(x=>x.getBoundingClientRect().height>0),
          observer:[...document.querySelectorAll('.fv-hf__observer-frame')].every(x=>x.getBoundingClientRect().height>0)},
        title:document.title};
    }""" % json.dumps(list(CHAPTERS)))


def assert_semantics(data, require_wp=True):
    failures=[]
    if require_wp and not data['wordpress_shell']: failures.append('not an actual WordPress shell')
    if not data['root']: failures.append('flagship root missing')
    if len(data['chapters']) != len(CHAPTERS) or not all(data['chapters']):
        failures.append('one or more of seven chapters missing')
    if data['record_count'] != 72: failures.append('72 historical records not preserved')
    if data['focus_links'] < 5: failures.append('Focus Fieldbook navigation incomplete')
    if not any(t.get('in_first_screen') and t.get('hit_clear') for t in data.get('focus_first_screen', [])):
        failures.append('no visible, unobstructed first-screen Focus CTA')
    if data['image_count'] != 2: failures.append('archival image count changed')
    if data['overflow'] > 1: failures.append('document horizontally overflows')
    if not data['has_review_label']: failures.append('unpublished/non-live marker missing')
    if data['source_actions'] != 3: failures.append('three cases missing')
    for image in data['archive_sources']:
        if not image['alt']: failures.append('archival image lacks alt text')
        if not image['src'].startswith('https://finalvestige.com/wp-content/uploads/'):
            failures.append('unapproved editorial image source')
    return failures


def run(url, output, authorized_host, axe_path):
    from playwright.sync_api import sync_playwright
    admit_url(url, authorized_host)
    output.mkdir(parents=True, exist_ok=True)
    report={"scope":"real isolated WordPress rendered page (NOT production parity)",
            "url":url,"checks":[],"failures":[],"axe":"NOT_RUN", "lighthouse":"NOT_RUN",
            "host_specific_cwv":"UNVERIFIED", "subscriber_confirmation":"NOT_TESTED"}
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True, executable_path=os.environ.get('FV_CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox'])
        for width,height in WIDTHS:
            for js in (True,False):
                ctx=browser.new_context(viewport={'width':width,'height':height},java_script_enabled=js,reduced_motion='reduce' if width==390 else 'no-preference')
                page=ctx.new_page(); errors=[]; responses={}
                page.on('pageerror',lambda exc: errors.append(str(exc)))
                # Fail closed on *all* unexpected outbound requests. A staged
                # preview must not call live APIs, merchants, beacons or trackers.
                # Only this isolated WP origin + the two reviewed archive image
                # origins/derivatives are permitted; redirects are rechecked.
                def gate_network(route):
                    req=route.request
                    try:
                        admit_request(req.url, url, navigation=(
                            req.is_navigation_request() and req.frame == page.main_frame))
                    except ValueError as exc:
                        # Do not copy URL query strings (possible tokens) to QA logs.
                        host=urlparse(req.url).hostname or 'opaque'
                        errors.append('blocked unexpected browser request: '+host+
                                      ' ('+str(exc)+')')
                        route.abort()
                        return
                    route.continue_()
                page.route('**/*', gate_network)
                def capture(resp):
                    if any(tag in resp.url for tag in IMAGES):
                        responses[resp.url]=resp
                page.on('response', capture)
                try:
                    page.goto(url,wait_until='domcontentloaded',timeout=20000)
                    page.wait_for_timeout(350)
                    evidence=read_semantics(page)
                    errs=assert_semantics(evidence)
                    if not js and not all(evidence['static_visible'].values()):
                        errs.append('no-JS hides historical entries or observation evidence')
                    errs += [f'JS: {x}' for x in errors]
                    if js:
                        # Actual user input, not merely a DOM text selector.
                        try:
                            page.locator('[data-fv-chronicle-view="original"]').click(timeout=4000)
                            if page.locator('#fv-hf-chronicle').get_attribute('data-fv-chronicle-mode')!='original':
                                errs.append('original chronicle interaction failed')
                            page.locator('[data-fv-chronicle-view="both"]').click(timeout=4000)
                            page.locator('[data-fv-case-button="franklin"]').click(timeout=4000)
                            if page.locator('[data-fv-case="franklin"]').is_hidden():
                                errs.append('Franklin interactive case inaccessible')
                            page.locator('[data-fv-observer-switch="b"]').click(timeout=4000)
                            if page.locator('[data-fv-observer-switch="b"]').get_attribute('aria-pressed')!='true':
                                errs.append('observation interaction failed')
                            if width == 390:
                                if page.locator('.fv-margin-strip__motion-toggle').is_visible():
                                    errs.append('reduced-motion control should not offer animation')
                                if page.locator('.fv-margin-strip__item:visible').count() != 72:
                                    errs.append('reduced-motion hides historical records')
                            else:
                                page.locator('.fv-margin-strip__motion-check').check(timeout=4000)
                                if not page.locator('.fv-margin-strip__motion-check').is_checked():
                                    errs.append('voluntary animation toggle failed')
                        except Exception as e: errs.append('interaction: '+str(e)[:180])
                        # Scroll lazy-loaded evidence onto the stage. Confirm actual RESPONSE BYTES,
                        # not image metadata or cached CSS status.
                        for index in range(2):
                            img=page.locator('[data-fv-archive-img]').nth(index)
                            try:
                                img.scroll_into_view_if_needed(timeout=6000)
                                img.evaluate('el=>el.loading="eager"')
                                page.wait_for_timeout(1000)
                                current=img.evaluate('x=>x.currentSrc || x.src')
                                matching=next((r for u,r in responses.items() if u==current),None)
                                if not matching:
                                    errs.append(f'archive {index}: no observed network response for {current}')
                                else:
                                    body=matching.body()
                                    approved=classify_source(img.get_attribute('src'),current,index)
                                    decoded=verify_image_bytes(body,approved['format'])
                                    receipt=verify_receipt(approved,decoded,matching.status,
                                                           matching.headers.get('content-type',''))
                                    evidence.setdefault('transfer',[]).append(receipt)
                            except Exception as e: errs.append(f'archive {index} bytes: {str(e)[:170]}')
                    if axe_path and width in (390,1440) and js:
                        try:
                            page.add_script_tag(path=str(axe_path))
                            ax=page.evaluate('async()=>await axe.run(document,{runOnly:{type:"tag",values:["wcag2a","wcag2aa","wcag21a","wcag21aa","wcag22aa"]}})')
                            report['axe'] = 'EXECUTED'
                            evidence['axe_violations']=[{'id':v['id'],'impact':v['impact'],'count':len(v['nodes'])} for v in ax['violations']]
                            if ax['violations']:errs.append('axe WCAG violations')
                        except Exception as e:errs.append('axe unable to execute: '+str(e)[:130])
                    stem=f'{width}x{height}_{"js" if js else "nojs"}'
                    page.screenshot(path=str(output/(stem+'.png')),full_page=(width==390 and js),animations='disabled')
                    if width in (390,1440) and js:
                        page.evaluate("document.documentElement.style.zoom='2'")
                        zoom=page.evaluate('document.documentElement.scrollWidth-document.documentElement.clientWidth')
                        evidence['zoom_200_overflow']=zoom
                        if zoom>1:errs.append('200% CSS zoom horizontal overflow: '+str(zoom))
                        page.screenshot(path=str(output/(stem+'_zoom200.png')),animations='disabled')
                    report['checks'].append({'scenario':stem,'pass':not errs,'errors':errs,'observations':evidence})
                    report['failures'] += [stem+': '+x for x in errs]
                except Exception as e:report['failures'].append(f'{width}x{height} {js}: {str(e)[:280]}')
                finally:ctx.close()
        browser.close()
    if not axe_path: report['failures'].append('axe-core bundle absent: WCAG gate CLOSED')
    report['failures'].append('Lighthouse/CWV not measured: release gate CLOSED')
    (output/'admission.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({'scenarios':len(report['checks']),'failures':len(report['failures']),
                      'axe':report['axe'],'receipt':str(output/'admission.json')},indent=2))
    return 1 if report['failures'] else 0


def self_test():
    from PIL import Image
    checks=[]
    for u in ['https://finalvestige.com/','https://a.finalvestige.com/','https://vestigefinal-tezws.wpcomstaging.com/','file:///tmp/f','http://evil.example/']:
        try: admit_url(u)
        except ValueError:checks.append(True)
        else:checks.append(False)
    checks.extend([admit_url('http://127.0.0.1:8899/fv-ex2-review/') is not None,
                   admit_url('https://playground.wordpress.net/', 'playground.wordpress.net') is not None])
    try: admit_url('http://evil.example/', 'evil.example')
    except ValueError:checks.append(True)
    else:checks.append(False)
    for fmt in ('WEBP','JPEG'):
        b=io.BytesIO()
        sample=Image.new('RGB',(360,360))
        sample.putdata([((x*3+y*11)%256,(x*13+y*7)%256,(x*17+y*5)%256) for y in range(360) for x in range(360)])
        sample.save(b,format=fmt)
        try: v=verify_image_bytes(b.getvalue(),fmt);checks.append(v['width']==360)
        except ValueError:checks.append(False)
        try:verify_image_bytes(b'<!doctype html><html>'*60,fmt)
        except ValueError:checks.append(True)
        else:checks.append(False)
    model={'wordpress_shell':True,'root':True,'chapters':[True]*7,'record_count':72,
           'focus_links':5,'focus_first_screen':[{'in_first_screen':True,'hit_clear':True}],
           'image_count':2,'overflow':0,'has_review_label':True,
           'source_actions':3,'archive_sources':[{'src':'https://finalvestige.com/wp-content/uploads/a.webp','alt':'A'},
           {'src':'https://finalvestige.com/wp-content/uploads/b.jpg','alt':'B'}]}
    checks.append(assert_semantics(model)==[])
    for focus in ([],[{'in_first_screen':True,'hit_clear':False}],
                  [{'in_first_screen':False,'hit_clear':True}]):
        checks.append(any('unobstructed first-screen Focus CTA' in f for f in
                          assert_semantics({**model,'focus_first_screen':focus})))
    for key,val in [('record_count',71),('focus_links',4),('wordpress_shell',False),('has_review_label',False),('overflow',12),('image_count',3),('source_actions',2)]:
        m={**model,key:val};checks.append(bool(assert_semantics(m)))
    print(json.dumps({'selftest_pass':sum(checks),'total':len(checks),'staging_run':False},indent=2))
    return 0 if all(checks) else 1


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--url',help='EXPLICIT ISOLATED WordPress/Assembler review URL')
    ap.add_argument('--authorized-host',help='Exact known isolated HTTPS preview hostname')
    ap.add_argument('--axe',type=Path,help='Local official axe-core bundle; missing means HOLD')
    ap.add_argument('--output',type=Path,default=Path('fv-ex2-staging-admission'))
    ap.add_argument('--selftest',action='store_true')
    args=ap.parse_args()
    if args.selftest: raise SystemExit(self_test())
    if not args.url: ap.error('--url is required for genuine staging admission')
    raise SystemExit(run(args.url,args.output,args.authorized_host,args.axe))
