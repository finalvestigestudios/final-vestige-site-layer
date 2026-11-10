'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {validate}=require('./validate_browser_bridge_20261110.cjs');
const original=JSON.parse(fs.readFileSync(path.join(__dirname,'browser_handoff_6_p0_15_oversize_20261110.json'),'utf8'));
const clone=()=>JSON.parse(JSON.stringify(original));
assert.equal(validate(original).pass,true,JSON.stringify(validate(original).errors));
const failures=[
 ['forged_guest_404',d=>d.p0_queue[0].guest_http_status=404],
 ['forged_guest_200',d=>d.p0_queue[0].guest_http_status=200],
 ['false_broken_claim',d=>d.release.claim_42_verified=true],
 ['false_savings_claim',d=>d.methodology.measured_saving_pct=76],
 ['source_swap',d=>d.p0_queue[0].original_src=d.p0_queue[1].original_src],
 ['priority_reorder',d=>d.p0_queue.reverse()],
 ['unapproved_cache',d=>d.p0_queue[0].caching_approved=true],
 ['rights_fabrication',d=>d.p0_queue[0].reuse_rights_cleared=true],
 ['oversize_byte_swap',d=>d.oversized_media[0].stored_original_bytes--],
 ['oversize_id_swap',d=>d.oversized_media[0].media_id=9999],
 ['invented_wire',d=>d.oversized_media[0].guest_wire_bytes=999],
 ['wider_than_original',d=>d.oversized_media[0].conditional_960px=[9600,720]],
 ['mismatched_cohort',d=>d.cohorts.historical.posts=66],
 ['worklist_sham',d=>d.authority.worklist.blob_sha='f'.repeat(40)],
 ['url_replaced',d=>d.oversized_media[0].original_url='https://elsewhere.example/impostor.jpg'],
 ['rights_approved',d=>d.oversized_media[0].derivative_authorized=true],
 ['wrong_inline_total',d=>d.methodology.inline_referenced_original_storage_bytes=1],
 ['forged_first_party_fix',d=>d.release.wordpress_writes=1],
 ['false_retriever_status',d=>d.p0_queue[0].retriever_only.wrapper_code=200],
 ['fake_catalog',d=>d.p0_queue[0].catalog_candidate_url='https://example.org/fake.jpg'],
 ['forged_catalog_rights',d=>d.p0_queue[0].rights_observation='CLEARED'],
 ['media_rights_swap',d=>d.oversized_media[0].rights_observation='PUBLIC_DOMAIN'],
 ['media_native_dimensions_swap',d=>d.oversized_media[0].native_px=[1500,999]],
 ['media_inline_post_swap',d=>d.oversized_media[0].inline_post_ids=[12345]],
 ['media_generated_subsize_swap',d=>d.oversized_media[0].generated_subsizes=0],
 ['media_runtime_source_swap',d=>d.oversized_media[0].published_direct_srcs=['https://example.org/fake.jpg']]
];
for(const [name,mutate] of failures){const d=clone();mutate(d);assert.equal(validate(d).pass,false,'forged manifest accepted: '+name);}
console.log('PASS '+(failures.length+1)+'/'+(failures.length+1)+' offline handoff integrity cases (1 positive, '+failures.length+' negative)');
