'use strict';
function validate(v) {
  if(v.schema_version!==1||v.post_id!==418||v.images?.length!==6) throw Error('identity');
  const p=v.policies||{};
  if(p.max_width!==960||p.wp_write_authorized!==false||p.allow_upscale!==false||
     p.allow_scrape!==false||p.claimed_42_broken_verified!==false||
     p.claimed_76_percent_reduction_measured!==false) throw Error('safety');
  const perf=v.performance||{};
  if(perf.claimed_saved_percent!==null||perf.actual_cold_browser_bytes!==null||
     perf.verified_sitewide_broken_count!==null) throw Error('unproven metric');
  if(v.totals?.visitor_broken_verified!==0||v.totals?.first_party_repairs!==0) throw Error('repair claim');
  const seen=new Set();let displayed=0;
  for(const item of v.images){
    if(item.key!==`418:${seen.size}`||seen.has(item.key)) throw Error('slot');
    seen.add(item.key);
    if(item.retrieval?.origin_http_status!==null||item.retrieval?.browser_http_status!==null||
       item.retrieval?.browser_decodes!==null) throw Error('invented HTTP');
    if(!/^https:\/\//.test(item.original_url)) throw Error('original URL');
    const c=item.candidate||{}, d=c.displayed_derivative;
    if(!Number.isInteger(c.max_width_px)||c.max_width_px<1||c.max_width_px>960) throw Error('max width');
    if(d&&(!Number.isInteger(d.width)||!Number.isInteger(d.height)||d.width<1||
           d.height<1||d.width>c.max_width_px)) throw Error('upscale');
    if(!c.rights||!item.hold?.length) throw Error('rights and staging hold');
    if(item.retrieval.outcome.startsWith('exact_published_')) displayed++;
  }
  if(displayed!==2) throw Error('independent image-display count');
  return true;
}
module.exports={validate};
if(require.main===module){
  const fs=require('node:fs'),path=require('node:path');
  validate(JSON.parse(fs.readFileSync(path.join(__dirname,'scotch_418_six_slot_verified_transport_20261103.json'),'utf8')));
  console.log('Scotch Cap 418 evidence: PASS (browser status unknown)');
}
