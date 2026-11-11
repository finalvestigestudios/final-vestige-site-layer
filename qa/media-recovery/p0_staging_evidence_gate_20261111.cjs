'use strict';

/**
 * Offline-only media-recovery decision contract.
 * Requires independently collected, complete, logged-out cold Chrome evidence.
 * Never fetches images or authorizes a WordPress/production mutation.
 * Source inventory: browser_handoff_6_p0_15_oversize_20261110.json.
 */
const P0_ORDER = Object.freeze(['285:5','285:2','287:5','418:1','418:2','407:1']);
const https = value => typeof value === 'string' && /^https:\/\/[^/\s]+\//.test(value);
const integer = value => Number.isSafeInteger(value) && value >= 0;
const px = value => Number.isSafeInteger(value) && value > 0;
const sha256 = value => typeof value === 'string' && /^[a-f0-9]{64}$/.test(value);
const imageMime = value => typeof value === 'string' && /^image\/(?:jpeg|png|gif|webp|avif|bmp|svg\+xml)(?:\s*;.*)?$/i.test(value.trim());

const PINNED_POST_PERMALINKS = Object.freeze({
  "285": "https://finalvestige.com/2026/08/19/the-light-said-closed-three-mile-island/",
  "287": "https://finalvestige.com/2026/08/19/the-warning-was-a-man-waving-sunshine-skyway/",
  "407": "https://finalvestige.com/2026/08/20/the-lake-wasnt-there-yesterday-hebgen/",
  "418": "https://finalvestige.com/2026/08/20/the-lighthouse-was-gone-at-dawn-1946-tsunami/"
});

function guestFinding(item, evidence) {
  if (!evidence) return {verdict:'UNVERIFIED', reason:'NO_GUEST_BROWSER_EVIDENCE'};
  if (evidence.source_slot !== item.slot || evidence.post_id !== item.post_id ||
      evidence.stored_original_src !== item.original_src)
    return {verdict:'HOLD', reason:'SOURCE_SLOT_OR_POST_MISMATCH'};
  // Verify that the CDP request, DOM source and screenshot were captured on
  // the actual published article, at its stored inline source position.
  // An unrelated page using the same image URL is not visitor evidence here.
  const pinnedPage = PINNED_POST_PERMALINKS[String(item.post_id)];
  const inlineOrdinal = Number(item.slot.split(':')[1]);
  if (!pinnedPage || evidence.page_url !== pinnedPage ||
      evidence.page_http_status !== 200 || evidence.page_census_complete !== true ||
      evidence.full_scroll_complete !== true ||
      !Number.isSafeInteger(inlineOrdinal) || inlineOrdinal < 0 ||
      evidence.stored_inline_ordinal !== inlineOrdinal ||
      evidence.dom_img_src !== item.original_src)
    return {verdict:'HOLD', reason:'PUBLISHED_PAGE_OR_DOM_SLOT_NOT_PROVEN'};
  if (typeof evidence.capture_run_id !== 'string' || !evidence.capture_run_id.trim() ||
      typeof evidence.request_id !== 'string' || !evidence.request_id.trim() ||
      evidence.response_request_id !== evidence.request_id ||
      evidence.dom_element_request_id !== evidence.request_id ||
      !sha256(evidence.screenshot_sha256))
    return {verdict:'HOLD', reason:'CDP_REQUEST_DOM_SCREENSHOT_CHAIN_NOT_PROVEN'};
  if (evidence.method !== 'CHROME_CDP_LOGGED_OUT_COLD' ||
      evidence.network_capture_complete !== true ||
      !https(evidence.current_src) || !https(evidence.request_url) ||
      evidence.request_url !== evidence.current_src ||
      evidence.final_response_url !== evidence.current_src)
    return {verdict:'HOLD', reason:'UNPROVEN_CURRENT_SRC_OR_NETWORK_CAPTURE'};
  // A different selected image's HTTP failure must not convict the frozen
  // published original. CDN/Jetpack/srcset changes require independent review.
  if (evidence.current_src !== item.original_src)
    return {verdict:'HOLD', reason:'SELECTED_SOURCE_NOT_THE_PUBLISHED_ORIGINAL'};
  if (evidence.was_cached !== false || evidence.from_disk_cache !== false ||
      evidence.from_memory_cache !== false || evidence.from_service_worker !== false)
    return {verdict:'HOLD', reason:'UNCLEAR_COLD_CACHE_STATUS'};
  if (!Number.isInteger(evidence.final_http_status) ||
      evidence.final_http_status < 100 || evidence.final_http_status > 599 ||
      !integer(evidence.natural_width) || !integer(evidence.natural_height) ||
      !integer(evidence.encoded_data_length))
    return {verdict:'HOLD', reason:'INVALID_HTTP_GEOMETRY_OR_BYTES'};
  if (!evidence.screenshot_evidence_id || typeof evidence.screenshot_evidence_id !== 'string')
    return {verdict:'HOLD', reason:'MISSING_SCREENSHOT_EVIDENCE'};
  if (evidence.final_http_status >= 400 && evidence.natural_width === 0 &&
      evidence.natural_height === 0)
    return {verdict:'CONFIRMED_GUEST_BROKEN', reason:'COLD_HTTP_ERROR_AND_ZERO_IMAGE_DIMENSIONS', observed_http:evidence.final_http_status};
  if (evidence.final_http_status >= 200 && evidence.final_http_status < 300 &&
      px(evidence.natural_width) && px(evidence.natural_height)) {
    // DOM dimensions alone cannot establish a transferred and decoded image:
    // HTML fallbacks, aborted CDP requests or zero-byte bodies all stay HOLD.
    if (evidence.resource_type !== 'Image' ||
        evidence.loading_finished !== true ||
        !imageMime(evidence.response_mime_type) ||
        evidence.encoded_data_length === 0)
      return {verdict:'HOLD', reason:'IMAGE_MIME_LIFECYCLE_OR_BODY_BYTES_NOT_PROVEN'};
    return {verdict:'CONFIRMED_GUEST_DISPLAYED',
      reason:'COLD_HTTP_IMAGE_WITH_POSITIVE_DIMENSIONS_AND_BODY',
      observed_http:evidence.final_http_status};
  }
  return {verdict:'HOLD', reason:'HTTP_AND_IMAGE_GEOMETRY_INCONCLUSIVE'};
}

