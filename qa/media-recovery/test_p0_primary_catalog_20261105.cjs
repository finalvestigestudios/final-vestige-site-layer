'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {verify}=require('./validate_p0_primary_catalog_20261105.cjs');
const data=JSON.parse(fs.readFileSync(path.join(__dirname,'p0_cdc_skyway_primary_catalog_20261105.json'),'utf8'));
const clone=()=>JSON.parse(JSON.stringify(data));
test('full primary source evidence ledger validates',()=>assert.deepEqual(verify(data),{pass:true,errors:[]}));
const cases=[
 ['invent_browser_failure',a=>a.rows[0].visitor_broken=true],
 ['invent_http_404',a=>a.rows[0].visitor_http_status=404],
 ['invent_http_200',a=>a.rows[1].visitor_http_status=200],
 ['invent_current_src',a=>a.rows[0].visitor_current_src=a.rows[0].published_source_url],
 ['invent_decode',a=>a.rows[1].visitor_natural_width=960],
 ['invent_wire_bytes',a=>a.rows[0].visitor_encoded_data_length=200000],
 ['call_wrapper_origin',a=>a.rows[1].retriever_observation.origin_http=true],
 ['call_wrapper_guest',a=>a.rows[0].retriever_observation.visitor_browser_http=true],
 ['old_src_drift',a=>a.rows[0].published_source_url+='?v=1'],
 ['skyway_alt_drift',a=>a.rows[1].published_alt='May 1980 collapse'],
 ['duplicate_key',a=>a.rows[1].key='285:5'],
 ['approve_wp',a=>a.rows[0].release.wp_upload_approved=true],
 ['approve_mirror',a=>a.rows[1].release.image_mirror_approved=true],
 ['approve_edit',a=>a.rows[1].release.published_post_edit_approved=true],
 ['bypass_guest',a=>a.rows[0].release.staging_requires_guest_failure=false],
 ['bypass_editorial',a=>a.rows[0].release.staging_requires_same_scene_editorial_review=false],
 ['bypass_binary',a=>a.rows[1].release.staging_requires_binary_decode=false],
 ['bypass_rights',a=>a.rows[0].release.staging_requires_source_attribution_and_disclaimer=false],
 ['bypass_screenshots',a=>a.rows[1].release.staging_requires_responsive_screenshots=false],
 ['claim_42',a=>a.scope.old_reported_broken_status='VERIFIED'],
 ['claim_76',a=>a.scope.claimed_reduction_status='MEASURED'],
 ['false_cdc_author',a=>a.rows[0].replacement_candidate.photographer='Unknown'],
 ['false_cdc_master_px',a=>a.rows[0].replacement_candidate.cdc_highres_intrinsic_px={width:2843,height:1817}],
 ['false_cdc_same_photo',a=>a.rows[0].replacement_candidate.identical_to_published_photo=true],
 ['false_cdc_master_identity',a=>a.rows[0].replacement_candidate.identical_to_official_cdc_master=true],
 ['omit_cdc_disclaimer',a=>a.rows[0].replacement_candidate.prominent_nonendorsement_disclaimer_required=false],
 ['omit_free_source',a=>a.rows[0].replacement_candidate.free_original_source_statement_required=false],
 ['omit_cdc_link',a=>a.rows[0].replacement_candidate.source_site_link_required=false],
 ['omit_cdc_credit',a=>a.rows[0].replacement_candidate.individual_credit_required=false],
 ['false_fl_date',a=>a.rows[1].replacement_candidate.catalog_date='1980-05-09'],
 ['false_fl_scene',a=>a.rows[1].replacement_candidate.depicts_old_and_replacement_bridge=false],
 ['false_fl_rights',a=>a.rows[1].replacement_candidate.rights_release_review='CLEARED'],
 ['false_fl_px',a=>a.rows[1].replacement_candidate.catalog_original_pixel_width=960],
 ['false_fl_alt_scene',a=>a.rows[1].replacement_candidate.alternate_rejected_for_this_alt.date='1987'],
 ['allow_upscale',a=>a.rows[1].replacement_candidate.no_upscale=false]
];
for(const [name,mutate] of cases)test('fail closed: '+name,()=>{const a=clone();mutate(a);assert.equal(verify(a).pass,false,name)});
