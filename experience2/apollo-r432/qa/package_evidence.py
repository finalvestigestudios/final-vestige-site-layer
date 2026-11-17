"""Reproducible source+QA ZIP. Sorted entries, fixed timestamps, stored bytes."""
import hashlib, json, zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
OUTPUT=HERE/'QA/Apollo_R432_Local_Evidence.zip'
FILES=[p for p in HERE.rglob('*') if p.is_file() and p!=OUTPUT and '__pycache__' not in str(p)]
FILES.sort(key=lambda p:p.relative_to(HERE).as_posix())
def make_bytes():
 from io import BytesIO
 out=BytesIO()
 with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_STORED) as z:
  for file in FILES:
   arc=file.relative_to(HERE).as_posix()
   info=zipfile.ZipInfo(arc,date_time=(1980,1,1,0,0,0))
   info.external_attr=0o644 << 16
   info.compress_type=zipfile.ZIP_STORED
   z.writestr(info,file.read_bytes())
 return out.getvalue()
def main():
 a,b=make_bytes(),make_bytes()
 assert a==b,'nondeterministic build'
 OUTPUT.write_bytes(a)
 report={'archive':OUTPUT.name,'sha256':hashlib.sha256(a).hexdigest(),'entries':len(FILES),'double_build_identical':True}
 print(json.dumps(report,sort_keys=True))
if __name__=='__main__':main()
