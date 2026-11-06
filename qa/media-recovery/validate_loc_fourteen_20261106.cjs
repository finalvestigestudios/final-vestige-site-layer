'use strict';
const KEYS=["166:1","190:0","190:1","190:2","190:3","190:4","190:5","214:0","214:4","413:1","413:3","413:4","413:5","428:5"];
function validate(a){
 const e=[];const fail=s=>e.push(s);
 if(!a||a.schema!=='fv-loc-fourteen-v1'||!Array.isArray(a.records))return ['bad schema'];
 if(a.records.length!==14||a.coverage?.loc_slots!==14)fail('cohort incomplete');
 if(a.reference_cohort?.confirmed_broken!==null||a.reference_cohort?.measured_transfer_reduction_percent!==null)fail('fabricated findings');
 if(!a.policy?.no_wordpress_writes||!a.policy?.no_unlicensed_caching||!a.policy?.no_upscaling||a.policy?.preview_max_px!==960||!a.policy?.map_panorama_full_detail_required)fail('unsafe policy');
 const seen=new Set();
 for(const r of a.records){
  if(!r||typeof r!=='object'){fail('invalid record');continue;}
  if(!KEYS.includes(r.key)||seen.has(r.key)||r.key!==r.post_id+':'+r.image_slot)fail('invalid key/slot '+r.key);
  seen.add(r.key);
  if(!(r.original_url?.startsWith('https://cdn.loc.gov/')||r.original_url?.startsWith('https://tile.loc.gov/')))fail('untrusted src '+r.key);
  if(!r.post_url?.startsWith('https://finalvestige.com/'))fail('untrusted article '+r.key);
  if(!r.archive_catalog_url?.startsWith('https://www.loc.gov/'))fail('untrusted catalog '+r.key);
  if(!['ITEM_MATCH','COLLECTION_ONLY','SECONDARY_CROSSWALK','UNCONFIRMED'].includes(r.archive_catalog_state))fail('unsupported source assurance '+r.key);
  if(r.source_http_status!==null||r.browser_http_status!==null||r.visitor_broken!==null)fail('fabricated HTTP/browser '+r.key);
  if(r.rights_decision!=='HOLD_ITEM_REVIEW'||r.cache_authorized!==false||r.production_write_authorized!==false)fail('unsafe rights/production '+r.key);
  if(r.max_preview_width_px!==960)fail('bad target width '+r.key);
  if(r.native_dimensions!==null){
   const n=r.native_dimensions;if(!Number.isSafeInteger(n?.width)||!Number.isSafeInteger(n?.height)||n.width<=0||n.height<=0)fail('bad native '+r.key);
  }
  if(r.conditional_preview_dimensions!==null){
   const n=r.native_dimensions,p=r.conditional_preview_dimensions;
   if(!n||!Number.isSafeInteger(p?.width)||!Number.isSafeInteger(p?.height)||p.width<=0||p.height<=0||p.width>960||p.width>n.width||p.height>n.height||Math.abs(p.width/n.width-p.height/n.height)>0.003)fail('unsafe resizing '+r.key);
  }
 }
 for(const key of KEYS)if(!seen.has(key))fail('missing '+key);
 if(a.coverage?.item_catalog_matches!==a.records.filter(x=>x.archive_catalog_state==='ITEM_MATCH').length)fail('match count incorrect');
 if(a.coverage?.other_catalog_states!==a.records.filter(x=>x.archive_catalog_state!=='ITEM_MATCH').length)fail('pending count incorrect');
 return e;
}
module.exports={validate,KEYS};
