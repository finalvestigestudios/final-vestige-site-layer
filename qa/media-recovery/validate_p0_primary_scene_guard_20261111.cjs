'use strict';
// Offline, strict provenance safeguard. No HTTP, WordPress, browser collector or asset writing.
const EXPECTED=[
  {
    "slot": "418:1",
    "url": "https://media.defense.gov/2021/Mar/30/2002610812/1920/1080/0/210330-G-DE713-0002.JPG",
    "primary": "https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/",
    "kind": "USCG_ITEM_CATALOG",
    "identifier": "210330-G-DE713-0002.JPG",
    "subject": "SERVICE_PORTRAIT_ANTHONY_PETTIT",
    "year": 1946,
    "rights": "CATALOG_ITEM_PD_RELEASE_WITH_COMMERCIAL_USE_LIMITATIONS",
    "date": "2021-04-01",
    "size": 0.04,
    "source_urls": [
      "https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/",
      "https://www.history.uscg.mil/Research/THE-LONG-BLUE-LINE/Article/2866442/the-long-blue-line-standing-a-deadly-watch-75-years-agofinal-hours-of-scotch-ca/"
    ],
    "note": "This is a portrait of chief petty officer Anthony Pettit, NOT wreckage or a lighthouse; the exact filename is present on the official catalog page. Byte equality with original media.defense.gov derivative is untested.",
    "retriever": {
      "method": "EXTERNAL_WEB_RETRIEVER_NOT_GUEST",
      "result": "FORBIDDEN",
      "wrapper_code": 403
    }
  },
  {
    "slot": "418:2",
    "url": "https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg",
    "primary": "https://www.history.uscg.mil/Research/THE-LONG-BLUE-LINE/Article/2866442/the-long-blue-line-standing-a-deadly-watch-75-years-agofinal-hours-of-scotch-ca/",
    "kind": "USCG_OFFICIAL_HISTORICAL_ARTICLE",
    "identifier": null,
    "subject": "SCOTCH_CAP_1946_DEBRIS_VIEWS",
    "year": 1946,
    "rights": "OFFICIAL_ARTICLE_NO_ITEM_SPECIFIC_REHOST_CLEARANCE",
    "date": "2021-04-01",
    "size": null,
    "source_urls": [
      "https://www.history.uscg.mil/Research/THE-LONG-BLUE-LINE/Article/2866442/the-long-blue-line-standing-a-deadly-watch-75-years-agofinal-hours-of-scotch-ca/",
      "https://www.history.uscg.mil/Browse-by-Topic/Assets/Land/All/Article/1988680/scotch-cap-light/"
    ],
    "note": "Official 2021 USCG history contains two *different* 1946 aftermath photos (view from bluff, aerial remains). Neither was proven identical to published debris2_1946.jpg; do not substitute a NOAA page labelled 1964 without resolving chronology.",
    "retriever": {
      "method": "EXTERNAL_WEB_RETRIEVER_NOT_GUEST",
      "result": "FORBIDDEN",
      "wrapper_code": 403
    }
  },
  {
    "slot": "407:1",
    "url": "https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg",
    "primary": "https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959-0",
    "kind": "USGS_ITEM_CATALOG_EDITORIAL_ALTERNATIVE",
    "identifier": null,
    "subject": "HEBGEN_LAKE_1959_FAULT_SCARP_J_R_STACY",
    "year": 1959,
    "rights": "USGS_ALTERNATIVE_ITEM_MARKED_PUBLIC_DOMAIN",
    "date": "2019-04-19",
    "size": null,
    "source_urls": [
      "https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959-0",
      "https://www.usgs.gov/observatories/yvo/news/1959-madison-slide-part-1-a-deadly-consequence-hebgen-lake-earthquake"
    ],
    "note": "USGS identifies a 1959 fault-scarp photograph by J. R. Stacy as public domain. The original img7535.jpg S3 object has NOT been matched to this photo or its exact crop; catalog is a scene-level alternative only.",
    "retriever": {
      "method": "EXTERNAL_WEB_RETRIEVER_NOT_GUEST",
      "result": "UNSUPPORTED_OCTET_STREAM",
      "wrapper_code": 400
    }
  }
];
const BRIDGE_SHA="d1a9c7a499510ec37bcdba5858d45165752587e0";
function validate(d) {
  const errors=[];const bad=x=>errors.push(x);
  if(!d||d.schema!=='fv-p0-three-primary-scene-guard-v1') return {pass:false,errors:['schema']};
  if(d.authority?.source_bridge_blob_sha!==BRIDGE_SHA||d.authority?.site_qa_pr!==154||d.authority?.recovery_pr!==1703||d.authority?.worklist_pr!==183)bad('authority');
  const s=d.sitewide||{};
  if(s.historical_posts!==61||s.historical_external_images_researched!==288||s.historical_external_images_total!==288||s.historical_claim_broken!==42||s.confirmed_guest_broken!==0||s.claimed_savings_pct!==76||s.actual_savings_pct!==null||s.oversized_wordpress_originals!==15||s.oversized_stored_bytes!==47096779)bad('scope');
  if(d.production_changes!==0||d.external_binary_downloads!==0||d.subscription_spend_usd!==0)bad('production');
  if(!Array.isArray(d.items)||d.items.length!==3)return {pass:false,errors:[...errors,'item_count']};
  d.items.forEach((x,i)=>{
    const e=EXPECTED[i],p=x.primary_evidence||{};
    if(x.slot!==e.slot||x.post_id!==Number(e.slot.split(':')[0])||x.exact_published_original_url!==e.url)bad('original_identity_'+i);
    if(p.catalog_url!==e.primary||p.catalog_kind!==e.kind||p.item_identifier!==e.identifier||p.primary_description_subject!==e.subject||p.depicted_historical_year!==e.year||p.rights_notice!==e.rights||p.catalog_publication_date!==e.date||p.advertised_download_size_mb_not_transfer!==e.size||p.notes!==e.note||JSON.stringify(p.source_urls)!==JSON.stringify(e.source_urls))bad('catalog_identity_'+i);
    if(JSON.stringify(x.independent_retriever_only)!==JSON.stringify(e.retriever)||x.independent_retriever_only?.method!=='EXTERNAL_WEB_RETRIEVER_NOT_GUEST')bad('retriever_'+i);
    for(const k of ['guest_http_status','actual_origin_http_status','guest_current_src','guest_natural_px','cold_encoded_image_bytes','native_dimensions_verified','conditional_candidate_output_dimensions'])if(x[k]!==null)bad('invented_observation_'+i+'_'+k);
    for(const k of ['exact_binary_or_crop_identity_proven','guest_failure_confirmed','commercial_reuse_approval','item_level_attribution_review_done','editor_scene_signoff','wordpress_cache_approval','wordpress_upload_approval','production_write_permitted'])if(x[k]!==false)bad('unsupported_release_'+i+'_'+k);
    if(x.max_width_px_without_upscale!==960||x.decision!=='HOLD_PRIMARY_SOURCE_LEAD_ONLY')bad('geometry_or_disposition_'+i);
    if(!Array.isArray(p.source_urls)||p.source_urls.some(u=>typeof u!=='string'||!u.startsWith('https://')))bad('source_links_'+i);
  });
  return {pass:errors.length===0,errors};
}
module.exports={validate};
