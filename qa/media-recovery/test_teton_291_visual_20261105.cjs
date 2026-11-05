'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {validate} = require('./validate_teton_291_visual_20261105.cjs');
const pristine = JSON.parse(fs.readFileSync(path.join(__dirname,'teton_291_live_visual_mismatch_20261105.json'),'utf8'));
const mutated = f => {const a=structuredClone(pristine);f(a);return a;};
test('pinned read-only audit passes',()=>assert.equal(validate(pristine).ok,true));
const mutations = [
  a=>a.schema='unsupported',
  a=>a.post.id=292,
  a=>a.pinned_inventory.git_blob='invented',
  a=>a.source_reused='https://example.com/not-the-image.jpg',
  a=>a.renderer.exact_url_rendered=false,
  a=>a.renderer.guest_browser_http_status=404,
  a=>a.renderer.bytes_transferred=1000,
  a=>a.rows.pop(),
  a=>a.rows[0].source_url='https://other.example/photo.jpg',
  a=>a.rows[0].retrieved_visual_matches_claim=true,
  a=>a.rows[1].retrieved_visual_matches_claim=false,
  a=>a.rows[0].caption='wrong photograph',
  a=>a.rows[1].caption='false date',
  a=>a.rows[0].visitor_visual_status='BROKEN',
  a=>a.rows[0].action='PUBLISH',
  a=>a.candidate_for_291_2.naid=28894688,
  a=>a.candidate_for_291_2.same_original_binary=true,
  a=>a.candidate_for_291_2.conditional_width_px=1200,
  a=>a.candidate_for_291_2.conditional_height_px=676,
  a=>a.candidate_for_291_2.rights_rehosting_authorized=true,
  a=>a.candidate_for_291_2.binary_fetched=true,
  a=>a.decision.browser_broken_images_confirmed=1,
  a=>a.decision.sitewide_claim_76_percent_weight_reduction_verified=true,
  a=>a.decision.wordpress_edit_authorized=true,
  a=>a.decision.cache_authorized=true,
  a=>a.decision.production_repairs=1
];
mutations.forEach((fn,i)=>test('reject unsafe or altered provenance / state #'+(i+1),()=>{assert.equal(validate(mutated(fn)).ok,false);}));
