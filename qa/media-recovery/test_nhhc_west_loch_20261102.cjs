'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const {validate}=require('./validate_nhhc_west_loch_20261102.cjs');
const {sameSource}=require('./browser_probe_core.cjs');
const audit=require('./nhhc_west_loch_370_source_crosswalk_20261102.json'),source=require('./parts/02.json');
const clone=o=>JSON.parse(JSON.stringify(o));
test('eight real published slots and four exact NHHC imageDownload catalog IDs pass',()=>assert.deepEqual(validate(audit,source),[]));
const modifications=[
 ['invented browser 404',a=>a.entries[0].guest_http_status=404],
 ['invented decoded pixels',a=>a.entries[1].decoded_width_px=900],
 ['invented browser pass',a=>a.entries[2].verified_broken_in_browser=false],
 ['fictitious transfer bytes',a=>a.entries[3].transfer_bytes=1900],
 ['claim 42 confirmed',a=>a.verified_42_broken_claim=true],
 ['claim 76 percent achieved',a=>a.verified_76_percent_weight_reduction=true],
 ['claim WordPress repaired',a=>a.production_repairs=1],
 ['wrong source URL',a=>a.entries[0].source_url=a.entries[3].source_url],
 ['altered historical ALT',a=>a.entries[1].stored_alt='West Loch disaster, 1944'],
 ['false source classification',a=>a.entries[2].source_kind='external'],
 ['duplicate source slot key',a=>a.entries[2].image_key='370:0'],
 ['bad catalog id',a=>a.entries[0].candidate.catalog_number='80-G-276940'],
 ['wrong event date',a=>a.entries[3].candidate.photograph_date='1944-05-21'],
 ['forged binary match',a=>a.entries[1].candidate.identity_hash_checked=true],
 ['unsupported license',a=>a.entries[3].candidate.rights_cleared_for_rehosting=true],
 ['unauthorized WordPress upload',a=>a.entries[0].candidate.wp_media_upload_allowed=true],
 ['unauthorized Gutenberg rewrite',a=>a.entries[0].candidate.post_rewrite_allowed=true],
 ['invented 960 square output',a=>a.entries[0].candidate.proposed_derived_dimensions_px={width:960,height:960}],
 ['upscaling allowed',a=>a.entries[3].candidate.no_upscaling=false],
 ['catalog medium label falsely intrinsic',a=>a.entries[0].candidate.medium_rendition_catalog_label='Image is 1280 by 1280'],
 ['hide Army Signal Corps origin',a=>a.entries[4].candidate.credit='U.S. Navy only'],
 ['claim LST-480 certain',a=>a.entries[4].candidate.scene='Definitely USS LST-480'],
 ['misrepresent Bougainville as 1944 West Loch',a=>a.entries[1].candidate.scene='West Loch disaster 1944'],
 ['claim retriever HTTP 404',a=>a.entries[0].independent_retrieval.http_status=404],
 ['claim image retriever success',a=>a.entries[3].independent_retrieval.outcome='200'],
 ['wrong full-res Navy dimensions',a=>a.entries[3].candidate.catalog_high_tiff_reported_dimensions_px.height=1280],
 ['remove primary-source rights policy',a=>a.rights_policy_url='https://some-blog.example/policy']
];
for(const [name,mutate] of modifications)test('fail-closed: '+name,()=>{
 const v=clone(audit);mutate(v);assert.ok(validate(v,source).length>0,name);
});
test('Navy imageDownload image= changes actual historical photo identity',()=>{
 assert.equal(sameSource(audit.entries[0].source_url,audit.entries[3].source_url),false);
});
test('Navy rendition= is not treated as a different historical photo',()=>{
 const src=audit.entries[0].source_url;
 assert.equal(sameSource(src,src.replace('cq5dam.web.1280.1280.jpeg','cq5dam.web.319.319.png')),true);
});
