'use strict';
/** Franklin post 433 provenance/rights gate. Offline, no network or CMS writes. */
const fs=require('node:fs'),path=require('node:path');
const expected={
 '433:1':{license:'PD_OLD_RECORD',dims:[750,523]},
 '433:2':{license:'PD_US_PRE_1931_RECORD',dims:[399,600]},
 '433:3':{license:'PD_OLD_RECORD',dims:[1477,2357]},
 '433:4':{license:'CC_BY_SA_4_0',dims:[3284,3966]},
 '433:5':{license:'PD_OLD_CANDIDATE_RIGHTS_HELD',dims:[726,1119]}
};
const file=p=>JSON.parse(fs.readFileSync(path.join(__dirname,p),'utf8'));
function validate(manifest,census){
 const errors=[],rows=Array.isArray(manifest?.rows)?manifest.rows:[],source=census?.images||[];
 if(manifest?.schema_version!==1||manifest?.scope?.post_id!==433)errors.push('schema_or_scope');
 if(rows.length!==5||new Set(rows.map(x=>x.image_key)).size!==5)errors.push('image_count_or_keys');
 if(manifest?.scope?.verified_browser_failures!==null||manifest?.scope?.reported_76pct_weight_reduction!=='NOT_MEASURED')errors.push('false_live_claim');
 if(manifest?.staging_cache_plan?.production_writes_authorized!==false)errors.push('production_write_gate');
 for(const r of rows){
  const x=source.find(s=>s.key===r.image_key),spec=expected[r.image_key];
  if(!x||!spec||x.source_url!==r.stored_url||x.alt!==r.stored_alt)errors.push('source_identity:'+r.image_key);
  if(r.post_id!==433||r.post_url!==x?.post_url||!/^https:\/\//.test(r.primary_record_url||''))errors.push('archive_identity:'+r.image_key);
  if(r.license_marker!==spec?.license||!r.rights_evidence||!r.credit_candidate||!r.review_note)errors.push('rights_metadata:'+r.image_key);
  const [w,h]=spec?.dims||[null,null],k=Math.min(1,960/w);
  if(!Number.isInteger(r.candidate_target_width_px)||!Number.isInteger(r.candidate_target_height_px)||
     r.candidate_target_width_px!==Math.round(w*k)||r.candidate_target_height_px!==Math.round(h*k)||
     r.max_width_px!==960||r.no_upscale!==true||r.preserve_aspect_ratio!==true)errors.push('size_policy:'+r.image_key);
  if(r.image_key==='433:5'){
   if(r.original_width_px!==null||r.original_height_px!==null||
      r.candidate_original_width_px!==726||r.candidate_original_height_px!==1119||
      r.viewer_decoded_offsite_source!==true||
      !r.candidate_same_document_url?.includes('Reward_for_finding_Franklin_Expedition'))
      errors.push('poster_provenance');
  }else if(r.original_width_px!==w||r.original_height_px!==h)errors.push('claimed_resolution:'+r.image_key);
  if(r.verified_broken_in_visitor_browser!==null||r.actual_visitor_http_status!==null||
     r.actual_decoded_width_px!==null||r.actual_transferred_bytes!==null||
     r.source_binary_sha256!==null||r.wp_media_id!==null||
     r.wp_upload_authorized!==false||r.wp_post_rewrite_authorized!==false||
     r.rights_clearance_for_republication!==false)errors.push('false_live_or_rights_claim:'+r.image_key);
  if(r.image_key==='433:4'&&!/CC BY-SA 4\.0/.test(r.rights_evidence||''))errors.push('missing_modern_photo_license');
 }
 return{ok:errors.length===0,errors,rows:rows.length};
}
if(require.main===module){const result=validate(file('franklin_433_primary_20261031.json'),file('parts/01.json'));console.log(JSON.stringify(result,null,2));if(!result.ok)process.exitCode=1}
module.exports={validate};
