"""Deterministic source/offer contract and adversarial mutation tests.
Does NOT make HTTP requests or claim actual WordPress staging acceptance.
"""
from pathlib import Path
import hashlib, json, re, shutil, subprocess, tempfile
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
ARTICLE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
SOURCE=['training','review-board','memorial','flammability']
FILES=[
 'apollo-r449/journey.php','apollo-r448/manifest.json','apollo-r448/crosswalk.php',
 'apollo-r440/staging-educator-intent.php','apollo-r450/assets/receipt.css','apollo-r450/assets/receipt.js'
]
def render(folder=ROOT, mode='staging'):
    p=subprocess.run(['php',str(folder/'apollo-r450/qa/fixture.php'),mode],capture_output=True,text=True,timeout=25)
    if p.returncode:raise RuntimeError(p.stderr)
    return p.stdout

def validate(html, mode='staging'):
    doc=BeautifulSoup(html,'html.parser')
    links=doc.select('a[href]')
    assert len([a for a in links if a['href']==ARTICLE])==1
    assert not doc.select('form,iframe,script[src],a[href*="payhip"],a[href*="checkout"]')
    assert not doc.select('[data-lat],[data-lon],[data-geo-pin]')
    if mode=='staging':
        assert len(doc.select('[data-fv-r449]'))==1
        assert len(doc.select('[data-fv-r450]'))==1
        assert len(doc.select('[data-fv-r448-card]'))==4
        assert len(doc.select('[data-r440-root]'))==1
        records=doc.select('[data-r450-claim]')
        assert [r['data-r450-claim'] for r in records]==SOURCE
        dates=[r.time['datetime'] for r in records]
        assert dates==['1966-10-18','1967-01-27','2017-01-27','2018-02-14']
        for r in records:
            assert r.select_one('h3') and 'Not established:' in r.text and 'Supported:' in r.text
            assert len(r.select('a[href^="https://www.nasa.gov/"]'))==1
        assert 'editorial review' in doc.select_one('[data-fv-r450]').text.lower()
        assert doc.select_one('[data-fv-r450] details summary')
        assert len(doc.select('[data-r450-export]'))==1
    else:
        assert not doc.select('[data-fv-r450],[data-fv-r449],[data-r450-claim]')

def run():
    results=[]
    for mode in ('staging','production','disabled','other-page'):
        validate(render(mode=mode),mode)
        results.append(f'{mode}: safe render + single CTA')
    duplicate=render(mode='double')
    validate(duplicate,'staging')
    results.append('duplicate shortcode suppresses second CTA')
    html=render()
    sha=hashlib.sha256(html.encode()).hexdigest()
    with tempfile.TemporaryDirectory() as td:
        dst=Path(td)/'experience2'
        dst.mkdir()
        for module in ('apollo-r440','apollo-r448','apollo-r449','apollo-r450'):
            shutil.copytree(ROOT/module,dst/module,ignore=shutil.ignore_patterns('QA','__pycache__'))
        for f in FILES:
            p=dst/f
            original=p.read_bytes()
            p.write_bytes(original+b'\n/* MUTATED SOURCE - MUST FAIL CLOSED TO FREE LINK */\n')
            fallback=render(dst)
            validate(fallback,'hold')
            p.write_bytes(original)
            validate(render(dst),'staging')
            results.append(f'{f}: mutation blocked + restore')
        # Deliberately ensure bad `manifest.json` which retains shape still fails via hash.
        p=dst/'apollo-r448/manifest.json';j=json.loads(p.read_text())
        j['claims'][1]['supported']='Conclusive explosive initiation.'
        p.write_text(json.dumps(j))
        validate(render(dst),'hold')
        results.append('altered NASA claim blocked')
        p.write_bytes((ROOT/'apollo-r448/manifest.json').read_bytes())
        # Exactly one untagged free link in all fail-open renders.
        validate(render(dst),'staging')
        results.append('dependency restoration yields full content')
    evidence={'status':'PASS','mode':'offline PHP fixture with genuine inherited source; NOT WordPress staging',
              'tests':len(results),'checks':results,'fixture_sha256':sha,
              'dependency_sha256':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in FILES},
              'actual_staging':'NOT_RUN','axe_core':'NOT_RUN','lab_LCP_CLS':'NOT_RUN','revenue':'NOT_VERIFIED'}
    path=BASE/'QA';path.mkdir(exist_ok=True)
    (path/'CONTRACT.json').write_text(json.dumps(evidence,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':'PASS','tests':len(results),'fixture_sha256':sha}))
    return 0
if __name__=='__main__':raise SystemExit(run())
