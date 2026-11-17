'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {validateTmi285}=require('./validate_tmi_285.cjs');
const ORIGINAL=JSON.parse(fs.readFileSync(path.join(__dirname,'tmi_285_nrc_recovery_20261101.json'),'utf8'));
const copy=()=>structuredClone(ORIGINAL);
test('valid six-slot published source and rights-held custody ledger',()=>{
  assert.deepEqual(validateTmi285(copy()),{ok:true,validated_slots:6,retriever_not_browser:true,wp_writes_authorized:0});
});
const mutationCases=[
['fabricated browser failure',d=>d.rows[5].browser.status=404],
['fabricated browser proof',d=>d.rows[5].browser.logged_out_verified=true],
['false original HTTP 404 from retriever',d=>d.rows[5].viewer.origin_http_status=404],
['false encoded image bytes',d=>d.rows[4].viewer.encoded_transfer_bytes=9999],
['wrong retriever status',d=>d.rows[5].viewer.result='IMAGE_RENDERED'],
['invented retriever response',d=>d.rows[1].viewer.retriever_error_code=200],
['false 42 broken claim',d=>d.claimed_broken_42_verified=true],
['false 76 percent savings',d=>d.claimed_76pct_weight_reduction_measured=true],
['fabricated before bytes',d=>d.measured_before_image_bytes=1000],
['claimed production repair',d=>d.production_images_repaired=1],
['wrong URL',d=>d.rows[0].original_source_url='https://example.invalid/image.jpg'],
['wrong ALT',d=>d.rows[1].original_alt='A different photo'],
['duplicate key',d=>d.rows[5].key='285:0'],
['illicit upload flag',d=>d.rows[5].candidate.wordpress_upload_authorized=true],
['rights auto-granted',d=>d.rows[0].candidate.rights_review='PUBLIC_DOMAIN'],
['copyright check skipped',d=>d.rows[4].candidate.rights_note=''],
['invented SHA',d=>d.rows[3].candidate.master_sha256='deadbeef'],
['invented identity match',d=>d.rows[4].candidate.binary_identity_verified=true],
['unauthorized editorial edit',d=>d.rows[3].candidate.wordpress_post_edit_authorized=true],
['fake visual QA',d=>d.rows[5].candidate.visual_QA_complete=true],
['upscale narrow Commons original',d=>d.rows[5].candidate.conditional_max_dimensions.width_px=960],
['incorrect portrait geometry',d=>d.rows[4].candidate.conditional_max_dimensions.height_px=960],
['invalid target policy',d=>d.rows[2].candidate.candidate_width_cap_px=1024],
['unmatched photo invented geometry',d=>d.rows[1].candidate.source_width_px=1024],
['post count mutated',d=>d.source_count=7],
['slot order mutated',d=>d.rows.reverse()],
];
for(const [name,mutate] of mutationCases){test(name+' fails closed',()=>{const d=copy();mutate(d);assert.throws(()=>validateTmi285(d));});}
