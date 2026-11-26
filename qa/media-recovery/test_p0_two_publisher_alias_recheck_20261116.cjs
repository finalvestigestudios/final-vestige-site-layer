'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {assess}=require('./assess_p0_two_publisher_alias_recheck_20261116.cjs');
const baseline=JSON.parse(fs.readFileSync(path.join(__dirname,'p0_two_publisher_alias_recheck_20261116_0930pt.json'),'utf8'));
const clone=()=>JSON.parse(JSON.stringify(baseline));
test('two independently rechecked P0 reader outcomes remain HOLD, not proven guest HTTP failures',()=>{const r=assess(clone());assert.deepEqual(r.errors,[]);assert.equal(r.ok,true);assert.equal(r.wordpress_writes_allowed,false);assert.equal(r.visitor_broken_confirmed,0)});
const mutations=[
  ["fake origin 404", x=>x.rows[0].source_numeric_http_get_status=404],
  ["fake USCG origin 403", x=>x.rows[1].source_numeric_http_get_status=403],
  ["proxy HTTP 404 invented", x=>x.rows[0].proxy_numeric_http_get_status=404],
  ["candidate HTTP 200 invented", x=>x.rows[1].candidate_numeric_http_get_status=200],
  ["site-wide 42 verified", x=>x.reported_42_browser_failures_confirmed=true],
  ["site-wide 76 verified", x=>x.claimed_76_percent_visitor_wire_reduction_verified=true],
  ["storage reinterpreted as wire", x=>x.oversized_wp_originals.guest_wire_bytes=64385752],
  ["source URL substituted", x=>x.rows[0].stored_image_url=x.rows[0].candidate_asset_url],
  ["proxy source changed", x=>x.rows[1].recorded_jetpack_view_url=x.rows[1].stored_image_url],
  ["wrong candidate publisher", x=>x.rows[0].candidate_asset_url="https://random.example/photo.jpg"],
  ["HTML catalog passed as image", x=>x.rows[1].candidate_asset_url=x.rows[1].candidate_catalog_url],
  ["unknown copyrights claimed cleared", x=>x.rows[0].candidate_rights="CLEARED"],
  ["museum copyright prematurely cleared", x=>x.rows[1].candidate_rights="CLEARED"],
  ["skyway fictional crop", x=>x.rows[0].same_frame_crop_proven=true],
  ["coast guard screenshot missing truth", x=>x.rows[1].browser_screenshot="https://example.com/image.png"],
  ["guest HTTP invented", x=>x.rows[1].browser_http_get_status=403],
  ["guest decode invented", x=>x.rows[0].browser_decoded=false],
  ["guest currentSrc invented", x=>x.rows[0].browser_current_src=x.rows[0].recorded_jetpack_view_url],
  ["visitor bytes invented", x=>x.rows[1].browser_transfer_bytes=55000],
  ["unsafe upscale", x=>x.rows[1].review_dimensions.width=960],
  ["invent original native size", x=>x.rows[1].candidate_native_dimensions={width:600,height:463}],
  ["caching authorized", x=>x.rows[0].cache_authorized=true],
  ["WordPress upload authorized", x=>x.rows[1].wp_upload_authorized=true],
  ["WordPress edit authorized", x=>x.rows[0].wp_post_edit_authorized=true],
  ["release approval invented", x=>x.rows[1].decision="STAGING_REVIEW_ONLY"],
  ["production write", x=>x.production_wordpress_writes=1],
  ["homepage scope invasion", x=>x.homepage_design_changes=1],
  ["paid spend", x=>x.paid_actions=1],
  ["source pin changed", x=>x.source_custody.p0_manifest_blob_sha="bad"],
  ["late cohort collapse", x=>x.later_cohort.posts=61],
  ["drop image slot", x=>x.rows.pop()],
  ["double same slot", x=>x.rows[1]=x.rows[0]],
];
for(const [name,mutate] of mutations){test('FAIL CLOSED: '+name,()=>{const x=clone();mutate(x);const r=assess(x);assert.equal(r.ok,false);assert.ok(r.errors.length>0,name)})}
