"""Reproducible ZIP: stable metadata, no timestamps, source and browser assertions included."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'QA'/'Apollo_R429_Local_Evidence.zip'
files=sorted(p for p in ROOT.rglob('*') if p.is_file() and p!=OUT and '__pycache__' not in p.parts and '.pytest_cache' not in p.parts)
manifest={'name':'FV Apollo R429','mode':'staging opt-in; not live','files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},'gates':{'local_php':'PASS','offline_chromium':'PASS','installed_staging':'HOLD','axe_core':'HOLD','navigated_LCP_CLS':'HOLD','field_CWV':'HOLD','paid_purchase':'UNVERIFIED'}}
manifest_bytes=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for name,data in [('MANIFEST.json',manifest_bytes)]+[(str(p.relative_to(ROOT)),p.read_bytes()) for p in files]:
        info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
        z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(json.dumps({'file':str(OUT),'entries':len(files)+1,'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'bytes':OUT.stat().st_size}))
