'use strict';
/* Offline source-integrity and release gate; never fetches URLs or writes WordPress. */
const expected = [{"record_id":"WP media 171 / credited H. T. Stearns (USGS)","record_url":"https://commons.wikimedia.org/wiki/File:The_St._Francis_Dam.jpg","rights":"FIRST_PARTY_CURRENT_ASSET_USGS_CREDIT_REVIEW","width":1400,"height":738},{"record_id":"LOC HAER CA-298 sheet 2 of 18 (ca3095.sheet.00002a)","record_url":"https://www.loc.gov/pictures/item/ca3095.sheet.00002a","rights":"LOC_HAER_ITEM_REVIEW_GOVERNMENT_CREATION_CAVEAT","width":null,"height":null},{"record_id":"H. T. Stearns USGS photo 682 / 17 March 1928","record_url":"https://commons.wikimedia.org/wiki/File:St._Francis_abutment.jpg","rights":"USGS_PUBLIC_DOMAIN_MARK_CATALOG_ITEM_CHECK","width":1400,"height":806},{"record_id":"USGS Flickr image 11449413284 / 18 March 1928","record_url":"https://commons.wikimedia.org/wiki/File:Twisted_Tracks.jpg","rights":"CC_BY_2_0_ATTRIBUTION_REQUIRED","width":1400,"height":1017},{"record_id":"H. T. Stearns USGS photo 665 / 17 March 1928","record_url":"https://commons.wikimedia.org/wiki/File:St._Francis_Dam_after_the_1928_failure.jpg","rights":"USGS_PUBLIC_DOMAIN_MARK_CATALOG_ITEM_CHECK","width":1400,"height":1043},{"record_id":"Los Angeles Public Library TESSA / 00009829","record_url":"https://commons.wikimedia.org/wiki/File:Standing_section.jpg","rights":"COMMONS_PD_NONRENEWAL_CLAIM_ITEM_REVIEW","width":1250,"height":936},{"record_id":"UCLA Daily News collection ARK 21198/zz00253zg8","record_url":"https://commons.wikimedia.org/wiki/File:Man_pointing_at_crack_in_Saint_Francis_Dam_after_its_collapse.jpg","rights":"CC_BY_4_0_ATTRIBUTION_LICENSE_AND_EDIT_NOTICE_REQUIRED","width":4431,"height":5760}];
const fail = (arr, why)=>arr.push(why);
function validate(a, census) {
 const e=[];
 if(!a||a.schema_version!==1||a?.article?.id!==166||a.article.image_count!==7) fail(e,'audit header');
 if(!a?.sitewide_baseline||a.sitewide_baseline.published_posts!==61||a.sitewide_baseline.image_slots!==355||a.sitewide_baseline.offsite_slots!==288||a.sitewide_baseline.oversize_originals_above_1_5MiB!==13||a.sitewide_baseline.reported_broken_42_browser_confirmed!==false||a.sitewide_baseline.claimed_76pct_weight_reduction_measured!==false||a.sitewide_baseline.production_images_repaired!==0||a.sitewide_baseline.confirmed_broken_count!==null||a.sitewide_baseline.measured_transfer_reduction_percent!==null)fail(e,'unsupported sitewide claims');
 if(!a?.safety||Object.values(a.safety).some(x=>x!==true))fail(e,'safety gate');
 if(a?.article?.source_part_git_blob_sha!=='21095161e633aba093b74c0ead9936c9f6186d00'||a?.article?.wordpress_read_only_editor_rechecked!==true)fail(e,'census identity/readonly');
 const actual=(census&&Array.isArray(census.images)?census.images:[]).filter(x=>x.post_id===166).sort((x,y)=>x.slot-y.slot);
 if(actual.length!==7||!Array.isArray(a?.slots)||a.slots.length!==7)return [...e,'slot count'];
 a.slots.forEach((s,i)=>{
  const src=actual[i],m=expected[i]; if(!src)return fail(e,'missing frozen slot');
  if(s?.key!==src.key||s?.slot!==i||s?.post_id!==166||s?.published_source_url!==src.source_url||s?.published_alt!==src.alt||s?.post_url!==src.post_url||s?.source_kind!==src.source_kind||s?.current_wp_editor_source_and_alt_match_frozen!==true)fail(e,'source or ALT '+i);
  const o=s?.independent_retriever||{};if(o.method!=='web_open_exact_published_asset_URL_not_guest_Chrome'||o.result!=='ASSET_NOT_ACCESSIBLE_TO_TEXT_RETRIEVER'||o.http_status!==null||o.origin_http_status!==null||o.visitor_http_status!==null)fail(e,'fabricated retrieval '+i);
  const ar=s?.authority_candidate||{};if(ar.record_identifier!==m.record_id||ar.record_url!==m.record_url||ar.rights_basis!==m.rights||ar.pixel_identity_confirmed!==false||ar.original_master_sha256!==null||ar.rights_review!=='HOLD'||ar.credit_review!=='PENDING'||!ar.rights_note)fail(e,'archival/rights '+i);
  if(i>=2) {
   const old=decodeURIComponent(new URL(s.published_source_url).pathname.split('/file/')[1]||'').replace(/_/g,' ');
   const canonical=decodeURIComponent(new URL(ar.record_url).pathname.split('/File:')[1]||'').replace(/_/g,' ');
   if(old!==canonical)fail(e,'Commons filename identity '+i);
  }
  const g=s?.geometry||{},w=m.width,h=m.height,tw=w===null?null:Math.min(w,960),th=h===null?null:Math.round(h*tw/w);
  if(g.catalog_or_media_width_px!==w||g.catalog_or_media_height_px!==h||g.conditional_width_px!==tw||g.conditional_height_px!==th||g.no_upscaling!==true||g.actual_visitor_transfer_bytes!==null||g.decoded_visitor_dimensions!==null)fail(e,'geometry or invented byte saving '+i);
  if(i===0&&g.observed_first_party_original_storage_bytes!==704922)fail(e,'WP media size '+i);
  if(i!==0&&g.observed_first_party_original_storage_bytes!==null)fail(e,'offsite bytes forged '+i);
  const vb=s?.guest_browser||{};if(vb.current_src!==null||vb.actual_image_get_status!==null||vb.final_url!==null||vb.content_type!==null||vb.natural_width_px!==null||vb.encoded_transfer_bytes!==null||vb.visibly_broken!==null)fail(e,'fake visitor evidence '+i);
  const r=s?.release||{};if(r.asset_downloaded!==false||r.cache_authorized!==false||r.wordpress_media_upload_authorized!==false||r.wordpress_post_edit_authorized!==false||r.homepage_design_changed!==false)fail(e,'unauthorized release '+i);
 });
 return e;
}
module.exports={validate};
