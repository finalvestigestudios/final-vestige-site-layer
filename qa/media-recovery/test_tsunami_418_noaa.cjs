'use strict';
/** All negatives use a known catalog candidate, never a live production media URL. */
const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {validate}=require('./validate_tsunami_418_noaa.cjs');
const baseline=JSON.parse(fs.readFileSync(path.join(__dirname,'tsunami_418_noaa_catalog_20261031.json'),'utf8'));
function mutation(name,fn){
 test('reject '+name,()=>{const copy=JSON.parse(JSON.stringify(baseline));fn(copy);assert.equal(validate(copy).ok,false)});
}
test('original documentary-only candidate passes',()=>{assert.equal(validate(baseline).ok,true)});
mutation('wrong target historical image',x=>x.image_key='418:5');
mutation('swapped current publisher URL',x=>x.exact_stored_url='https://example.org/other.jpg');
mutation('invented NOAA catalog ID',x=>x.source_catalog_candidate.catalog_id='theb2706');
mutation('fabricated binary match',x=>x.source_catalog_candidate.same_binary_as_stored_url=true);
mutation('fabricated original width',x=>x.source_catalog_candidate.original_intrinsic_width_px=1920);
mutation('missing publisher caption evidence',x=>x.evidence=x.evidence.filter(v=>v.basis!=='publisher_caption'));
mutation('premature public-domain clearance',x=>x.rights.public_domain_assumed=true);
mutation('image upscaling',x=>x.candidate_delivery.upscale=true);
mutation('target width beyond 960',x=>x.candidate_delivery.max_width_px=1200);
mutation('invented WordPress media ID',x=>x.candidate_delivery.wordpress_media_id=90001);
mutation('production post rewrite approval',x=>x.candidate_delivery.wordpress_post_rewrite_authorized=true);
mutation('invented live browser 404',x=>x.visitor_verification.original_image_http_status=404);
mutation('invented browser success',x=>x.visitor_verification.verified_broken_in_browser=false);
mutation('invented 76% saving',x=>x.visitor_verification.image_weight_reduction_percent=76);
mutation('confusing candidate with cleared asset',x=>x.p0_candidate_tracking.source_candidate_only_not_rights_or_binary_clearance=false);
