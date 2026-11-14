'use strict';
/** Read-only fail-closed stored-media baseline validator; no network/CMS operations. */

// Frozen Nov 13 WordPress readback: prevent same-host source substitution, byte swaps,
// media metadata drift and silent addition of permissions. This is NOT live HTTP verification.
const FROZEN_IDENTITIES={
 "39": [
  "https://finalvestige.com/wp-content/uploads/2026/08/bceca0bd-a16f-44f7-be08-16376fbf08ca.png",
  "2026-08-16T22:03:37",
  34,
  "image/png",
  2892087,
  1672,
  941,
  []
 ],
 "40": [
  "https://finalvestige.com/wp-content/uploads/2026/08/377e08da-e121-4f57-9174-1548343402b3.png",
  "2026-08-16T22:03:42",
  35,
  "image/png",
  2552136,
  1672,
  941,
  []
 ],
 "41": [
  "https://finalvestige.com/wp-content/uploads/2026/08/a44f673d-a8a8-4c83-9f29-7e24dd55156b.png",
  "2026-08-16T22:03:47",
  36,
  "image/png",
  2498247,
  1672,
  941,
  []
 ],
 "42": [
  "https://finalvestige.com/wp-content/uploads/2026/08/c1237ffd-4a47-4988-8254-e3b021069e72.png",
  "2026-08-16T22:03:52",
  37,
  "image/png",
  2488823,
  1672,
  941,
  []
 ],
 "43": [
  "https://finalvestige.com/wp-content/uploads/2026/08/01340c2e-1165-4ca0-aa96-87398a83d13a.png",
  "2026-08-16T22:03:58",
  38,
  "image/png",
  2836245,
  1672,
  941,
  []
 ],
 "293": [
  "https://finalvestige.com/wp-content/uploads/2026/08/ne.png",
  "2026-08-19T13:46:39",
  null,
  "image/png",
  2090327,
  1122,
  1402,
  [
   {
    "name": "medium",
    "virtual": true
   },
   {
    "name": "large",
    "virtual": true
   },
   {
    "name": "thumbnail",
    "virtual": true
   },
   {
    "name": "medium_large",
    "virtual": true
   },
   {
    "name": "full",
    "virtual": false
   }
  ]
 ],
 "382": [
  "https://finalvestige.com/wp-content/uploads/2026/08/vasa-med-gamla-och-nya-stottor_vasa-with-old-and-new-supports.jpg",
  "2026-08-20T00:02:02",
  299,
  "image/jpeg",
  2318980,
  1800,
  1200,
  [
   {
    "name": "medium",
    "virtual": true
   },
   {
    "name": "large",
    "virtual": true
   },
   {
    "name": "thumbnail",
    "virtual": true
   },
   {
    "name": "medium_large",
    "virtual": true
   },
   {
    "name": "1536x1536",
    "virtual": true
   },
   {
    "name": "full",
    "virtual": false
   }
  ]
 ],
 "388": [
  "https://finalvestige.com/wp-content/uploads/2026/08/vasa-modell-2020.jpg",
  "2026-08-20T00:02:12",
  299,
  "image/jpeg",
  8176362,
  4256,
  2832,
  [
   {
    "name": "medium",
    "virtual": true
   },
   {
    "name": "large",
    "virtual": true
   },
   {
    "name": "thumbnail",
    "virtual": true
   },
   {
    "name": "medium_large",
    "virtual": true
   },
   {
    "name": "1536x1536",
    "virtual": true
   },
   {
    "name": "2048x2048",
    "virtual": true
   },
   {
    "name": "full",
    "virtual": false
   }
  ]
 ],
 "389": [
  "https://finalvestige.com/wp-content/uploads/2026/08/vasa-01-2020.jpg",
  "2026-08-20T00:02:14",
  299,
  "image/jpeg",
  2822969,
  2147,
  1417,
  [
   {
    "name": "medium",
    "virtual": true
   },
   {
    "name": "large",
    "virtual": true
   },
   {
    "name": "thumbnail",
    "virtual": true
   },
   {
    "name": "medium_large",
    "virtual": true
   },
   {
    "name": "1536x1536",
    "virtual": true
   },
   {
    "name": "2048x2048",
    "virtual": true
   },
   {
    "name": "full",
    "virtual": false
   }
  ]
 ],
 "405": [
  "https://finalvestige.com/wp-content/uploads/2026/08/The20Water20Resilience20Field20Manual.png",
  "2026-08-20T00:15:36",
  85,
  "image/png",
  2201573,
  1122,
  1402,
  [
   {
    "name": "medium",
    "virtual": true
   },
   {
    "name": "large",
    "virtual": true
   },
   {
    "name": "thumbnail",
    "virtual": true
   },
   {
    "name": "medium_large",
    "virtual": true
   },
   {
    "name": "full",
    "virtual": false
   }
  ]
 ],
 "482": [
  "https://finalvestige.com/wp-content/uploads/2026/08/050e21e0-7b54-4f9a-ba0b-7f594657af05.png",
  "2026-08-20T19:48:17",
  null,
  "image/png",
  2293016,
  1672,
  941,
  [
   {
    "name": "medium",
    "virtual": true
   },
   {
    "name": "large",
    "virtual": true
   },
   {
    "name": "thumbnail",
    "virtual": true
   },
   {
    "name": "medium_large",
    "virtual": true
   },
   {
    "name": "1536x1536",
    "virtual": true
   },
   {
    "name": "full",
    "virtual": false
   }
  ]
 ],
 "1257": [
  "https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v01-malbone-tunnel-generalpunger-original.jpg",
  "2026-08-31T13:58:33",
  null,
  "image/jpeg",
  4798395,
  4000,
  3000,
  [
   {
    "name": "medium",
    "virtual": true
   },
   {
    "name": "large",
    "virtual": true
   },
   {
    "name": "thumbnail",
    "virtual": true
   },
   {
    "name": "medium_large",
    "virtual": true
   },
   {
    "name": "1536x1536",
    "virtual": true
   },
   {
    "name": "2048x2048",
    "virtual": true
   },
   {
    "name": "full",
    "virtual": false
   }
  ]
 ],
 "1258": [
  "https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v02-nypl-5003296-original.jpg",
  "2026-08-31T13:58:36",
  null,
  "image/jpeg",
  5553669,
  5667,
  3831,
  [
   {
    "name": "medium",
    "virtual": true
   },
   {
    "name": "large",
    "virtual": true
   },
   {
    "name": "thumbnail",
    "virtual": true
   },
   {
    "name": "medium_large",
    "virtual": true
   },
   {
    "name": "1536x1536",
    "virtual": true
   },
   {
    "name": "2048x2048",
    "virtual": true
   },
   {
    "name": "full",
    "virtual": false
   }
  ]
 ],
 "1714": [
  "https://finalvestige.com/wp-content/uploads/2026/10/halifax-explosion-map.png",
  "2026-10-29T15:20:33",
  null,
  "image/png",
  1543002,
  1280,
  1280,
  [
   {
    "name": "medium",
    "virtual": true
   },
   {
    "name": "large",
    "virtual": true
   },
   {
    "name": "thumbnail",
    "virtual": true
   },
   {
    "name": "medium_large",
    "virtual": true
   },
   {
    "name": "full",
    "virtual": false
   }
  ]
 ],
 "2148": [
  "https://finalvestige.com/wp-content/uploads/2026/11/1927-caernarvon-levee-explosion-noaa-archive.jpg",
  "2026-11-07T11:37:04",
  null,
  "image/jpeg",
  2030948,
  1821,
  1190,
  [
   {
    "name": "medium",
    "virtual": true
   },
   {
    "name": "large",
    "virtual": true
   },
   {
    "name": "thumbnail",
    "virtual": true
   },
   {
    "name": "medium_large",
    "virtual": true
   },
   {
    "name": "1536x1536",
    "virtual": true
   },
   {
    "name": "full",
    "virtual": false
   }
  ]
 ],
 "2432": [
  "https://finalvestige.com/wp-content/uploads/2026/11/final-vestige-artifact-editions-editorial-concept.png",
  "2026-11-12T01:53:45",
  2429,
  "image/png",
  2010886,
  1280,
  720,
  [
   {
    "name": "medium",
    "virtual": true
   },
   {
    "name": "large",
    "virtual": true
   },
   {
    "name": "thumbnail",
    "virtual": true
   },
   {
    "name": "medium_large",
    "virtual": true
   },
   {
    "name": "full",
    "virtual": false
   }
  ]
 ]
};
const FROZEN_ROW_KEYS="conditional_derivative_max_px,exact_visual_parity_verified,local_copy_or_cache_authorized,media_id,mime_type,native_dimensions_px,original_stored_bytes,parent_content_id,rights_status,rights_to_rehost_verified,source_url,uploaded_date,visitor_encoded_transfer_bytes,visitor_image_http_status,wordpress_size_descriptors";
const FROZEN_ROOT_KEYS="inventory,notes,observed_local_date,oversized_media,production_media_changes,rights_and_quality_policy,schema,scope,source_method,visitor_verified_repair_count";
const FROZEN_INVENTORY_KEYS="added_media_is_proven_published_article_image,added_media_parent_page_id,added_media_parent_status,added_media_published_inline_usage,added_original_media_id,added_original_stored_bytes,claimed_76_percent_wire_reduction_measured,historical_reported_broken_42_guest_confirmed,older_frozen_inline_image_count,older_frozen_post_count,originals_above_1500000_decimal_bytes,originals_above_1500000_total_storage_bytes,prior_15_originals_total_storage_bytes,published_post_count,wordpress_image_media_count";
const FROZEN_POLICY_KEYS="binary_downloads_authorized,cache_authorized,cold_uncached_browser_bytes_required,css_width_dpr_verification_required,exact_scene_and_crop_review_required,homepage_design_in_scope,max_conditional_width_px,no_upscale,rights_copyright_attribution_review_required,wordpress_rewrites_authorized";
const FROZEN_DIMENSION_KEYS="height,width";
const FROZEN_DERIVATIVE_KEYS="approved,height,no_upscale,width";
const FROZEN_DESCRIPTOR_KEYS="name,virtual";
const exactKeys=(o,expected)=>!!o&&typeof o==='object'&&!Array.isArray(o)&&Object.keys(o).sort().join(',')===expected;
const frozenTuple=r=>[r.source_url,r.uploaded_date,r.parent_content_id,r.mime_type,r.original_stored_bytes,r.native_dimensions_px?.width,r.native_dimensions_px?.height,r.wordpress_size_descriptors];

