'use strict';
/** Source-only New London school image audit: no HTTP requests, downloads, or WordPress writes. */
const fs = require('node:fs');
const path = require('node:path');
const EXPECTED = Object.freeze([
  ['New_London_School_explosion.jpg',760,609,'PD-US-not-renewed','The shattered New London School after the March 18, 1937 gas explosion, with rescuers gathered around the ruins.'],
  ['New_London_School_before_explosion.webp',960,685,'PD-US-not-renewed','London School in East Texas before the March 1937 explosion, showing the large modern school building intact.'],
  ['INP_Photos_of_New_London_School_explosion.jpg',2861,2244,'PD-scan/PD-US-not-renewed','Rescuers and debris at New London School after the 1937 explosion, photographed for International News Photos.'],
  ['INP_Photos_of_New_London_School_explosion_(1).jpg',2457,1950,'PD-scan/PD-US-not-renewed','Emergency workers at the New London School ruins after the March 1937 explosion.'],
  ['INP_Photos_of_New_London_School_explosion_(2).jpg',2457,1862,'PD-scan/PD-US-not-renewed','Rescue and recovery activity among the wreckage of New London School after the gas explosion.'],
  ['New_London_School_Explosion_Memorial_-_46699056584.jpg',3840,2160,'CC-BY-SA-2.0','New London School Explosion Memorial in Texas, photographed in 2016.']
]);
const BASE = 'https://commons.wikimedia.org/wiki/';
function validate(a) {
  const errors=[]; const check=(x,msg)=>{if(!x)errors.push(msg);};
  if(!a||typeof a!=='object') return {ok:false,errors:['not an object']};
  check(a.schema_version===1,'schema');
  check(a.audited_date==='2026-11-05','audit date');
  check(a.audit_method.includes('no visitor Chrome'),'scope');
  check(a.source_snapshot?.blob_sha==='0f3dfe398a76838049cebba7cb773d5c5a0c8c69','inventory SHA');
  check(a.source_snapshot?.part_path==='qa/media-recovery/parts/06.json','inventory part');
  check(a.source_snapshot?.post_modified_at_inventory==='2026-10-29T16:04:52','inventory modified date');
  check(a.article?.id===217 && a.article?.url==='https://finalvestige.com/2026/08/18/the-gas-had-no-smell/','article identity');
  check(Array.isArray(a.images)&&a.images.length===6,'six slots');
  const keys=new Set();
  for(const [i, e] of EXPECTED.entries()) {
    const x=a.images?.[i]; if(!x){errors.push('missing slot '+i);continue;}
    const [name,w,h,rights,alt]=e;
    const expectedSource=BASE+'Special:Redirect/file/'+encodeURIComponent(name)+'?width=1280';
    const expectedCatalog=BASE+'File:'+encodeURIComponent(name);
    check(x.key==='217:'+i && x.post_id===217 && x.slot===i && !keys.has(x.key),'slot '+i);
    keys.add(x.key);
    check(x.source_url===expectedSource && x.catalog_url===expectedCatalog && x.same_file_title_verified===true,'source/title '+i);
    check(x.published_alt===alt,'published alt '+i);
    check(x.catalog_original_width_px===w && x.catalog_original_height_px===h,'catalog dimensions '+i);
    check(x.requested_redirect_width_px===1280,'request width '+i);
    const dw=Math.min(960,w), dh=Math.round(h*dw/w);
    check(x.conditional_derivative_width_px===dw && x.conditional_derivative_height_px===dh && dw<=w && dh<=h,'no-upscale geometry '+i);
    check(x.catalog_license_claim===rights && typeof x.catalog_credit==='string' && x.catalog_credit.length>2,'rights claim/credit '+i);
    check(x.source_http_status===null && x.browser_http_status===null && x.visitor_image_broken===null && x.visitor_natural_width_px===null && x.network_transferred_bytes===null,'no invented HTTP/decode/wire '+i);
    check(x.binary_hash_verified===false && x.rights_cleared_for_fv_republication===false && x.rehost_authorized===false && x.wp_write_authorized===false && x.replace_published_source_authorized===false,'no premature permission '+i);
  }
  check(Array.isArray(a.primary_custodial_alternatives)&&a.primary_custodial_alternatives.length===3,'three archived alternatives');
  for(const x of a.primary_custodial_alternatives||[]) {
    check(/^https:\/\//.test(x.catalog_url||'') && x.exact_original_photo_match===false && x.reuse_status==='HOLD' && x.catalog_http_status===null && x.pixel_dimensions===null,'alternative provenance and rights');
  }
  const uta=a.primary_custodial_alternatives?.find(x=>x.archive?.includes('Arlington'));
  check(uta?.catalog_identifier==='10013106' && uta?.license.includes('CC BY-NC 4.0') && uta?.license.includes('commercial use NOT approved'),'UTA commercial restriction');
  check((a.visual_integrity_findings||[]).length>=5,'chronology and source risks');
  check(a.visual_integrity_findings?.some(x=>x.key==='217:0' && x.finding.includes('17 March 1937') && x.post_change_proposed===false),'anachronism flag');
  check(a.visual_integrity_findings?.some(x=>x.key==='217:5' && x.finding.includes('CC BY-SA 2.0') && x.post_change_proposed===false),'memorial license flag');
  const b=a.baseline||{};
  check(b.post_count_frozen===61 && b.image_slots_frozen===355 && b.offsite_source_refs_frozen===288,'census frozen');
  check(b.reported_broken_42==='NOT_BROWSER_VERIFIED' && b.claimed_76_percent_transfer_savings==='NOT_MEASURED','unverified claims');
  check(b.first_party_originals_over_1_5MiB===13 && b.first_party_oversized_original_storage_bytes===43522829 && b.production_repairs_this_batch===0,'stored not wire');
  const r=a.release_gates||{};
  check(r.max_width_px===960 && r.no_upscale===true && r.visitor_browser_test_required===true && r.source_and_rights_review_required===true && r.visual_comparison_required===true && r.attribution_review_required===true,'release review gates');
  check(r.wordpress_media_import_approved===false && r.production_changes_approved===false && r.third_party_binary_download_approved===false,'no production or download authority');
  return {ok:errors.length===0,errors,metrics:{catalog_records:keys.size,requested_width_gt_original:a.images?.filter(x=>x.requested_redirect_width_px>x.catalog_original_width_px).length||0,browser_confirmed_broken:0,publication_actions:0}};
}
if(require.main===module){
  try{const a=JSON.parse(fs.readFileSync(path.join(__dirname,'new_london_217_six_catalog_20261105.json'),'utf8'));const out=validate(a);console.log(JSON.stringify(out,null,2));if(!out.ok)process.exitCode=1;}
  catch(err){console.error('SOURCE_AUDIT_ERROR',err.message);process.exitCode=2;}
}
module.exports={validate,EXPECTED};
