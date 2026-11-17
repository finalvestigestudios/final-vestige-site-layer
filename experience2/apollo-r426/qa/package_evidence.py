"""Deterministic no-network R426 QA package. All file paths deliberately fixed."""
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
files = [
    'README.md', 'staging-source-comparison.php', 'assets/source-comparison.css',
    'qa/render_fixture.php', 'qa/test_contract.py', 'qa/browser_qa.py',
    'qa/package_evidence.py', 'QA/unit-tests.txt', 'QA/php-lint.txt',
    'QA/browser-results.json', 'QA/qa-boundary.md',
]
files += [x.relative_to(ROOT).as_posix() for x in sorted((ROOT/'QA/screenshots').glob('*.png'))]
manifest = {'name':'Apollo R426 local offline QA evidence',
            'limits':['No navigated LCP/CLS','No installed WordPress staging','No genuine axe-core','No confirmed paid orders'],
            'files':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(files)}}
out = ROOT / 'QA/Apollo_R426_Local_Evidence.zip'
archive_files = {'MANIFEST.json':(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode()}
archive_files.update({p:(ROOT/p).read_bytes() for p in files})
with zipfile.ZipFile(out,'w') as z:
    for name in sorted(archive_files):
        info = zipfile.ZipInfo(name, (1980,1,1,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED
        info.external_attr=(0o100644)<<16
        z.writestr(info,archive_files[name],compresslevel=9)
print(out.name,'entries',len(archive_files),'sha256',hashlib.sha256(out.read_bytes()).hexdigest())
