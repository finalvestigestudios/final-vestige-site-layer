'use strict';
/** Offline, fail-closed reconciler for frozen 61-post media provenance. No website access. */
function reconcile(a, parts, csv) {
 const errors=[], assert=(ok,msg)=>{if(!ok)errors.push(msg)};
 assert(a && a.schema==='fv-media-origin-duplicate-crosswalk-v1','schema');
 assert(Array.isArray(parts)&&parts.length===8,'parts');
 const ims=parts.flatMap(p=>p.images||[]), ids=new Set(), hosts={};
 for(const p of parts)for(const post of (p.posts||[]))ids.add(post.id);
 const M=new Map(), P=new Map(), counts={};
 for(const im of ims) {
  counts[im.source_kind]=(counts[im.source_kind]||0)+1;
  const arr=M.get(im.source_url)||[];arr.push(im);M.set(im.source_url,arr);
  const row=P.get(im.post_id)||[];row.push(im);P.set(im.post_id,row);
  assert(im.key===im.post_id+':'+im.slot,'slot_key '+im.key);
  assert(im.actual_http_status===null&&im.broken_in_browser===null,'invented HTTP '+im.key);
  assert(im.allowed_to_localize===false,'unapproved source use '+im.key);
  if(im.source_host==='i0.wp.com'){
   const upstream=String(im.source_url).match(/^https:\/\/i[012]\.wp\.com\/([^/?#]+)/i)?.[1]?.toLowerCase();
   assert(!!upstream,'invalid wp proxy '+im.key);
   assert(im.source_kind===(upstream==='finalvestige.com'?'jetpack_proxy':'external'),'proxy owner misclassified '+im.key);
  }
 }
 assert(ids.size===61&&P.size===61&&ims.length===355,'census size');
 assert(M.size===353,'exact-src uniqueness');
 assert(counts.external===170&&counts.wikimedia_redirect===118&&counts.first_party===60&&counts.jetpack_proxy===7,'origin totals');
 const qa=new Map(); for(const l of String(csv).trim().split(/\r?\n/).slice(1)) {
  const f=l.split(',').map(Number);
  assert(f.length===3&&f.every(Number.isInteger),'csv format');
  qa.set(f[0],{images:f[1],offsite:f[2]});
 }
 assert(qa.size===61,'csv posts');
 const mismatches=[...P].map(([id,rows])=>{
  const prior=qa.get(id);assert(!!prior,'missing qa post '+id);
  assert(prior&&prior.images===rows.length,'post ref count '+id);
  return{id,qa:prior?.offsite,media:rows.filter(im=>im.source_kind==='external'||im.source_kind==='wikimedia_redirect').length};
 }).filter(x=>x.qa!==x.media).sort((x,y)=>x.id-y.id);
 assert(mismatches.map(x=>x.id).join(',')==='285,291','unexpected census discrepancy');
 assert(mismatches.every(x=>x.media-x.qa===1),'unexpected discrepancy magnitude');
 const qaOffsite=[...qa.values()].reduce((n,v)=>n+v.offsite,0);
 assert(qaOffsite===286&&a.metrics.qa_csv_offsite===286,'qa count');
 assert(a.metrics.media_offsite===288&&a.metrics.unique_exact_source_urls===353&&a.metrics.img_src_references===355,'media count');
 const db=[...M].filter(([u,rows])=>rows.length>1).map(([u,rows])=>({url:u,slots:rows.map(x=>({key:x.key,alt:x.alt})),same_post:rows.every(x=>x.post_id===rows[0].post_id)})).sort((x,y)=>x.slots[0].key.localeCompare(y.slots[0].key));
 assert(db.length===2,'duplicate group count');
 for(let i=0;i<db.length;i++){
  const expected=a.duplicates?.[i], got=db[i];
  assert(expected?.url===got.url,'duplicate URL '+i);
  assert(expected?.same_post===got.same_post,'duplicate scope '+i);
  assert(JSON.stringify(expected?.slots)===JSON.stringify(got.slots),'duplicate slots/ALT '+i);
  assert(expected?.visitor_http_status===null&&expected?.actual_transfer_bytes===null&&expected?.rights_clearance===false&&expected?.wordpress_write_allowed===false,'duplicate evidence gate '+i);
 }
 for(const m of mismatches) {
  const target=a.mismatches?.find(x=>x.post_id===m.id);
  assert(target?.qa_csv_offsite===m.qa&&target?.media_offsite===m.media,'mismatch provenance '+m.id);
  const predicted=P.get(m.id).filter(x=>x.source_host==='i0.wp.com'&&x.source_kind==='external');
  assert(predicted.length===1&&target?.external_jetpack?.length===1&&predicted[0].key===target.external_jetpack[0].key&&predicted[0].source_url===target.external_jetpack[0].url,'proxy mismatch '+m.id);
 }
 assert(a.metrics.broken_images_42==='not_guest_browser_verified'&&a.metrics.image_transfer_reduction_76pct==='unmeasured'&&a.metrics.production_repairs===0,'performance/repair claim');
 assert(a.gate?.allow_wp_write===false&&a.gate?.allow_caching===false&&a.gate?.allow_derivative===false&&a.gate?.do_not_upscale===true&&a.gate?.width_cap_px===960,'publication safety');
 for(const candidate of a.source_candidates||[]) assert(candidate.binary_match===false&&candidate.permission_to_cache===false&&String(candidate.rights).startsWith('HOLD')&&(!candidate.derivative_max_width_px||candidate.derivative_max_width_px<=960),'candidate provenance '+candidate.for_slot);
 return{ok:errors.length===0,errors,metrics:{posts:P.size,refs:ims.length,unique_exact_src:M.size,offsite:counts.external+counts.wikimedia_redirect,qa_offsite:qaOffsite,discrepant_posts:mismatches.map(x=>x.id),same_exact_src_groups:db.map(x=>x.slots.map(y=>y.key))}};
}
module.exports={reconcile};
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path'),root=__dirname;
 const json=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
 const audit=json('census_reconciliation_and_duplicate_src_20261104.json');
 const parts=Array.from({length:8},(_,i)=>json('parts/'+String(i+1).padStart(2,'0')+'.json'));
 // QA CSV lives in a separate draft PR: supply a checked-out path explicitly, don't silently fabricate it.
 const csvPath=process.argv[2];
 if(!csvPath){console.error('Usage: node validate_census_reconciliation_20261104.cjs /path/to/qa154/cms_image_census_20261030.csv');process.exitCode=2}
 else {const res=reconcile(audit,parts,fs.readFileSync(csvPath,'utf8'));console.log(JSON.stringify(res,null,2));if(!res.ok)process.exitCode=1}
}
