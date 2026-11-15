'use strict';
const assert=require('node:assert/strict');
const {test}=require('node:test');
const {validate}=require('./validate_wp_media_census_20261115.cjs');
const clone=x=>JSON.parse(JSON.stringify(x));
function fixture(){
 const spec=new Map([[2640,[1917,7422309,1964,2619]],[2638,[1920,1745282,2720,3649]],
  [2636,[1924,4462854,2988,3538]],[2637,[1926,1647642,1436,2001]]]);
 const extra=64385752-15278087;
 const media=[...spec].map(([id,[parent,bytes,w,h]])=>({id,parent_post_id:parent,stored_original_bytes:bytes,
   native_width_px:w,native_height_px:h,source_url:`https://finalvestige.com/wp-content/uploads/2026/11/${id}.jpg`}));
 // 16 non-new oversized originals, one of which balances the known 49,107,665 B baseline.
 for(let i=0;i<16;i++)media.push({id:100+i,parent_post_id:null,stored_original_bytes:i?1500001:extra-15*1500001,
 native_width_px:2000,native_height_px:1200,source_url:`https://finalvestige.com/wp-content/uploads/2026/08/old${i}.jpg`});
 // Remaining 112 smaller originals: synthetic only, chosen to balance actual census total.
 const remainder=90403013-64385752;
 for(let i=0;i<112;i++)media.push({id:500+i,parent_post_id:null,stored_original_bytes:i===0?remainder-111*232000:232000,
 native_width_px:960,native_height_px:540,source_url:`https://finalvestige.com/wp-content/uploads/2026/08/small${i}.jpg`});
 const licenses=['PD-Art','CC-BY-4.0','CC-BY-4.0','CC0-1.0'];
 const feature=[...spec].map(([id,[p,b,w,h]],i)=>({post_id:p,media_id:id,featured_media_id_from_post:id,
   wp_original_url:`https://finalvestige.com/wp-content/uploads/2026/11/${id}.jpg`,stored_original_bytes:b,
   inline_external_image_count:1,inline_contains_wp_original:false,placement:'featured_media_not_inline',
   source_catalog_url:`https://commons.wikimedia.org/wiki/File:${id}.jpg`,catalog_rights_claim:licenses[i],
   rights_review:id===2636?'source_rights_conflict':'review_required',
   review_width_px:960,review_height_px:Math.round(960*h/w),rehost_or_resize_authorized:false,
   wordpress_write_authorized:false,actual_guest_http_status:null,actual_guest_transfer_bytes:null,
   binary_sha256_verified:false,current_src_verified:false}));
 return {schema:'fv-wp-media-featured-oversize-20261115-v1',source:{kind:'authenticated_wordpress_media_list_read_only',page_count:2,per_page:100},
  census:{image_count:132,stored_original_bytes:90403013,oversize_count_decimal_1500000:20,
   oversize_stored_original_bytes:64385752,new_oversized_featured_bytes:15278087,
   historical_oct_30_published_posts:61,historical_oct_30_inline_images:355,reported_broken_unverified:42,
   claim_76_percent_guest_transfer_measured:false,guest_broken_confirmed_count:null,production_changes_this_audit:0},
  published_post_ids:Array.from({length:66},(_,i)=>i+1),media,new_oversized_featured_media:feature};
}
test('accept complete synthetic aggregate and properly held four-featured crosswalk',()=>{
 const r=validate(fixture());assert.equal(r.ok,true,JSON.stringify(r.errors));
 assert.equal(r.summary.oversized_stored_original_bytes,64385752);
});
const hold=(name,mut,term)=>test(name,()=>{const f=fixture();mut(f);const r=validate(f);assert.equal(r.ok,false);assert.ok(r.errors.some(s=>s.includes(term)),JSON.stringify(r.errors));});
hold('reject invented guest status',x=>x.new_oversized_featured_media[0].actual_guest_http_status=200,'premature_optimization');
hold('reject invented transfer savings',x=>x.census.claim_76_percent_guest_transfer_measured=true,'forbidden_or_inferred');
hold('reject publish permission without clearance',x=>x.new_oversized_featured_media[0].wordpress_write_authorized=true,'premature_optimization');
hold('reject fabricated inline placement',x=>x.new_oversized_featured_media[0].inline_contains_wp_original=true,'featured_vs_inline');
hold('reject duplicate WordPress media ID',x=>x.media[5].id=x.media[4].id,'duplicate_or_bad_id');
hold('reject altered stored bytes',x=>x.media[4].stored_original_bytes++, 'stored_original_total_mismatch');
hold('reject offsite masquerading as first-party media',x=>x.media[0].source_url='https://cdn.invalid/test.jpg','non_first_party');
hold('reject oversize threshold count changes',x=>x.media[5].stored_original_bytes=1499999,'oversize_count_mismatch');
hold('reject incorrect 960px proportional geometry',x=>x.new_oversized_featured_media[2].review_height_px=540,'unverified_960px');
hold('reject claimed binary identity based on equal metadata',x=>x.new_oversized_featured_media[0].binary_sha256_verified=true,'premature_optimization');
hold('reject false assertion that currentSrc was inspected',x=>x.new_oversized_featured_media[0].current_src_verified=true,'premature_optimization');
hold('reject omitted rights status',x=>x.new_oversized_featured_media[1].rights_review='cleared','missing_catalog');
hold('reject stale 61-post count treated as current',x=>x.published_post_ids.length=61,'published_post_census');
hold('reject 1.5MiB confusion on 1.5 decimal MB',x=>x.census.oversize_count_decimal_1500000=19,'oversize_count_mismatch');
