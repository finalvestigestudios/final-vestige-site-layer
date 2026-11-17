#!/usr/bin/env python3
"""Negative mutation tests of six original blob pins and commercial claims."""
import importlib.util
import json
import shutil
import tempfile
from pathlib import Path

spec=importlib.util.spec_from_file_location('source_guard',Path(__file__).with_name('source_guard.py'))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
source=Path(__file__).resolve().parents[3];checks=0;fail=[]
with tempfile.TemporaryDirectory() as temp:
 root=Path(temp)
 for name in module.BLOBS:
  target=root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source/name,target)
 checks+=1
 if module.inspect(root)['status']!='PASS':fail.append('unchanged source should pass')
 for name in module.BLOBS:
  target=root/name;data=target.read_bytes();target.write_bytes(data+b'\nUNAUTHORIZED')
  checks+=1
  if module.inspect(root)['status']!='HOLD':fail.append('tamper not caught '+name)
  target.write_bytes(data)
 file=root/'experience2/apollo-r440/product_evidence.json';data=file.read_bytes()
 edited=json.loads(data);edited['merchant_seller_identity_verified']=True
 file.write_text(json.dumps(edited));checks+=1
 if module.inspect(root)['status']!='HOLD':fail.append('false commercial proof not caught')
 file.write_bytes(data)
 path=root/'experience2/apollo-r440/assets/educator-intent.js';path.unlink();path.symlink_to(source/'experience2/apollo-r440/assets/educator-intent.js');checks+=1
 if module.inspect(root)['status']!='HOLD':fail.append('symlink not caught')
result={'status':'PASS' if not fail else 'FAIL','checks':checks,'failures':fail,'type':'LOCAL_NEGATIVE_MUTATION_ONLY'}
qa=Path(__file__).resolve().parents[1]/'QA';qa.mkdir(exist_ok=True)
(qa/'negative_tests.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result));raise SystemExit(bool(fail))
