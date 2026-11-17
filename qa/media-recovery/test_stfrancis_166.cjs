'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {validate}=require('./validate_stfrancis_166.cjs');
const audit=JSON.parse(fs.readFileSync(path.join(__dirname,'stfrancis_166_archival_20261101.json'),'utf8'));
const census=JSON.parse(fs.readFileSync(path.join(__dirname,'parts/07.json'),'utf8'));
const clone=()=>JSON.parse(JSON.stringify(audit));
const mutations=[
 a=>a.sitewide_baseline.reported_broken_42_browser_confirmed=true,
 a=>a.sitewide_baseline.claimed_76pct_weight_reduction_measured=true,
 a=>a.sitewide_baseline.confirmed_broken_count=42,
 a=>a.sitewide_baseline.measured_transfer_reduction_percent=76,
 a=>a.sitewide_baseline.production_images_repaired=1,
 a=>a.sitewide_baseline.oversize_originals_above_1_5MiB=0,
 a=>a.safety.no_production_wordpress_writes=false,
 a=>a.article.source_part_git_blob_sha='invented',
 a=>a.article.wordpress_read_only_editor_rechecked=false,
 a=>a.slots.pop(),
 a=>a.slots[2].published_source_url='https://example.com/counterfeit.jpg',
 a=>a.slots[6].published_alt='invented',
 a=>a.slots[3].authority_candidate.rights_basis='PUBLIC_DOMAIN',
 a=>a.slots[6].authority_candidate.rights_review='CLEARED',
 a=>a.slots[1].authority_candidate.record_url='https://example.com/',
 a=>a.slots[2].authority_candidate.pixel_identity_confirmed=true,
 a=>a.slots[6].authority_candidate.original_master_sha256='unverifiedhash',
 a=>a.slots[2].geometry.conditional_width_px=1400,
 a=>a.slots[6].geometry.conditional_height_px=1200,
 a=>a.slots[6].geometry.actual_visitor_transfer_bytes=19311352,
 a=>a.slots[1].geometry.catalog_or_media_width_px=14420,
 a=>a.slots[3].independent_retriever.http_status=404,
 a=>a.slots[4].guest_browser.actual_image_get_status=404,
 a=>a.slots[5].guest_browser.visibly_broken=true,
 a=>a.slots[2].release.cache_authorized=true,
 a=>a.slots[0].release.wordpress_post_edit_authorized=true,
 a=>a.slots[5].geometry.observed_first_party_original_storage_bytes=123456
];
assert.deepEqual(validate(audit,census),[], 'authoritative ledger passes');
let passed=1;
mutations.forEach((change,i)=>{const a=clone();change(a);assert.ok(validate(a,census).length>0,'mutation '+i+' must fail closed');passed++;});
console.log(passed+'/'+passed+' stfrancis archival/rights/guest-proof test cases PASS');
