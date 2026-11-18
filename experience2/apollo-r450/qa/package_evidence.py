"""Reproducible local evidence archive, fixed timestamp and sorted file order.
Read-only: does not communicate with GitHub, WordPress, merchant or email.
"""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'QA/Apollo_R450_Local_Proof.zip'
FILES=[p for p in ROOT.rglob('*') if p.is_file() and p!=OUT and '__pycache__' not in p.parts and p.suffix!='pyc']
def build(dest):
    with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for file in sorted(FILES):
            rel=str(file.relative_to(ROOT))
            info=zipfile.ZipInfo(rel,date_time=(1980,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o644<<16
            z.writestr(info,file.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
def main():
    OUT.parent.mkdir(parents=True,exist_ok=True)
    build(OUT)
    other=OUT.with_suffix('.repro.tmp')
    build(other)
    a=hashlib.sha256(OUT.read_bytes()).hexdigest()
    b=hashlib.sha256(other.read_bytes()).hexdigest()
    other.unlink()
    if a!=b:raise RuntimeError('non-deterministic archive')
    print(json.dumps({'files':len(FILES),'sha256':a,'bytes':OUT.stat().st_size,'reproduced':a==b}))
if __name__=='__main__':main()
