'use strict';
/** Offline P0 source/rights guard. No network, WordPress, or image downloads. */
function check(a,base){
 const ok=(v,m)=>{if(!v)throw Error(m)};
 const safeUrl=s=>typeof s==='string'&&/^https:\/\/[^\s/@]+(?:\/|$)/.test(s);
 ok(a?.schema==='fv-uscg-418-item-lineage-20261111-v1','schema');
 ok(base?.schema==='fv-media-coverage-288-exact-v1'&&base.rows?.length===288,'frozen ledger');
 ok(a.pinned_source?.blob_sha==='4965a862f7de7de46c1f4a1e26f3ca70a8c38805','pinned blob');
 const s=a.site_status;
 ok(s?.historical_posts===61&&s.historical_inline_images===355&&s.external_slots===288&&s.research_completed===288,'site denominator');
 ok(s.reported_broken_guest_unverified===42&&s.guest_failures_confirmed===0&&s.proposed_transfer_reduction_pct===76&&s.measured_transfer_reduction_pct===null,'guest failure/76 unmeasured');
 ok(s.oversized_wp_originals_gt_1500000===15&&s.stored_original_bytes===47096779,'storage only');
 ok(a.items?.length===2&&a.items[0].slot==='418:1'&&a.items[1].slot==='418:2','slots');
 for(const it of a.items){
  const src=base.rows.find(r=>r.slot===it.slot);
  ok(src&&it.exact_published_url===src.stored_url&&it.post_url===src.post_url,'exact original source '+it.slot);
  ok(safeUrl(it.official_catalog)&&safeUrl(it.asset_url)&&safeUrl(it.exact_published_url),'urls');
  ok(it.guest_http_status===null&&it.origin_http_status===null&&it.guest_current_src===null&&it.guest_natural_px===null&&it.guest_transfer_bytes===null,'no fabricated HTTP '+it.slot);
  ok(it.web_retriever_only?.method==='WEB_RETRIEVER_NOT_GUEST_OR_ORIGIN'&&it.web_retriever_only.wrapper_code===403,'retriever status distinct');
  ok(it.master_native_px===null&&it.conditional_960px===null&&it.maximum_derivative_width_px===960&&it.do_not_upscale===true&&it.do_not_crop===true,'conditional geometry');
  ok(it.rights_cleared_to_rehost===false&&it.pixel_match_verified===false&&it.download_allowed===false&&it.cache_allowed===false&&it.wordpress_write_allowed===false,'rights/image hold');
  ok(it.catalog_size_is_network_bytes===false,'catalog bytes not transfer');
 }
 const [p,d]=a.items;
 ok(p.exact_published_url===p.asset_url&&p.official_virin==='210330-G-DE713-0002.JPG'&&p.asset_url.endsWith('/'+p.official_virin),'USCG same URL and VIRIN');
 ok(p.official_catalog==='https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/'&&p.subject.includes('Anthony Pettit')&&p.subject.includes('PORTRAIT'),'Pettit identity');
 ok(p.catalog_rights==='COAST_GUARD_ITEM_SAYS_PUBLIC_DOMAIN_CLEARED_FOR_RELEASE_CREDIT_REQUESTED'&&p.catalog_advertised_download_mb===0.04&&safeUrl(p.rights_limitations_url),'USCG item rights/size');
 ok(p.decision==='OFFICIAL_CATALOG_ID_AND_RIGHTS_DOCUMENTED_GUEST_EDITOR_STAGE_HOLD','no premature portrait repair');
 ok(d.source_correspondence==='SAME_BASENAME_SIMILAR_SCENE_NOT_PROVEN_BINARY_IDENTITY'&&d.catalog_rights==='THIRD_PARTY_COPY_RIGHTS_AND_IDENTICAL_PHOTO_UNVERIFIED'&&d.official_virin===null,'debris copy not same pixels/license');
 ok(d.alternate_retriever_only?.method==='WEB_RETRIEVER_NOT_GUEST_OR_ORIGIN'&&d.alternate_retriever_only.origin_status===null,'secondary retriever not guest');
 ok(d.decision==='SCENE_RELATED_ALT_IDENTITY_RIGHTS_GUEST_HOLD','debris hold');
 ok(JSON.stringify(a.siteqa_existing_browser_order)===JSON.stringify(['285:5','285:2','287:5','418:1','418:2','407:1']),'Site QA queue');
 const r=a.release;
 ok(r?.guest_cdp_required&&r.source_identity_required&&r.rights_review_required&&r.editor_staging_review_required,'QA gating');
 ok(r.third_party_image_binary_download===false&&r.rehost_or_cache===false&&r.wordpress_production_write===false&&r.homepage_changes===false&&r.merge_or_deploy===false&&r.subscription_spend_usd===0,'no production or spending');
 return {ok:true,official_identified:1,third_party_uncleared:1,guest_confirmed:0};
}
module.exports={check};
