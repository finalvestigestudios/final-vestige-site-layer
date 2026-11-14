"""Deterministic archive of frozen tests/screenshots, not a claim of deterministic browser runtimes."""
from pathlib import Path
import hashlib, json, zipfile
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'Apollo_R367_Evidence.zip'
need=[ROOT/'experience2/apollo-r365/chrono-rail.php', ROOT/'experience2/apollo-r365/assets/chrono-rail.css']
here=ROOT/'experience2/apollo-r367'
need+=list(here.rglob('*'))
need=[f for f in need if f.is_file() and f.suffix not in ('.pyc',) and '__pycache__' not in f.parts]
need=sorted(set(need),key=lambda p:p.relative_to(ROOT).as_posix())
manifest={'sprint':'R367','scope':'source-controlled draft; local PHP and Chromium fixtures; no WordPress or hosted CI','files':{f.relative_to(ROOT).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in need},'frozen_artifacts':True,'browser_qa_method':'set_content, not actual HTTP navigation','production_release':'HARD HOLD'}
manifest_bytes=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for name,data in [('R367_MANIFEST.json',manifest_bytes)]+[(f.relative_to(ROOT).as_posix(),f.read_bytes()) for f in need]:
        info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=0o644<<16
        z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(json.dumps({'archive':str(OUT),'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'files':len(need)+1},indent=2))
