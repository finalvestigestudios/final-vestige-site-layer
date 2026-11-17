'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const {validate}=require('./validate_tang_274_20261102.cjs');
const data=require('./tang_274_nhhc_20261102.json');
const clone=()=>JSON.parse(JSON.stringify(data));
test('seven source and rights records exactly match frozen WordPress source',()=>assert.deepEqual(validate(data),[]));
const cases=[
 ['invented origin HTTP 404',x=>x.records[0].independent_source_retrieval.origin_http_status=404],
 ['invented visitor status',x=>x.records[5].independent_source_retrieval.guest_browser_status=200],
 ['invented encoded bytes',x=>x.records[5].independent_source_retrieval.transfer_bytes=6000],
 ['invented natural pixels',x=>x.records[5].independent_source_retrieval.decoded_pixels=[1280,937]],
 ['not actually displayed',x=>x.records[0].independent_source_retrieval.result='browser_loaded'],
 ['false production read',x=>x.fresh_production_post_read=true],
 ['source inventory mismatch',x=>x.snapshot_blob_sha='f'.repeat(40)],
 ['altered source URL',x=>x.records[3].published_source_url='https://bad.example/abc.jpg'],
 ['altered historical ALT',x=>x.records[3].published_alt='1944 Tang escape'],
 ['changed accession',x=>x.records[2].authority.catalog_id='NH 84497'],
 ['catalog phishing',x=>x.records[2].authority.catalog_url='https://evil.example'],
 ['zero master dimensions',x=>x.records[2].authority.official_catalog_master_dimensions_px.width=0],
 ['wrong crop reported',x=>x.records[0].authority.commons_current_original_px.height=3672],
 ['false same frame',x=>x.records[5].authority.commons_current_original_px.width=6102],
 ['wrong Commons scene crop',x=>x.records[6].authority.commons_scene_copy_px.height=4926],
 ['rights prematurely cleared',x=>x.records[0].rights.review_status='CLEARED'],
 ['unauthorized copying',x=>x.records[0].rights.download_authorized=true],
 ['unauthorized rehost',x=>x.records[0].rights.wp_rehost_authorized=true],
 ['too wide derivative',x=>x.records[0].transform.max_width_px=1280],
 ['allow enlargement',x=>x.records[0].transform.no_upscale=false],
 ['fake input pixels verified',x=>x.records[0].transform.actual_source_dimensions_verified=true],
 ['guessed output height',x=>x.records[5].transform.derivative_height_px=703],
 ['fabricated SHA256',x=>x.records[3].transform.original_binary_sha256='a'.repeat(64)],
 ['binary identity assumed',x=>x.records[6].release.exact_image_binary_identity_verified=true],
 ['crop identity assumed',x=>x.records[6].release.crop_identity_verified=true],
 ['premature WordPress edit',x=>x.records[6].release.wordpress_write_authorized=true],
 ['staging without approval',x=>x.records[6].release.staging_authorized=true],
 ['visual proof fabricated',x=>x.records[6].release.visual_review_passed=true],
 ['broken photo claim invented',x=>x.confirmed_guest_browser_broken_count=2],
 ['sitewide 42 claimed proven',x=>x.sitewide_42_image_claim_verified=true],
 ['unmeasured 76 claimed proven',x=>x.weight_reduction_76_percent_measured=true],
 ['production fake repair',x=>x.production_media_repaired=1],
 ['row removed',x=>x.records.pop()],
 ['row swapped',x=>x.records.reverse()]
];
cases.forEach(([name,mutate])=>test('fail-closed: '+name,()=>{const x=clone();mutate(x);assert.ok(validate(x).length>0,name)}));
