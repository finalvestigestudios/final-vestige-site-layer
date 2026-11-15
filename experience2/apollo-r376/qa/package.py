#!/usr/bin/env python3
"""Pack byte-stable R376 evidence and reviewed upstream inputs; no timestamps/IO network."""
import argparse, hashlib, io, json, zipfile
from pathlib import Path

def sha(data): return hashlib.sha256(data).hexdigest()
def main():
    a=argparse.ArgumentParser();a.add_argument('--out',type=Path,required=True);args=a.parse_args()
    p=Path(__file__).resolve();repo=p.parents[3];own=p.parents[1]
    upstream=['apollo-r365/chrono-rail.php','apollo-r367/sealed-chronology.php',
        'apollo-r371/source-gallery.php','apollo-r372/evidence-path.php',
        'apollo-r372/staging-assets.php','apollo-r372/assets/evidence-path.css']
    paths=[repo/'experience2'/x for x in upstream]
    paths += [x for x in own.rglob('*') if x.is_file() and x.suffix not in ('.zip','.pyc') and '__pycache__' not in x.parts]
    entries={str(x.relative_to(repo)):x.read_bytes() for x in sorted(paths)}
    manifest={'label':'R376_LOCAL_PHP_CHROMIUM_PASS_NOT_WORDPRESS',
              'not_staging':True,'sha256_by_path':{name:sha(data) for name,data in sorted(entries.items())}}
    entries['R376_MANIFEST.json']=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode()
    def build():
        b=io.BytesIO()
        with zipfile.ZipFile(b,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
            for path,data in sorted(entries.items()):
                info=zipfile.ZipInfo(path,date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
                info.external_attr=0o644<<16;z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
        return b.getvalue()
    one=build();assert one==build(),'archive not byte-stable'
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_bytes(one)
    print(json.dumps({'archive':str(args.out),'bytes':len(one),'entries':len(entries),
        'sha256':sha(one),'byte_identical_rebuild':True},sort_keys=True))
if __name__=='__main__':main()
