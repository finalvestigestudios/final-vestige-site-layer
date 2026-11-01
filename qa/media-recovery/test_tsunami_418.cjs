'use strict';
// Offline adversarial Node regression tests; source and CMS remain read-only.
const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {validateTsunami418}=require('./validate_tsunami_418.cjs');
const ORIGINAL=JSON.parse(fs.readFileSync(path.join(__dirname,'tsunami_418_uscg_noaa_usgs_20261101.json'),'utf8'));
const clone=()=>JSON.parse(JSON.stringify(ORIGINAL));
test('valid six-slot publisher custody ledger',()=>{
 assert.deepEqual(validateTsunami418(clone()),{ok:true,validated_slots:6,web_retriever_not_browser:true,production_writes_allowed:0});
});
const mutations=[
 ["false guest 404",d=>{d.rows[2].browser.status=404;}],
 ["false guest proof",d=>{d.rows[2].browser.logged_out_verified=true;}],
 ["false currentSrc",d=>{d.rows[2].browser.current_src='https://fake.invalid';}],
 ["false content type",d=>{d.rows[1].browser.content_type='image/jpeg';}],
 ["false decoded dimensions",d=>{d.rows[5].browser.natural_width_px=1024;}],
 ["false guest image bytes",d=>{d.rows[5].browser.encoded_transfer_bytes=100;}],
 ["false screenshot",d=>{d.rows[1].browser.failed_visible_screenshot='fake.png';}],
 ["false origin response",d=>{d.rows[1].viewer.origin_http_status=403;}],
 ["false final image HTTP",d=>{d.rows[1].viewer.final_image_http_status=403;}],
 ["false retriever bytes",d=>{d.rows[4].viewer.encoded_transfer_bytes=9999;}],
 ["false retriever decoded width",d=>{d.rows[4].viewer.decoded_natural_width_px=909;}],
 ["false viewer category",d=>{d.rows[1].viewer.result='RETRIEVER_RENDERED';}],
 ["false retriever code",d=>{d.rows[2].viewer.retriever_error_code=200;}],
 ["fake Chrome method",d=>{d.rows[0].viewer.method='Chrome visitor';}],
 ["false 42 broken",d=>{d.claimed_broken_42_verified=true;}],
 ["false 76 percent",d=>{d.claimed_76pct_weight_reduction_measured=true;}],
 ["invent browser broken count",d=>{d.verified_sitewide_browser_broken_count=42;}],
 ["invent before bytes",d=>{d.measured_before_image_bytes=123;}],
 ["invent after bytes",d=>{d.measured_after_image_bytes=23;}],
 ["claim production repair",d=>{d.production_images_repaired=1;}],
 ["change published source URL",d=>{d.rows[0].original_source_url='https://fake.invalid';}],
 ["change historical ALT",d=>{d.rows[1].original_alt='another subject';}],
 ["duplicate post slot",d=>{d.rows[5].key='418:0';}],
 ["reverse slots",d=>{d.rows.reverse();}],
 ["incorrect post slot count",d=>{d.source_count=5;}],
 ["incorrect offsite count",d=>{d.offsite_source_count=5;}],
 ["incorrect post ID",d=>{d.post_id=419;}],
 ["false WordPress readback",d=>{d.source_inventory_verified_current_cms=false;}],
 ["corrupt frozen source SHA",d=>{d.frozen_source_blob_sha='fake';}],
 ["wrong post count",d=>{d.sitewide_post_count=60;}],
 ["wrong source count",d=>{d.sitewide_reference_count=356;}],
 ["wrong external count",d=>{d.sitewide_external_reference_count=286;}],
 ["erase oversized queue",d=>{d.oversized_originals_above_1_5MiB=0;}],
 ["unauthorized upload",d=>{d.rows[5].candidate.wordpress_upload_authorized=true;}],
 ["unauthorized post write",d=>{d.rows[4].candidate.wordpress_post_edit_authorized=true;}],
 ["rights auto cleared",d=>{d.rows[1].candidate.rights_review='PUBLIC_DOMAIN';}],
 ["visual QA invented",d=>{d.rows[1].candidate.visual_QA_complete=true;}],
 ["binary identity invented",d=>{d.rows[5].candidate.binary_identity_verified=true;}],
 ["master SHA invented",d=>{d.rows[5].candidate.master_sha256='abcdef';}],
 ["too-wide derivative cap",d=>{d.rows[0].candidate.candidate_width_cap_px=1200;}],
 ["allow upscale",d=>{d.rows[4].candidate.no_upscale=false;}],
 ["remove aspect protection",d=>{d.rows[5].candidate.preserve_aspect_ratio=false;}],
 ["fabricated original width",d=>{d.rows[5].candidate.source_width_px=1024;}],
 ["invent output dimensions",d=>{d.rows[1].candidate.conditional_max_dimensions={width_px:960,height_px:768};}],
 ["treat hint as measured",d=>{d.rows[0].candidate.filename_geometry_hint.unverified=false;}],
 ["fabricate hint",d=>{d.rows[1].candidate.filename_geometry_hint={width_px:1200,height_px:900,unverified:true};}],
 ["NOAA exact identity overclaim",d=>{d.rows[4].candidate.relationship='pixels are identical';}],
 ["wrong NOAA catalog ID",d=>{d.rows[4].candidate.identifier='other.jpg';}],
 ["wrong USGS file identity",d=>{d.rows[5].candidate.identifier='other.jpg';}],
 ["wrong USCG photo ID",d=>{d.rows[1].candidate.identifier='other.jpg';}],
 ["remove rights caveat",d=>{d.rows[5].candidate.rights_note='';}],
 ["record mismatch",d=>{d.rows[0].candidate.record='https://example.org/wrong';}],
];
for(const [name,mutate] of mutations){
 test(name+' fails closed',()=>{const d=clone();mutate(d);assert.throws(()=>validateTsunami418(d));});
}
