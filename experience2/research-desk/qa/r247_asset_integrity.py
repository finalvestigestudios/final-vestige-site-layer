#!/usr/bin/env python3
"""R247 release gate: real six-record NASA source AND optional asset-custody checks.
No WordPress install, browser/axe claim, or commercial media-rights approval.
Run from repository: python experience2/research-desk/qa/r247_asset_integrity.py
"""
import hashlib, json, shutil, subprocess, tempfile
from pathlib import Path
from bs4 import BeautifulSoup
from r243_core import SHIM

ROOT=Path(__file__).resolve().parents[1]
PINS={
 'templates/ledger.html':'403d128c57b9bc82dac7c619651689070edef86c',
 'assets/source-ledger.css':'db531213e6f8dbaa44fba2885eefdd016dab93e3',
 'assets/source-ledger.js':'32e757cc4dc8708397ff65ac21e89dd319781d78'
}
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'

def git_blob(data):
 return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def invoke(root,phase='late'):
 p=subprocess.run(['php',str(root/'shim.php'),phase],capture_output=True,text=True,check=True)
 return json.loads(p.stdout)

def verify_records(result):
 parts=BeautifulSoup(result['first']+result['second'],'html.parser')
 assert len(parts.select('[data-fvx-record]'))==12,'two exact six-record ledgers required'
 ids=[x.get('id') for x in parts.select('[id]')]
 assert len(ids)==len(set(ids)),'repeated shortcode IDs collide'
 for attr in ('for','aria-labelledby','aria-controls'):
  for el in parts.select('['+attr+']'):
   assert all(ref in ids for ref in el.get(attr).split()),(attr,el)
 return True

def main():
 for path,pin in PINS.items():
  current=(ROOT/path).read_bytes()
  assert git_blob(current)==pin,(path,'protected source changed')
 plugin=(ROOT/'final-vestige-ex2-research-desk.php').read_text()
 assert all(pin in plugin for pin in PINS.values()),'source guards absent'
 with tempfile.TemporaryDirectory(prefix='apollo-r247-exact-') as folder:
  root=Path(folder)
  for path in PINS:
   target=root/path;target.parent.mkdir(parents=True,exist_ok=True)
   shutil.copy2(ROOT/path,target)
  shutil.copy2(ROOT/'final-vestige-ex2-research-desk.php',root/'final-vestige-ex2-research-desk.php')
  # Distinguish style/script enqueue instead of conflating the two handles.
  shim=SHIM.replace("$GLOBALS['queued'][]=$h;","$GLOBALS['queued'][]='style:'.$h;",1)
  shim=shim.replace("$GLOBALS['queued'][]=$h;","$GLOBALS['queued'][]='script:'.$h;",1)
  (root/'shim.php').write_text(shim)
  lint=subprocess.run(['php','-l',str(root/'final-vestige-ex2-research-desk.php')],capture_output=True,text=True)
  assert lint.returncode==0,lint.stderr
  for phase in ('early','late'):
   result=invoke(root,phase);verify_records(result)
   assert result['queued'].count('style:fv-ex2-research-desk')==2 if phase=='late' else result['queued'].count('style:fv-ex2-research-desk')>=2
   assert 'script:fv-ex2-research-desk' in result['queued']
   assert ('fv-ex2-research-desk-late-style' in result['first'])==(phase=='late')
  for name in ('css','js'):
   path=root/('assets/source-ledger.'+name)
   original=path.read_bytes()
   path.write_bytes(original+b'\n/* unsanctioned mutation */')
   result=invoke(root)
   verify_records(result)
   assert ('style:fv-ex2-research-desk' in result['queued'])==(name=='js')
   assert ('script:fv-ex2-research-desk' in result['queued'])==(name=='css')
   assert ('fv-ex2-research-desk-late-style' in result['first'])==(name=='js')
   path.unlink()
   result=invoke(root)
   verify_records(result)
   assert ('style:fv-ex2-research-desk' in result['queued'])==(name=='js')
   assert ('script:fv-ex2-research-desk' in result['queued'])==(name=='css')
   path.write_bytes(original)
  for name in ('css','js'):
   (root/('assets/source-ledger.'+name)).write_text('</style><script>alert("unsafe")</script>')
  result=invoke(root)
  verify_records(result)
  assert not result['queued'] and '<style' not in result['first']
  original=(root/'templates/ledger.html').read_bytes()
  (root/'templates/ledger.html').write_bytes(original+b' tampered')
  fallback=invoke(root)
  assert fallback['queued']==[] and FREE in fallback['first']
  assert 'data-fvx-record' not in fallback['first']
 print(json.dumps({'status':'PASS','scope':'EXACT_ORIGINAL_NASA_SOURCE',
                   'protected_pins':PINS,'cases':['early','late','duplicate-ids',
                   'css-mutated','css-missing','js-mutated','js-missing',
                   'both-attacked','html-tampered'], 'installed_wp':False,
                   'browser_or_axe':False},sort_keys=True))

if __name__=='__main__':main()