const LEGACY_IDS = [39,40,41,42,43,293,382,388,389,405,482,1257,1258,1714,2148];
function validate(data) {
 const errors=[];
 const fail=x=>errors.push(x);
 if(!data || typeof data!=='object' || Array.isArray(data))return {ok:false,errors:['invalid_audit']};
 if(data.schema!=='fv-media-current-16-draft-exposure-20261113-v1')fail('schema');
 if(data.source_method!=='read-only authenticated WordPress media.list images pages 1+2, posts.list published and pages.get 2429 edit')fail('source_method');
 const meta=data.inventory||{},rows=data.oversized_media;
 if(!exactKeys(data,FROZEN_ROOT_KEYS)||!exactKeys(meta,FROZEN_INVENTORY_KEYS)||!exactKeys(data.rights_and_quality_policy,FROZEN_POLICY_KEYS))fail('unexpected_evidence_fields');
 if(!Array.isArray(rows)||rows.length!==16)fail('row_count');
 if(meta.published_post_count!==66||meta.wordpress_image_media_count!==123||meta.older_frozen_post_count!==61||meta.older_frozen_inline_image_count!==355)fail('cohort_counts');
 if(meta.originals_above_1500000_decimal_bytes!==16||meta.originals_above_1500000_total_storage_bytes!==49107665||meta.prior_15_originals_total_storage_bytes!==47096779)fail('storage_baseline');
 if(meta.added_original_media_id!==2432||meta.added_original_stored_bytes!==2010886||meta.added_media_parent_page_id!==2429||meta.added_media_parent_status!=='draft'||meta.added_media_is_proven_published_article_image!==false||meta.added_media_published_inline_usage!==null)fail('draft_exposure');
 if(meta.historical_reported_broken_42_guest_confirmed!==false||meta.claimed_76_percent_wire_reduction_measured!==false)fail('unsupported_claim');
 const policy=data.rights_and_quality_policy||{};
 for(const x of ['exact_scene_and_crop_review_required','rights_copyright_attribution_review_required','no_upscale','css_width_dpr_verification_required','cold_uncached_browser_bytes_required'])if(policy[x]!==true)fail('policy_'+x);
 for(const x of ['wordpress_rewrites_authorized','binary_downloads_authorized','cache_authorized','homepage_design_in_scope'])if(policy[x]!==false)fail('unsafe_policy_'+x);
 if(policy.max_conditional_width_px!==960||data.visitor_verified_repair_count!==0||data.production_media_changes!==0)fail('release_claim');
 const ids=new Set();let stored=0,legacy=0;
 for(const r of Array.isArray(rows)?rows:[]){
  if(!Number.isSafeInteger(r.media_id)||ids.has(r.media_id))fail('duplicate_or_invalid_media_id');
  ids.add(r.media_id);
  if(!exactKeys(r,FROZEN_ROW_KEYS)||!exactKeys(r.native_dimensions_px,FROZEN_DIMENSION_KEYS)||!exactKeys(r.conditional_derivative_max_px,FROZEN_DERIVATIVE_KEYS)||!Array.isArray(r.wordpress_size_descriptors)||r.wordpress_size_descriptors.some(d=>!exactKeys(d,FROZEN_DESCRIPTOR_KEYS)))fail('unexpected_media_fields');
  if(!Object.prototype.hasOwnProperty.call(FROZEN_IDENTITIES,r.media_id)||JSON.stringify(frozenTuple(r))!==JSON.stringify(FROZEN_IDENTITIES[r.media_id]))fail('frozen_source_identity_'+r.media_id);
  if(typeof r.source_url!=='string'||!/^https:\/\/finalvestige\.com\/wp-content\/uploads\/[^\s]+$/i.test(r.source_url))fail('media_origin');
  if(!Number.isSafeInteger(r.original_stored_bytes)||r.original_stored_bytes<=1500000)fail('threshold');
  stored+=Number.isSafeInteger(r.original_stored_bytes)?r.original_stored_bytes:0;
  if(LEGACY_IDS.includes(r.media_id))legacy+=r.original_stored_bytes;
  const d=r.native_dimensions_px||{},z=r.conditional_derivative_max_px||{};
  if(!Number.isSafeInteger(d.width)||d.width<1||!Number.isSafeInteger(d.height)||d.height<1||!Number.isSafeInteger(z.width)||z.width<1||z.width>960||z.width>d.width||!Number.isSafeInteger(z.height)||z.height<1||z.height>d.height||Math.abs(z.height-Math.round(d.height*z.width/d.width))>1||z.no_upscale!==true||z.approved!==false)fail('unsafe_derivative');
  if(!Array.isArray(r.wordpress_size_descriptors)||r.wordpress_size_descriptors.some(x=>typeof x.name!=='string'||typeof x.virtual!=='boolean'))fail('size_evidence');
  if(r.rights_status!=='PENDING_ITEM_LEVEL_REVIEW'||r.rights_to_rehost_verified!==false||r.exact_visual_parity_verified!==false||r.visitor_image_http_status!==null||r.visitor_encoded_transfer_bytes!==null||r.local_copy_or_cache_authorized!==false)fail('fabricated_rights_or_browser_evidence');
  if(r.media_id===2432&& (r.parent_content_id!==2429||r.original_stored_bytes!==2010886||r.native_dimensions_px.width!==1280||r.native_dimensions_px.height!==720||!r.source_url.endsWith('/2026/11/final-vestige-artifact-editions-editorial-concept.png')))fail('new_draft_asset_identity');
 }
 if(ids.size!==16||LEGACY_IDS.some(id=>!ids.has(id))||!ids.has(2432))fail('membership');
 if(stored!==49107665||legacy!==47096779)fail('sum_mismatch');
 return {ok:errors.length===0,errors:[...new Set(errors)]};
}
module.exports={validate};