function candidateReview(item, approval, guestVerdict) {
  const hold = reason => ({state:'HOLD',reason,staging_permitted:false,production_permitted:false,output_px:null});
  if (guestVerdict !== 'CONFIRMED_GUEST_BROKEN') return hold('NO_CONFIRMED_GUEST_FAILURE');
  if (!approval) return hold('NO_INDEPENDENT_RIGHTS_AND_EDITOR_APPROVAL');
  if (approval.source_slot !== item.slot || approval.original_src !== item.original_src ||
      approval.candidate_catalog_url !== item.catalog_candidate_url ||
      !https(approval.candidate_catalog_url))
    return hold('CANDIDATE_NOT_BOUND_TO_EXACT_SOURCE');
  if (!https(approval.item_rights_evidence_url) || !approval.rights_reviewer ||
      !/^\d{4}-\d\d-\d\d$/.test(String(approval.rights_reviewed_date || '')) ||
      approval.commercial_republication_cleared !== true ||
      approval.attribution_plan_checked !== true)
    return hold('ITEM_SPECIFIC_COMMERCIAL_RIGHTS_NOT_CLEARED');
  if (approval.exact_photographic_identity_verified !== true ||
      approval.historical_date_and_scene_verified !== true ||
      approval.alt_and_caption_editor_approved !== true ||
      approval.crop_and_layout_editor_approved !== true ||
      !sha256(approval.candidate_asset_sha256))
    return hold('SCENE_CROP_EDITOR_OR_ASSET_IDENTITY_NOT_VERIFIED');
  if (!px(approval.native_width) || !px(approval.native_height) ||
      !px(approval.output_width) || !px(approval.output_height))
    return hold('DIMENSIONS_MISSING');
  const naturalCap = Math.min(960,approval.native_width);
  const naturalHeight = Math.round(approval.native_height * naturalCap / approval.native_width);
  if (approval.output_width !== naturalCap || approval.output_height !== naturalHeight)
    return hold('960PX_NO_UPSCALE_AND_FULL_FRAME_PARITY_FAILED');
  if (item.slot === '285:5' &&
      (approval.native_width !== 819 || approval.native_height !== 614))
    return hold('TMI_ORIGINAL_DIMENSIONS_IDENTITY_CONFLICT');
  return {state:'ELIGIBLE_FOR_HUMAN_STAGING_REVIEW_ONLY',
    reason:'ALL_EVIDENCE_GATES_PASSED_NO_UPLOAD_AUTHORITY',
    staging_permitted:false,production_permitted:false,
    output_px:[naturalCap,naturalHeight]};
}


