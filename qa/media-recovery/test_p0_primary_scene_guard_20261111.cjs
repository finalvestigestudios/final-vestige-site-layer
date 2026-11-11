'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {validate}=require('./validate_p0_primary_scene_guard_20261111.cjs');
const baseline=JSON.parse(fs.readFileSync(path.join(__dirname,'p0_primary_scene_guard_20261111.json'),'utf8'));
const clone=()=>JSON.parse(JSON.stringify(baseline));
assert.equal(validate(baseline).pass,true,JSON.stringify(validate(baseline).errors));
const mutations=[
  ["invented_browser_404", d=>{d.items[0].guest_http_status=404;}],
  ["invented_200", d=>{d.items[0].actual_origin_http_status=200;}],
  ["forged_current_src", d=>{d.items[1].guest_current_src='https://example.org/impostor.jpg';}],
  ["forged_pixels", d=>{d.items[2].guest_natural_px=[960,540];}],
  ["invented_wire_bytes", d=>{d.items[0].cold_encoded_image_bytes=40000;}],
  ["invented_native_size", d=>{d.items[0].native_dimensions_verified=[960,540];}],
  ["invented_derivative_size", d=>{d.items[1].conditional_candidate_output_dimensions=[960,540];}],
  ["image_width_upscale", d=>{d.items[2].max_width_px_without_upscale=1920;}],
  ["claim_guest_broken", d=>{d.items[0].guest_failure_confirmed=true;}],
  ["claim_full_42", d=>{d.sitewide.confirmed_guest_broken=42;}],
  ["claim_savings", d=>{d.sitewide.actual_savings_pct=76;}],
  ["fake_binary_match", d=>{d.items[0].exact_binary_or_crop_identity_proven=true;}],
  ["rights_by_catalog_alone", d=>{d.items[2].commercial_reuse_approval=true;}],
  ["wrong_1946_date", d=>{d.items[1].primary_evidence.depicted_historical_year=1964;}],
  ["portrait_mislabeled_debris", d=>{d.items[0].primary_evidence.primary_description_subject='SCOTCH_CAP_DEBRIS';}],
  ["stacy_mislabeled_exact", d=>{d.items[2].primary_evidence.notes='Same photo as S3 original';}],
  ["wrong_usgs_artist", d=>{d.items[2].primary_evidence.catalog_url='https://example.org/stock.jpg';}],
  ["wrong_filenamed_portrait", d=>{d.items[0].primary_evidence.item_identifier='wrong.jpg';}],
  ["false_download_measurement", d=>{d.items[0].primary_evidence.advertised_download_size_mb_not_transfer=40000;}],
  ["source_swapped", d=>{d.items[0].exact_published_original_url=d.items[1].exact_published_original_url;}],
  ["slots_reordered", d=>{d.items.reverse();}],
  ["broken_proven_by_403_wrapper", d=>{d.items[1].independent_retriever_only.result='HTTP_403_CONFIRMED';}],
  ["wordpress_upload", d=>{d.items[0].wordpress_upload_approval=true;}],
  ["cache_without_rights", d=>{d.items[0].wordpress_cache_approval=true;}],
  ["editor_approved", d=>{d.items[0].editor_scene_signoff=true;}],
  ["claim_prod_write", d=>{d.production_changes=1;}],
  ["swap_source_evidence", d=>{d.items[0].primary_evidence.source_urls[0]=d.items[1].primary_evidence.source_urls[0];}],
  ["break_audit_lineage", d=>{d.authority.source_bridge_blob_sha='f'.repeat(40);}],
  ["invented_published_post_count", d=>{d.sitewide.historical_posts=66;}],
  ["prod_permitted", d=>{d.items[2].production_write_permitted=true;}]
];
for(const [name,mutate] of mutations){const d=clone();mutate(d);assert.equal(validate(d).pass,false,'admitted forged provenance: '+name);}
console.log('PASS '+(mutations.length+1)+'/'+(mutations.length+1)+' P0 provenance/scene/rights fail-closed checks');
