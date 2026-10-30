"""Deterministic source and anti-speculation contracts for documentary trails."""
from pathlib import Path
import sys,json,re,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from trail import validate,section,BOARD,RESPONSE
response=json.loads((ROOT/'response-crosswalk.json').read_text())
custody=json.loads((ROOT/'custody.json').read_text())
validate(response,custody)
html=section(response,custody)
assert len(re.findall(r'<li class="ex2-trail__card"',html))==6
assert all(html.count(f'id="trail-{n:02}"')==1 for n in range(1,7))
assert all(html.count(f'href="#custody-{n:02}"')>=0 for n in range(1,7))
assert html.count(BOARD)==6 and html.count(RESPONSE)==6
assert 'A Board recommendation is a proposed remedy' in html
assert '<img' not in html and '<script' not in html and 'latitude' not in html
assert 'NASA endorsement' in html and 'thematic' in html.lower()
assert html.count('data-ex2-trail-card')==6
assert 'data-ex2-trail-controls hidden' in html
for r in response['records']:
 for key in ('board_locator','response_locator','board_summary','response_summary','status'):
  assert r[key] in html, (r['id'],key)
assert all(r['related_stage'] in {x['stage_id'] for x in custody['claims']} for r in response['records'])
source=(ROOT/'render.py').read_text();assert '{trails_html}' in source
assert "from trail import section as trail_section" in source
css=(ROOT/'assets/trail.css').read_text();assert '.ex2-trail__card[hidden]{display:none!important}' in css
js=(ROOT/'assets/trail.js').read_text();assert 'reveal()' in js and 'hashchange' in js
original=hashlib.sha256((ROOT/'index.html').read_bytes()).hexdigest()
from subprocess import run
p=run([sys.executable,str(ROOT/'render.py')],capture_output=True,text=True)
assert p.returncode==0,p.stderr
assert hashlib.sha256((ROOT/'index.html').read_bytes()).hexdigest()==original
print('TRAIL_SOURCE_CONTRACT_PASS: 6 audited routes, verified source origins, no NASA media or geography, deterministic HTML',original)
