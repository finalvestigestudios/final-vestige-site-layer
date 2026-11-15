#!/usr/bin/env python3
"""Deterministic evidence archive, excludes generated ZIP and inherited R377/R384 code."""
import hashlib, json, pathlib, zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1];QA=ROOT/'QA';QA.mkdir(exist_ok=True)
sources=[ROOT/'gallery-asset-guard.php',ROOT/'README.md',ROOT/'qa/contract.php',ROOT/'qa/browser.py',ROOT/'qa/package.py']
outputs=[p for p in sorted(QA.iterdir()) if p.is_file() and p.suffix in ('.png','.json','.pdf') and p.name!='MANIFEST.json']
source_deps=[ROOT.parent/'apollo-r377/custody.json',ROOT.parent/'apollo-r384/document-gallery.php',ROOT.parent/'apollo-r384/assets/gallery.css']
sha=lambda x: hashlib.sha256(x).hexdigest()
manifest={'scope':'R385 local fixture / no WordPress install / no hosting','files':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in sources+outputs},'inherited_dependencies':{str(p.relative_to(ROOT.parent)):sha(p.read_bytes()) for p in source_deps},'limitations':['actual axe-core unavailable','browser local HTTP blocked by administrator; urllib HTTP verification only','no installed WordPress/Assembler','no hosted exact-HEAD CI','no commercial attribution or verified sales']}
(QA/'MANIFEST.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
entries=[*sources,*outputs,QA/'MANIFEST.json'];zip_path=QA/'Apollo_R385_Evidence.zip'
with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(entries,key=lambda x:str(x.relative_to(ROOT))):
  name=str(p.relative_to(ROOT));info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
  z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(json.dumps({'files':len(entries),'zip_sha256':sha(zip_path.read_bytes()),'path':str(zip_path)},indent=2))
