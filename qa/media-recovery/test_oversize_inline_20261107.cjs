'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const {inspect}=require('./validate_oversize_inline_20261107.cjs');
const original=require('./oversize_inline_61x355_20261107.json');
const clone=()=>JSON.parse(JSON.stringify(original));
test('actual immutable source audit passes',()=>assert.equal(inspect(clone()).ok,true));
const attacks=[
 ['fabricate 42 browser failures',a=>a.cohort.reported_42_broken_images='42 confirmed'],
 ['claim measured 76%',a=>a.cohort.claimed_76pct_wire_savings='ACHIEVED'],
 ['fake browser bytes',a=>a.rows[0].web_browser_image_encoded_bytes=10],
 ['fake HTTP OK',a=>a.rows[0].web_browser_http_status=200],
 ['claim rights cleared',a=>a.rows[0].rights_clearance='APPROVED'],
 ['allow WP edit',a=>a.wordpress_writes=1],
 ['allow rehost',a=>a.rows[0].allow_rehosting=true],
 ['change origin',a=>a.rows[0].original_src='http://example.com/a.jpg'],
 ['duplicate media id',a=>a.rows[1].media_id=a.rows[0].media_id],
 ['tamper provenance SHA',a=>a.source_blob_shas['qa/media-recovery/parts/01.json']='wrong'],
 ['upscale',a=>a.rows[0].conditional_preview_pixels=[961,639]],
 ['distort image',a=>a.rows[0].conditional_preview_pixels=[960,500]],
 ['add invented inline',a=>a.rows[0].inline_source_matches.push({slot:'999:1',post_url:'https://finalvestige.com/x/',post_title:'x',stored_alt:'x'})],
 ['remove live inline ref',a=>a.rows[1].inline_source_matches=[]],
 ['fabricate original bytes',a=>a.rows[2].original_bytes+=1],
 ['assert no other site usage',a=>a.rows[0].inline_source_status='UNUSED_SITEWIDE'],
 ['fabricate CDN variant tested',a=>a.rows[0].proxy_variant_visitor_verified=true],
 ['claim live modified',a=>a.rows[0].live_asset_changed=true],
 ['invent wire savings',a=>a.measured_page_image_weight_reduction_pct=76],
 ['drop media original',a=>a.rows.pop()]
];
for(const [label,attack] of attacks)test('reject: '+label,()=>{const a=clone();attack(a);assert.equal(inspect(a).ok,false,label)});
