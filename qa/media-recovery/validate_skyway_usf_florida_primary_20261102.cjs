'use strict';
/* Offline, fail-closed catalog-only validator; never fetches or writes media. */
const fs = require('node:fs');
const path = require('node:path');
const EXPECTED = new Map([
  ['USF Gandy 21_1014', ['https://digitalcommons.usf.edu/gandy/4785/', '1982-01-28', true]],
  ['USF Gandy 21_0970', ['https://digitalcommons.usf.edu/gandy/4742/', '1982-01-28', true]],
  ['Florida Memory RC09236', ['https://floridamemory.com/items/show/32082', '1980-05-09', false]],
  ['Florida Memory RC09237', ['https://www.floridamemory.com/items/show/32083', '1980-05-09', false]],
]);
const isHttps = s => typeof s === 'string' && /^https:\/\/[^\s/]+\//.test(s);
function validate(a) {
  const errors=[]; const fail=(why)=>errors.push(why);
  if(a?.schema_version!==1 || a?.kind!=='primary_archive_license_and_scene_crosswalk_not_guest_browser_audit') fail('schema/label');
  const i=a?.investigation, c=a?.catalog_checks, s=a?.sitewide_context;
  if(i?.image_key!=='287:5' || i?.article_url!=='https://finalvestige.com/2026/08/19/the-warning-was-a-man-waving-sunshine-skyway/' || i?.published_source_url!=='https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg' || i?.published_alt!=='The old Sunshine Skyway wreckage and the later bridge replacement in Tampa Bay.') fail('published identity');
  if(i?.retriever_observation?.method!=='independent_web_retriever_prior_committed_batch' || i?.retriever_observation?.result!=='retriever_404' || i?.retriever_observation?.wrapper_code!==404) fail('source retriever provenance');
  for(const [key,v] of [['origin',i?.retriever_observation?.origin_http_status],['guest',i?.retriever_observation?.guest_browser_http_status],['wire',i?.retriever_observation?.guest_transfer_bytes],['decode',i?.retriever_observation?.guest_image_decoded]]) if(v!==null) fail('invented source '+key);
  if(i?.original_photo_identity_verified!==false||i?.production_repair_count!==0) fail('original identity or repairs');
  if(c?.catalog_http_status!==null||c?.binary_http_status!==null||c?.browser_status!==null) fail('invented catalog HTTP');
  if(!Array.isArray(a?.candidates)||a.candidates.length!==EXPECTED.size) fail('candidate count');
  const seen=new Set();
  for(const p of a?.candidates||[]) {
    if(seen.has(p?.record_id)) fail('duplicate candidate'); seen.add(p?.record_id);
    const e=EXPECTED.get(p?.record_id);
    if(!e||p.catalog_url!==e[0]||p.photographed_on!==e[1]||p.catalog_explicit_license!==e[2]) fail('catalog identity/date/license '+p?.record_id);
    if(!isHttps(p?.catalog_url)||!p?.creator||!p?.catalog_subject||!p?.scene_vs_published||!p?.record_identification_method) fail('missing identity/source '+p?.record_id);
    if(!p?.scene_vs_published.includes('different')) fail('alternate scene not disclosed '+p?.record_id);
    if(p.catalog_explicit_license) {
      if(p.catalog_license_statement!=='Creative Commons Attribution 3.0 License'||p.license_url!=='https://creativecommons.org/licenses/by/3.0/'||!p.credit_plan.includes('CC BY 3.0')) fail('CC BY 3.0 provenance/attribution '+p.record_id);
    } else if(p.catalog_license_statement!==null||p.license_url!==null||!String(p.license_confidence).includes('no_republication_grant')) fail('Florida Memory invented license '+p.record_id);
    if(p.master_dimensions_px!==null||p.preview_dimensions_px!==null||p.conditional_resize?.output_dimensions_px!==null||p.conditional_resize?.max_width_px!==960||p.conditional_resize?.no_upscale!==true||p.conditional_resize?.needs_binary_geometry!==true) fail('invented geometry or unauthorized upscaling '+p.record_id);
    for(const field of ['image_binary_downloaded','matched_published_photo_binary','rights_review_complete','cache_to_wordpress_authorized','publish_authorized']) if(p[field]!==false) fail('unsupported release/media claim '+p.record_id+' '+field);
    if(p.editorial_alt_and_caption_revision_needed!==true) fail('silently changing historical image '+p.record_id);
    if(p.media_binary_url!==null && !isHttps(p.media_binary_url)) fail('binary URL invalid '+p.record_id);
  }
  if(seen.size!==EXPECTED.size) fail('missing expected IDs');
  if(s?.published_post_inventory!==61 || s?.stored_inline_image_references!==355 || JSON.stringify(s?.external_reference_count_snapshot_discrepancy)!=='[286,288]' || s?.wordpress_originals_over_1_5_mib!==13 || s?.images_repaired_in_production!==0 || s?.reported_42_broken_chrome_verified!==false || s?.claimed_76_percent_transfer_savings_measured!==false) fail('sitewide overclaim');
  for(const key of ['wordpress_production_write','homepage_design_modification','site_qa_pr_154_modified','unlicensed_media_scrape','subscription_spend']) if(a?.safety?.[key]!==false) fail('unsafe action asserted: '+key);
  for(const key of ['first','second','third','fourth','fifth']) if(typeof a?.workflow_gate?.[key]!=='string'||a.workflow_gate[key].length<20) fail('missing safe workflow gate: '+key);
  return {ok:errors.length===0,errors};
}
function load(file=path.join(__dirname,'skyway_usf_florida_primary_recovery_20261102.json')) {return JSON.parse(fs.readFileSync(file,'utf8'));}
if(require.main===module) {const res=validate(load(process.argv[2])); console.log(JSON.stringify(res)); if(!res.ok)process.exitCode=1;}
module.exports={validate,load};
