/** Strict offline/source-only Texas City 216 media provenance gate. No networking or CMS writes. */
export function validateTexasCity216(data){
 const errors=[],err=(x)=>errors.push(x);
 const fixed=[
 ["216:0","https://commons.wikimedia.org/wiki/Special:Redirect/file/Txcitydisasterparkinglot.jpg?width=1280",3111,2421,"uh_rights_conflict_review","none"],
 ["216:1","https://commons.wikimedia.org/wiki/Special:Redirect/file/Texas_City_Disaster_Firemen_Memorial.jpg?width=960",1917,1544,"cc_by_sa_4","none"],
 ["216:2","https://commons.wikimedia.org/wiki/Special:Redirect/file/Txcitydisaster5storybuilding.jpg",2765,2112,"uh_rights_conflict_review","none"],
 ["216:3","https://commons.wikimedia.org/wiki/Special:Redirect/file/Texas_-_Texas_City_-_NARA_-_68149862.jpg?width=1280",6923,5485,"us_federal_pd_claim_review","dating_unsubstantiated"],
 ["216:4","https://commons.wikimedia.org/wiki/Special:Redirect/file/Txcitydisasterboat.jpg",2768,2120,"uh_rights_conflict_review","vessel_identity_conflict"],
 ["216:5","https://commons.wikimedia.org/wiki/Special:Redirect/file/Grandcampanchor.jpg",480,320,"uploader_public_domain_claim_review","no_upscale"]
 ];
 if(!data||typeof data!=="object")return ["missing audit"];
 if(data.schema!=="fv.media-recovery.texas-city-216.v1"||data.post_id!==216||data.image_count!==6||data.post_status!=="publish")err("cohort/schema");
 if(data.source_cohort!=="frozen-2026-10-30-61posts-355images"||data.post_modified!=="2026-11-02T21:39:36")err("source binding");
 if(data.guest_browser_verified!==false||data.claimed_42_broken_images_verified!==false||data.claimed_76pct_wire_reduction_measured!==false)err("unverified claims");
 for(const key of ["observed_broken_guest_images","measured_transfer_delta_bytes"])if(data[key]!==null)err("fabricated runtime metric "+key);
 for(const key of ["wp_production_writes","downloaded_media","cached_media","spend_usd"])if(data[key]!==0)err("unapproved operation "+key);
 if(JSON.stringify(data.priority_order_not_replaced)!==JSON.stringify(["285:5","285:2","287:5","418:1","418:2","407:1"]))err("P0 order changed");
 if(!Array.isArray(data.images)||data.images.length!==6)return errors.concat("six entries required");
 const seen=new Set();
 for(let i=0;i<6;i++){
  const x=data.images[i],f=fixed[i];if(!x||typeof x!=="object"){err("missing slot "+i);continue;}
  if(seen.has(x.key))err("duplicate key "+x.key);seen.add(x.key);
  if(x.key!==f[0]||x.slot!==i||x.published_src!==f[1]||x.published_src_host!=="commons.wikimedia.org")err("source identity "+i);
  if(x.frozen_src_match!==true||x.wp_source_readback_match!==true||typeof x.stored_alt!=="string"||x.stored_alt.length<18)err("source text "+i);
  if(x.declared_html_width!==null||x.declared_html_height!==null)err("invented HTML geometry "+i);
  const dim=x.catalog_master_px||{},p=x.conditional_preview_px||{},width=Math.min(960,f[2]);
  if(dim.width!==f[2]||dim.height!==f[3]||p.width!==width||p.height!==Math.round(f[3]*width/f[2])||p.width>dim.width||p.height>dim.height)err("catalog no-upscale geometry "+i);
  if(x.rights_review!==f[4]||x.editorial_hold!==f[5]||!x.catalog_file_url?.startsWith("https://")||!x.institutional_collection_or_record_url?.startsWith("https://")||!x.source_credit||!x.identity_note||!x.rights_and_staging_note)err("archive/rights "+i);
  if(x.rights_for_local_cache_approved!==false||x.wp_upload_authorized!==false||x.exact_photo_replacement_approved!==false)err("unauthorized use "+i);
  for(const k of ["actual_http_status","guest_current_src","guest_natural_width","guest_network_transfer_bytes","guest_broken","local_master_sha256","wp_attachment_id"])if(x[k]!==null)err("fabricated observation "+k+" "+i);
  if(x.web_retriever_result!=="url_inaccessible_not_origin_http"||x.asset_downloaded!==false||x.derivative_generated!==false)err("unsupported tool/result "+i);
  if(!x.candidate_relation.startsWith("documented archival catalog lineage"))err("false equivalence "+i);
 }
 return errors;
}
