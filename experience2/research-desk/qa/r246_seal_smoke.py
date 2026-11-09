#!/usr/bin/env python3
"""Staging-only Research Desk source-seal checks; --fixture is NOT NASA-template acceptance."""
import argparse,hashlib,json,subprocess,tempfile
from pathlib import Path
from bs4 import BeautifulSoup
from r243_core import SHIM
BLOB='403d128c57b9bc82dac7c619651689070edef86c'
APOLLO='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
def git_blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--fixture',action='store_true');a=ap.parse_args()
    root=a.source;plugin=(root/'final-vestige-ex2-research-desk.php').read_text()
    assert BLOB in plugin,'Protected NASA source guard missing'
    if a.fixture:
        template=('<section data-fvx-ledger>'+''.join('<article data-fvx-record>Fixture '+str(i)+'</article>' for i in range(6))+'</section>').encode()
        plugin=plugin.replace(BLOB,git_blob(template)) # temporary fixture-only seal
    else:
        template=(root/'templates/ledger.html').read_bytes()
        assert git_blob(template)==BLOB,'Original NASA template Git blob mismatch'
    with tempfile.TemporaryDirectory(prefix='fv-r246-smoke-') as d:
        t=Path(d);(t/'templates').mkdir();(t/'assets').mkdir()
        (t/'final-vestige-ex2-research-desk.php').write_text(plugin)
        (t/'shim.php').write_text(SHIM)
        (t/'assets/source-ledger.css').write_text('.fv-ex2-ledger{color:#fff}')
        p=t/'templates/ledger.html'
        def render(b):
            p.write_bytes(b)
            r=subprocess.run(['php',str(t/'shim.php'),'late'],capture_output=True,text=True,check=True)
            return json.loads(r.stdout)['first']
        accepted=render(template)
        assert len(BeautifulSoup(accepted,'html.parser').select('[data-fvx-record]'))==6
        attacks={'byte':template+b'X','script':template+b'<script>alert(1)</script>','redirect':template+b'<a href="https://invalid.example/">Buy</a>','truncated':template[:len(template)//2],'empty':b''}
        for name,b in attacks.items():
            got=render(b)
            assert APOLLO in got and 'data-fvx-record' not in got and '<script' not in got,name
        p.unlink()
        r=subprocess.run(['php',str(t/'shim.php'),'late'],capture_output=True,text=True,check=True)
        assert APOLLO in json.loads(r.stdout)['first']
    print(json.dumps({'status':'PASS','scope':'SYNTHETIC' if a.fixture else 'EXACT_NASA_TEMPLATE','accepted_records':6,'reject_cases':len(attacks)+1,'installed_wp':False},sort_keys=True))
if __name__=='__main__':main()
