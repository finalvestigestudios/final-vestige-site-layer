#!/usr/bin/env python3
"""R467 source-safety + accessible-control QA without external services."""
from pathlib import Path
import hashlib
import re
import shutil
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
PHP=ROOT/'apollo_rights_gallery.php'
checks=0

def verify(condition,msg):
    global checks
    assert condition,msg
    checks+=1

def render(base=ROOT,n=1):
    snippet='require '+repr(str(base/'apollo_rights_gallery.php'))+';'+('echo fv457_render();'*n)
    return subprocess.check_output(['php','-r',snippet],text=True)

source=PHP.read_text()
verify(hashlib.sha256((ROOT/'assets/gallery.css').read_bytes()).hexdigest() in source,'CSS SHA-256 integrity pin')
verify(hashlib.sha256((ROOT/'assets/gallery.js').read_bytes()).hexdigest() in source,'JS SHA-256 integrity pin')
verify(hashlib.sha256((ROOT/'evidence_plates.php').read_bytes()).hexdigest() in source,'PHP source SHA-256 integrity pin')
markup=render()
verify(markup.count('data-fv457-card=')==6,'six archive records')
verify(markup.count('data-fv457-plate=')==3,'three source plates')
verify(markup.count('class="fv457__moment"')==3,'three chronology entries')
verify(markup.count('class="fv457__cta"')==1,'one free editorial CTA')
verify(markup.count('class="fv457__skip"')==1,'one same-page skip link')
verify('href="#fv457-1-records"' in markup,'skip target')
verify('id="fv457-1-records" tabindex="-1"' in markup,'keyboard focus landing')
verify(markup.count('aria-controls="fv457-1-records"')==5,'all filter buttons reference controlled list')
verify(len(re.findall(r'<button[^>]*aria-pressed=',markup))==5,'filter selection states')
verify(len(re.findall(r'<summary>NASA source and rights limits — ',markup))==6,'six contextual card drawers')
verify(len(re.findall(r'<summary>NASA source and date limits — ',markup))==3,'three contextual chronology drawers')
verify(len(re.findall(r'<summary>NASA record and limits — ',markup))==3,'three contextual source plates')
verify('KSC-20170124-PH_KLS01_0129 catalogue lookup remains inaccessible' in markup,'uncertain source custody remains visible')
verify('no signup is required' in markup.lower(),'free educator inquiry retained')
verify('data-fv457-home="confirmed"' in markup,'homepage cross-check retained')
verify(markup.count('aria-labelledby=')>=3,'region headings')
verify('Read the complete free Apollo 1 investigation' in markup,'aligned end action')
verify('utm_' not in markup,'no invented measurement scripts or campaign IDs')
verify('https://www.nasa.gov/' in markup,'primary-source links retained')
multi=render(n=2)
verify('id="fv457-1-records"' in multi and 'id="fv457-2-records"' in multi,'unique target IDs for repeated embed')
verify(multi.count('data-fv457-card=')==12,'two instances retain evidence')
with tempfile.TemporaryDirectory() as td:
    base=Path(td);(base/'assets').mkdir()
    for f in ('apollo_rights_gallery.php','evidence_plates.php','assets/gallery.css','assets/gallery.js'):shutil.copy2(ROOT/f,base/f)
    css=base/'assets/gallery.css';css.write_text(css.read_text()+'/* unexpected mutation */')
    fallback=render(base)
    verify('The image provenance list is temporarily unavailable' in fallback,'tampered CSS fails closed')
    verify('data-fv457-card=' not in fallback,'altered source never accepted')
print(f'PASS R467: {checks} source integrity, accessible name, no-JS and fail-closed contract checks')
