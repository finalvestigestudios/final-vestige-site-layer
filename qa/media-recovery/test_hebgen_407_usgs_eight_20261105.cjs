'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {validate}=require('./validate_hebgen_407_usgs_eight_20261105.cjs');
const audit=JSON.parse(fs.readFileSync(path.join(__dirname,'hebgen_407_usgs_eight_original_links_20261105.json'),'utf8'));
const frozen=JSON.parse(fs.readFileSync(path.join(__dirname,'parts/02.json'),'utf8'));
const cp=()=>JSON.parse(JSON.stringify(audit));
assert.deepEqual(validate(audit,frozen),[]);
const cases=[
 ['false browser status',a=>a.rows[1].guest_browser_http_status=200],
 ['false origin 400',a=>a.rows[1].origin_http_status=400],
 ['invent image width',a=>a.rows[0].guest_browser_natural_width=960],
 ['invent transfer',a=>a.rows[1].guest_browser_transferred_bytes=1024],
 ['invent visitor broken',a=>a.rows[1].visitor_broken=true],
 ['claim 42 verified',a=>a.snapshot_caveats.reported_broken_images_42='VERIFIED'],
 ['claim 76 measured',a=>a.snapshot_caveats.reported_wire_reduction_76_pct='MEASURED'],
 ['wrong original image',a=>a.rows[1].published_src='https://example.com/no.jpg'],
 ['changed caption alt',a=>a.rows[2].published_alt='Wrong'],
 ['wrong USGS catalog',a=>a.rows[1].official_usgs_record=a.rows[2].official_usgs_record],
 ['changed WP catalog link',a=>a.rows[0].live_caption_usgs_record='https://example.com'],
 ['invent exact match',a=>a.rows[2].usgs_original_link_exactly_matches_src=false],
 ['wrong item rights label',a=>a.rows[2].usgs_item_sources_usage='Unknown'],
 ['lost attribution',a=>a.rows[3].catalog_credit=''],
 ['wrapper-as-browser error',a=>a.rows[1].retriever_method='BROKEN_IMAGE'],
 ['invent source wrapper 404',a=>a.rows[0].retriever_wrapper_status=404],
 ['fake original binary dimensions',a=>a.rows[0].original_binary_pixel_dimensions=[1024,768]],
 ['upscaled derivative',a=>a.rows[0].proposed_max_width_px=1200],
 ['invent fixed output geometry',a=>a.rows[2].proposed_derivative_dimensions=[960,674]],
 ['drop no-upscale',a=>a.rows[2].no_upscale=false],
 ['claim rehost cleared',a=>a.rows[3].item_specific_rehost_review='CLEARED'],
 ['claim hash checked',a=>a.rows[2].binary_identity_verified=true],
 ['claim savings measured',a=>a.rows[2].wire_savings_measured=true],
 ['allow cache',a=>a.rows[0].media_caching_authorized=true],
 ['allow WordPress upload',a=>a.rows[0].wp_media_upload_authorized=true],
 ['allow post rewrite',a=>a.rows[0].post_rewrite_authorized=true],
 ['wrong declared geometry',a=>a.rows[2].html_declared_height=720],
 ['duplicate slot',a=>a.rows[7].image_key='407:6'],
 ['fewer rows',a=>a.rows.pop()],
 ['wrong historical blob',a=>a.frozen.git_blob_sha='invalid'],
 ['wrong 61 count',a=>a.snapshot_caveats.posts=62],
 ['claim one production fix',a=>a.snapshot_caveats.production_fixes=1]
];
for(const [name,alter] of cases){const x=cp();alter(x);assert.notDeepEqual(validate(x,frozen),[],name);}
console.log('Hebgen baseline + '+cases.length+' adversarial source/rights/HTTP guards PASS');
