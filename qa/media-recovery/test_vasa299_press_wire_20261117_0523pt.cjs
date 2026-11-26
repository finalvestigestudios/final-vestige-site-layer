'use strict';
const {test}=require('node:test');const assert=require('node:assert/strict');
const a=require('./vasa299_primary_press_rights_20261117_0523pt.json');
const {checks,assessWirePair}=require('./validate_vasa299_press_wire_20261117_0523pt.cjs');
const cp=x=>JSON.parse(JSON.stringify(x));
test('pinned primary press/WordPress audit validates',()=>assert.deepEqual(checks(a),[]));
const muts=[
 ['false guest status',v=>v.images[0].browser.http_status=200],
 ['false 76%',v=>v.summary.claimed_76_percent_wire_saving_verified=true],
 ['wrong 13MB total',v=>v.summary.original_stored_bytes=1],
 ['upscale',v=>v.images[0].proposed_geometry_only.width=2000],
 ['bad aspect',v=>v.images[2].proposed_geometry_only.height=99],
 ['rights override',v=>v.images[0].cache_authorized=true],
 ['false exact 389 match',v=>v.images[1].official_candidate.match_basis='EXACT_FILENAME_AND_DESCRIPTION'],
 ['made-up official master HTTP',v=>v.images[0].official_candidate.numeric_http_status=200],
 ['invented official pixels',v=>v.images[0].official_candidate.pixel_crop_match=true],
 ['unknown official host',v=>v.images[0].official_candidate.url='https://example.com/a.jpg'],
 ['permission as public domain',v=>v.official_press.permission_scope='PUBLIC_DOMAIN'],
 ['wrong photographer credit',v=>v.images[0].official_candidate.credit='unknown'],
 ['unapproved WordPress writes',v=>v.safety.wordpress_writes=true],
 ['duplicate media identifier',v=>v.images[1].media_id=388],
 ['tampered source blob',v=>v.source_oversized_exposure.git_blob_sha='wrong'],
 ['false 42 failures',v=>v.summary.sitewide_reported_broken_42_verified=true]
];
for(const [name,fn] of muts)test(name,()=>{const v=cp(a);fn(v);assert.ok(checks(v).length>0);});
const shot=()=>({origin:'SITE_QA_154_LOGGED_OUT_CDP',cache:'cold',page_status:200,post_url:a.post.url,revision:a.post.wp_revision,viewport_width:1366,viewport_height:768,dpr:1,user_agent:'test-ua',complete_image_waterfall:true,screenshot_sha256:'a'.repeat(64),visual_review_approved:true,images:[{slot:'hero',request_id:'one',current_src:'https://i0.wp.com/finalvestige.com/a.jpg',status:200,mime:'image/jpeg',decoded:true,natural_width:960,natural_height:640,encoded_transfer_bytes:1000,byte_source:'CDP.Network.loadingFinished.encodedDataLength',from_cache:false,from_service_worker:false},{slot:'body',request_id:'two',current_src:'https://i0.wp.com/finalvestige.com/b.jpg',status:200,mime:'image/jpeg',decoded:true,natural_width:960,natural_height:640,encoded_transfer_bytes:1000,byte_source:'CDP.Network.loadingFinished.encodedDataLength',from_cache:false,from_service_worker:false}]});
const pair=()=>{const before=shot(),after=shot();after.images.forEach(x=>x.encoded_transfer_bytes=200);return {schema:'fv-cold-image-transfer-pair-v1',expected_post_url:a.post.url,expected_revision:a.post.wp_revision,before,after};};
test('no guest captures stays HOLD',()=>assert.equal(assessWirePair({...pair(),before:null}).status,'HOLD'));
test('synthetic pair computes 80 percent page-only, never sitewide',()=>{const r=assessWirePair(pair());assert.equal(r.status,'MEASURED_PAGE_ONLY');assert.equal(r.reduction_percent,80);assert.equal(r.sitewide_claim_authorized,false);});
const bad=[
 ['cached',v=>v.before.images[0].from_cache=true],['service worker',v=>v.after.images[0].from_service_worker=true],
 ['404',v=>v.after.images[0].status=404],['html MIME',v=>v.after.images[0].mime='text/html'],
 ['decode false',v=>v.after.images[0].decoded=false],['zero pixels',v=>v.after.images[0].natural_width=0],
 ['revision changed',v=>v.after.revision='wrong'],['viewport different',v=>v.after.viewport_width=390],
 ['missing image',v=>v.after.images.pop()],['not CDP bytes',v=>v.before.images[0].byte_source='stored'],
 ['missing visual review',v=>v.after.visual_review_approved=false],['warm cache',v=>v.before.cache='warm'],
 ['incomplete image waterfall',v=>v.after.complete_image_waterfall=false],['duplicate request ID',v=>v.before.images[1].request_id='one'],
 ['invalid screenshot hash',v=>v.before.screenshot_sha256='no'],['zero transferred bytes',v=>v.before.images[0].encoded_transfer_bytes=0],
 ['curl instead of browser',v=>v.after.origin='curl']
];
for(const [name,fn] of bad)test(name,()=>{const p=pair();fn(p);assert.equal(assessWirePair(p).status,'HOLD');});
