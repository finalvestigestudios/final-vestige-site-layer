'use strict';
const {test}=require('node:test');const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');
const {validate}=require('./validate_p0_six_live_source_retriever_20261108.cjs');
const base=JSON.parse(fs.readFileSync(path.join(__dirname,'p0_six_live_source_retriever_20261108.json'),'utf8'));
test('actual six-P0 CMS readback and wrapper-only audit',()=>assert.deepEqual(validate(base),[]));
const changes=[
['fake browser 404',a=>a.rows[0].wrapper.guest_http=404],
['fake origin 404',a=>a.rows[0].wrapper.origin_http=404],
['false browser pixel evidence',a=>a.rows[0].wrapper.guest_pixels=[960,640]],
['false transfer bytes',a=>a.rows[0].wrapper.guest_bytes=300],
['false browser break',a=>a.rows[0].wrapper.guest_broken=true],
['swapped src',a=>a.rows[0].published_src=''],
['unverified CMS src',a=>a.rows[0].live_wp_exact_src_found=false],
['unpublished post',a=>a.rows[0].live_wp_post_published=false],
['one missing slot',a=>a.rows.pop()],
['duplicate slot',a=>a.rows[1].slot=a.rows[0].slot],
['wrong retriever status',a=>a.rows[1].wrapper.tool_status=404],
['method browser mislabel',a=>a.rows[1].wrapper.method='Chrome'],
['invented 960px TMI upscale',a=>a.rows[0].candidate.conditional_max_960_derivative=[960,720]],
['invented native size',a=>a.rows[1].candidate.native_dimensions=[900,600]],
['invented binary match',a=>a.rows[0].candidate.binary_sha256='hash'],
['false rights clearance',a=>a.rows[3].candidate.right_to_cache_or_republish_proven=true],
['editor approved falsely',a=>a.rows[3].candidate.editor_approved=true],
['fabricated 42 failures',a=>a.counts.verified_broken_42=true],
['fabricated 76 savings',a=>a.counts.measured_transfer_reduction_76=true],
['invented browser failure count',a=>a.counts.visitor_confirmed_broken=6],
['modified code date',a=>a.date_local='2026-11-09'],
['wrong readback count',a=>a.counts.p0_exact_wp_sources_verified=5],
['fake alternate render',a=>a.rows[0].candidate.rendered_by_retriever=true],
['WP write',a=>a.rows[0].actions.wp_post=true],
['cache third-party',a=>a.rows[1].actions.cache=true],
['media download',a=>a.rows[1].actions.fetch_binary=true],
['production writes',a=>a.release.wordpress_writes=1],
['spent subscription',a=>a.release.spend_usd=10],
['false completion',a=>a.release.guest_browser_verification=true],
['broken frozen provenance',a=>a.frozen_git_source.blob_sha='no']
];
for(const [n,f] of changes)test('fail closed: '+n,()=>{const a=JSON.parse(JSON.stringify(base));f(a);assert.ok(validate(a).length>0,n);});
