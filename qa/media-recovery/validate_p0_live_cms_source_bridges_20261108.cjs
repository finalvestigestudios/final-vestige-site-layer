'use strict';
const fs=require('node:fs');
const pins={
 '418:2':{p:418,src:'https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg',alt:'Broken concrete and debris where Scotch Cap Lighthouse stood after the April 1, 1946 tsunami.',c:'https://www.lighthousefriends.com/Scotch_Cap_debris2_1946.jpg',s:403},
 '287:5':{p:287,src:'https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg',alt:'The old Sunshine Skyway wreckage and the later bridge replacement in Tampa Bay.',c:'https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg',s:404},
 '407:1':{p:407,src:'https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg',alt:'Fresh fault scarp near Hebgen Lake produced by the August 1959 earthquake.',c:'https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/thumbnails/image/img7535.jpg',s:400}
};
function validate(o){
 const errors=[];const fail=m=>errors.push(m);
 if(o?.schema!=='fv-live-cms-3-p0-source-bridges-v1'||o.date_utc!=='2026-11-08')fail('schema_or_date');
 if(o?.method?.visitor_chrome!==false||o?.method?.binary_downloaded!==false||!o?.method?.cms?.includes('read-only'))fail('evidence_method');
 const b=o?.baseline;
 if(b?.historic_posts!==61||b?.historic_images!==355||b?.expanded_posts!==66||b?.expanded_images!==361||b?.reported_broken_42!=='UNVERIFIED'||b?.measured_76pct_reduction!==false||b?.measured_visitor_broken!==null||b?.measured_visitor_image_transfer_bytes!==null)fail('unverified_claims');
 if(b?.oversize_wp_decimal_mb_count!==15||b?.oversize_original_storage_bytes!==47096779)fail('storage_snapshot');
 for(const k of ['cms_write','media_cache','image_rehost','publish','homepage_edit','spend'])if(o?.permissions?.[k]!==false)fail('permission_'+k);
 if(!Array.isArray(o?.rows)||o.rows.length!==3)return {ok:false,errors:[...errors,'row_count']};
 const seen=new Set();
 for(const r of o.rows){
  const p=pins[r.key];if(!p){fail('unexpected_key');continue;}if(seen.has(r.key))fail('duplicate_key');seen.add(r.key);
  if(r.post!==p.p||r.original!==p.src||r.alt!==p.alt||r.status!=='publish'||!r.post_url?.startsWith('https://finalvestige.com/')||!/^2026-/.test(r.modified))fail('source_drift_'+r.key);
  if(r.retriever?.code!==p.s||r.retriever?.origin_http!==false||r.retriever?.visitor_http!==false||!r.retriever?.meaning?.startsWith('tool_'))fail('wrapper_mislabel_'+r.key);
  for(const k of ['visitor_http_status','visitor_current_src','visitor_natural_px','visitor_transfer_bytes','visitor_broken','source_binary_sha256'])if(r[k]!==null)fail('invented_evidence_'+r.key+'_'+k);
  const c=r.candidate;
  if(c?.url!==p.c||c?.binary_match!==false||!c?.evidence||!c?.scene_note||!c?.catalog||!c?.credit)fail('unproven_candidate_'+r.key);
  if(r.key!=='407:1'&&(c?.rights_status!=='HOLD'||c?.license_proven!==false))fail('copyright_clearance_faked_'+r.key);
  if(r.key==='407:1'&&(c?.rights_status!=='ITEM_PD_SOURCE_BINARY_HOLD'||c?.license_proven!==true||c?.evidence!=='PRIOR_VIEWER_RENDERED_LATEST_TOOL_INACCESSIBLE'))fail('usgs_custody_'+r.key);
  if(r.key==='418:2'&&(!c?.scene_note.includes('1964')||c?.evidence!=='IMAGE_DISPLAYED_SAME_BASENAME'))fail('1946_identity_hold');
  if(r.derive?.max_width!==960||r.derive?.no_upscale!==true||r.derive?.native_px!==null||r.derive?.target_px!==null||r.cache_or_wp_edit_authorized!==false)fail('unsafe_derivative_'+r.key);
 }
 for(const k of Object.keys(pins))if(!seen.has(k))fail('missing_'+k);
 return {ok:errors.length===0,errors};
}
module.exports={validate};
if(require.main===module){const o=JSON.parse(fs.readFileSync(process.argv[2]||__dirname+'/p0_live_cms_3_source_bridges_20261108.json','utf8'));const r=validate(o);console.log(JSON.stringify(r));process.exitCode=r.ok?0:1;}
