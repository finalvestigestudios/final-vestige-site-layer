"""Source custody, safe staging gate and meaning tests for R436."""
import json, hashlib, subprocess, tempfile, shutil
from pathlib import Path
here=Path(__file__).resolve().parents[1]
root=here.parent
checks=0
def check(value, message):
 global checks
 assert value,message
 checks+=1
def run(*args):
 p=subprocess.run(args,capture_output=True,text=True)
 return p.returncode,p.stdout,p.stderr
ret,out,err=run("php","-l",str(here/"staging-source-proof.php"))
check(ret==0 and "No syntax errors" in out,"PHP lint")
ret,out,err=run("php",str(here/"qa/fixture.php"))
check(ret==0 and not err,"fixture php execution")
check(out.count('data-fv-r436-proof')==2,"two semantic source comparisons")
check(out.count('class="fv-r429__cta"')==2,"exactly one original free CTA per instance")
check(out.count('Crew photograph / catalogue ID not confirmed')==2,"unsubstantiated crew photo ID removed from visitor output")
check('S67-19766 / crew portrait' not in out,"no false image ID")
check(out.count('https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/find.html')>=2,"Board primary-source citation")
check(out.count('class="fv-r435__catalog"')==2,"original source gallery kept")
check(out.count('class="fv-r434__deep"')==2,"original Research Desk kept")
check('<img ' not in out.lower(),"no NASA images embedded")
check('<form ' not in out.lower(),"no new signup or checkout forms")
check('type="application/ld+json"' not in out,"no invented structured-data claims")
check('utm_content=fixture_not_a_published_asset' in out,"inherited campaign continuity")
check("fv-r436__grid" in out,"comparison rendered")
parent={
 "apollo-r435/staging-photo-custody.php":"68f276e9d7ad8cb2eaa9d992379b497e6ce15ddd",
 "apollo-r435/assets/photo-custody.css":"fdd83485823f708e22230cc9ca9fa1c2368c11d9",
 "apollo-r435/source_catalog.json":"0c0401f651a24c8a1bec16980e519df9df9e6762"}
for name,want in parent.items():
 b=(root/name).read_bytes()
 check(hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()==want,"exact Git blob "+name)
# staging opt-in absent in the PHP fixture, the shortcode must fall back safely.
phpcode='define("ABSPATH","/fixture/");require '+json.dumps(str(here/'staging-source-proof.php'))+';echo fv_r436_shortcode();'
ret,out,err=run('php','-r',phpcode)
check(ret==0 and 'data-fv-r436' not in out and "free Apollo 1 investigation" in out,"unapproved environment fail open")
# Edit one parent file in a copied tree: the component must not render unreviewed evidence.
with tempfile.TemporaryDirectory() as tmp:
 target=Path(tmp)/'experience2'
 shutil.copytree(root,target)
 source=target/'apollo-r435/staging-photo-custody.php'
 source.write_text(source.read_text()+'\n// simulated corruption\n')
 ret,out,err=run('php',str(target/'apollo-r436/qa/fixture.php'))
 check(ret==0 and out.count('data-fv-r436-proof')==0,"reject mutated parent source")
 check('free Apollo 1 investigation' in out,"fail open to free article")
 Path(tmp,'mutation.json').write_text(json.dumps({"rejected":True}))
with tempfile.TemporaryDirectory() as tmp:
 target=Path(tmp)/'experience2'
 shutil.copytree(root,target)
 css=target/'apollo-r436/assets/source-proof.css'
 css.write_text(css.read_text()+'/* malicious style mutation */')
 ret,out,err=run('php',str(target/'apollo-r436/qa/fixture.php'))
 check(ret==0 and out.count('data-fv-r436-proof')==0,"reject own CSS mutation")
 check('free Apollo 1 investigation' in out,"CSS tamper safely falls back")
report={"status":"PASS_LOCAL","assertions":checks,"scope":"PHP/source custody only","staging":"NOT TESTED"}
qa=here/'QA';qa.mkdir(exist_ok=True)
(qa/'contract.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
print('PASS',checks,'PHP/source custody assertions')
