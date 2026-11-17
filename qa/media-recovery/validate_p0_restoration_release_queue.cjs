'use strict';
/**
 * Fail-closed, read-only P0 external-media restoration readiness validator.
 * All browser HTTP/status and transferred-byte fields are UNKNOWN until
 * independent logged-out Chrome verifies them. No filesystem or network calls.
 */
const expectedKeys=['285:5','407:1','418:1','418:2','285:0','407:3','268:8','268:4','285:2','418:0'];
const pinnedEvidence=Object.freeze({
  "285:5": {
    "frozen_blob": "49183f66f880f7c4dfd363acca906876877f2e5e",
    "viewer_result": "RETRIEVER_FETCH_404",
    "viewer_code": 404,
    "record": "https://commons.wikimedia.org/wiki/File:Three_mile_island_062010.jpg",
    "identifier": "Three mile island 062010.jpg",
    "relationship": "publisher_credit_exact_scene_candidate_unconfirmed_pixel_match",
    "candidate_asset": "https://commons.wikimedia.org/wiki/File:Three_mile_island_062010.jpg"
  },
  "407:1": {
    "frozen_blob": "48e1ebf07207e948ba5802e714eb39659d2e1c1d",
    "viewer_result": "RETRIEVER_UNSUPPORTED_OCTET_STREAM",
    "viewer_code": 400,
    "record": "https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959",
    "identifier": "J. R. Stacy 1959 Hebgen fault-scarp USGS record",
    "relationship": "same_record_alternative_original_path_binary_unverified",
    "candidate_asset": "https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/thumbnails/image/img7535.jpg"
  },
  "418:1": {
    "frozen_blob": "948bc1b65b42799aa40cfdb810ddf6ffd80886b6",
    "viewer_result": "RETRIEVER_FETCH_403",
    "viewer_code": 403,
    "record": "https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/",
    "identifier": "210330-G-DE713-0002.JPG",
    "relationship": "official_virin_filename_match_no_master_hash",
    "candidate_asset": "https://media.defense.gov/2021/Mar/30/2002610812/1920/1080/0/210330-G-DE713-0002.JPG"
  },
  "418:2": {
    "frozen_blob": "948bc1b65b42799aa40cfdb810ddf6ffd80886b6",
    "viewer_result": "RETRIEVER_FETCH_403",
    "viewer_code": 403,
    "record": "https://www.history.uscg.mil/Research/THE-LONG-BLUE-LINE/Article/2866442/the-long-blue-line-standing-a-deadly-watch-75-years-agofinal-hours-of-scotch-ca/",
    "identifier": "5_ Scotch_Cap_debris2_1946.jpg (individual accession unknown)",
    "relationship": "publisher_article_original_filename_catalog_unmatched",
    "candidate_asset": null
  },
  "285:0": {
    "frozen_blob": "49183f66f880f7c4dfd363acca906876877f2e5e",
    "viewer_result": "RETRIEVER_FETCH_403",
    "viewer_code": 403,
    "record": "https://www.flickr.com/photos/nrcgov/7447166686",
    "identifier": "Flickr 7447166686",
    "relationship": "same_photo_id_external_rendition_binary_unverified",
    "candidate_asset": "https://www.flickr.com/photos/nrcgov/7447166686"
  },
  "407:3": {
    "frozen_blob": "48e1ebf07207e948ba5802e714eb39659d2e1c1d",
    "viewer_result": "RETRIEVER_INACCESSIBLE_NO_HTTP",
    "viewer_code": null,
    "record": "https://www.usgs.gov/media/images/dragline-working-lower-outlet-channel-earthquake-lake-october-18-1959",
    "identifier": "EarthquakeLake3.jpg / Mrs. Steven W. Nile",
    "relationship": "official_subject_filename_match_item_rights_unknown",
    "candidate_asset": null
  },
  "268:8": {
    "frozen_blob": "6df3251e5a67a971d87a516a1ba4a0cc32f51f96",
    "viewer_result": "RETRIEVER_INACCESSIBLE_NO_HTTP",
    "viewer_code": null,
    "record": "https://archimedespalimpsest.org/0_ReadMe.html",
    "identifier": "imaging_x9.jpg publisher asset",
    "relationship": "publisher_asset_no_individual_catalog",
    "candidate_asset": null
  },
  "268:4": {
    "frozen_blob": "6df3251e5a67a971d87a516a1ba4a0cc32f51f96",
    "viewer_result": "RETRIEVER_REDIRECT_DESTINATION_UNAVAILABLE",
    "viewer_code": null,
    "record": "https://archimedespalimpsest.org/0_ReadMe.html",
    "identifier": "imagecapture-capture2b.jpg publisher asset",
    "relationship": "publisher_asset_no_individual_catalog",
    "candidate_asset": null
  },
  "285:2": {
    "frozen_blob": "49183f66f880f7c4dfd363acca906876877f2e5e",
    "viewer_result": "RETRIEVER_REDIRECT_DESTINATION_UNAVAILABLE",
    "viewer_code": 500,
    "record": "https://commons.wikimedia.org/wiki/File:Control_room_Number_2._Nuclear_Regulatory_Commission_inspector_looking_at_meters._-_NARA_-_540034.tif",
    "identifier": "NARA 540034",
    "relationship": "different_photo_same_topic_not_a_drop_in_replacement",
    "candidate_asset": null
  },
  "418:0": {
    "frozen_blob": "948bc1b65b42799aa40cfdb810ddf6ffd80886b6",
    "viewer_result": "RETRIEVER_INACCESSIBLE_NO_HTTP",
    "viewer_code": null,
    "record": "https://www.history.uscg.mil/Research/THE-LONG-BLUE-LINE/Article/2866442/the-long-blue-line-standing-a-deadly-watch-75-years-agofinal-hours-of-scotch-ca/",
    "identifier": "2_ new and old lighthouses 19849609_web1_1_ (individual accession unknown)",
    "relationship": "publisher_article_original_filename_catalog_unmatched",
    "candidate_asset": null
  }
});
const isHttps=u=>typeof u==='string'&&/^https:\/\/[a-z0-9.-]+\//i.test(u);
const int=n=>Number.isSafeInteger(n)&&n>0;
function validateP0(board,parts){
 const e=[];
 const fail=(x)=>e.push(x);
 if(!board||typeof board!=='object'||Array.isArray(board))
  return{ok:false,errors:['invalid_board']};
 if(board.schema_version!==1||board.generated_on!=='2026-11-01')
  fail('schema_or_date_changed');
 const census=board.frozen_census||{};
 if(census.published_posts!==61||census.stored_img_src_references!==355||
    census.offsite_source_references!==288||census.external_distinct_urls!==286||
    !Array.isArray(census.source_parts_blob_shas)||census.source_parts_blob_shas.length!==8||
    census.source_parts_blob_shas.some(s=>!/^[0-9a-f]{40}$/.test(s)))
  fail('source_census_not_frozen');
 const oversize=board.oversized_media||{};
 if(oversize.originals_exceeding_1_5_mib!==13||
    oversize.original_storage_bytes_of_13!==43522829||
    oversize.real_visitor_transfer_bytes!==null)fail('original_storage_is_not_wire_bytes');
 const claims=board.claims||{};
 if(claims.reported_broken_42_browser_verified!==false||
    claims.confirmed_site_wide_broken_count!==null||
    claims.claimed_76pct_transfer_reduction_measured!==false||
    claims.measured_transfer_reduction_percent!==null||
    claims.production_images_repaired!==0)fail('unsupported_site_wide_claim');
 if(!Array.isArray(parts)||parts.length!==8)fail('missing_frozen_census_parts');
 const all=(Array.isArray(parts)?parts:[]).flatMap(p=>Array.isArray(p?.images)?p.images:[]);
 if(all.length!==355||new Set(all.map(x=>x.key)).size!==355||
    new Set(all.map(x=>x.post_id)).size!==61)fail('frozen_inventory_corrupt');
 const inventory=new Map(all.map(x=>[x.key,x]));
 const report=board.wordpress_live_readback||{},posts=report.posts;
 if(report.selected_posts!==4||report.all_image_slots_checked!==30||
    report.selected_high_risk_slots!==10||!Array.isArray(posts)||
    posts.length!==4||new Set(posts.map(x=>x.id)).size!==4)
  fail('cms_readback_scope_missing');
 const expectedPostCounts=new Map([[268,10],[285,6],[407,8],[418,6]]);
 const checked=new Map();
 for(const p of (Array.isArray(posts)?posts:[])){
  const sourcePosts=all.filter(x=>x.post_id===p.id);
  if(!expectedPostCounts.has(p.id)||p.image_count!==expectedPostCounts.get(p.id)||
     sourcePosts.length!==p.image_count||p.matched_frozen_exact_source_and_alt!==true||
     !isHttps(p.link)||sourcePosts.some(s=>s.post_url!==p.link)||
     !Number.isFinite(Date.parse(p.modified||'')))
   fail('cms_source_attestation_invalid:'+p.id);
  checked.set(p.id,p);
 }
 for(const id of expectedPostCounts.keys())if(!checked.has(id))fail('cms_post_missing:'+id);
 const rows=board.rows;
 if(!Array.isArray(rows)||rows.length!==10)
  return{ok:false,errors:[...e,'priority_queue_not_ten']};
 if(new Set(rows.map(x=>x.image_key)).size!==10)fail('duplicate_priority_image_key');
 rows.forEach((r,i)=>{
  const key=expectedKeys[i];
  if(r.image_key!==key||r.priority_rank!==i+1)fail('priority_or_key_changed:'+i);
  const stored=inventory.get(r.image_key);
  if(!stored||!isHttps(r.current_published_source_url)||
     r.current_published_source_url!==stored.source_url||
     r.current_published_alt!==stored.alt||
     r.post_url!==stored.post_url||r.post_id!==stored.post_id||
     r.post_slot!==stored.slot||r.source_kind!==stored.source_kind||
     r.current_cms_source_and_alt_verified!==true||
     r.wp_last_modified!==checked.get(r.post_id)?.modified)
   fail('source_identity_mismatch:'+key);
  if(typeof r.source_census_blob_sha!=='string'||
     !census.source_parts_blob_shas.includes(r.source_census_blob_sha))
   fail('unrecognized_frozen_blob:'+key);
  const pinned=pinnedEvidence[r.image_key];
  if(!pinned||r.source_census_blob_sha!==pinned.frozen_blob)
    fail('unpinned_frozen_source_record:'+key);
  const v=r.source_viewer||{};
  const methods=['RETRIEVER_FETCH_404','RETRIEVER_FETCH_403',
   'RETRIEVER_UNSUPPORTED_OCTET_STREAM','RETRIEVER_INACCESSIBLE_NO_HTTP',
   'RETRIEVER_REDIRECT_DESTINATION_UNAVAILABLE'];
  const validCodes={
   RETRIEVER_FETCH_404:[404],RETRIEVER_FETCH_403:[403],
   RETRIEVER_UNSUPPORTED_OCTET_STREAM:[400],
   RETRIEVER_INACCESSIBLE_NO_HTTP:[null],
   RETRIEVER_REDIRECT_DESTINATION_UNAVAILABLE:[null,500]
  };
  if(!pinned||v.result!==pinned.viewer_result||
     v.retriever_wrapper_error_code!==pinned.viewer_code)
    fail('viewer_evidence_changed_from_observation:'+key);
  if(v.method!=='independent_web_retriever_NOT_logged_out_visitor_browser'||
     v.observed_on!=='2026-11-01'||!methods.includes(v.result)||
     !(validCodes[v.result]||[]).includes(v.retriever_wrapper_error_code)||
     v.origin_http_status!==null||v.visitor_http_status!==null||
     v.actual_transferred_bytes!==null||
     v.rechecked_this_sprint!==[0,1,2].includes(i))
   fail('retriever_mistaken_for_browser:'+key);
  const b=r.guest_browser||{};
  for(const field of ['current_src','final_image_url','http_status','content_type',
   'natural_width_px','natural_height_px','encoded_transfer_bytes','visibly_broken'])
   if(b[field]!==null)fail('invented_visitor_measurement:'+key+':'+field);
  const c=r.candidate||{};
  if(!pinned||c.archive_record_url!==pinned.record||
     c.identifier!==pinned.identifier||c.source_relationship!==pinned.relationship||
     c.candidate_asset_url!==pinned.candidate_asset)
    fail('archival_record_substituted:'+key);
  if(!isHttps(c.archive_record_url)||!c.identifier||!c.authority||
    typeof c.source_relationship!=='string'||!c.source_relationship||
    (c.candidate_asset_url!==null&&!isHttps(c.candidate_asset_url))||
    c.binary_identity_verified!==false||c.original_master_sha256!==null||
    c.reproduction_rights_review!=='HOLD'||!c.rights_basis_note||
    c.credit_and_caption_review_required!==true)
   fail('archival_source_or_rights_unverified:'+key);
  const g=r.geometry||{};
  if(g.no_upscale!==true||g.aspect_ratio_preserved!==true||
    g.master_binary_dimensions_verified!==false)fail('geometry_custody_invalid:'+key);
  const w=g.conditional_960px_width,h=g.conditional_960px_height,
   sw=g.catalog_original_width_px,sh=g.catalog_original_height_px;
  if((w===null)!==(h===null)||(sw===null)!==(sh===null))fail('incomplete_geometry:'+key);
  if(w!==null&&(!int(w)||!int(h)||w>960))fail('invalid_960_derivative:'+key);
  if(sw!==null){
   const expectedW=Math.min(960,sw);
   const expectedH=Math.round(expectedW*sh/sw);
   if(!int(sw)||!int(sh)||w!==expectedW||h!==expectedH)
    fail('catalog_geometry_mismatch:'+key);
  }else if(w!==null&&!(key==='407:3'&&g.basis==='stored_html_1024x730_unverified_binary'&&w===960&&h===684))
   fail('hypothetical_geometry_unjustified:'+key);
  const a=r.approval||{};
  if(a.replacement_ready!==false||a.media_cache_authorized!==false||
    a.wordpress_upload_authorized!==false||
    a.wordpress_post_edit_authorized!==false||
    a.homepage_design_changed!==false||!r.next_verified_action)
   fail('unapproved_production_action:'+key);
 });
 return{ok:e.length===0,errors:e,checked_slots:rows.length,checked_census_images:all.length,
  independent_guest_browser_failures_verified:0,rights_approved_assets:0};
}
module.exports={validateP0,expectedKeys};
