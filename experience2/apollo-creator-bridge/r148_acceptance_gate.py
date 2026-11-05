#!/usr/bin/env python3
"""Apollo R148: fail-closed, read-only offline evidence-acceptance gate.

No direct WordPress/HTTP navigation, publication, payment or analytics actions.
Validates an R147 review receipt before invoking R146 browser checks, then adds
keyboard, no-JS and reduced-motion browser checks and screenshot custody.
Only a real raw-Gutenberg export with its independently validated R147 receipt
can enter the production-provenance track. Even a green offline run is NOT a
live WordPress or CWV acceptance.
"""
import argparse, hashlib, json, os, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
import r146_offline_browser_acceptance as base

PINNED_REVIEW_SHA='39dd5adcfe1a4ad1d501a1a94d760b1037111a487908698e649ecaa5103334e7'
EXACT_WIDTHS=(320,360,390,768,1440,1920)
ACTION='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'

def sha(data):return hashlib.sha256(data).hexdigest()

def validate_snapshot(html, receipt, synthetic=False):
    issues=[]
    actual=sha(html.encode('utf8'))
    if not isinstance(receipt,dict):return ['R147_RECEIPT_ABSENT']
    if receipt.get('release')!='STAGING_HOLD' or receipt.get('approved_to_publish') is not False:
        issues.append('UNAUTHORIZED_RELEASE_RECEIPT')
    if receipt.get('status')!='SOURCE_SNAPSHOT_MATCH_OFFLINE_QA_PENDING':
        issues.append('R147_SOURCE_GATE_NOT_PASSED')
    if actual!=receipt.get('review_sha256'):
        issues.append('REVIEW_EXPORT_HASH_MISMATCH')
    if len(html)!=receipt.get('review_characters'):
        issues.append('REVIEW_EXPORT_LENGTH_MISMATCH')
    if receipt.get('source_scope')!='RAW_GUTENBERG_CONTENT_NOT_RENDERED_WORDPRESS_THEME':
        issues.append('WP_SOURCE_SCOPE_MISMATCH')
    if receipt.get('network')!='NOT_USED' or receipt.get('browser')!='NOT_EXECUTED':
        issues.append('SPOOFED_EXECUTION_RECEIPT')
    wp=receipt.get('wordpress') or {}
    if not synthetic:
        if actual!=PINNED_REVIEW_SHA:issues.append('PINNED_WP_EXPORT_NOT_MATCHED')
        if wp.get('id')!=2017 or wp.get('link')!='https://finalvestige.com/apollo-1-evidence-atlas/':
            issues.append('WP_RECORD_NOT_MATCHED')
    return issues

def review_browser(html, out):
    checks=[]; artifacts=[]
    def record(width, name, ok, detail=''):
        checks.append({'width':width,'name':name,'pass':bool(ok),'detail':str(detail)[:160]})
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True,executable_path=os.environ.get('FV_CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox'])
        try:
            for width in EXACT_WIDTHS:
                for js in (True,False):
                    ctx,page=base.local_page(b,width,js=js,touch=(width==390),reduce=True)
                    try:
                        page.set_content(html,wait_until='domcontentloaded',timeout=15000)
                        figures=page.locator('[data-fvx-chrono-gallery] [data-fvx-chrono-photo]')
                        record(width,f'figures_3_js_{js}',figures.count()==3)
                        cta=page.get_by_role('link',name='Read the full investigation',exact=True)
                        record(width,f'cta_present_js_{js}',cta.count()==1 and cta.is_visible())
                        if cta.count()==1:
                            record(width,f'cta_correct_destination_js_{js}',cta.get_attribute('href')==ACTION)
                            cta.focus()
                            record(width,f'cta_keyboard_focus_js_{js}',cta.evaluate('(e)=>document.activeElement===e'))
                        if not js:
                            record(width,'all_archival_context_visible_without_js',figures.count()==3 and all(figures.nth(i).is_visible() for i in range(3)))
                        else:
                            slider=page.locator('[data-fvx-chrono-tool] input[type=range]')
                            record(width,'range_accessible_name',slider.count()==1 and bool(slider.get_attribute('id')) and page.locator('label[for="'+(slider.get_attribute('id') or '')+'"]').count()==1)
                            record(width,'reduced_motion_enabled',page.evaluate('matchMedia("(prefers-reduced-motion: reduce)").matches'))
                        record(width,f'no_horizontal_overflow_js_{js}',page.evaluate('document.documentElement.scrollWidth <= innerWidth + 2'))
                        f=out/f'r148-{width}-{"js" if js else "nojs"}.png'
                        page.screenshot(path=str(f),full_page=True,animations='disabled',timeout=20000)
                        artifacts.append({'file':f.name,'sha256':sha(f.read_bytes()),'width':width,'js':js})
                    except Exception as e:
                        record(width,f'browser_js_{js}',False,e)
                    finally:ctx.close()
        finally:b.close()
    return checks,artifacts

