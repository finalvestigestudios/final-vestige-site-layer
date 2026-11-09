#!/usr/bin/env python3
"""R236 staging-only source-action accessible names, based on SHA-pinned R235."""
import hashlib, json, re, shutil, sys
from pathlib import Path

PARENT='eccfee83d2856185f216345c58ad83fb85224da41047de7b6b2d6fbefd526082'
INDEX='e95101467cd278a13cf8a4959a29ae17260577dab2ed4d3f4f9910423795f4d9'
RECORDS=(
 ('Apollo 204 Review Board','Apollo 204 Review Board report','https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/','#fv-apollo-finding-fire','fv-apollo-plate-apollo-204-review-board-limit'),
 ('S66-58038','NASA photograph S66-58038','https://www.nasa.gov/image-detail/amf-s66-58038/','#fv-apollo-photo-1966','fv-apollo-plate-s66-58038-limit'),
 ('S67-15717','NASA photograph S67-15717','https://www.nasa.gov/image-detail/amf-s67-15717/','#fv-apollo-photo-prep','fv-apollo-plate-s67-15717-limit'),
 ('S67-21294','NASA photograph S67-21294','https://www.nasa.gov/image-detail/amf-s67-21294/','#fv-apollo-photo-aftermath','fv-apollo-plate-s67-21294-limit'),
)
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def transform(html):
 seen=[]
 def change(m):
  v=m.group();key=re.search(r'Source options for ([^\"<]+)',v).group(1)
  row=next((r for r in RECORDS if r[0]==key),None)
  assert row is not None, 'Unexpected source ID: '+key
  _,name,url,target,limit=row
  a=f'<a href="{url}" rel="noopener noreferrer" aria-describedby="{limit}">Verify at NASA ↗</a>'
  b=f'<a href="{target}">Find this source in the investigation ↓</a>'
  assert v.count(a)==v.count(b)==1, 'Source link custody mismatch: '+key
  seen.append(key)
  return v.replace(a,a.replace('>Verify at NASA ↗',f' aria-label="Verify at NASA: {name}">Verify at NASA ↗')).replace(b,b.replace('>Find this source',f' aria-label="Find {name} in the investigation">Find this source'))
 out=re.sub(r'<nav class="fv-apollo-plate-links" aria-label="Source options for [^"]+">.*?</nav>',change,html,flags=re.S)
 assert seen==[r[0] for r in RECORDS], 'Source ordering changed'
 return out

def build(parent,dest):
 assert sha(parent/'manifest.json')==PARENT and sha(parent/'index.html')==INDEX,'Parent not verified'
 manifest=json.loads((parent/'manifest.json').read_text())
 for rel,h in manifest['files'].items():assert sha(parent/rel)==h,'Modified parent: '+rel
 assert not dest.exists(),'No overwrites of staging artifacts'
 shutil.copytree(parent,dest)
 for rel in ('index.html','templates/atlas-fragment.html'):
  target=dest/rel;target.write_text(transform(target.read_text()))
 template=dest/'templates/atlas-fragment.html'
 php=dest/'fv-ex2-apollo-r224.php';src=php.read_text()
 old=manifest['files']['templates/atlas-fragment.html']
 assert src.count(old)==2,'Unexpected PHP integrity contract'
 php.write_text(src.replace(old,sha(template)))
 for rel in ('templates/atlas-fragment.html','fv-ex2-apollo-r224.php'):
  manifest['files'][rel]=sha(dest/rel)
 manifest.update(r236_change='Eight uniquely accessible NASA source actions; visible text and URLs unchanged',release='R236_STAGING_HOLD',status='STAGING_HOLD')
 (dest/'manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
 for rel,h in manifest['files'].items():assert sha(dest/rel)==h,rel
 return {'manifest_sha256':sha(dest/'manifest.json'),'template_sha256':sha(template),'php_sha256':sha(php)}

if __name__=='__main__':
 if len(sys.argv)!=3:raise SystemExit('Usage: r236_patch.py <verified-R235-dir> <new-output-dir>')
 print(json.dumps(build(Path(sys.argv[1]),Path(sys.argv[2])),sort_keys=True))
