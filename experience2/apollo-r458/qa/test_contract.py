#!/usr/bin/env python3
"""R458 deterministic local source/negative security and fail-open checks. No WP deployment."""
import copy, hashlib, json, re, shutil, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PHP=ROOT/'apollo_editorial_reconciliation.php'
DATA=ROOT/'data/records.json'
CSS=ROOT/'assets/audit.css'
JS=ROOT/'assets/audit.js'
results=[]
def check(name,yes):
    results.append({'case':name,'pass':bool(yes)})
    if not yes:raise AssertionError(name)
def php(code,root=ROOT):
    return subprocess.run(['php','-r',f'require {json.dumps(str(root/"apollo_editorial_reconciliation.php"))};'+code],capture_output=True,text=True)
def php_valid(payload):
    encoded=json.dumps(payload,ensure_ascii=False)
    r=php('echo fv458_valid(json_decode('+json.dumps(encoded)+',true))?"YES":"NO";')
    if r.returncode:raise RuntimeError(r.stderr)
    return r.stdout=='YES'
data=json.loads(DATA.read_text())
r=php('echo fv458_render();')
check('PHP lint',subprocess.run(['php','-l',str(PHP)],capture_output=True).returncode==0)
check('render success',r.returncode==0 and '<section class="fv458"' in r.stdout and 'Review record / Issue #150' in r.stdout)
check('all six records',r.stdout.count('data-fv458-card=')==6)
check('three primary claims',r.stdout.count('Read primary NASA finding')==3)
check('single free investigation CTA',r.stdout.count('Read the full free Apollo 1 investigation')==1)
check('no embedded NASA imagery or map pins',not re.search(r'<(?:img|iframe|video|audio|canvas|svg|form)\b',r.stdout,re.I) and 'data-lat' not in r.stdout)
check('no purchase or tracking endpoint',not re.search(r'<(?:script)[^>]+src=|utm_|fbq\(|gtag\(|checkout|affiliate',r.stdout,re.I))
check('local validated data',php_valid(data))
check('six-record source dated',len(data['records'])==6 and all(x['event_date'] for x in data['records']))
check('one flagged mismatch and one catalogue hold',sum(x['review_state']=='reconcile' for x in data['records'])==1 and sum(x['review_state']=='source_hold' for x in data['records'])==1)
check('February independent editorial source boundary',all('nasa.gov' in c['source_url'] for c in data['claims']))
for name,mutator in [
 ('duplicate image ID',lambda x:x['records'][1].update(id=x['records'][0]['id'])),
 ('spoofed NASA host',lambda x:x['records'][0].update(source_url='https://www.nasa.gov.evil.example/image-detail/id')),
 ('nonHTTPS NASA link',lambda x:x['records'][0].update(source_url='http://www.nasa.gov/image-detail/id')),
 ('URL credentials',lambda x:x['records'][0].update(source_url='https://u@www.nasa.gov/image-detail/id')),
 ('malformed day',lambda x:x['records'][0].update(event_date='1966-02-30')),
 ('invented day precision',lambda x:x['records'][2].update(precision='day')),
 ('misstated homepage observation',lambda x:x['records'][2].update(homepage_use='not_reviewed')),
 ('false Atlas photo clearance',lambda x:x['records'][2].update(atlas_use='shown')),
 ('unreviewed item certified',lambda x:x['records'][-1].update(catalogue_status='located')),
 ('forgotten catalogue hold',lambda x:x['records'][-1].update(review_state='recorded')),
 ('unreviewed external photo URL',lambda x:x['claims'][0].update(source_url='https://example.com/source')),
 ('extra unrelated pin record',lambda x:x['records'].append(copy.deepcopy(x['records'][0]))),
 ('ordered timeline regression',lambda x:x['records'].reverse()),
]:
    obj=copy.deepcopy(data);mutator(obj);check('reject '+name,not php_valid(obj))
for target in ['data/records.json','assets/audit.css','assets/audit.js']:
    with tempfile.TemporaryDirectory() as d:
        clone=Path(d);shutil.copytree(ROOT,clone/'src');file=clone/'src'/target
        file.write_bytes(file.read_bytes()+b'\nCORRUPTED\n')
        run=php('echo fv458_render();',clone/'src')
        check('pinned asset tampering '+target,run.returncode==0 and 'Archival source-review cards are temporarily unavailable' in run.stdout and '<section class="fv458"' not in run.stdout)
check('default WordPress gate does not register shortcode','add_shortcode(' not in php('echo fv458_render();').stdout)
report={'sprint':'R458','test_type':'local_php_source_contract_and_mutations','passed':sum(x['pass'] for x in results),'total':len(results),'failures':[x for x in results if not x['pass']],'exact_source':'local candidate; SHA recorded after GitHub commit','hosted':'NOT_RUN','image_rights':'NOT_CERTIFIED'}
(ROOT/'QA/CONTRACT_RESULTS.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'total':report['total']},indent=2))
