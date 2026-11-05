'use strict';
/** Offline native Node tests, no network access or production mutations. */
const {test}=require('node:test'),assert=require('node:assert/strict');
const a=require('./live_wp_p0_and_oversize_13_20261105.json');
const {validateLiveRecheck}=require('./validate_live_wp_p0_and_oversize_13_20261105.cjs');
const clone=()=>structuredClone(a),bad=(mutate)=>{const v=clone();mutate(v);const r=validateLiveRecheck(v);assert.equal(r.pass,false,JSON.stringify(r));};
test('live WordPress image and media provenance audit passes its own release gates',()=>{
 const r=validateLiveRecheck(a);assert.equal(r.pass,true,JSON.stringify(r));
 assert.equal(r.live_large_originals,13);assert.equal(r.live_original_storage_bytes,43522829);
 assert.equal(r.production_media_changes_authorized,false);
});
const mutations=[
 ['invented 76% performance claim',v=>v.performance_claims.reported_76_percent_reduction='VERIFIED'],
 ['fabricated fresh sitewide census',v=>v.fresh_sitewide_posts_count=61],
 ['invented origin HTTP 404',v=>v.prioritized_existing_p0_exact_live_sources[0].actual_browser_status=404],
 ['cached P0 photo without rights',v=>v.prioritized_existing_p0_exact_live_sources[0].localize_or_rewrite_authorized=true],
 ['deleted P0 check',v=>v.prioritized_existing_p0_exact_live_sources.pop()],
 ['wrong P0 slot',v=>v.prioritized_existing_p0_exact_live_sources[1].image_key='285:3'],
 ['unverified P0 CMS source',v=>v.prioritized_existing_p0_exact_live_sources[2].frozen_source_url_matches_latest_read_only_wp=false],
 ['invented visitor bytes',v=>v.oversized_media[0].visitor_transfer_bytes=182000],
 ['fabricated rehost rights',v=>v.oversized_media[0].media_rights='CLEARED'],
 ['authorized production upload',v=>v.oversized_media[0].wp_upload_authorized=true],
 ['upscaled derivative',v=>v.oversized_media[0].proposed_max_derivative_px=[1920,1279]],
 ['incorrect output height',v=>v.oversized_media[0].proposed_max_derivative_px[1]++],
 ['duplicate WordPress media ID',v=>v.oversized_media[1].media_id=v.oversized_media[0].media_id],
 ['stored-size drift',v=>v.oversized_media[1].wp_original_stored_bytes++],
 ['below-threshold original',v=>v.oversized_media[1].wp_original_stored_bytes=1048576],
 ['missing mapped live article',v=>v.oversized_media.find(x=>x.live_published_post_exact_image_source_confirmed).live_published_post_id=null],
 ['falsely mapped previously unverified article',v=>v.oversized_media.find(x=>!x.live_published_post_exact_image_source_confirmed).live_published_post_id=777],
 ['fake additional current originals',v=>v.live_media_inventory.oversized_original_count=14],
 ['invented downloaded binary',v=>v.oversized_media[0].image_downloaded=true],
 ['out-of-scope homepage action',v=>v.staging_plan.no_homepage_design_change=false]
];
for(const [name,mutate] of mutations)test('fail closed: '+name,()=>bad(mutate));
