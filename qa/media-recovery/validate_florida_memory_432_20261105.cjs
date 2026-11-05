'use strict';
/** Fail-closed Florida Memory archival crosswalk. Read-only; metadata != license or browser proof. */
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const EXPECTED=[
 ['432:0','PR04493','4144','1928'],
 ['432:1','RC17068','38362','1928-09'],
 ['432:2','RC10673','33289','1928'],
 ['432:3','N031889','141398','1928'],
 ['432:4','RC04344','27848','1928'],
 ['432:5','RC07668','30741','1928'],
 ['432:6','MSF-PB11548-001','340182','2001']
];
const FROZEN_BLOB='948bc1b65b42799aa40cfdb810ddf6ffd80886b6';
function gitBlob(raw){const b=Buffer.isBuffer(raw)?raw:Buffer.from(raw,'utf8');
 return crypto.createHash('sha1').update(Buffer.from('blob '+b.length+'\\0')).update(b).digest('hex')}
function validateAudit(a,part){
 const errors=[],bad=(cond,msg)=>{if(!cond)errors.push(msg)};
 bad(a?.schema==='fv-media-florida-memory-archival-custody-v1','schema');
 bad(a?.input_source?.git_blob_sha===FROZEN_BLOB,'frozen_git_blob');
 bad(a?.article?.post_id===432&&a?.inventory_media_slots===7,'article_and_slots');
 bad(a?.primary_catalog_exact_path_matches===7,'catalog_claim');
 bad(Array.isArray(a?.images)&&a.images.length===7,'seven_records');
 bad(Array.isArray(part?.images),'inventory_missing');
 if(!Array.isArray(a?.images)||!Array.isArray(part?.images))return {ok:false,errors};
 const source=part.images.filter(i=>i.post_id===432);
 bad(source.length===7,'source_seven');
 const seen=new Set();
 for(let n=0;n<EXPECTED.length;n++){
  const [key,id,item,date]=EXPECTED[n],r=a.images[n],s=source.find(x=>x.key===key);
  if(!r||!s){errors.push('missing_slot:'+key);continue}
  bad(!seen.has(r.image_key),'duplicate_slot:'+key);seen.add(r.image_key);
  bad(r.image_key===key&&r.slot===n&&r.post_id===432,'slot_mapping:'+key);
  bad(r.post_url===s.post_url&&r.exact_published_alt===s.alt,'alt_or_post_mismatch:'+key);
  bad(r.exact_published_source_url===s.source_url&&r.exact_published_source_url.startsWith('https://www.floridamemory.com/fpc/'),'source_mismatch:'+key);
  bad(r.catalog_identifier===id&&r.catalog_date===date&&r.catalog_item_url==='https://www.floridamemory.com/items/show/'+item,'catalog_mismatch:'+key);
  bad(r.catalog_image_path===new URL(s.source_url).pathname&&r.catalog_image_url==='https://floridamemory.com'+r.catalog_image_path,'catalog_path_mismatch:'+key);
  bad(r.catalog_item_and_path_match===true&&r.catalog_verified_via==='publisher_indexed_metadata','catalog_provenance:'+key);
  bad(r.binary_identity_sha256===null&&r.binary_dimensions_px===null&&r.same_binary_proven===false,'no_binary_evidence:'+key);
  bad(r.origin_http_status===null&&r.visitor_http_status===null&&r.visitor_image_decoded===null&&r.actual_network_transfer_bytes===null&&r.final_browser_current_src===null,'no_browser_or_origin_evidence:'+key);
  bad(r.rights_status==='HOLD_ITEM_SPECIFIC_REPRODUCTION_AND_CREDIT_REVIEW'&&r.license_verified===false,'rights_hold:'+key);
  bad(r.max_allowed_derivative_width_px===960&&r.derivative_width_px===null&&r.derivative_height_px===null&&r.no_upscaling_required===true&&r.original_pixels_required===true,'no_invented_dimensions:'+key);
  bad(r.cache_or_rehost_allowed===false&&r.wordpress_production_write_allowed===false&&r.production_repair_confirmed===false,'no_production_authorization:'+key);
  bad(r.image_retriever_observation?.type==='not_tested'||r.image_retriever_observation?.type==='retriever_redirect_wrapper_error','source_observation_type:'+key);
  if(r.image_retriever_observation?.type==='retriever_redirect_wrapper_error')bad(r.image_retriever_observation.code===500,'wrapper_status_not_origin:'+key);
  if(n===6)bad(r.editorial_note?.includes('2001')&&r.catalog_date==='2001','modern_photo_date_must_be_explicit');
 }
 bad(a?.checks?.visitor_http_status_known===0&&a?.checks?.rights_cleared===0&&a?.checks?.production_repairs===0,'false_claim');
 bad(a?.release_gate?.wp_write_allowed===false&&a?.release_gate?.localization_allowed===false&&a?.release_gate?.no_upscale===true,'release_gate');
 return {ok:errors.length===0,errors,metrics:{records:a.images.length,catalog_path_matches:7,known_visitor_http:0,approved_replacements:0}};
}
if(require.main===module){
 const root=__dirname,read=x=>JSON.parse(fs.readFileSync(path.join(root,x),'utf8'));
 const raw=fs.readFileSync(path.join(root,'parts/01.json'));
 if(gitBlob(raw)!==FROZEN_BLOB)throw Error('Pinned source Git blob mismatch');
 const out=validateAudit(read('florida_memory_432_seven_originals_20261105.json'),JSON.parse(raw));
 console.log(JSON.stringify(out,null,2));if(!out.ok)process.exitCode=1;
}
module.exports={EXPECTED,FROZEN_BLOB,gitBlob,validateAudit};
