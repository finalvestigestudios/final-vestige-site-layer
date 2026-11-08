#!/usr/bin/env python3
"""R215 real local PHP/Playwright evidence, without claiming installed WP, axe or field metrics."""
import hashlib,json,os,subprocess,sys,tempfile,shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

D=Path(__file__).resolve().parents[1]/'dist'
BUILD=Path(__file__).resolve().parents[1]/'build_r215.py'
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ok(v,msg):
    if not v: raise AssertionError(msg)
def php(mode):
    return json.loads(subprocess.check_output(['php',str(D/'wp-render-shim-r215.php'),str(D/'fv-ex2-apollo-r215.php'),mode],text=True))
def run(out):
    out.mkdir(exist_ok=True,parents=True)
    manifest=json.loads((D/'manifest.json').read_text());ok(manifest['release']=='r215','Wrong release')
    ok(not (D/'assets/campaign-handoff.js').exists(), 'Dormant campaign script was packaged')
    sys.path.insert(0,str(D.parent))
    from build_r215 import audit_html
    custody=audit_html((D/'templates/atlas-fragment.html').read_bytes())
    ok(custody['single_free_cta']==FREE and custody['active_scripts']==0,'Evidentiary link custody')
    mutants=[(b'class="cta"',b'class="cta" href="https://fake.invalid"'),
             (b'href="#fv-apollo-chronology"',b'href="#missing"'),
             (b'href="https://www.nasa.gov/',b'href="https://nasa.gov.evil.invalid/'),
             (b'<article ',b'<article data-lat="1" '),
             (b'<article ',b'<article ><img src="https://nasa.gov.evil.invalid/photo" alt="x">'),
             (b'<article ',b'<article ><script>track()</script>'),
             (b'id="fv-apollo-page-title"',b'id="duplicate-title"'),
             (b'1967-01-27',b'1967-01-26'),
             (b'class="cta"',b'class="other"'),
             (b'<article ',b'<article ><a href="javascript:alert(1)">bad</a>') ]
    raw=(D/'templates/atlas-fragment.html').read_bytes()
    caught=0
    for src,dst in mutants:
        ok(src in raw,'Mutation anchor absent '+str(src))
        try:audit_html(raw.replace(src,dst,1))
        except ValueError:caught+=1
    ok(caught==len(mutants), 'Evidentiary mutations not caught: '+str(caught))
    for name,dig in manifest['files'].items():ok(sha(D/name)==dig,'Tampered '+name)
    for flag in ['script_shipped','approved_purchase_offer','upstream_R198_reconciled','axe_core_accepted','installed_WordPress_accepted']:
        ok(manifest[flag] is False,'Unsafe release flag '+flag)
    ok(subprocess.run(['php','-l',str(D/'fv-ex2-apollo-r215.php')],capture_output=True).returncode==0,'PHP syntax')
    normal,late,printed=[php(x) for x in ['normal','late','printed']]
    ok(normal['css']=='enqueued' and normal['js'] is False and not normal['fallback'],'No script in staged artifact')
    ok(printed['css']=='done' and printed['js'] is False and not printed['fallback'],'Print must not load JS')
    ok(late['fallback'] and late['js'] is False and FREE in late['html'],'Late fail-open')
    html=normal['html'];ok(html.count('class="cta"')==1 and html.count(FREE)==1,'Exactly one free CTA')
    ok(html.count('href="#fv-apollo-reading-bridge"')==2,'Single nav and footer return')
    ok('data-lat=' not in html and 'data-lng=' not in html,'No invented map pins')
    gate=json.loads((D/'attribution-release-gate.json').read_text());ok(gate['state']=='DENY' and not gate['script_enqueued'],'False attribution cannot pass')
    stylesheet=(D/'assets/atlas-scoped.css').read_text()
    cases=[('320',320,{}),('360',360,{}),('390',390,{}),('768',768,{}),('1440',1440,{}),('1920',1920,{}),
           ('no-js',390,{'java_script_enabled':False}),('touch',390,{'is_mobile':True,'has_touch':True}),
           ('reduced',390,{'reduced_motion':'reduce'}),('forced',390,{'forced_colors':'active'}),
           ('css-zoom',768,{'zoom':2})]
    entries=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for label,width,opts in cases:
            config={key:val for key,val in opts.items() if key!='zoom'}
            ctx=browser.new_context(viewport={'width':width,'height':850},**config)
            page=ctx.new_page(); errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            content=f'<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>{stylesheet}</style></head><body>{html}</body></html>'
            page.set_content(content)
            if opts.get('zoom'):page.locator('.fv-apollo-atlas').evaluate('(el)=>{el.style.zoom="200%"}')
            page.screenshot(path=str(out/(label+'.png')),full_page=True,animations='disabled')
            ok(not errors,'Browser error '+label)
            ok(page.evaluate('document.documentElement.scrollWidth<=document.documentElement.clientWidth+1'),'Horizontal overflow '+label)
            nav=page.locator('.fv-apollo-atlas .mast a[href="#fv-apollo-reading-bridge"]');ok(nav.count()==1,'Nav missing '+label)
            nav.focus();page.keyboard.press('Enter');ok(page.evaluate('location.hash')=='#fv-apollo-reading-bridge','Keyboard nav '+label)
            dest=page.locator('.fv-apollo-reading-bridge .cta');ok(dest.count()==1 and dest.get_attribute('href')==FREE,'Link changed '+label)
            ok(page.locator('.fv-apollo-nav-read-note').count()==1,'Accessible context missing')
            if opts.get('has_touch'):
                nav.tap();ok(page.evaluate('location.hash')=='#fv-apollo-reading-bridge','Touch nav')
            if label=='no-js':
                ok(dest.is_visible(),'No-JS CTA missing')
                detail=page.locator('.fv-apollo-atlas details').first
                detail.locator('summary').click();ok(detail.get_attribute('open') is not None,'No-JS disclosure failed')
            if label=='forced':ok(page.locator('.fv-apollo-reading-bridge').is_visible(),'Forced-color CTA missing')
            # Fixture observer: only labels as local; excludes excluded true JS-disabled and print.
            perf=None
            if 'java_script_enabled' not in config:
                perf=page.evaluate("""() => ({cls: window.__cls||0, bodyHeight:document.body.scrollHeight})""")
            entries.append({'context':label,'width':width,'sha256':sha(out/(label+'.png')),'local_fixture_observation':perf})
            ctx.close()
        ctx=browser.new_context();page=ctx.new_page();page.set_content(f'<style>{stylesheet}</style>'+html);page.emulate_media(media='print')
        ok(page.locator('.fv-apollo-lesson-key>div p').first.is_visible(),'Closed answer hidden in print');ctx.close()
        browser.close()
    # Actual altered parent files must fail closed, before any generated outputs are written.
    with tempfile.TemporaryDirectory() as tmp:
        base=Path(tmp)/'ancestor';shutil.copytree(D.parents[1]/'r214'/'dist',base)
        targets=[('templates/atlas-fragment.html',b'class="cta"',b'class="paid-cta"'),
                 ('fv-ex2-apollo-r214.php',b'return false;',b'return true;'),
                 ('assets/atlas-scoped.css',b'@media',b'@fake'),
                 ('attribution-release-gate.json',b'"state": "DENY"',b'"state": "ALLOW"'),
                 ('source-records.json',b'https://www.nasa.gov',b'https://fake-nasa.invalid'),
                 ('manifest.json',b'"approved_purchase_offer": false',b'"approved_purchase_offer": true')]
        for path,src,dst in targets:
            f=base/path;raw=f.read_bytes();ok(src in raw,'Mutation anchor not found '+path)
            f.write_bytes(raw.replace(src,dst,1));env=os.environ.copy();env['FV_APOLLO_R214_DIST']=str(base)
            p=subprocess.run([sys.executable,str(BUILD)],env=env,capture_output=True,text=True)
            ok(p.returncode!=0,'Adversarial mutation accepted: '+path);f.write_bytes(raw)
    receipt={'status':'LOCAL_BROWSER_AND_PHP_PASS','chromium':'system /usr/bin/chromium',
             'contexts':entries,'adversarial_mutations_rejected':len(targets), 'semantic_html_mutations_rejected':caught,
             'axe_core':'NOT_EXECUTED','installed_wordpress':'NOT_TESTED','real_browser_navigation':'NOT_TESTED',
             'true_browser_zoom':'NOT_TESTED','cls_lcp':'NOT_FIELD_METRICS',
             'published_grok_asset_id':None,'verified_orders':None,'realized_net_revenue':None}
    (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print('R215 PASS: PHP; script removed; 11 Chromium contexts; evidence links/ARIA; build+semantic mutations; print; one free CTA')
if __name__=='__main__':run(Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/apollo-r215-qa'))
