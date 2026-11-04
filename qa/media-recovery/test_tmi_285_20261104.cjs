'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {validate,unproxy}=require('./validate_tmi_285_20261104.cjs');
const a=JSON.parse(fs.readFileSync(path.join(__dirname,'tmi_285_p0_live_wp_source_custody_20261104.json'),'utf8'));
const p=JSON.parse(fs.readFileSync(path.join(__dirname,'parts','03.json'),'utf8'));
const clone=()=>JSON.parse(JSON.stringify(a));
test('actual frozen 6/6 CMS source and ALT / null network truth',()=>assert.deepEqual(validate(a,p),[]));
test('Jetpack proxy unwrapped not mistaken for origin status',()=>assert.equal(unproxy(a.source_checks[5].published_html_src),a.source_checks[5].source_url_frozen));
const mutations=[
 ['invented visitor 404',x=>x.source_checks[5].guest_browser_http_status=404],
 ['invented failure conclusion',x=>x.source_checks[5].confirmed_broken_for_visitors=true],
 ['invented CDP transfer size',x=>x.source_checks[5].cold_cdp_transfer_bytes=4000],
 ['invented browser currentSrc',x=>x.source_checks[2].guest_browser_current_src=x.source_checks[2].source_url_frozen],
 ['invented successful decode',x=>x.source_checks[1].guest_browser_decode_ok=true],
 ['frozen source changed',x=>x.source_checks[5].source_url_frozen='https://example.com/fake.jpg'],
 ['live Jetpack source changed',x=>x.source_checks[2].published_html_src='https://i0.wp.com/example.com/fake.jpg?ssl=1'],
 ['ALT drift',x=>x.source_checks[0].alt_live='An unknown crew'],
 ['claim all images have dimensions',x=>x.live_missing_html_dimension_pairs=0],
 ['wrong old inventory blob',x=>x.frozen_inventory_blob_sha='0'.repeat(40)],
 ['tool 500 miscast as a successful displayed image',x=>x.source_checks[2].web_retriever.result='rendered_image'],
 ['turn tool retrieval success into fabricated HTTP code',x=>x.source_checks[1].web_retriever.retriever_error_code=200],
 ['candidate enlarged beyond 960',x=>x.candidates[2].max_recommended_width=1267],
 ['candidate enlarged beyond intrinsic',x=>x.candidates[3].max_recommended_width=960],
 ['candidate aspect ratio damaged',x=>x.candidates[0].max_recommended_height=200],
 ['candidate silently exact-photo verified',x=>x.candidates[1].historical_relation='exact_same_photo_verified'],
 ['candidate approved without release gates',x=>x.candidates[0].approved=true],
 ['grant rehosting rights without review',x=>x.source_checks[5].rights_to_rehost_approved=true],
 ['authorize a WP upload',x=>x.candidate_rules.wordpress_uploads_approved=true],
 ['authorize CDN caching',x=>x.candidate_rules.cdn_cache_approved=true],
 ['assert real weight reduction',x=>x.site_baseline.cold_cdp_reduction_measured=true],
 ['inflate verified broken-image count',x=>x.site_baseline.visitor_broken_verified=42]
];
for(const [label,change] of mutations)test('reject '+label,()=>{const obj=clone();change(obj);assert.ok(validate(obj,p).length>0,label);});
