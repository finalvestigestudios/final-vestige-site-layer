#!/usr/bin/env python3
"""R217 isolated Apollo staging: record-to-link crosswalk and same-byte rendering."""
import hashlib, json, os, re, shutil, sys
from html.parser import HTMLParser
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'apollo-r216'))
from build_r216 import protect_markup as inherited_guard, FREE
BASE=Path(os.environ.get('FV_APOLLO_R216_DIST', HERE/'../apollo-r216/dist')).resolve()
OUT=HERE/'dist'
PIN='a7546ae18c7970183c003ddcc4ac1bbc13f14cb87933982e6113a8792bec0128'
DATES=('1966-10-18','1967-01-03','1967-01-27','1967-01-28')
IDS=('S66-58038','S67-15717','Apollo 204 Review Board','S67-21294')
def sha(v):return hashlib.sha256(v).hexdigest()
def encode(v):return (json.dumps(v,sort_keys=True,ensure_ascii=False,indent=2)+'\n').encode()
def check(v,msg):
    if not v:raise ValueError(msg)
class EvidenceLinks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True);self.external=[];self.sources=[];self.ctas=[];self.times=[];self.rail=False
    def handle_starttag(self,tag,pairs):
        a=dict(pairs)
        if tag=='ol' and 'rail' in a.get('class','').split():self.rail=True
        if tag=='time' and self.rail:self.times.append(a.get('datetime'))
        if tag=='a':
            href=a.get('href','')
            if not href.startswith('#'):self.external.append(href)
            if a.get('data-source-id'):self.sources.append((a['data-source-id'],href))
            if 'cta' in a.get('class','').split():self.ctas.append(href)
    def handle_endtag(self,tag):
        if tag=='ol' and self.rail:self.rail=False
def verify(html,css,files):
    inherited_guard(html,css)
    records=json.loads(files['source-records.json'])
    ledger=json.loads(files['custody-ledger.json'])
    receipt=json.loads(files['link-custody-receipt.json'])
    h=EvidenceLinks();h.feed(html.decode());h.close()
    r={x['source_id']:x for x in records}
    check(tuple(r)==IDS and tuple(x['date'] for x in records)==DATES,'Source records changed')
    check(tuple(h.times)==DATES,'ChronologyRail dates are not the approved sequence')
    check(h.ctas==[FREE],'Only the free investigation may be a CTA')
    check(set(h.external)==set(receipt['distinct_external']) and len(h.external)==receipt['links_total'],
          'Unreviewed/missing NASA or editorial destination')
    check(receipt['map_pins']==0 and receipt['images']==0 and ledger['geo_pins']==[] and ledger['speculative_edges']==[],
          'Speculative geographic or image data')
    check(not ledger['commercial_photo_rights_cleared'] and not ledger['purchase_sku_verified'] and not ledger['implied_endorsement_permitted'],
          'Unverified NASA rights/paid offer opened')
    check(ledger['chronology_date_contract']['board_report_completed_month']=='1967-04','Report/event chronology conflated')
    check(all(x['commercial_advertising_clearance']=='NOT CERTIFIED' and x['media_copied'] is False for x in records),
          'NASA commercial rights or copied photos not cleared')
    check(len(h.sources)>=len(r),'NASA record anchors missing')
    for name,url in h.sources:
        check(name in r and r[name]['source_url']==url,'False NASA source association: '+name)
    for name,record in r.items():
        check((name,record['source_url']) in h.sources,'Required NASA primary-source anchor absent: '+name)
        matched=[x for x in ledger['records'] if x['id']==name]
        check(len(matched)==1 and matched[0]['url']==record['source_url'] and matched[0]['date']==record['date'],
              'Research Desk and Atlas source custody disagree: '+name)
    return {'source_bindings':[{'source_id':k,'url':u} for k,u in h.sources],
            'chronology_dates':list(h.times),'external_urls':sorted(set(h.external)),
            'external_anchor_count':len(h.external),'single_free_editorial_cta':FREE,
            'commercial_rights':'NOT CLEARED','published_grok_asset':None,'paid_order':None,
            'realized_net_revenue':None,'r198_ancestry':'NOT RECONCILED','axe_core':'NOT VERIFIED'}
