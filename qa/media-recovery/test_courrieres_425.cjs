'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {validate}=require('./validate_courrieres_425.cjs');
const audit=JSON.parse(fs.readFileSync(path.join(__dirname,'courrieres_425_commons_20261101.json'),'utf8'));
const census=JSON.parse(fs.readFileSync(path.join(__dirname,'parts/01.json'),'utf8'));
const clone=()=>JSON.parse(JSON.stringify(audit));
assert.deepEqual(validate(audit,census),[],'authoritative frozen source and catalog rights gates');
const mutations=[
 a=>a.article.current_wordpress_authenticated_recheck_done=true,
 a=>a.article.stored_external_images=9,
 a=>a.article.source_blob_sha='wrong',
 a=>a.sitewide.reported_42_broken_browser_confirmed=true,
 a=>a.sitewide.claimed_76_percent_weight_reduction_measured=true,
 a=>a.sitewide.actual_broken_count=42,
 a=>a.sitewide.actual_transfer_reduction_percent=76,
 a=>a.sitewide.production_replacements=1,
 a=>a.safety.no_wordpress_production_writes=false,
 a=>a.slots.pop(),
 a=>a.slots[3].published_alt='invented',
 a=>a.slots[4].published_source_url='https://example.com/fake.jpg',
 a=>a.slots[1].inventory_blob_sha='fake',
 a=>a.slots[3].requested_width_in_stored_url=960,
 a=>a.slots[7].candidate.file_catalog_url='https://commons.wikimedia.org/wiki/File:unrelated.jpg',
 a=>a.slots[6].candidate.catalog_html_opened=false,
 a=>a.slots[6].candidate.credit_or_caption_note='Unknown',
 a=>a.slots[7].candidate.credit_or_caption_note='Unknown',
 a=>a.slots[8].candidate.us_rights_independently_confirmed=true,
 a=>a.slots[4].candidate.exact_binary_match_confirmed=true,
 a=>a.slots[1].candidate.caching_rights_cleared=true,
 a=>a.slots[2].candidate.master_sha256='unverified',
 a=>a.slots[3].geometry.proposed_width_px=960,
 a=>a.slots[6].geometry.proposed_width_px=960,
 a=>a.slots[8].geometry.proposed_height_px=602,
 a=>a.slots[2].geometry.visitor_transfer_bytes=90000,
 a=>a.slots[8].visitor.image_http_status=404,
 a=>a.slots[0].visitor.natural_width=900,
 a=>a.slots[6].release.wp_post_modified=true,
 a=>a.slots[8].release.asset_downloaded=true
];
let passed=1;mutations.forEach((fn,i)=>{const x=clone();fn(x);assert.ok(validate(x,census).length>0,'mutation '+i+' must fail closed');passed++;});
console.log(passed+'/'+passed+' Courrieres archival/rights/960px negative-mutation regressions PASS');
