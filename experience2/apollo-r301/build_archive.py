#!/usr/bin/env python3
"""Build repeatable R301 staging evidence; fixed times and explicit integrity manifest."""
import hashlib
import json
import zipfile
from pathlib import Path

here = Path(__file__).resolve()
root = here.parents[2]
site = here.parents[1]
qa = root / 'QA'
out = root / 'Apollo_R301_Evidence.zip'
sources = [site/'apollo-r281/apollo-source-experience.php',
           site/'apollo-r281/assets/apollo-source-experience.css',
           site/'apollo-r301/README.md',
           site/'apollo-r301/build_archive.py',
           site/'apollo-r301/qa/local_http_fixture.php',
           site/'apollo-r301/qa/source_controlled_browser_gate.py']
outputs = [qa/f'r301-{w}-nojs.png' for w in (320,390,768,1440,1920)]
outputs += [qa/'r301-390-print.pdf', qa/'r301-browser-receipt.json']
files = sorted(sources + outputs, key=lambda f: str(f.relative_to(root)))
assert all(f.is_file() for f in files), 'Required source/QA artifact missing'
manifest = {'sprint':'R301', 'status':'LOCAL STAGING; UNMERGED; NOT LIVE',
            'repro':'extract and run python experience2/apollo-r301/qa/source_controlled_browser_gate.py',
            'scope':'PHP-backed Chromium offline fixture; not installed WordPress or axe-core',
            'payloads':{str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files},
            'hold':'Genuine axe, native browser HTTP/CSP, WP/Assembler, screen readers, field CWV, QD, founder approval'}
entries = {str(f.relative_to(root)):f.read_bytes() for f in files}
entries['EVIDENCE-MANIFEST.json'] = (json.dumps(manifest, sort_keys=True, indent=2)+'\n').encode()
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for name in sorted(entries):
        zi=zipfile.ZipInfo(name,(1980,1,1,0,0,0))
        zi.compress_type=zipfile.ZIP_DEFLATED
        zi.create_system=3
        zi.external_attr=0o644 << 16
        z.writestr(zi,entries[name],compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print('R301 zip',out,'sha256',hashlib.sha256(out.read_bytes()).hexdigest(),'payloads',len(files))
