'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {validateLedger}=require('./validate_port_chicago_211_20261103.cjs');
const baseline=JSON.parse(fs.readFileSync(__dirname+'/port_chicago_211_nps_proxy_20261103.json','utf8'));
const clone=()=>structuredClone(baseline);
test('baseline six-image audit accepted',()=>assert.equal(validateLedger(clone()).ok,true));
const cases=[
 ['invent 200 origin HTTP',d=>{d.rows[0].source_transport.numeric_origin_http_status=200}],
 ['invent browser failure 404',d=>{d.rows[0].source_transport.guest_browser_http_status=404}],
 ['invent CDP bytes',d=>{d.rows[0].source_transport.guest_cdp_uncached_wire_bytes=17000}],
 ['claim 76% weight reduction',d=>{d.summary.weight_reduction_pct_measured=76}],
 ['claim visitor images confirmed broken',d=>{d.summary.confirmed_guest_broken_images=6}],
 ['claim all loaded by Chrome',d=>{d.summary.confirmed_guest_broken_images_observed=true}],
 ['change frozen source blob',d=>{d.article.frozen_inventory_blob_sha='unknown'}],
 ['forget content modification timestamp',d=>{d.article.wp_last_modified='2026-10-30'}],
 ['mistake Jetpack NPS proxy for first-party',d=>{d.rows[0].effective_rendered_src_host='finalvestige.com'}],
 ['change NPS proxy to wrong publisher',d=>{d.rows[0].wp_api_rendered_img_url='https://i0.wp.com/attacker.invalid/photo.jpg'}],
 ['swap NPS image filenames',d=>{d.rows[1].archived_20261030_url=d.rows[0].archived_20261030_url}],
 ['swap alt',d=>{d.rows[2].wp_api_rendered_alt='Another historical event'}],
 ['hallucinate NPS media catalog ID',d=>{d.rows[0].registered_nps_item_id='POCH UNKNOWN'}],
 ['assign unsourced image intrinsic pixels',d=>{d.rows[3].original_intrinsic_width_px=960}],
 ['upscale derivative to 1200',d=>{d.rows[0].conditional_960_derivative.width_px=1200}],
 ['fabricate caption image rights',d=>{d.rows[5].rights.item_level_rights_approved=true}],
 ['approve wordpress live upload',d=>{d.rows[5].hold.wordpress_upload=true}],
 ['approve wordpress live post edit',d=>{d.rows[5].hold.wordpress_post_edit=true}],
 ['pretend trial image has layout aspect ratio',d=>{d.rows[4].wp_html_img_width_px=1024}],
 ['remove original master orientation discrepancy',d=>{d.rows[1].master_aspect_ratio_conflict=false}],
 ['rewrite NPS gallery master identity',d=>{d.rows[1].nps_gallery_master_candidate.source_record='another'}],
 ['set master as exact matching binary without check',d=>{d.rows[1].nps_gallery_master_candidate.proven_same_binary=true}],
 ['claim permission from NPS custody',d=>{d.release_gate.rights_per_item_required=false}],
 ['claim production repaired',d=>{d.summary.wordpress_replacements_made=6}],
 ['duplicate image slot',d=>{d.rows[3].image_key='211:2'}],
 ['remove a slot',d=>{d.rows.pop()}]
];
for(const [name,mut] of cases)test('fail closed: '+name,()=>{const d=clone();mut(d);assert.equal(validateLedger(d).ok,false,name)});
