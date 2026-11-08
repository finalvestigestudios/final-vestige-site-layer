'use strict';
const SRC={
 '418:1':'https://media.defense.gov/2021/Mar/30/2002610812/1920/1080/0/210330-G-DE713-0002.JPG',
 '407:1':'https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg'
};
function validate(a){
 const e=[],fail=s=>e.push(s);
 if(a?.schema!=='fv-p0-4181-4071-item-rights-and-media-path-v1'||a?.prior_p0_ledger?.git_blob_sha!=='9bf9a973fce37a546f8c3e79ecd0c34345eb2457')fail('frozen_provenance');
 if(a?.historical_42_broken!=='NOT_GUEST_VERIFIED'||a?.claimed_76pct_wire_reduction!=='UNMEASURED'||a?.verified_guest_broken_total!==null)fail('unsupported_sitewide_claim');
 if(a?.production_repaired!==0||a?.assets_downloaded!==0||a?.wordpress_writes!==0||a?.publication_authorized!==false)fail('production_unsafe');
 if(!Array.isArray(a?.records)||a.records.length!==2)return {ok:false,errors:[...e,'row_count']};
 const by=Object.fromEntries(a.records.map(r=>[r.image_key,r]));
 if(Object.keys(by).length!==2)fail('duplicate_or_wrong_keys');
 for(const [key,url] of Object.entries(SRC)){
  const r=by[key];if(!r){fail('missing_'+key);continue}
  if(r.post_id!==Number(key.split(':')[0])||r.original_stored_src!==url)fail('source_binding_'+key);
  const obs=r.original_retrieval||{};
  if(obs.method!=='web.open_retriever'||obs.date!=='2026-11-08'||obs.is_origin_http!==false||obs.is_guest_browser_http!==false||obs.guest_http!==null||obs.guest_decode!==null||obs.guest_bytes!==null)fail('false_guest_evidence_'+key);
  const c=r.candidate||{};
  if(c.max_long_edge_px!==960||c.no_upscale!==true||c.binary_sha256!==null||c.cache_or_upload_authorized!==false||c.exact_scene_match_approved!==false||!String(c.wordpress_action).startsWith('HOLD_'))fail('release_gate_'+key);
  if(!r.rights?.credit_required||!String(r.rights.rights_gate).includes('CATALOG'))fail('rights_gate_'+key);
 }
 const uscg=by['418:1']||{}, usgs=by['407:1']||{};
 if(uscg.original_retrieval?.wrapper_http_code!==403||uscg.original_retrieval?.wrapper_result!=='FORBIDDEN')fail('uscg_wrapper');
 if(uscg.item?.official_virin!=='210330-G-DE713-0002.JPG'||!uscg.item?.catalog_identifies?.includes('Anthony Pettit')||!uscg.item?.catalog_identifies?.includes('NOT lighthouse debris'))fail('uscg_scene');
 if(uscg.item?.primary_catalog!=='https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/'||uscg.item?.by!=='U.S. Coast Guard'||uscg.rights?.item_statement!=='photo considered public domain and cleared for release')fail('uscg_item_license');
 if(uscg.frozen_post_source?.blob_sha!=='948bc1b65b42799aa40cfdb810ddf6ffd80886b6'||!uscg.stored_alt?.includes('Anthony L. Petit')||uscg.item?.name_variants?.official_photo_caption!=='Anthony Pettit'||uscg.item?.name_variants?.official_2021_uscg_remembrance_roll!=='Chief Boatswain Anthony L. Petit'||uscg.item?.name_variants?.editorial_decision!=='DO_NOT_AUTOCORRECT_PUBLISHED_ALT')fail('uscg_primary_spelling_conflict');
 if(usgs.frozen_post_source?.blob_sha!=='48e1ebf07207e948ba5802e714eb39659d2e1c1d'||!usgs.stored_alt?.includes('August 1959'))fail('usgs_source_alt');
 if(uscg.candidate?.original_px!==null||uscg.candidate?.proposed_px!==null||uscg.candidate?.relationship!=='OFFICIAL_VIRIN_SAME_FILENAME_NOT_BINARY_MATCH')fail('uscg_unknown_dimensions');
 if(usgs.original_retrieval?.wrapper_http_code!==400||usgs.original_retrieval?.wrapper_result!=='UNSUPPORTED_BINARY_OCTET_STREAM')fail('usgs_wrapper');
 if(usgs.item?.primary_catalog!=='https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959'||usgs.item?.candidate_image_url!=='https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/thumbnails/image/img7535.jpg')fail('usgs_path');
 if(usgs.item?.catalog_usage!=='Public Domain'||usgs.item?.by!=='J. R. Stacy (USGS)'||usgs.item?.native_px_verified!==false||usgs.item?.candidate_web_viewer!=='RENDERED')fail('usgs_catalog_evidence');
 if(JSON.stringify(usgs.item?.candidate_web_viewer_display_px)!=='[1000,1000]'||usgs.candidate?.original_px!==null||JSON.stringify(usgs.candidate?.proposed_px)!=='[960,960]'||usgs.candidate?.proposed_px_is_conditional!==true)fail('usgs_conditional_geometry');
 return {ok:e.length===0,errors:e};
}
module.exports={validate};
if(typeof require==='function'&&require.main===module){const fs=require('node:fs');const doc=JSON.parse(fs.readFileSync(process.argv[2]||__dirname+'/p0_4181_4071_item_rights_20261108.json','utf8'));const res=validate(doc);console.log(JSON.stringify(res));if(!res.ok)process.exitCode=1}
