'use strict';
// Fail-closed, read-only validator for the 2026-11-04 seven-slot Florida Memory
// catalog/redirect audit. This validates SOURCE assertions, NOT live HTTP health.
// Node: node qa/media-recovery/validate_okeechobee_432_20261104.cjs path/to/audit.json
const EXPECTED_IDS = Object.freeze(['PR04493','RC17068','RC10673','N031889','RC04344','RC07668','MSF-PB11548-001']);
const EXPECTED_PATHS = Object.freeze([
 '/fpc/prints/pr04493.jpg','/fpc/reference/rc17068.jpg',
 '/fpc/reference/rc10673.jpg','/fpc/general/n031889.jpg',
 '/fpc/reference/rc04344.jpg','/fpc/reference/rc07668.jpg',
 '/fpc/msf/MSF-PB11548-001.jpg'
]);
const CATALOG_PAGES = Object.freeze(['4144','38362','33289','141398','27848','30741','340182']);
const EXPECTED_FLAGS = Object.freeze(['MATCH','PRECISION_IMPROVEMENT','MATCH','UNSUPPORTED_POST_DISASTER_TIMING','MATCH','MATCH','MODERN_SITE_PHOTOGRAPH_NOT_1928_EVENT']);
const FROZEN_PART_BLOB = '948bc1b65b42799aa40cfdb810ddf6ffd80886b6';
function validate(d) {
 const errors = [];
 const fail = (ok,msg) => { if(!ok) errors.push(msg); };
 fail(d && d.schema === 'fv.media_recovery.okeechobee_432.v1','schema');
 fail(d && d.audit_date === '2026-11-04' && d.mode === 'SOURCE_ONLY_READ_ONLY','date_or_mode');
 const s = d && d.frozen_inventory || {};
 fail(s.blob_sha === FROZEN_PART_BLOB && s.post_id === 432,'frozen_source_identity');
 fail(s.sitewide_posts === 61 && s.sitewide_slots === 355 && s.sitewide_external_origins === 288,'frozen_census');
 fail(s.reported_broken_unverified === 42 && s.claimed_wire_savings_percent_unmeasured === 76 && s.wordpress_originals_above_1_5_mib === 13,'not_verified_claims');
 const r = d && d.results || {};
 fail(r.slots === 7 && r.exact_primary_catalog_image_paths === 7 && r.www_to_apex_redirect_targets_observed === 7,'tally');
 fail(r.real_browser_checks === 0 && r.verified_origin_http_codes === 0 && r.verified_broken_images === 0 && r.production_replacements === 0,'no_unsubstantiated_production_or_http');
 fail(r.editorial_review_flags === 3,'editorial_count');
 fail(Array.isArray(d && d.images) && d.images.length === 7,'seven_slots');
 if (!Array.isArray(d && d.images) || d.images.length !== 7) return {ok:false,errors};
 const seen = new Set();
 d.images.forEach((im,i) => {
  const p = 'slot_'+i+'_';
  fail(im.key === '432:'+i && !seen.has(im.key),p+'ordered_identity');
  seen.add(im.key);
  const src='https://www.floridamemory.com'+EXPECTED_PATHS[i];
  const cat = im.primary_archive || {}, snap=im.snapshot||{}, net=im.retrieval||{}, ed=im.editorial||{}, fix=im.restoration||{};
  fail(snap.original_src === src && snap.git_blob_sha===FROZEN_PART_BLOB,p+'frozen_exact_src');
  fail(snap.post_url === s.post_url && typeof snap.alt==='string' && snap.alt.length>10,p+'original_post_and_alt');
  fail(cat.item_id===EXPECTED_IDS[i] && cat.catalog_url==='https://floridamemory.com/items/show/'+CATALOG_PAGES[i] && cat.catalog_image_path===EXPECTED_PATHS[i] && cat.exact_catalog_path_match===true,p+'primary_catalog_id_and_path');
  fail(net.original_requested===src && net.observed_redirect_target==='https://floridamemory.com'+EXPECTED_PATHS[i],p+'www_redirect');
  fail(net.method==='web.open text retriever, not browser' && net.tool_error==='500 wrapper cannot access redirected apex image',p+'transport_separation');
  for (const k of ['actual_origin_http_status','guest_browser_http_status','mime_type','guest_decoded','natural_width_px','natural_height_px','image_transfer_bytes','broken_for_visitors']) {
    fail(net[k]===null,p+'no_fabricated_'+k);
  }
  fail(ed.status===EXPECTED_FLAGS[i] && ed.production_caption_changed===false,p+'editorial_integrity');
  fail((i===1||i===3||i===6) ? typeof ed.suggested_alt_for_review==='string' && ed.suggested_alt_for_review.length>25 : ed.suggested_alt_for_review===null,p+'editorial_review_suggestions');
  fail(fix.primary_candidate_catalog===cat.catalog_url && fix.max_width_px===960 && fix.target_height_px===null && fix.original_intrinsic_width_px===null && fix.original_intrinsic_height_px===null && fix.no_upscale===true,p+'no_invented_geometry');
  fail(fix.license===null && fix.rights==='REVIEW_REQUIRED' && fix.binary_identity_verified===false,p+'rights_and_binary_hold');
  fail(fix.wordpress_upload_permitted===false && fix.local_cache_permitted===false && fix.post_rewrite_permitted===false,p+'publication_hold');
  fail(fix.required_credit==='State Archives of Florida, Florida Memory, '+EXPECTED_IDS[i],p+'credit');
 });
 return {ok:errors.length===0,errors};
}
module.exports={validate,EXPECTED_IDS,EXPECTED_PATHS};
if (typeof require==='function' && require.main===module) {
 const fs=require('node:fs'), path=process.argv[2];
 if(!path){process.stderr.write('Usage: node validate_okeechobee_432_20261104.cjs audit.json\n'); process.exitCode=2;}
 else {const result=validate(JSON.parse(fs.readFileSync(path,'utf8'))); process.stdout.write(JSON.stringify(result,null,2)+'\n');if(!result.ok) process.exitCode=1;}
}
