"""R435 local source custody and actual PHP output contract; no external network."""
from pathlib import Path
from bs4 import BeautifulSoup
import hashlib, json, subprocess
R=Path(__file__).resolve().parents[2]
HERE=R/'apollo-r435'
checks=0
def ok(v,reason):
 global checks
 assert v,reason
 checks+=1
def php(script):
 p=subprocess.run(['php','-r',script],capture_output=True,text=True)
 ok(p.returncode==0,p.stderr)
 return p.stdout

def main():
 assert subprocess.run(['php','-l',str(HERE/'staging-photo-custody.php')],capture_output=True).returncode==0
 ok(True,'php lint')
 data=json.loads((HERE/'source_catalog.json').read_text())
 ok(len(data)==6,'6 reviewed NASA records')
 ok(len(set(x['url'] for x in data))==6,'six distinct official URLs')
 ok(all(x['media_reuse'].startswith('NOT REVIEWED') for x in data),'no invented media license')
 ok(all(x['url'].startswith('https://www.nasa.gov/image-detail/') for x in data),'NASA links only')
 by_id={x['id']:x for x in data}
 ok('1966' in by_id['S66-58038']['date'],'pre-accident chamber photo accurately dated')
 ok('telemetry' in by_id['S66-58038']['limits'],'training photo not telemetry')
 ok('2017' in by_id['KSC-20170124-PH_KLS01_0090']['date'],'2017 redesigned hatch')
 ok('2017' in by_id['KSC-20170124-PH_KLS01_0164']['date'],'2017 tribute')
 ok('ignition' in by_id['S67-21294']['limits'],'damage photo not unique spark')
 path=str(HERE/'staging-photo-custody.php')
 prefix='define("ABSPATH","/test/");require '+json.dumps(path)+';'
 ok(php(prefix+'echo fv_r435_verify()?"yes":"no";')=='yes','verified chain')
 ok(php(prefix+'echo fv_r435_allowed()?"yes":"no";')=='no','production fail closed')
 ok('Read the free Apollo 1 investigation' in php(prefix+'echo fv_r435_shortcode();'),'free link fallback')
 ok(php(prefix+'echo count(fv_r435_catalog());')=='6','runtime validated catalog')
 ok('unavailable' in php(prefix+'echo fv_r435_render(31,[]);'),'instance limit')
 ok('unavailable' in php('define("ABSPATH","/test/");function fv_r434_render(){};require '+json.dumps(path)+';echo fv_r435_render(1,[]);'),'no preloaded unknown parents')
 allowed='define("ABSPATH","/test/");define("FV_R435_ENABLED",true);define("FV_R435_STAGING_PAGE_ID",77);function wp_get_environment_type(){return "staging";}function is_singular(){return true;}function get_queried_object_id(){return 77;}'
 ok('data-fv-r435' in php(allowed+';require '+json.dumps(path)+';echo fv_r435_shortcode();'),'staging only positive gate')
 ok('unavailable' in php(allowed.replace('return 77;','return 78;')+';require '+json.dumps(path)+';echo fv_r435_shortcode();'),'wrong page denied')
 fixture=subprocess.check_output(['php',str(HERE/'qa/fixture.php')],text=True)
 soup=BeautifulSoup(fixture,'html.parser')
 galleries=soup.select('[data-fv-r435-catalog]')
 ok(len(galleries)==2,'two instances')
 for g in galleries:
  ok(len(g.select('li.fv-r435__plate'))==6,'six catalog cards')
  ok(len(g.select('details.fv-r435__drawer'))==6,'per-record source drawer')
  ok(len(g.select('img'))==0,'no images copied/hotlinked')
  ok(len(g.select('a[href^="https://www.nasa.gov/image-detail/"]'))==6,'six NASA links')
  ok(all(x.get('datetime') for x in g.select('time')),'time semantics')
  ok('NASA' in g.get_text(),'NASA provenance visible')
 for r in soup.select('[data-fv-r435]'):
  ok(len(r.select('.fv-r429__cta'))==1,'one relevant free CTA')
  ok(r.select_one('.fv-r429__cta').find_parent('details') is None,'CTA visible above source disclosures')
  ok(len(r.select('.fv-r434__row'))==3,'inherited chronology unchanged')
  ok(len(r.select('.fv-r430__question'))==3,'inherited teacher content unchanged')
  ok(not r.select('a[href*="checkout"],a[href*="payhip"],form'),'no unsupported commerce')
 ids=[x['id'] for x in soup.select('[id]')]
 ok(len(ids)==len(set(ids)),'IDs remain unique')
 ok('fixture_not_a_published_asset' in soup.select_one('.fv-r429__cta')['href'],'test UTM only')
 ok(not '?' in soup.select('.fv-r429__cta')[1]['href'],'untracked visitor no invented UTM')
 # Attack test: a strict exact-file hash must reject a mutated R434 parent in an isolated copy.
 import tempfile, shutil
 with tempfile.TemporaryDirectory() as temp:
  copy=Path(temp)/'experience2'
  for name in ['apollo-r429','apollo-r430','apollo-r431','apollo-r432','apollo-r433','apollo-r434','apollo-r435']:
   shutil.copytree(R/name,copy/name,ignore=shutil.ignore_patterns('QA','__pycache__'))
  f=copy/'apollo-r434/staging-research-route.php'
  f.write_bytes(f.read_bytes()+b'\n// unauthorized drift\n')
  ok('unavailable' in php('define("ABSPATH","/");require '+json.dumps(str(copy/'apollo-r435/staging-photo-custody.php'))+';echo fv_r435_render(1,[]);'),'upstream mutation rejects')
  f.write_bytes((R/'apollo-r434/staging-research-route.php').read_bytes())
  j=copy/'apollo-r435/source_catalog.json'; j.write_bytes(j.read_bytes()+b' ')
  ok('unavailable' in php('define("ABSPATH","/");require '+json.dumps(str(copy/'apollo-r435/staging-photo-custody.php'))+';echo fv_r435_render(1,[]);'),'catalog mutation rejects')
 report={'status':'PASS_LOCAL_ONLY','checks':checks,'browser_integration':'separate','real_wp_staging':'NOT_TESTED','axe_core':'NOT_TESTED','purchase':'NOT_VERIFIED'}
 (HERE/'QA/contract.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
 print('PASS',checks,'R435 PHP/source-contract assertions; LOCAL ONLY')
if __name__=='__main__': main()
