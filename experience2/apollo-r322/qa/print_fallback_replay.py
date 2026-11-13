#!/usr/bin/env python3
"""R322 source-controlled replay gate. Offline Chromium; NOT installed WordPress."""
import hashlib, json, subprocess
from pathlib import Path
from urllib.parse import parse_qsl,urlsplit
import tinycss2
from playwright.sync_api import sync_playwright
from pypdf import PdfReader

BASE=Path(__file__).resolve().parents[2]
PHP=BASE/'apollo-r281/apollo-source-experience.php'
CSS=BASE/'apollo-r281/assets/apollo-source-experience.css'
JS=BASE/'apollo-r281/assets/apollo-cache-continuation.js'
STUB=BASE/'apollo-r320/qa/wp_late_shortcodes.php'
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
QUERY='utm_source=youtube&utm_medium=organic_social&utm_campaign=history_pilot_2026_11&utm_content=apollo1_yt_longform001'
EXPECTED_CSS='2c6b72cab4860f9eec36fb3ea206ffa8973e438e60321e98e8eb91fae190764c'
def blob(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()

def guarded(source):
    hidden=[]
    def walk(rules, parents=()):
        for r in rules:
            if r.type=='at-rule' and r.content is not None:
                walk(tinycss2.parse_rule_list(r.content,skip_whitespace=True,skip_comments=True),
                     parents+((r.lower_at_keyword,tinycss2.serialize(r.prelude).replace(' ','')),))
            elif r.type=='qualified-rule':
                selector=tinycss2.serialize(r.prelude)
                decls=tinycss2.parse_declaration_list(r.content,skip_whitespace=True,skip_comments=True)
                if 'summary' in selector and any(d.type=='declaration' and d.lower_name=='display'
                        and tinycss2.serialize(d.value).strip()=='none' for d in decls) and
                        any(t=='media' and 'print' in p for t,p in parents):
                    if '.fv-r281' in selector:
                        hidden.append((selector,any(t=='supports' and 'selector(details::details-content)' in p
                              for t,p in parents)))
    walk(tinycss2.parse_stylesheet(source,skip_whitespace=True,skip_comments=True))
    assert len(hidden)>=2 and all(allowed for _,allowed in hidden),hidden
    for required in ('fv-r281__drawer','fv-r291__authority-disclosure','fv-r296__date-disclosure'):
        assert any(required in selector for selector,_ in hidden),required
    assert '.fv-r281 details.fv-r291__authority-disclosure::details-content' in source
    assert '.fv-r281 details.fv-r296__date-disclosure::details-content' in source
    return len(hidden)

def fixture():
    raw=subprocess.check_output(['php',str(STUB),'late-dynamic','2'],text=True)
    doc,meta=raw.split('<!--R320_QUEUE:')
    assert json.loads(meta.split('-->')[0])['calls']==1
    return doc.replace('</head>','<style>'+CSS.read_text()+'</style></head>')

def replay():
    subprocess.run(['php','-l',str(PHP)],check=True,stdout=subprocess.DEVNULL)
    subprocess.run(['node','--check',str(JS)],check=True,stdout=subprocess.DEVNULL)
    assert blob(PHP.read_bytes())=='c17c7ffb385905b47315631ad49cc7ada96bf7f4'
    assert blob(JS.read_bytes())=='a3c858b51005495ebebb326086badc155c1b7e5a'
    assert hashlib.sha256(CSS.read_bytes()).hexdigest()==EXPECTED_CSS
    assert 'r322-'+EXPECTED_CSS[:12] in PHP.read_text()
    count=guarded(CSS.read_text())
    bad=CSS.read_text()+'\n@media print{.fv-r281 .fv-r291__authority-disclosure>summary{display:none!important}}'
    try: guarded(bad)
    except AssertionError: pass
    else: raise AssertionError('R321 print fallback regression undetected')
    cases=0;pdfs=0
    with sync_playwright() as play:
        b=play.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        try:
            for width in (320,390,1440):
                for mode in ('js','nojs','forced'):
                    ctx=b.new_context(viewport={'width':width,'height':900},
                       java_script_enabled=mode!='nojs',
                       forced_colors='active' if mode=='forced' else 'none',
                       reduced_motion='reduce',has_touch=width<=390)
                    page=ctx.new_page()
                    page.goto('about:blank?'+QUERY)
                    page.set_content(fixture())
                    if mode!='nojs':page.add_script_tag(content=JS.read_text())
                    assert page.locator('section.fv-r281').count()==2
                    assert page.locator('section.fv-r281 details').count()==14
                    assert page.locator('a[data-fv-cta]').count()==2
                    assert page.locator('[data-fv-media-record]').count()==8
                    assert page.locator('img,canvas,iframe,[data-latitude],[data-longitude]').count()==0
                    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
                    assert page.locator('section.fv-r281 a[data-fv-cta]').first.get_attribute('href')==FREE
                    if width==390 and mode=='nojs':
                        assert page.locator('section.fv-r281 details[open]').count()==0
                        page.emulate_media(media='print')
                        data=page.pdf(format='A4',print_background=True)
                        from io import BytesIO
                        text='\n'.join(p.extract_text() or '' for p in PdfReader(BytesIO(data)).pages)
                        for token in ('Custodian: NASA','January 27','January 28','January 31',
                                      'February 3','Source relationship:','S67-21294'):
                            assert token in text,token
                        for token in ('Inspect all four dated Board authority records',
                                      'Compare all three NASA source descriptions'):
                            assert token not in text,token
                        pdfs+=1
                        page.emulate_media(media='screen')
                    a=page.locator('.fv-r281__authority-jump a').first
                    a.click()
                    target=page.locator(a.get_attribute('href'))
                    assert target.is_visible() and target.evaluate('(e)=>e===document.activeElement')
                    assert target.evaluate('(e)=>e.closest("details").open')
                    cta=page.locator('section.fv-r281 a[data-fv-cta]').first
                    cta.focus()
                    page.keyboard.press('Shift+F10')
                    if mode!='nojs':
                        assert dict(parse_qsl(urlsplit(cta.get_attribute('href')).query))==dict(parse_qsl(QUERY))
                    else:assert cta.get_attribute('href')==FREE
                    assert page.locator('section.fv-r281 a[data-fv-cta]').nth(1).get_attribute('href')==FREE
                    cases+=1
                    ctx.close()
        finally:b.close()
    print(json.dumps({'source_controlled_replay_pass':cases,
      'actual_print_pdf_pass':pdfs,'print_summary_rule_groups':count,
      'R321_negative_control':'rejected','installed_WordPress':'NOT VERIFIED',
      'axe_core':'NOT EXECUTED'},sort_keys=True))
if __name__=='__main__':replay()
