'use strict';
const fs=require('node:fs');
const frozenEvidence=Object.freeze({
  "source_method": "Frozen 2026-10-30 WP source census, 2026-11-14 LOC catalog and independent image retriever; no guest browser, origin HTTP or fresh WordPress edit read.",
  "post_url": "https://finalvestige.com/2026/08/20/the-cell-was-built-to-hold-a-man-mount-pelee/",
  "rights_note": "LOC no known restrictions is not an image-specific permission grant; verify exact 1902-1903 stereograph copyright, credit, provenance, and original two-eye frame before any reuse. https://data.labs.loc.gov/stereographs/README.html",
  "provenance": Object.freeze({
    "413:1": "LOC scene pre-1902; Underwood & Underwood stereograph published 1903; catalog has no-known-restrictions rights advisory and copyright note",
    "413:3": "LOC exact catalog not matched; frozen post ALT asserts early-morning eruption photo; event-time photographic evidence not established",
    "413:4": "LOC 1902 post-eruption looking north; older LOC caption-card data unverified; stereograph whole card visible",
    "413:5": "LOC 1902 post-eruption dead city and bay from Boulevard; older LOC caption-card data unverified; not verified as single-lens panorama"
  })
});
const fixed={
'413:1':['1s41590','1s41500','https://www.loc.gov/item/98504788/','RETRIEVER_INACCESSIBLE','PRE_ERUPTION_CITY_VIEW'],
'413:3':['1s41518','1s41500',null,'RETRIEVER_INACCESSIBLE','EVENT_TIME_UNVERIFIED'],
'413:4':['1s41424','1s41400','https://www.loc.gov/item/2006688499/','RETRIEVER_RENDERED','POST_ERUPTION_RUINS'],
'413:5':['1s41568','1s41500','https://www.loc.gov/item/2004680426/','RETRIEVER_INACCESSIBLE','POST_ERUPTION_RUINS']
};
function validate(a){
let errors=[],bad=s=>errors.push(s);
if(!a||Array.isArray(a)||typeof a!=='object')return {ok:false,errors:['not_object']};
if(a.schema!=='fv-pelee-413-loc-primary-custody-v1'||a.observation_date!=='2026-11-14')bad('schema_date');
if(a.source_snapshot?.git_blob!=='48e1ebf07207e948ba5802e714eb39659d2e1c1d'||a.source_snapshot?.path!=='qa/media-recovery/parts/02.json'||a.source_snapshot?.pr!==183)bad('source_snapshot');
if(a.post?.id!==413||a.post?.inline_images!==6||a.post?.loc_external_images!==4||a.post?.modified_frozen!=='2026-10-29T15:30:32')bad('post_custody');
if(a.source_method!==frozenEvidence.source_method||a.post?.url!==frozenEvidence.post_url||a.rights_note!==frozenEvidence.rights_note)bad('evidence_custody_drift');
const s=a.summary||{};
if(s.catalog_matched!==3||s.catalog_missing!==1||s.retriever_rendered!==1||s.retriever_inaccessible!==3||s.guest_broken_verified!==null||s.sitewide_reported_42!=='UNCONFIRMED'||s.sitewide_76_percent!=='UNMEASURED'||s.oversized_wp_originals!==16||s.oversized_wp_stored_bytes!==49107665)bad('inaccurate_measurements');
if(!Array.isArray(a.rows)||a.rows.length!==4)bad('four_rows');
let found=new Set();
for(let r of (Array.isArray(a.rows)?a.rows:[])){
let f=fixed[r?.slot];if(!f||found.has(r.slot)){bad('duplicate_or_foreign_slot');continue;}found.add(r.slot);
let url='https://tile.loc.gov/storage-services/service/pnp/stereo/1s40000/1s41000/'+f[1]+'/'+f[0]+'v.jpg';
if(r.digital_id!==f[0]||r.published_src!==url||r.loc_item!==f[2]||r.retriever_observation!==f[3]||r.scene_status!==f[4])bad('source_identity_drift:'+r.slot);
if(r.visitor_http_status!==null||r.visitor_current_src!==null||r.visitor_transfer_bytes!==null||r.origin_http_status!==null)bad('invented_guest_http:'+r.slot);
if(r.native_width_px!==null||r.native_height_px!==null||r.derivative_dimensions_px!==null||r.conditional_max_width_px!==960||r.full_stereo_pair_required!==true)bad('geometry_or_stereo_gate:'+r.slot);
if(r.binary_identity_verified!==false||r.right_to_rehost_cleared!==false||r.cache_allowed!==false||r.wordpress_write_allowed!==false||r.release_status!=='HOLD')bad('unauthorized_reuse:'+r.slot);
if(typeof r.provenance!=='string'||r.provenance.length<45)bad('missing_provenance:'+r.slot);
if(r.provenance!==frozenEvidence.provenance[r.slot])bad('provenance_or_chronology_drift:'+r.slot);
}
if(found.size!==4)bad('slot_count');
const p=a.release||{};
if(p.qa_browser_owner_pr!==154||p.priority!=='P1_BEHIND_SIX_P0'||p.no_upscale!==true||p.conditional_width_cap_px!==960||p.preserve_full_two_eye_pair!==true||p.guest_evidence_required!==true||p.rights_review_required!==true||p.visual_editorial_review_required!==true||p.wp_prod_writes!==0||p.image_downloads!==0||p.rehosted!==0||p.homepage_changes!==0||p.merged!==false||p.deployed!==false||p.subscription_usd!==0)bad('release_safety');
if(typeof a.rights_note!=='string'||!a.rights_note.includes('https://data.labs.loc.gov/stereographs/README.html'))bad('rights_source');
return {ok:errors.length===0,errors};
}
if(require.main===module){try{const v=validate(JSON.parse(fs.readFileSync(process.argv[2],'utf8')));console.log(JSON.stringify(v));if(!v.ok)process.exitCode=2;}catch(e){console.error(String(e));process.exitCode=2;}}
module.exports={validate};