/**
 * Custody gate for the immutable source-only P0 + oversize snapshot.
 * Do not silently accept a substituted image URL/catalog or manipulated stored
 * media sizes as proof for an unrelated original. A new approved census needs
 * an explicit reviewed update to these independent source pins.
 */
const PINNED_P0_SOURCE_ROWS = [
  {
    "slot": "285:5",
    "post_id": 285,
    "original_src": "https://images.saymedia-content.com/.image/ar_16:9,c_fill,cs_srgb,fl_progressive,q_auto:eco,w_1200/MTg5ODU1MTM1NjYzNDAwNjM2/the-china-syndrome-blockbuster-movie-becomes-eerie-prophecy.jpg",
    "catalog_candidate_url": "https://commons.wikimedia.org/wiki/File:Three_mile_island_062010.jpg",
    "candidate_kind": "COMMONS_CATALOG_RECORD",
    "rights_observation": "PD_SELF",
    "conditional_960px": [
      819,
      614
    ],
    "retriever_only": {
      "method": "EXTERNAL_WEB_RETRIEVER_NOT_GUEST",
      "result": "NOT_FOUND",
      "wrapper_code": 404
    }
  },
  {
    "slot": "285:2",
    "post_id": 285,
    "original_src": "https://blog.ucsusa.org/wp-content/uploads/2022/10/DBD-42-Figure-4-tmi-panel.jpg",
    "catalog_candidate_url": "https://blog.ucs.org/wp-content/uploads/2022/10/DBD-42-Figure-4-tmi-panel.jpg",
    "candidate_kind": "THIRD_PARTY_OR_PUBLISHER_REFERENCE",
    "rights_observation": "UNKNOWN",
    "conditional_960px": null,
    "retriever_only": {
      "method": "EXTERNAL_WEB_RETRIEVER_NOT_GUEST",
      "result": "REDIRECT_TARGET_INACCESSIBLE",
      "wrapper_code": 500
    }
  },
  {
    "slot": "287:5",
    "post_id": 287,
    "original_src": "https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg",
    "catalog_candidate_url": "https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg",
    "candidate_kind": "THIRD_PARTY_OR_PUBLISHER_REFERENCE",
    "rights_observation": "RIGHTS_UNVERIFIED",
    "conditional_960px": null,
    "retriever_only": {
      "method": "EXTERNAL_WEB_RETRIEVER_NOT_GUEST",
      "result": "NOT_FOUND",
      "wrapper_code": 404
    }
  },
  {
    "slot": "418:1",
    "post_id": 418,
    "original_src": "https://media.defense.gov/2021/Mar/30/2002610812/1920/1080/0/210330-G-DE713-0002.JPG",
    "catalog_candidate_url": "https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/",
    "candidate_kind": "OFFICIAL_PRIMARY_CATALOG",
    "rights_observation": "USCG_PUBLIC_DOMAIN_RELEASE_CATALOG",
    "conditional_960px": null,
    "retriever_only": {
      "method": "EXTERNAL_WEB_RETRIEVER_NOT_GUEST",
      "result": "FORBIDDEN",
      "wrapper_code": 403
    }
  },
  {
    "slot": "418:2",
    "post_id": 418,
    "original_src": "https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg",
    "catalog_candidate_url": "https://www.lighthousefriends.com/Scotch_Cap_debris2_1946.jpg",
    "candidate_kind": "THIRD_PARTY_OR_PUBLISHER_REFERENCE",
    "rights_observation": "RIGHTS_UNVERIFIED",
    "conditional_960px": null,
    "retriever_only": {
      "method": "EXTERNAL_WEB_RETRIEVER_NOT_GUEST",
      "result": "FORBIDDEN",
      "wrapper_code": 403
    }
  },
  {
    "slot": "407:1",
    "post_id": 407,
    "original_src": "https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg",
    "catalog_candidate_url": "https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/thumbnails/image/img7535.jpg",
    "candidate_kind": "THIRD_PARTY_OR_PUBLISHER_REFERENCE",
    "rights_observation": "USGS_PUBLIC_DOMAIN_CATALOG",
    "conditional_960px": null,
    "retriever_only": {
      "method": "EXTERNAL_WEB_RETRIEVER_NOT_GUEST",
      "result": "UNSUPPORTED_OCTET_STREAM",
      "wrapper_code": 400
    }
  }
];
const PINNED_OVERSIZE_ROWS = [
  {
    "media_id": 388,
    "original_url": "https://finalvestige.com/wp-content/uploads/2026/08/vasa-modell-2020.jpg",
    "stored_original_bytes": 8176362,
    "native_px": [
      4256,
      2832
    ],
    "conditional_960px": [
      960,
      639
    ],
    "inline_post_ids": [
      299
    ],
    "published_direct_srcs": [
      "https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/vasa-modell-2020.jpg?fit=1024%2C681&ssl=1"
    ],
    "generated_subsizes": 7,
    "rights_observation": "EDITORIAL_ONLY_MUSEUM_CREDIT_REQUIRED"
  },
  {
    "media_id": 1258,
    "original_url": "https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v02-nypl-5003296-original.jpg",
    "stored_original_bytes": 5553669,
    "native_px": [
      5667,
      3831
    ],
    "conditional_960px": [
      960,
      649
    ],
    "inline_post_ids": [
      621
    ],
    "published_direct_srcs": [
      "https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v02-nypl-5003296-original.jpg"
    ],
    "generated_subsizes": 7,
    "rights_observation": "ITEM_LEVEL_REVIEW_REQUIRED"
  },
  {
    "media_id": 1257,
    "original_url": "https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v01-malbone-tunnel-generalpunger-original.jpg",
    "stored_original_bytes": 4798395,
    "native_px": [
      4000,
      3000
    ],
    "conditional_960px": [
      960,
      720
    ],
    "inline_post_ids": [
      621
    ],
    "published_direct_srcs": [
      "https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v01-malbone-tunnel-generalpunger-original.jpg"
    ],
    "generated_subsizes": 7,
    "rights_observation": "ITEM_LEVEL_REVIEW_REQUIRED"
  },
  {
    "media_id": 39,
    "original_url": "https://finalvestige.com/wp-content/uploads/2026/08/bceca0bd-a16f-44f7-be08-16376fbf08ca.png",
    "stored_original_bytes": 2892087,
    "native_px": [
      1672,
      941
    ],
    "conditional_960px": [
      960,
      540
    ],
    "inline_post_ids": [
      34
    ],
    "published_direct_srcs": [
      "https://finalvestige.com/wp-content/uploads/2026/08/bceca0bd-a16f-44f7-be08-16376fbf08ca.png"
    ],
    "generated_subsizes": 0,
    "rights_observation": "HISTORICAL_RECONSTRUCTION_CREATOR_LICENSE_UNVERIFIED"
  },
  {
    "media_id": 43,
    "original_url": "https://finalvestige.com/wp-content/uploads/2026/08/01340c2e-1165-4ca0-aa96-87398a83d13a.png",
    "stored_original_bytes": 2836245,
    "native_px": [
      1672,
      941
    ],
    "conditional_960px": [
      960,
      540
    ],
    "inline_post_ids": [
      38
    ],
    "published_direct_srcs": [
      "https://finalvestige.com/wp-content/uploads/2026/08/01340c2e-1165-4ca0-aa96-87398a83d13a.png"
    ],
    "generated_subsizes": 0,
    "rights_observation": "HISTORICAL_RECONSTRUCTION_CREATOR_LICENSE_UNVERIFIED"
  },
  {
    "media_id": 389,
    "original_url": "https://finalvestige.com/wp-content/uploads/2026/08/vasa-01-2020.jpg",
    "stored_original_bytes": 2822969,
    "native_px": [
      2147,
      1417
    ],
    "conditional_960px": [
      960,
      634
    ],
    "inline_post_ids": [
      299
    ],
    "published_direct_srcs": [
      "https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/vasa-01-2020.jpg?fit=1024%2C676&ssl=1"
    ],
    "generated_subsizes": 7,
    "rights_observation": "ITEM_LEVEL_REVIEW_REQUIRED"
  },
  {
    "media_id": 40,
    "original_url": "https://finalvestige.com/wp-content/uploads/2026/08/377e08da-e121-4f57-9174-1548343402b3.png",
    "stored_original_bytes": 2552136,
    "native_px": [
      1672,
      941
    ],
    "conditional_960px": [
      960,
      540
    ],
    "inline_post_ids": [
      35
    ],
    "published_direct_srcs": [
      "https://finalvestige.com/wp-content/uploads/2026/08/377e08da-e121-4f57-9174-1548343402b3.png"
    ],
    "generated_subsizes": 0,
    "rights_observation": "HISTORICAL_RECONSTRUCTION_CREATOR_LICENSE_UNVERIFIED"
  },
  {
    "media_id": 41,
    "original_url": "https://finalvestige.com/wp-content/uploads/2026/08/a44f673d-a8a8-4c83-9f29-7e24dd55156b.png",
    "stored_original_bytes": 2498247,
    "native_px": [
      1672,
      941
    ],
    "conditional_960px": [
      960,
      540
    ],
    "inline_post_ids": [
      36
    ],
    "published_direct_srcs": [
      "https://finalvestige.com/wp-content/uploads/2026/08/a44f673d-a8a8-4c83-9f29-7e24dd55156b.png"
    ],
    "generated_subsizes": 0,
    "rights_observation": "HISTORICAL_RECONSTRUCTION_CREATOR_LICENSE_UNVERIFIED"
  },
  {
    "media_id": 42,
    "original_url": "https://finalvestige.com/wp-content/uploads/2026/08/c1237ffd-4a47-4988-8254-e3b021069e72.png",
    "stored_original_bytes": 2488823,
    "native_px": [
      1672,
      941
    ],
    "conditional_960px": [
      960,
      540
    ],
    "inline_post_ids": [
      37
    ],
    "published_direct_srcs": [
      "https://finalvestige.com/wp-content/uploads/2026/08/c1237ffd-4a47-4988-8254-e3b021069e72.png"
    ],
    "generated_subsizes": 0,
    "rights_observation": "HISTORICAL_RECONSTRUCTION_CREATOR_LICENSE_UNVERIFIED"
  },
  {
    "media_id": 382,
    "original_url": "https://finalvestige.com/wp-content/uploads/2026/08/vasa-med-gamla-och-nya-stottor_vasa-with-old-and-new-supports.jpg",
    "stored_original_bytes": 2318980,
    "native_px": [
      1800,
      1200
    ],
    "conditional_960px": [
      960,
      640
    ],
    "inline_post_ids": [
      299
    ],
    "published_direct_srcs": [
      "https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/vasa-med-gamla-och-nya-stottor_vasa-with-old-and-new-supports.jpg?fit=1024%2C683&ssl=1"
    ],
    "generated_subsizes": 6,
    "rights_observation": "ITEM_LEVEL_REVIEW_REQUIRED"
  },
  {
    "media_id": 482,
    "original_url": "https://finalvestige.com/wp-content/uploads/2026/08/050e21e0-7b54-4f9a-ba0b-7f594657af05.png",
    "stored_original_bytes": 2293016,
    "native_px": [
      1672,
      941
    ],
    "conditional_960px": [
      960,
      540
    ],
    "inline_post_ids": [],
    "published_direct_srcs": [],
    "generated_subsizes": 6,
    "rights_observation": "ITEM_LEVEL_REVIEW_REQUIRED"
  },
  {
    "media_id": 405,
    "original_url": "https://finalvestige.com/wp-content/uploads/2026/08/The20Water20Resilience20Field20Manual.png",
    "stored_original_bytes": 2201573,
    "native_px": [
      1122,
      1402
    ],
    "conditional_960px": [
      960,
      1200
    ],
    "inline_post_ids": [],
    "published_direct_srcs": [],
    "generated_subsizes": 5,
    "rights_observation": "ITEM_LEVEL_REVIEW_REQUIRED"
  },
  {
    "media_id": 293,
    "original_url": "https://finalvestige.com/wp-content/uploads/2026/08/ne.png",
    "stored_original_bytes": 2090327,
    "native_px": [
      1122,
      1402
    ],
    "conditional_960px": [
      960,
      1200
    ],
    "inline_post_ids": [],
    "published_direct_srcs": [],
    "generated_subsizes": 5,
    "rights_observation": "ITEM_LEVEL_REVIEW_REQUIRED"
  },
  {
    "media_id": 2148,
    "original_url": "https://finalvestige.com/wp-content/uploads/2026/11/1927-caernarvon-levee-explosion-noaa-archive.jpg",
    "stored_original_bytes": 2030948,
    "native_px": [
      1821,
      1190
    ],
    "conditional_960px": [
      960,
      627
    ],
    "inline_post_ids": [],
    "published_direct_srcs": [],
    "generated_subsizes": 6,
    "rights_observation": "COMMONS_NOAA_PD_ASSERTION_CROP_REVIEW_REQUIRED"
  },
  {
    "media_id": 1714,
    "original_url": "https://finalvestige.com/wp-content/uploads/2026/10/halifax-explosion-map.png",
    "stored_original_bytes": 1543002,
    "native_px": [
      1280,
      1280
    ],
    "conditional_960px": [
      960,
      960
    ],
    "inline_post_ids": [
      269
    ],
    "published_direct_srcs": [
      "https://finalvestige.com/wp-content/uploads/2026/10/halifax-explosion-map.png"
    ],
    "generated_subsizes": 5,
    "rights_observation": "ORIGINAL_MAP_AUTHOR_RIGHTS_UNVERIFIED"
  }
];

