#!/usr/bin/env python3
"""R308 committed gate: PHP-rendered, no-JS attribution continuity in real offline Chromium."""
from pathlib import Path
from urllib.parse import urlencode,urlparse,parse_qs
from html.parser import HTMLParser
import subprocess,json,re
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[2]
P=R/'apollo-r281/apollo-source-experience.php'
F=R/'apollo-r301/qa/local_http_fixture.php'
C=R/'apollo-r281/assets/apollo-source-experience.css'
BASE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
GOOD={'utm_source':'youtube','utm_medium':'organic_social','utm_campaign':'history_pilot_2026_11','utm_content':'apollo_lf_001'}
class Links(HTMLParser):
 def __init__(self):super().__init__();self.hrefs=[]
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if tag=='a' and d.get('data-fv-cta')=='apollo-read-free-investigation':self.hrefs.append(d.get('href'))
def render(query):
 data=urlencode({'instances':'2',**query},doseq=True)
 code='$_SERVER["QUERY_STRING"]=$argv[2];parse_str($argv[2],$_GET);include $argv[1];'
 return subprocess.check_output(['php','-r',code,str(F),data],text=True)
def links(query):
 p=Links();p.feed(render(query));return p.hrefs
def accepted(h):
 p=urlparse(h)
 return (p.scheme+'://'+p.netloc+p.path)==BASE and parse_qs(p.query)=={k:[v] for k,v in GOOD.items()}
subprocess.run(['php','-l',str(P)],check=True)
assert links({})==[BASE,BASE]
valid=0
for source in ['youtube','tiktok','instagram','facebook','pinterest','x','bluesky']:
 q={**GOOD,'utm_source':source}
 for h in links(q):
  assert (urlparse(h).scheme+'://'+urlparse(h).netloc+urlparse(h).path)==BASE
  assert parse_qs(urlparse(h).query)=={k:[v] for k,v in q.items()};valid+=1
 for h in links({**q,'email':'person@example.test','gclid':'secret'}):
  assert 'email' not in h and 'gclid' not in h
bad=[{**GOOD,'utm_source':'google'},{**GOOD,'utm_medium':'paid'},{**GOOD,'utm_campaign':'history_pilot_2026_12'},
 {**GOOD,'utm_content':'x'},{**GOOD,'utm_content':'email@example.org'},
 {**GOOD,'utm_content':['abc','def']},{**GOOD,'utm_source':['youtube','tiktok']},
 {k:v for k,v in GOOD.items() if k!='utm_content'}]
for q in bad:assert links(q)==[BASE,BASE],q
contexts=focus=0
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for w in [320,390,768,1440,1920]:
  for js in [False,True]:
   page=b.new_page(viewport={'width':w,'height':900},java_script_enabled=js,has_touch=w<800,reduced_motion='reduce')
   raw=render(GOOD);raw=re.sub(r'<link\b[^>]+rel="stylesheet"[^>]*>','',raw)
   html=raw.replace('</head>','<style>'+C.read_text()+'</style></head>')
   page.set_content(html)
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
   assert page.locator('section.fv-r281').count()==2
   for i in [1,2]:
    region=page.locator('section.fv-r281').nth(i-1)
    assert accepted(region.locator('[data-fv-cta]').get_attribute('href'))
    assert region.locator('[data-fv-cta]').get_attribute('data-fv-conversion-kind')=='editorial-continuation'
    back=region.locator('.fv-r307__continue-return').first
    back.focus();page.keyboard.press('Enter')
    assert page.evaluate('location.hash')==f'#fv-r281-{i}-continue';focus+=1
   contexts+=1;page.close()
 b.close()
print(json.dumps({'contexts':contexts,'accepted_source_links':valid,'invalid_cases':len(bad),'fragment_focus':focus,
 'axe':'NOT_EXECUTED','wordPress':'NOT_TESTED','performance':'OFFLINE_FIXTURE_ONLY'}))
