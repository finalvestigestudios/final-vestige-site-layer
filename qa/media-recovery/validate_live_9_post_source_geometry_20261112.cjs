'use strict';
/** Validates live WordPress markup evidence without confusing HTML entities,
 * original-host failures or rights approval with actual guest browser evidence. */
const audit=require('./live_9_post_61_source_geometry_20261112.json');
const frozen=require('./coverage_288_exact_pr1703_20261110.json');
const expected={211:6,268:10,280:6,285:6,287:6,288:6,407:8,418:6,432:7};
const p0=new Set(["285:5","285:2","287:5","418:1","418:2","407:1"]);
const norm=x=>typeof x==='string'?x.replace(/&amp;/g,'&'):null;
function validate(a=audit){
 const hold=reason=>({status:'HOLD',reason,production_change_allowed:false});
 if(a?.schema!=='fv-live-9-post-source-geometry-61-v1'||a.evidence?.frozen_sha!=='4965a862f7de7de46c1f4a1e26f3ca70a8c38805')return hold('SCHEMA_OR_FROZEN_SHA');
 if(a.historical?.posts!==61||a.historical?.inline_images!==355||a.historical?.external_images!==288||a.historical?.wire_savings_76_percent_measured!==false)return hold('FALSE_HISTORICAL_CLAIM');
 if(!a.policy?.no_wordpress_write||!a.policy?.no_cache||!a.policy?.all_replacements_require_rights_scene_dimensions)return hold('UNSAFE_POLICY');
 if(!Array.isArray(a.posts)||a.posts.length!==9||!Array.isArray(a.records)||a.records.length!==61)return hold('MISSING_ROWS');
 const postMap=new Map(a.posts.map(x=>[x.id,x])),slots=new Map(frozen.rows.map(x=>[x.slot,x])),seen=new Set(),postCounts={},parts={pairs:0,missing_both:0,partial:0,html_entity_equivalent:0,p0:0};
 if(postMap.size!==9)return hold('DUPLICATE_POST');
 for(const [id,n] of Object.entries(expected)){const p=postMap.get(Number(id));if(!p||p.images!==n||!/^https:\/\/finalvestige\.com\//.test(p.url))return hold('POST_METADATA');}
 for(const row of a.records){
  if(!row||seen.has(row.slot)||!postMap.has(row.post_id)||!new RegExp('^'+row.post_id+':\\d+$').test(row.slot))return hold('SLOT_IDENTITY');
  seen.add(row.slot);postCounts[row.post_id]=(postCounts[row.post_id]||0)+1;
  const f=slots.get(row.slot),p=postMap.get(row.post_id);
  if(!f||row.post_url!==p.url||f.post_url!==p.url||f.stored_url!==row.frozen_src||norm(row.html_src)!==f.stored_url||row.parsed_src!==f.stored_url||row.source_host!==row.parsed_src.match(/^https:\/\/([^/]+)/i)?.[1])return hold('SOURCE_DRIFT');
  if(row.p0!==p0.has(row.slot)||typeof row.alt!=='string'||typeof row.candidate_rights!=='string')return hold('EDITORIAL_SOURCE_METADATA');
  const rawCandidate=f.candidate_sources?.[0]?.catalog_url||null;
  if(!row.p0&&row.candidate_catalog!==rawCandidate)return hold('CATALOG_TAMPER');
  for(const n of [row.width,row.height])if(n!==null&&(!Number.isSafeInteger(n)||n<=0))return hold('BAD_HTML_DIMENSIONS');
  if(row.width!==null&&row.height!==null)parts.pairs++;
  else if(row.width===null&&row.height===null)parts.missing_both++;
  else parts.partial++;
  if(row.html_src!==row.frozen_src)parts.html_entity_equivalent++;
  if(row.p0)parts.p0++;
  if(row.conditional_max_960_px!==null&&(!Array.isArray(row.conditional_max_960_px)||row.conditional_max_960_px.length!==2||row.conditional_max_960_px[0]>960||row.conditional_max_960_px.some(n=>!Number.isSafeInteger(n)||n<1)))return hold('INVALID_960_CANDIDATE');
  if(row.source_http_status!==null||row.browser_http_status!==null||row.decoded_px!==null||row.wire_bytes!==null||row.rights_cleared!==false||row.exact_scene_verified!==false||row.cache_allowed!==false||row.wp_edit_allowed!==false)return hold('FALSE_HTTP_RIGHTS_OR_RELEASE');
 }
 for(const [id,n] of Object.entries(expected)){if(postCounts[id]!==n)return hold('POST_ROW_COUNT');for(let i=0;i<n;i++)if(!seen.has(id+':'+i))return hold('MISSING_ORDINAL');}
 const c=a.counts;
 if(parts.pairs!==9||parts.missing_both!==52||parts.partial!==0||parts.html_entity_equivalent!==6||parts.p0!==6||c?.posts!==9||c?.images!==61||c?.source_drift!==0||c?.real_browser_tests!==0||c?.production_repairs!==0||Object.keys(parts).some(k=>c[k]!==parts[k]))return hold('AGGREGATE_MISMATCH');
 return {status:'VERIFIED_SOURCE_MARKUP_ONLY',images:61,missing_dimension_pairs:52,html_entity_equivalent:6,priority_source_matches:6,visitor_failures_confirmed:0,production_change_allowed:false};
}
module.exports={validate,norm};
