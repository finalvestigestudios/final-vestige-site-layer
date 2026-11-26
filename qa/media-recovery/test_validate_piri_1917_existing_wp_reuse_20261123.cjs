'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const {validate}=require('./validate_piri_1917_existing_wp_reuse_20261123.cjs');
const source=require('./piri_1917_existing_wp_reuse_20261123.json');
const copy=()=>JSON.parse(JSON.stringify(source));
test('read-only two-image Piri audit passes',()=>assert.deepEqual(validate(source),[]));
const changes=[
 ['invented mobile CLS',a=>a.source_provenance.mobile_cls=0.02],
 ['invented mobile browser pass',a=>a.post.guest_mobile_tested=true],
 ['campaign attribution without evidence',a=>a.post.campaign_attribution_verified=true],
 ['stale WordPress revision',a=>a.post.wp_modified='2026-11-01T00:00:00'],
 ['fabricated visitor HTTP',a=>a.source_provenance.live_guest_image_http=200],
 ['wrong current external image',a=>a.images[0].current_src='https://commons.wikimedia.org/wiki/File:Piri_Reis_Map.jpg'],
 ['different image despite same label',a=>a.images[0].catalog_sha1='0'.repeat(40)],
 ['misreported source bytes',a=>a.images[0].catalog_original_bytes=1000],
 ['different WordPress attachment',a=>a.images[0].wp_existing_media_id=1],
 ['unverified image declared byte-identical',a=>a.images[0].same_binary_sha256_verified=true],
 ['unverified rights declared clear',a=>a.images[0].item_rights_editorially_cleared=true],
 ['WordPress write declared approved',a=>a.images[0].wordpress_write_approved=true],
 ['Cantino WP media fabricated',a=>a.images[1].wp_existing_media_id=2640],
 ['force crop disguised as fit',a=>a.images[0].wp_existing_virtual_768_url+='&crop=center'],
 ['960x960 crop substituted for map',a=>a.images[0].proposed_proportional_height=960],
 ['over-960 derivative',a=>a.images[1].proposed_max_width=1280],
 ['sitewide 76 claim fabricated',a=>a.release.sitewide_76_percent_wire_savings_verified=true],
 ['reported 42 marked proven',a=>a.release.status_42_reported_guest_failures_verified=true],
 ['unapproved media rehosting',a=>a.release.new_wp_media_uploads=1],
 ['mobile collector duplicated',a=>a.release.new_browser_collector=true],
 ['stored bytes conflated with downloads',a=>a.release.oversize_visitor_download_confirmed=true],
 ['misstated current census',a=>a.release.newer_inline=355]
];
for(const [label,change] of changes)test('reject '+label,()=>{const a=copy();change(a);assert.ok(validate(a).length>0);});