def run(html, receipt, out, axe_source=None, synthetic=False):
    out.mkdir(parents=True,exist_ok=False)
    record={'schema':'fv.apollo.r148.offline-acceptance.v1','release':'STAGING_HOLD',
            'approved_to_publish':False,'published_browser':'NOT_TESTED',
            'production_lcp_cls':'NOT_MEASURED','paid_order':'NOT_OBSERVED',
            'commercial_image_rights':'NOT_CLEARED','input_sha256':sha(html.encode()),
            'source_scope':'SYNTHETIC_FIXTURE' if synthetic else 'PINNED_RAW_WORDPRESS_EXPORT',
            'axe':'NOT_EXECUTED' if not axe_source else 'OFFLINE_ONLY',
            'checks':[],'screenshots':[]}
    failures=validate_snapshot(html,receipt,synthetic)
    for reason in failures:record['checks'].append({'name':reason,'pass':False,'width':0})
    if failures:record['status']='SOURCE_HOLD'
    else:
        bresult=base.run(html,out/'r146-browser',axe_source)
        record['r146_status']=bresult['status']
        record['r146_sha256']=sha((out/'r146-browser'/'r146_receipt.json').read_bytes())
        record['checks'] += [{'name':'R146_'+e['name'],'pass':e['pass'],'width':e['width']} for e in bresult['checks']]
        record['screenshots'] += [{'file':'r146-browser/'+a['file'],'sha256':a['sha256']} for a in bresult['screenshots']]
        extra,screens=review_browser(html,out)
        record['checks'] += extra
        record['screenshots'] += screens
        for item in record['screenshots']:
            if sha((out/item['file']).read_bytes())!=item['sha256']:
                record['checks'].append({'name':'SCREENSHOT_DIGEST_MISMATCH','pass':False,'width':0})
        # Offline functionality is testable. Accessibility acceptance requires
        # actual axe-core; neither test can establish production CWV.
        if not axe_source:record['checks'].append({'name':'AXE_CORE_NOT_SUPPLIED','pass':False,'width':0})
        record['status']='OFFLINE_QA_INCOMPLETE' if any(not c['pass'] for c in record['checks']) else 'OFFLINE_QA_PASS_STAGING_HOLD'
    (out/'r148_receipt.json').write_text(json.dumps(record,sort_keys=True,indent=2)+'\n')
    return record

def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--input',required=True,type=Path)
    a.add_argument('--r147-receipt',required=True,type=Path)
    a.add_argument('--out',required=True,type=Path)
    a.add_argument('--axe-js',type=Path)
    z=a.parse_args()
    if not z.input.is_file() or not z.r147_receipt.is_file() or (z.axe_js and not z.axe_js.is_file()):a.error('inputs and optional axe script must exist')
    try:
        result=run(z.input.read_text(),json.loads(z.r147_receipt.read_text()),z.out,
                   z.axe_js.read_text() if z.axe_js else None)
        print(json.dumps({'status':result['status'],'passed':sum(c['pass'] for c in result['checks']),
                          'failed':sum(not c['pass'] for c in result['checks']),'out':str(z.out)}))
        return 0 if result['status']=='OFFLINE_QA_PASS_STAGING_HOLD' else 2
    except Exception as e:
        print('STAGING_HOLD: '+str(e),file=sys.stderr);return 2
if __name__=='__main__':sys.exit(main())
