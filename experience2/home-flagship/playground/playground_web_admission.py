#!/usr/bin/env python3
"""SHA-guarded FV EX2 PR #1509 package fix for official browser WordPress Playground.

This changes ONLY the Blueprint admission preflight and both private MU-plugin
host gates. The real seven-chapter HTML/CSS/JS remains byte-identical. It is
an unexecuted WordPress import candidate, never a production deployment.
"""
import hashlib,io,json,zipfile
from pathlib import Path

PARENT_SHA='dbc305c6047756665a2fd54ffb88ab4822b7b43dad370c575423a627fd4ce061'
PINS={'blueprint.json':'17a9ea5428f0c56a36ce376793d9b53521871dd0bc38a9f947d0ff49c91be4ca',
'mu-plugins/fv-ex2-playground-review.php':'a1d5f495856003d75cd1b87bcb45e86c990499a2ae2b602effa8952f50d2bbc8',
'mu-plugins/fv-ex2-private-browser-receipt.php':'de3b67b6871190add9b1aeae4980d1f6c5837211bded38c508fa3e131ab85368'}
FILES=sorted(['REVIEW.txt','SOURCE_CUSTODY.json',*PINS])
OLD_PRE="if (!$loopback) {"
NEW_PRE="// Official WordPress Playground web PHP host (not the parent UI).\n$trusted_web_sandbox = $host === 'wpsandbox.wordpress.net';\nif (!$loopback && !$trusted_web_sandbox) {"
OLD_MU="if (!$fv_ex2_review_loopback || (defined('WP_ENVIRONMENT_TYPE') && WP_ENVIRONMENT_TYPE === 'production')) { return; }"
NEW_MU="// Only the official browser WordPress sandbox OR existing loopback hosts.\n$fv_ex2_review_websandbox = $fv_ex2_review_host === 'wpsandbox.wordpress.net';\nif ((!$fv_ex2_review_loopback && !$fv_ex2_review_websandbox) || (defined('WP_ENVIRONMENT_TYPE') && WP_ENVIRONMENT_TYPE === 'production')) { return; }"

def digest(b):return hashlib.sha256(b).hexdigest()
def once(b,old,new):
 a=old.encode();n=new.encode()
 if b.count(a)!=1:raise ValueError('REFUSE: expected patch anchor is not unique')
 return b.replace(a,n,1)
def build(source):
 if digest(source)!=PARENT_SHA:raise ValueError('REFUSE: PR #1509 source SHA mismatch')
 with zipfile.ZipFile(io.BytesIO(source)) as z:
  if sorted(z.namelist())!=FILES:raise ValueError('REFUSE: source ZIP file inventory changed')
  data={p:z.read(p) for p in FILES}
 for p,h in PINS.items():
  if digest(data[p])!=h:raise ValueError('REFUSE: source file mismatch '+p)
 bp=json.loads(data['blueprint.json']);assert bp['steps'][0]['step']=='runPHP' and bp['steps'][1]['step']=='installTheme'
 bp['steps'][0]['code']=once(bp['steps'][0]['code'].encode(),OLD_PRE,NEW_PRE).decode()
 data['blueprint.json']=(json.dumps(bp,indent=2)+'\n').encode()
 for p in PINS:
  if p.startswith('mu-plugins/'):
   data[p]=once(data[p],OLD_MU,NEW_MU)
 archive=data['mu-plugins/fv-ex2-playground-review.php']
 if archive.count(b'class="fv-margin-strip__item"')!=72 or archive.count(b'https://finalvestige.com/focus/')!=5 or archive.count(b'<img ')!=2:
  raise ValueError('REFUSE: source content inventory changed')
 custody=json.loads(data['SOURCE_CUSTODY.json']);custody['files_sha256'].update({p:digest(data[p]) for p in PINS if p.startswith('mu-plugins/')})
 custody['official_playground_web_host_candidate']={'wordpress_host':'wpsandbox.wordpress.net','host_match':'exact',
 'original_7_chapter_html_css_js':'unchanged','wp_core_tested':False,'release':'HOLD'}
 data['SOURCE_CUSTODY.json']=(json.dumps(custody,indent=2,sort_keys=True)+'\n').encode()
 stream=io.BytesIO()
 with zipfile.ZipFile(stream,'w') as z:
  for p in FILES:
   info=zipfile.ZipInfo(p,date_time=(2026,11,7,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
   z.writestr(info,data[p],compresslevel=9)
 return stream.getvalue()
if __name__=='__main__':
 import argparse
 a=argparse.ArgumentParser();a.add_argument('parent_zip',type=Path);a.add_argument('--out',type=Path,required=True);x=a.parse_args()
 result=build(x.parent_zip.read_bytes());x.out.parent.mkdir(parents=True,exist_ok=True);x.out.write_bytes(result)
 print(json.dumps({'status':'DERIVED_NOT_WP_CORE_TESTED','parent_sha256':PARENT_SHA,'candidate_sha256':digest(result),'release':'HOLD'},indent=2))
