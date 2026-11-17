'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {validate}=require('./validate_akron_219.cjs');
const A=JSON.parse(fs.readFileSync(path.join(__dirname,'akron_219_nhhc_20261101.json'),'utf8'));
const I=JSON.parse(fs.readFileSync(path.join(__dirname,'parts/05.json'),'utf8'));
const clone=()=>JSON.parse(JSON.stringify(A));
assert.deepEqual(validate(A,I),[],'exact-source positive acceptance');
const mutations=[
 a=>a.images[0].published_source_url='https://example.com/unrelated.jpg',
 a=>a.images[2].published_alt='invented caption',
 a=>a.images[4].key='219:99',
 a=>a.images.pop(),
 a=>a.article.source_blob_sha='wrong',
 a=>a.article.modified='2026-10-30T10:00:00',
 a=>a.article.current_wp_matches_frozen_src_and_alt=5,
 a=>a.sitewide.claimed_42_broken_verified=true,
 a=>a.sitewide.claimed_76_percent_transfer_reduction_measured=true,
 a=>a.sitewide.actual_guest_broken_count=42,
 a=>a.sitewide.actual_transfer_reduction_percent=76,
 a=>a.sitewide.production_replacements=1,
 a=>a.probe_method.guest_browser_run=true,
 a=>a.probe_method.origin_http_checks_performed=true,
 a=>a.images[1].guest.network_http_status=200,
 a=>a.images[2].guest.visibly_broken=true,
 a=>a.images[3].guest.transfer_bytes=57000,
 a=>a.images[4].authority.catalog_number='NH 12345',
 a=>a.images[5].authority.exact_binary_sha256='pretend hash',
 a=>a.images[2].authority.creator_caution='U.S. Navy employee',
 a=>a.images[5].authority.creator_caution='U.S. Navy employee',
 a=>a.images[3].geometry.proposed_max_width_px=960,
 a=>a.images[5].geometry.proposed_height_px=1245,
 a=>a.images[0].geometry.catalog_commons_original_width_px=1000,
 a=>a.images[1].geometry.visitor_encoded_bytes=10000,
 a=>a.images[0].rights.local_cache_authorized=true,
 a=>a.images[2].rights.individual_reuse_review_complete=true,
 a=>a.images[3].release.asset_downloaded=true,
 a=>a.images[4].release.wp_media_uploaded=true,
 a=>a.images[5].release.wp_post_edited=true,
 a=>a.safety.homepage_design_changes=true,
 a=>a.safety.site_qa_code_changes=true,
 a=>a.safety.subscription_spend_usd=1
];
mutations.forEach((fn,i)=>{const a=clone();fn(a);assert.ok(validate(a,I).length>0,'must fail closed: mutation '+i)});
console.log((mutations.length+1)+'/'+(mutations.length+1)+' Akron source / image sizing / rights regressions PASS');
