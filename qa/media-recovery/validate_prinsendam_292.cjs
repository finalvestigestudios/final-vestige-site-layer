'use strict';
/** Fail-closed, OFFLINE Prinsendam provenance + WordPress no-write validation. */
const exact={
'292:0':'https://nationalcoastguardmuseum.org/wp-content/uploads/2023/08/DF-SN-86-12843-header-image-900x675.jpeg',
'292:1':'https://stadsarchief.rotterdam.nl/sites/default/files/styles/gallery_large/public/2025-04/hal-prinsendam-nl-rtsa_4121_24162-1-14.jpg?h=3e6ca723&itok=wjXwUo3w',
'292:2':'https://images.pubble.cloud/worker/jpg/quick/1920/3077598/96897487/content/2024/6/cf6d9b51-c16b-4938-800c-833b86ac5740',
'292:3':'https://cgaviationhistory.org/wp-content/uploads/MS_Prisendam_sinking_off_Alaska_with_USCG_HH-3F_1980.jpg',
'292:4':'https://www.travelserver.net/travelpage/aspgallery/pictures/Ad_1981_12.jpg',
'292:5':'https://static.thisdayinaviation.com/wp-content/uploads/tdia/2020/10/Screen-Shot-2020-10-03-at-14.51.27.png'};
const official=/^https:\/\/(?:commons\.wikimedia\.org\/wiki\/File:|www\.history\.uscg\.mil\/Our-Collections\/Photos\/igphoto\/|nationalcoastguardmuseum\.org\/articles\/prinsendam\/|stadsarchief\.rotterdam\.nl\/en\/archives-and-collections)/;
function validate(doc){
 const e=[];
 if(!doc||typeof doc!=='object'||Array.isArray(doc))return ['invalid_audit'];
 if(doc.schema_version!==1||doc.article_id!==292||doc.audit_date!=='2026-10-31')e.push('scope_mismatch');
 const s=doc.safety||{},q=doc.scope||{};
 if(s.site_writes!==false||s.downloaded_third_party_assets!==false||s.rights_cleared_count!==0||
 s.authorized_uploads!==0||s.master_hashes_known!==0||s.target_max_width_px!==960||
 s.no_upscale!==true||s.homepage_files_edited!==false||s.site_qa_draft_edited!==false||s.spend_usd!==0)e.push('safety_boundary_invalid');
 if(q.stored_image_slots!==6||q.stored_offsite_slots!==6||q.confirmed_browser_broken_count!==null||
 q.confirmed_weight_reduction_percent!==null)e.push('unsupported_sitewide_claim');
 if(!Array.isArray(doc.images)||doc.images.length!==6)return [...e,'must_have_six_slots'];
 const seen=new Set();
 for(const x of doc.images){
  if(!x||!Object.hasOwn(exact,x.image_key)||seen.has(x.image_key)||x.stored_url!==exact[x.image_key])e.push('image_identity_modified');
  seen.add(x?.image_key);
  if(x.article_url!==doc.article_url||x.actual_browser_http_status!==null||x.actual_browser_current_src!==null||
  x.actual_source_byte_size!==null||x.actual_source_pixel_dimensions!==null||x.master_sha256!==null)e.push('fabricated_observation:'+x.image_key);
  if(!official.test(x.candidate_record_url||'')||(x.secondary_evidence_url!==null&&!official.test(x.secondary_evidence_url||'')))e.push('untrusted_or_missing_reference:'+x.image_key);
  if(!['archive_id_subject','strong_photo_identifier','same_subject_alternative','no_exact_candidate'].includes(x.candidate_match_level))e.push('unknown_match_class:'+x.image_key);
  if(x.rights_status!=='HOLD_ITEM_REVIEW'||x.asset_downloaded!==false||x.wordpress_write_authorized!==false||x.wordpress_media_item_id!==null)e.push('rights_or_cms_override:'+x.image_key);
  if(x.candidate_master_dimensions===null){
   if(x.candidate_output_dimensions!==null)e.push('invented_dimensions:'+x.image_key);
  }else{
   const m=x.candidate_master_dimensions,d=x.candidate_output_dimensions||{};
   if(!Number.isSafeInteger(m.width)||m.width<1||!Number.isSafeInteger(m.height)||m.height<1||
    d.width!==Math.min(m.width,960)||d.height!==Math.round(m.height*Math.min(m.width,960)/m.width))e.push('upscale_or_wrong_dimensions:'+x.image_key);
  }
  if(x.image_key==='292:1'&&!String(x.editorial_caption_note||'').includes('Koningsbruggen'))e.push('missing_caption_integrity_warning');
  if(x.image_key==='292:5'&&(x.candidate_match_level!=='no_exact_candidate'||x.candidate_master_dimensions!==null))e.push('unlicensed_artwork_cannot_be_exact');
 }
 if(seen.size!==6)e.push('missing_key');
 return [...new Set(e)];
}
module.exports={validate,exact};