function assertFrozenBridge(bridge) {
  const mismatch = name => {throw new Error('FROZEN_BRIDGE_MISMATCH:'+name);};
  const same = (a,b) => JSON.stringify(a) === JSON.stringify(b);
  if (!bridge || !Array.isArray(bridge.p0_queue) || !Array.isArray(bridge.oversized_media))
    mismatch('SHAPE');
  if (!same(bridge.p0_queue.map(x=>pickFrozen(x,["slot","post_id","original_src","catalog_candidate_url","candidate_kind","rights_observation","conditional_960px","retriever_only"])),PINNED_P0_SOURCE_ROWS))
    mismatch('P0_ORIGINAL_URL_CATALOG_OR_METADATA');
  if (!same(bridge.oversized_media.map(x=>pickFrozen(x,["media_id","original_url","stored_original_bytes","native_px","conditional_960px","inline_post_ids","published_direct_srcs","generated_subsizes","rights_observation"])),PINNED_OVERSIZE_ROWS))
    mismatch('OVERSIZE_URL_BYTES_DIMENSIONS_OR_INLINE_REFERENCES');
  if (bridge.p0_queue.some(x=>x.actual_origin_http_status!==null ||
      x.guest_http_status!==null || x.guest_current_src!==null ||
      x.guest_natural_px!==null || x.cold_encoded_image_bytes!==null ||
      x.exact_visual_identity_proven!==false || x.reuse_rights_cleared!==false ||
      x.caching_approved!==false || x.wordpress_upload_approved!==false))
    mismatch('SOURCE_ONLY_P0_FABRICATED_OBSERVATION_OR_APPROVAL');
  if (bridge.oversized_media.some(x=>x.guest_current_src!==null ||
      x.guest_wire_bytes!==null || x.derivative_authorized!==false))
    mismatch('SOURCE_ONLY_OVERSIZE_FABRICATED_WIRE_OR_APPROVAL');
  const a=bridge.authority,c=bridge.cohorts,r=bridge.release,m=bridge.methodology;
  if (!a || !a.source_ledger || !a.full_provenance || !a.worklist ||
      a.site_qa_pr!==154 || a.media_recovery_pr!==1703 ||
      a.source_ledger.blob_sha!=='8526557c7a5138e1ca22a347e3f9839503d48b2c' ||
      a.full_provenance.blob_sha!=='4965a862f7de7de46c1f4a1e26f3ca70a8c38805' ||
      a.worklist.blob_sha!=='2acd06a4ca4317646006eb6591face3fe76fedec' ||
      a.worklist.pr!==183) mismatch('CROSS_DRAFT_SOURCE_PROVENANCE');
  if (!c || !c.historical || !c.expanded_live_nov_08 ||
      c.historical.posts!==61 || c.historical.inline_positions!==355 ||
      c.historical.external_positions!==288 || c.historical.research_completed!==288 ||
      c.expanded_live_nov_08.posts!==66 || c.expanded_live_nov_08.inline_positions!==361 ||
      c.expanded_live_nov_08.media_records!==122) mismatch('MIXED_COHORT_DENOMINATORS');
  if (!r || r.guest_verified_broken_count!==0 || r.claimed_historical_broken!==42 ||
      r.claim_42_verified!==false || r.claim_76_percent_measured!==false ||
      r.rights_preapproved!==false || r.production_repairs!==0 ||
      r.wordpress_writes!==0 || r.third_party_downloads!==0)
    mismatch('FABRICATED_SOURCE_ONLY_RELEASE_CLAIM');
  const sum=bridge.oversized_media.reduce((acc,x)=>acc+x.stored_original_bytes,0);
  const inlineSum=bridge.oversized_media.reduce((acc,x)=>acc+(x.inline_post_ids.length?x.stored_original_bytes:0),0);
  if (sum!==47096779 || inlineSum!==38480915 || !m ||
      m.original_storage_byte_total!==sum || m.inline_referenced_original_storage_bytes!==inlineSum ||
      m.decimal_threshold_bytes!==1500000 || m.stated_target_pct!==76 ||
      m.measured_cold_baseline_image_bytes!==null || m.measured_cold_candidate_image_bytes!==null ||
      m.measured_saving_pct!==null)
    mismatch('STORAGE_VERSUS_ACTUAL_COLD_TRANSFER_CUSTODY');
  return true;
}
function pickFrozen(row,keys){const out={}; for (const key of keys) out[key]=row?.[key]; return out;}

