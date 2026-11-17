'use strict';
/** Offline inventory host-concentration audit; NOT a browser HTTP or rights-clearance tool. */
const FIXED_SHAS=['948bc1b65b42799aa40cfdb810ddf6ffd80886b6','48e1ebf07207e948ba5802e714eb39659d2e1c1d','49183f66f880f7c4dfd363acca906876877f2e5e','6df3251e5a67a971d87a516a1ba4a0cc32f51f96','9b16b828342a9ac338f3e65610fd3d8d508355e9','0f3dfe398a76838049cebba7cb773d5c5a0c8c69','21095161e633aba093b74c0ead9936c9f6186d00','5659ec243c188928be3f89c0f96354b660608ca2'];
const host=u=>typeof u==='string'?(u.match(/^https:\/\/([a-z0-9.-]+)(?:[/?#]|$)/i)||[])[1]?.toLowerCase()||null:null;
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const n=i=>String(i).padStart(2,'0');
function rollup(parts){
 const imgs=parts.flatMap(p=>p.images),posts=parts.flatMap(p=>p.posts),off=imgs.filter(i=>['external','wikimedia_redirect'].includes(i.source_kind));
 const byHost=new Map(),byUrl=new Map();
 for(const i of off){
  const h=host(i.source_url),g=byHost.get(h)||{host:h,image_keys:[],post_ids:new Set(),urls:new Set(),source_kinds:new Set()};
  g.image_keys.push(i.key);g.post_ids.add(i.post_id);g.urls.add(i.source_url);g.source_kinds.add(i.source_kind);byHost.set(h,g);
  const d=byUrl.get(i.source_url)||[];d.push(i.key);byUrl.set(i.source_url,d);
 }
 const host_groups=[...byHost.values()].map(g=>({host:g.host,refs:g.image_keys.length,unique_urls:g.urls.size,
  post_count:g.post_ids.size,post_ids:[...g.post_ids].sort((a,b)=>a-b),image_keys:g.image_keys.sort(),
  source_kinds:[...g.source_kinds].sort(),sample_urls:[...g.urls].slice(0,2)}))
  .sort((a,b)=>b.refs-a.refs||a.host.localeCompare(b.host));
 const duplicate_exact_urls=[...byUrl].filter(([u,a])=>a.length>1).map(([url,image_keys])=>({url,image_keys:image_keys.sort()})).sort((a,b)=>a.url.localeCompare(b.url));
 const proxy_upstream_exceptions=off.filter(i=>host(i.source_url)==='i0.wp.com').map(i=>({
  image_key:i.key,url:i.source_url,upstream_origin_host:(i.source_url.match(/^https:\/\/i0\.wp\.com\/([^/?#]+)\//)||[])[1],origin_is_finalvestige:false}));
 return{imgs,posts,off,host_groups,duplicate_exact_urls,proxy_upstream_exceptions,unique_urls:byUrl.size};
}
function validate(parts,ledger,large){
 const errors=[],bad=e=>errors.push(e);
 if(!Array.isArray(parts)||parts.length!==8||!ledger||ledger.schema_version!==1)return{ok:false,errors:['schema_or_parts_invalid']};
 for(let i=0;i<8;i++){
  const p=parts[i];if(!p||!Array.isArray(p.images)||!Array.isArray(p.posts)||p.image_count!==p.images.length||p.post_count!==p.posts.length)bad('source_part_corrupt:'+n(i+1));
  if(ledger.baseline_part_blob_sha?.[n(i+1)]!==FIXED_SHAS[i])bad('source_sha_reference_changed:'+n(i+1));
 }
 if(errors.length)return{ok:false,errors};
 const r=rollup(parts),s=ledger.scope||{},a=ledger.accuracy_gates||{};
 if(r.posts.length!==61||r.imgs.length!==355||r.off.length!==288||r.unique_urls!==286||r.host_groups.length!==79)bad('census_baseline_changed');
 if(!eq([s.published_posts,s.stored_image_refs,s.offsite_refs,s.offsite_distinct_exact_urls,s.offsite_source_hostnames,s.first_party_refs,s.first_party_jetpack_refs],[61,355,288,286,79,60,7]))bad('ledger_counts_changed');
 if(new Set(r.imgs.map(i=>i.key)).size!==355||new Set(r.posts.map(p=>p.id)).size!==61)bad('duplicate_keys');
 for(const i of r.imgs)if(host(i.source_url)!==i.source_host||i.actual_http_status!==null||i.broken_in_browser!==null||i.allowed_to_localize!==false||i.target_max_width_px!==960)bad('source_status_or_rights_fabricated:'+i.key);
 if(!eq(r.host_groups,ledger.host_groups))bad('host_rollup_changed');
 if(!eq(r.duplicate_exact_urls,ledger.duplicate_exact_urls)||!eq(r.duplicate_exact_urls.map(x=>x.image_keys),[['291:2','291:5'],['213:2','213:6']]))bad('duplicate_url_proof_changed');
 if(!eq(r.proxy_upstream_exceptions,ledger.proxy_upstream_exceptions)||!eq(r.proxy_upstream_exceptions.map(x=>x.image_key),['291:0','285:1']))bad('proxied_external_origin_mislabeled');
 if(!eq([a.claimed_42_broken_images_confirmed,a.confirmed_guest_browser_broken_count,a.claimed_76_percent_saved_measured,a.measured_reduction_percent,a.production_media_repaired,a.wp_writes,a.asset_downloads,a.homepage_design_changes,a.subscription_spend],[false,null,false,null,0,false,false,false,false]))bad('invented_browser_or_optimization_result');
 const c=ledger.priority_cases;
 if(!Array.isArray(c)||!eq(c.map(x=>x.image_key),['285:5','287:5','407:1','418:1','418:2']))bad('priority_evidence_order_changed');
 else for(const p of c){
  const orig=r.imgs.find(i=>i.key===p.image_key);
  if(!orig||orig.source_url!==p.published_url||orig.alt!==p.alt||orig.post_id!==p.post_id)bad('p0_url_or_alt_unmatched:'+p.image_key);
  if(!/NOT_(guest_browser|logged_out_visitor_browser)/.test(p.wrapper_method||'')||![null,400,403,404].includes(p.wrapper_error_code)||typeof p.wrapper_result!=='string')bad('retriever_not_browser_confusion:'+p.image_key);
  if(p.origin_status!==null||p.guest_browser_status!==null||p.guest_browser_broken!==null||p.actual_transfer_bytes!==null||p.legal_status!=='HOLD'||p.rights_clear!==false||p.cache_authorized!==false||p.wordpress_publish_authorized!==false||p.exact_visual_match_verified!==false||p.candidate_master_sha256!==null||p.max_width_px!==960)bad('p0_rights_or_browser_fabrication:'+p.image_key);
  if(!host(p.record_url)||p.candidate_url!==null&&!host(p.candidate_url))bad('archive_candidate_url_invalid:'+p.image_key);
  const w=p.original_width_px,h=p.original_height_px,tw=p.conditional_width_px,th=p.conditional_height_px;
  if(w===null||h===null){if(tw!==null||th!==null)bad('unmeasured_dimensions_invented:'+p.image_key)}
  else if(!Number.isSafeInteger(w)||!Number.isSafeInteger(h)||w<1||h<1||tw!==Math.min(w,960)||!Number.isSafeInteger(th)||Math.abs(th-tw*h/w)>1.01)bad('upscale_or_distorted_dimensions:'+p.image_key);
 }
 if(!large||large.schema_version!==1||!Array.isArray(large.rows)||large.rows.length!==13)bad('oversize_census_missing');
 else{
  const total=large.rows.reduce((z,v)=>z+v.original_bytes,0),five=large.rows.filter(x=>x.wp_media_details_subsizes_present===false);
  if(total!==43522829||five.length!==5||five.reduce((z,v)=>z+v.original_bytes,0)!==13267538||five.some(x=>x.dimensions_px?.width!==1672||x.dimensions_px?.height!==941))bad('oversize_source_measurement_changed');
  if(!eq([s.oversized_originals_over_1_5_mib,s.oversized_original_storage_bytes,s.first_party_pngs_without_subsizes,s.first_party_pngs_without_subsizes_original_storage_bytes],[13,43522829,5,13267538]))bad('original_bytes_mislabeled');
 }
 return{ok:errors.length===0,errors,summary:{posts:r.posts.length,images:r.imgs.length,offsite:r.off.length,unique_offsite_urls:r.unique_urls,offsite_hosts:r.host_groups.length,p0_cases:c?.length||0,visitor_failures_established:null}};
}
module.exports={validate,rollup,host,FIXED_SHAS};
if(typeof require==='function'&&require.main===module){
 const fs=require('node:fs'),crypto=require('node:crypto'),path=require('node:path'),root=path.resolve(__dirname,'../..');
 const parts=FIXED_SHAS.map((sha,j)=>{const b=fs.readFileSync(path.join(__dirname,'parts',n(j+1)+'.json')),actual=crypto.createHash('sha1').update(Buffer.from('blob '+b.length+'\0')).update(b).digest('hex');if(actual!==sha)throw Error('source_blob_sha_mismatch:'+n(j+1));return JSON.parse(b.toString('utf8'))});
 const ledger=JSON.parse(fs.readFileSync(path.join(__dirname,'host_exposure_20261101.json'),'utf8')),large=JSON.parse(fs.readFileSync(path.join(__dirname,'large_first_party_20261101.json'),'utf8'));
 const out=validate(parts,ledger,large);console.log(JSON.stringify(out,null,2));if(!out.ok)process.exitCode=2;
}
