'use strict';
/** Offline integrity gate: Wikimedia request-width candidates are NOT publication approvals. */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const PREFIX='https://commons.wikimedia.org/wiki/Special:Redirect/file/';
const expected={historic_posts:61,historic_inline_image_refs:355,wikimedia_redirect_refs:118,width_1280_refs:75,width_960_refs:17,unbounded_width_refs:26,conditional_jpeg_960_candidates:68,format_or_detail_review_refs:7,gif_1280:1,png_1280:4,webp_1280:2};
function parseSource(s) {
 if(typeof s!=='string')return null;
 const m=/^https:\/\/commons\.wikimedia\.org\/wiki\/Special:Redirect\/file\/([^?#]+)(?:\?width=(960|1280))?$/.exec(s);
 if(!m)return null;
 return {title:m[1],width:m[2]?Number(m[2]):null,ext:(m[1].match(/\.([^.]+)$/)||[])[1]?.toLowerCase()||null};
}
function validate(report,parts,observedShas=null) {
 const errors=[],assert=(ok,msg)=>{if(!ok)errors.push(msg)};
 if(!report||!Array.isArray(report.rows)||!Array.isArray(report.sources)||!Array.isArray(parts)||parts.length!==8)
   return {ok:false,errors:['invalid_report_or_parts']};
 assert(report.schema==='fv-wikimedia-width-census-v1','schema');
 assert(report.method==='OFFLINE_PINNED_61_POST_WORDPRESS_STORED_SRC_NO_BROWSER_NETWORK','method');
 assert(report.historical_42_report==='VISITOR_UNVERIFIED'&&report.historical_76_percent_transfer_reduction==='UNMEASURED','claims');
 assert(report.wordpress_production_writes===0&&report.assets_downloaded===0&&report.cache_upload_or_publication_authorized===false,'safety');
 assert(JSON.stringify(report.totals)===JSON.stringify(expected),'totals');
 const source=[],postMap=new Map(),all=[];
 parts.forEach((part,i)=>{
   assert(!!part&&part.batch===i+1&&Array.isArray(part.posts)&&Array.isArray(part.images),'part:'+i);
   if(!part||!Array.isArray(part.posts)||!Array.isArray(part.images))return;
   part.posts.forEach(p=>{assert(!postMap.has(p.id),'duplicate_post:'+p.id);postMap.set(p.id,p)});
   part.images.forEach(s=>{all.push(s);if(s.source_kind==='wikimedia_redirect')source.push(s)});
   assert(report.sources[i]?.path==='qa/media-recovery/parts/'+String(i+1).padStart(2,'0')+'.json','part_path:'+i);
   assert(/^[a-f0-9]{40}$/.test(report.sources[i]?.git_blob_sha||''),'part_blob:'+i);
   if(observedShas)assert(report.sources[i]?.git_blob_sha===observedShas[i],'part_sha_changed:'+i);
 });
 assert(postMap.size===61&&all.length===355&&source.length===118,'inventory_counts');
 assert(report.rows.length===source.length,'row_count');
 const byKey=new Map(source.map(x=>[x.key,x]));assert(byKey.size===source.length,'source_duplicate_keys');
 const seen=new Set(),counts={w1280:0,w960:0,unbounded:0,jpeg:0,nonjpeg:0,gif:0,png:0,webp:0};
 for(const row of report.rows){
  const key=row?.image_key,raw=byKey.get(key);
  assert(!seen.has(key),'duplicate_row:'+key);seen.add(key);
  if(!raw){errors.push('unknown_key:'+key);continue;}
  const p=parseSource(raw.source_url);
  assert(!!p,'invalid_frozen_url:'+key);if(!p)continue;
  assert(row.post_id===raw.post_id&&key===raw.post_id+':'+raw.slot&&row.post_url===postMap.get(raw.post_id)?.url,'post_slot_binding:'+key);
  assert(row.exact_stored_source_url===raw.source_url&&row.stored_alt===raw.alt,'source_or_caption_changed:'+key);
  assert(row.commons_file_catalog_url==='https://commons.wikimedia.org/wiki/File:'+p.title,'catalog_identity:'+key);
  assert(row.source_ext===p.ext&&row.stored_requested_width_px===p.width,'file_metadata:'+key);
  assert(row.source_native_px===null&&row.guest_current_src===null&&row.guest_http_status===null&&row.guest_decoded_px===null&&row.guest_encoded_transfer_bytes===null,'invented_guest_evidence:'+key);
  assert(row.network_savings_measured===false&&row.per_file_license_reverified===false&&row.cached_or_rehosted===false,'claims_or_download:'+key);
  assert(row.rights_and_attribution_review==='HOLD'&&row.visual_readability_review==='HOLD'&&row.native_geometry_review==='HOLD'&&row.no_upscale===true&&row.wordPress_production_write_authorized===false,'release_gate:'+key);
  const eligible=p.width===1280&&p.ext==='jpg';
  if(p.width===1280){counts.w1280++;if(eligible)counts.jpeg++;else{counts.nonjpeg++;if(['gif','png','webp'].includes(p.ext))counts[p.ext]++}}
  else if(p.width===960)counts.w960++;else counts.unbounded++;
  const priority=eligible?'CONDITIONAL_JPEG_960_QUERY_CANDIDATE':p.width===1280?'FORMAT_OR_DETAIL_REVIEW':p.width===960?'ALREADY_REQUESTS_960':'NO_WIDTH_BOUND_QUERY_REVIEW';
  assert(row.priority===priority,'priority:'+key);
  const target=eligible?raw.source_url.replace(/\?width=1280$/,'?width=960'):null;
  assert(row.conditional_960_url===target&&row.conditional_target_width_px===(eligible?960:null)&&row.conditional_target_height_px===null,'candidate_url_or_geometry:'+key);
  assert(row.same_file_title_preserved===(eligible?true:null),'same_file_title:'+key);
 }
 assert(seen.size===source.length,'missing_slots');
 assert(counts.w1280===75&&counts.w960===17&&counts.unbounded===26&&counts.jpeg===68&&counts.nonjpeg===7&&counts.gif===1&&counts.png===4&&counts.webp===2,'recomputed_counts');
 return {ok:errors.length===0,errors:[...new Set(errors)],counts};
}
function loadLocal(root=__dirname) {
 const report=JSON.parse(fs.readFileSync(path.join(root,'wikimedia_118_width_960_census_20261108.json'),'utf8'));
 const buffers=Array.from({length:8},(_,i)=>fs.readFileSync(path.join(root,'parts',String(i+1).padStart(2,'0')+'.json')));
 const shas=buffers.map(buf=>crypto.createHash('sha1').update('blob '+buf.length+'\0').update(buf).digest('hex'));
 return validate(report,buffers.map(b=>JSON.parse(b.toString('utf8'))),shas);
}
if(require.main===module){const result=loadLocal();process.stdout.write(JSON.stringify(result,null,2)+'\n');if(!result.ok)process.exitCode=2;}
module.exports={validate,parseSource,loadLocal};
