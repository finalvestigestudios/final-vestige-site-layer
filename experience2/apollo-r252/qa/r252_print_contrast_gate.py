#!/usr/bin/env python3
"""R252 staging-only original Atlas print contrast regression (not WCAG certification).

Fails unless the original unpatched PDF demonstrates the known low-contrast
problem and the isolated print override corrects all extracted text colors.
Assumes printed white paper; does not replace browser axe or manual review.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
import fitz
from playwright.sync_api import sync_playwright

MANIFEST='f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68'

def sha(data):return hashlib.sha256(data).hexdigest()
def luminance(color):
    values=[((color>>v)&255)/255 for v in (16,8,0)]
    lin=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in values]
    return .2126*lin[0]+.7152*lin[1]+.0722*lin[2]

def analyze(pdf_bytes):
    doc=fitz.open(stream=pdf_bytes,filetype='pdf')
    issues=[];text=[]
    for num,page in enumerate(doc,1):
        for b in page.get_text('dict')['blocks']:
            for line in b.get('lines',[]):
                for span in line.get('spans',[]):
                    content=span.get('text','').strip()
                    if content:
                        text.append(content)
                        ratio=1.05/(.05+luminance(span['color']))
                        if ratio<4.5:
                            issues.append({'page':num,'text':content[:90],
                                           'ratio':round(ratio,2),'ink':hex(span['color'])})
    return {'pages':len(doc),'failures':issues,'all_text':' '.join(text)}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--atlas',type=Path,required=True)
    p.add_argument('--css',type=Path,default=Path(__file__).resolve().parents[1]/'r252-print-custody.css')
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    manifest=(a.atlas/'manifest.json').read_bytes()
    assert sha(manifest)==MANIFEST, 'original NASA manifest changed'
    for name,expected in json.loads(manifest)['files'].items():
        assert sha((a.atlas/name).read_bytes())==expected,'sealed asset drift: '+name
    cmd=['php',str(a.atlas/'wp-render-shim-r224.php'),str((a.atlas/'fv-ex2-apollo-r224.php').resolve()),'normal']
    html=json.loads(subprocess.check_output(cmd,text=True))['html']
    assert html==(a.atlas/'templates/atlas-fragment.html').read_text()
    base=(a.atlas/'assets/atlas-scoped.css').read_text()
    patch=a.css.read_text()
    assert '@media print' in patch and '.notice strong' in patch
    def render(css):
        doc='<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style></head><body>'+html+'</body></html>'
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
            page=browser.new_page(viewport={'width':390,'height':800})
            page.set_content(doc,wait_until='load');page.emulate_media(media='print')
            pdf=page.pdf(print_background=True,prefer_css_page_size=True)
            browser.close()
        return pdf
    before=analyze(render(base))
    raw=render(base+'\n'+patch)
    after=analyze(raw)
    assert len(before['failures'])>=10,'regression control did not reproduce low-contrast spans'
    assert not after['failures'],'print contrast remains below 4.5: '+str(after['failures'])
    assert after['all_text'].count('nasa.gov')>=8,'print NASA source URLs lost'
    assert 'Archival source and rights index' in after['all_text'],'rights index missing'
    pdf=fitz.open(stream=raw,filetype='pdf')
    metadata=pdf.metadata;metadata.update({'creationDate':"D:20000101000000+00'00'",'modDate':"D:20000101000000+00'00'"})
    pdf.set_metadata(metadata)
    dest=a.out/'apollo-r252-high-contrast-archival-print.pdf'
    pdf.save(dest,garbage=4,deflate=True,no_new_id=1)
    receipt={'result':'PASS','scope':'ORIGINAL_R238_CHROMIUM_PRINT_WHITENED_PAPER_CONTRAST',
             'not_live':True,'sealed_manifest_sha256':MANIFEST,'patch_sha256':sha(a.css.read_bytes()),
             'baseline_low_contrast_spans':len(before['failures']),
             'patched_low_contrast_spans':len(after['failures']),
             'source_urls_visible':after['all_text'].count('nasa.gov'),
             'pages':after['pages'],'pdf_sha256':sha(dest.read_bytes()),
             'limits':'Assumes white printed backgrounds; not genuine axe, WCAG certification, WP or screen reader.'}
    (a.out/'print-contrast-receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(receipt,sort_keys=True))

if __name__=='__main__':main()
