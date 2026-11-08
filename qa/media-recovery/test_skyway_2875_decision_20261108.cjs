'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {verify,previewSize}=require('./validate_skyway_2875_decision_20261108.cjs');
const original=JSON.parse(fs.readFileSync(path.join(__dirname,'skyway_2875_source_candidate_decision_20261108.json'),'utf8'));
function clone(){return structuredClone(original)}
test('valid evidence holds all 4 candidates',()=>assert.deepEqual(verify(clone()),{decision:'HOLD_NO_CMS_WRITE',audited_candidates:4,known_guest_broken:null,can_publish:false}));
const mutations=[
 ['invented status',a=>a.visitor_browser_http_status=404],
 ['invented browser broken',a=>a.visitor_broken=true],
 ['invented transferred bytes',a=>a.visitor_browser_transferred_bytes=200],
 ['sitewide 42 proven',a=>a.reported_42_broken='CONFIRMED'],
 ['76 percent claimed',a=>a.reported_76_percent_transfer_reduction='MEASURED'],
 ['auto release',a=>a.replacement_authorized=true],
 ['wp write',a=>a.wordpress_write_authorized=true],
 ['image download',a=>a.image_downloaded=true],
 ['QA change',a=>a.site_qa_collector_modified=true],
 ['homepage change',a=>a.homepage_modified=true],
 ['spend',a=>a.spend_usd=1],
 ['upscale ceiling',a=>a.conditional_max_width_px=2000],
 ['invented native pixels',a=>a.candidates[0].pixel_width=1920],
 ['unapproved license',a=>a.candidates[0].item_level_rights_verified=true],
 ['unapproved upload',a=>a.candidates[2].wp_upload_authorized=true],
 ['catalog alt conflict lost',a=>a.candidates[2].description='Just a damaged bridge'],
 ['duplicate candidate',a=>a.candidates[1].candidate_id=a.candidates[0].candidate_id],
 ['wrong publisher URL',a=>a.published_original_source_url='https://example.com/different.jpg'],
 ['claim origin 404',a=>a.observations[0].status_is_authoritative_origin_http=true],
 ['claim browser 404',a=>a.observations[0].status_is_guest_browser_http=true],
 ['unsupported retrieval result',a=>a.observations[0].result='HTTP_ORIGIN_404'],
 ['missing rollback requirement',a=>a.restoration_requirements=[]]
];
for(const [name,mutate] of mutations)test('reject '+name,()=>{const a=clone();mutate(a);assert.throws(()=>verify(a),/Skyway recovery HOLD/)});
test('preview 960 cap and preserved ratio',()=>assert.deepEqual(previewSize(1920,1080),{width:960,height:540}));
test('preview never upscales 600 original',()=>assert.deepEqual(previewSize(600,595),{width:600,height:595}));
test('no fabricated geometry',()=>assert.throws(()=>previewSize(null,800),/Skyway recovery HOLD/));