function compileRecovery(bridge, observations = {}, approvals = {}) {
  if (!bridge || bridge.schema !== 'fv-media-recovery-siteqa-bridge-v1' ||
      !Array.isArray(bridge.p0_queue) || !Array.isArray(bridge.oversized_media) ||
      bridge.p0_queue.length !== 6 || bridge.oversized_media.length !== 15 ||
      bridge.authority.site_qa_pr !== 154)
    throw new Error('unsupported or incomplete source-only bridge');
  assertFrozenBridge(bridge);
  const slots = bridge.p0_queue.map(x=>x.slot);
  if (P0_ORDER.some((slot,i)=>slot!==slots[i]) ||
      new Set(slots).size!==6 ||
      bridge.p0_queue.some(x=>!https(x.original_src) || !https(x.catalog_candidate_url)) ||
      new Set(bridge.oversized_media.map(x=>x.media_id)).size!==15)
    throw new Error('source inventory or priority order changed');
  const priority = bridge.p0_queue.map(item=>{
    const guest = guestFinding(item,observations[item.slot]);
    const candidate = candidateReview(item,approvals[item.slot],guest.verdict);
    return {slot:item.slot,post_id:item.post_id,original_src:item.original_src,
      candidate_catalog_url:item.catalog_candidate_url,
      rights_observation_not_clearance:item.rights_observation,
      guest_browser:guest,candidate_review:candidate};
  });
  const oversized = bridge.oversized_media.map(item=>({
    media_id:item.media_id,original_url:item.original_url,
    stored_original_bytes:item.stored_original_bytes,
    inline_post_ids:item.inline_post_ids,
    delivery_source:item.published_direct_srcs.some(x=>x.includes('i0.wp.com'))?'JETPACK_TRANSFORMED_IN_STORED_SRC':item.inline_post_ids.length?'DIRECT_INLINE_ORIGINAL':'NO_INLINE_MATCH',
    guest_wire_bytes:null,optimization_savings_bytes:null,
    rights_cleared_for_new_derivative:false
  }));
  const confirmed = priority.filter(x=>x.guest_browser.verdict==='CONFIRMED_GUEST_BROKEN');
  return {schema:'fv-media-evidence-gate-v1',source_bridge:'browser_handoff_6_p0_15_oversize_20261110.json',
    historical_reported_broken:42,
    verified_broken_in_supplied_guest_evidence:confirmed.length,
    historical_42_fully_adjudicated:false,
    priority,oversized,
    proposed_wire_saving_target_pct:76,actual_wire_saving_pct:null,
    actual_cold_baseline_image_bytes:null,actual_cold_candidate_image_bytes:null,
    restrictions:{browser_collector_owner_pr:154,homepage_design_changes:false,
      wordPress_production_writes_permitted:false,third_party_binary_copy_permitted:false,
      automatic_staging_upload_permitted:false,subscription_spend_permitted:false}};
}

module.exports={P0_ORDER,PINNED_POST_PERMALINKS,guestFinding,candidateReview,compileRecovery,assertFrozenBridge};