def build():
    parent=(BASE/'manifest.json').read_bytes()
    check(sha(parent)==PIN,'R216 pinned parent manifest mismatch')
    manifest=json.loads(parent)
    check(manifest['release']=='r216','Unexpected parent')
    for flag in ('creator_attribution_verified','approved_purchase_offer','media_commercial_rights_cleared',
                 'installed_WordPress_accepted','upstream_R198_reconciled','axe_core_accepted','commercial_release_allowed'):
        check(manifest[flag] is False,'Parent release gate incorrectly cleared: '+flag)
    files={name:(BASE/name).read_bytes() for name in manifest['files']}
    for name,hash_value in manifest['files'].items():
        check(sha(files[name])==hash_value,'Parent source hash mismatch: '+name)
    html=files['templates/atlas-fragment.html'];css=files['assets/atlas-scoped.css']
    audit=verify(html,css,files);audit['parent_manifest_sha256']=PIN
    audit['verified_render_bytes_sha256']=sha(html)
    audit_bytes=encode(audit)
    php=files.pop('fv-ex2-apollo-r216.php').decode()
    check('function fv_ex2_r216_assets_ok()' in php and 'wp_enqueue_script(' not in php,'Unexpected PHP adapter')
    php=php.replace('r216','r217').replace('R216','R217')
    old="$html=file_get_contents(plugin_dir_path(__FILE__).'templates/atlas-fragment.html');\n    if ($html===false) return fv_ex2_r217_fallback();"
    new="$html=fv_ex2_r217_verified_fragment(plugin_dir_path(__FILE__).'templates/atlas-fragment.html');\n    if ($html===false) return fv_ex2_r217_fallback();"
    check(php.count(old)==1,'Missing render-byte integrity insertion point')
    php=php.replace(old,new)
    helper=("\nfunction fv_ex2_r217_verified_fragment($path) {\n"
            "    $bytes=@file_get_contents($path);\n"
            "    if ($bytes===false || hash('sha256',$bytes)!=='"+sha(html)+"') return false;\n"
            "    return $bytes;\n}\n\n")
    marker='function fv_ex2_r217_render($atts=array(),$content=null) {'
    check(php.count(marker)==1,'Missing verifiable render entry')
    php=php.replace(marker,helper+marker)
    marker='return is_readable($html) && is_readable($css)'
    check(php.count(marker)==1,'Missing source hash gate')
    php=php.replace(marker,marker+"\n        && is_readable($root.'source-url-crosswalk.json') && hash_file('sha256',$root.'source-url-crosswalk.json')==='"+sha(audit_bytes)+"'")
    shim=files.pop('wp-render-shim-r216.php').decode().replace('r216','r217').replace('R216','R217')
    shim=shim.replace("['normal','late','printed']","['normal','late','printed','tamper-helper']")
    marker='require $plugin;'
    check(shim.count(marker)==1,'Cannot install PHP helper regression')
    shim=shim.replace(marker,marker+"""
if($mode==='tamper-helper') {
  $original=plugin_dir_path($plugin).'templates/atlas-fragment.html';
  $tmp=tempnam(sys_get_temp_dir(),'fv-apollo-');
  if($tmp===false) exit(5);
  $valid=fv_ex2_r217_verified_fragment($original);
  file_put_contents($tmp,file_get_contents($original).'<!--modified-->');
  $rejected=fv_ex2_r217_verified_fragment($tmp)===false;
  @unlink($tmp);
  echo json_encode(['valid_original'=>is_string($valid),'tamper_rejected'=>$rejected],JSON_THROW_ON_ERROR);
  exit(0);
}
""")
    files.update({'fv-ex2-apollo-r217.php':php.encode(),
                  'wp-render-shim-r217.php':shim.encode(),
                  'source-url-crosswalk.json':audit_bytes})
    files['manifest.json']=encode({'release':'r217','parent_manifest_sha256':PIN,
        'files':{n:sha(v) for n,v in sorted(files.items())},
        'source_and_commerce_gate_runtime_hash_checked':manifest['source_and_commerce_gate_runtime_hash_checked']+['source-url-crosswalk.json'],
        'read_bytes_verified_at_render':True,'source_url_crosswalk_guard':True,
        'script_shipped':False,'creator_attribution_verified':False,'approved_purchase_offer':False,
        'media_commercial_rights_cleared':False,'installed_WordPress_accepted':False,
        'upstream_R198_reconciled':False,'axe_core_accepted':False,'commercial_release_allowed':False,
        'release_gate':'STAGING HOLD: full WP, source/rights, axe, CI, QD and founder review'})
    temp=HERE/'_dist_pending'
    if temp.exists():shutil.rmtree(temp)
    for name,data in sorted(files.items()):
        path=temp/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    if OUT.exists():shutil.rmtree(OUT)
    temp.rename(OUT)
    return sha(files['manifest.json'])
if __name__=='__main__':print('R217 staging SHA:',build())
