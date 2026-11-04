'use strict';
/**
 * Apollo 12 post 257 image-custody manifest validator. Offline; never calls the web
 * or WordPress. User-facing availability requires independent logged-out Chrome.
 */
function validate(a,snapshot){
 const errors=[],bad=(flag,msg)=>{if(flag)errors.push(msg)};
 if(!a||typeof a!=='object')return ['audit missing'];
 bad(a.schema_version!==1||a.article_id!==257,'wrong audit schema/article');
 bad(a.snapshot_date!=='2026-10-30'||a.source_snapshot_blob_sha!=='6df3251e5a67a971d87a516a1ba4a0cc32f51f96','wrong frozen source');
 bad(a.fresh_wordpress_read!==false,'unsupported fresh WordPress read');
 const s=a.summary||{};
 bad(s.image_count!==7||s.offsite_reference_count!==7||s.commons_redirect_count!==7||s.html_images_without_declared_dimensions!==7,'census mismatch');
 bad(s.origin_http_statuses_verified!==0||s.guest_browser_images_verified!==0||s.visitor_broken_images_confirmed!==0||s.wordPress_production_images_repaired!==0,'fabricated verified result');
 bad(s.alleged_42_broken_visitor_verified!==false||s.claimed_76_percent_wire_reduction_measured!==false,'unverified sitewide claim');
 bad(!Array.isArray(a.rows)||a.rows.length!==7,'seven exact slots required');
 bad(!snapshot||!Array.isArray(snapshot.images),'frozen source missing');
 if(!Array.isArray(a.rows)||!snapshot||!Array.isArray(snapshot.images))return errors;
 const original=snapshot.images.filter(v=>v.post_id===257);
 bad(original.length!==7,'frozen inventory mismatch');
 if(original.length!==7)return errors;
 const names=['Apollo_12_Blitzeinschlag.jpg','Apollo_12_crew_walk_to_transfer_van_(KSC-69PC-646).jpg',
 'Apollo_12_Saturn_V_launch.jpg','KSC-69P-0856.jpg','Apollo_Command_Module_Main_Control_Panel.gif',
 'Lunar_module_AS12-51-7507.jpg','Apollo_12_LRO.jpg'];
 for(let i=0;i<7;i++){
  const r=a.rows[i],src=original[i];
  if(!r||typeof r!=='object'){errors.push('missing row '+i);continue}
  bad(r.image_key!==src.key||r.image_key!=='257:'+i,'slot identity '+i);
  bad(r.published_source_url!==src.source_url||r.published_alt!==src.alt,'exact source/ALT mismatch '+i);
  bad(r.source_snapshot_blob_sha!==a.source_snapshot_blob_sha||r.post_id!==257,'source custody '+i);
  bad(r.published_html_width_px!==src.width_px||r.published_html_height_px!==src.height_px,'invented HTML geometry '+i);
  bad(r.source_kind!=='wikimedia_redirect'||r.redirect_width_request_px!==1280,'source class '+i);
  bad(r.retriever_observation!=='exact_redirect_not_accessible_in_text_retriever','retriever semantics '+i);
  for(const k of ['retriever_origin_http_status','final_browser_http_status','final_browser_current_src',
   'final_browser_image_mime','final_browser_natural_width_px','final_browser_image_bytes','final_browser_redirect_chain',
   'visitor_broken_image_confirmed']) bad(r[k]!==null,'unsupported origin/browser result '+i+' '+k);
  bad(r.commons_catalog_url!=='https://commons.wikimedia.org/wiki/File:'+names[i],'catalog filename '+i);
  bad(typeof r.nasa_primary_subject_reference_url!=='string'||
    !/^https:\/\/(?:[a-z0-9-]+\.)*nasa\.gov\//i.test(r.nasa_primary_subject_reference_url),'official NASA URL '+i);
  bad(!Number.isInteger(r.commons_catalog_master_width_px)||r.commons_catalog_master_width_px<1||
    !Number.isInteger(r.commons_catalog_master_height_px)||r.commons_catalog_master_height_px<1,'catalog dimensions '+i);
  const w=Math.min(960,r.commons_catalog_master_width_px);
  bad(r.conditional_staged_width_px!==w||
    r.conditional_staged_height_px!==Math.round(w*r.commons_catalog_master_height_px/r.commons_catalog_master_width_px)||
    r.no_upscale!==true,'wrong derivative / upscale '+i);
  bad(r.commons_catalog_original_bytes!==null&&
    (!Number.isInteger(r.commons_catalog_original_bytes)||r.commons_catalog_original_bytes<1),'invented original bytes '+i);
  bad(r.same_published_image_binary_hash_verified!==false||r.rights_item_cleared!==false,'false image identity/rights '+i);
  for(const k of ['download_authorized','cache_authorized','wordpress_media_upload_authorized',
   'wordpress_post_edit_authorized','asset_downloaded','performance_transfer_reduction_measured'])
   bad(r[k]!==false,'publication/cache/measurement falsely authorized '+i+' '+k);
  bad(r.publication_state!=='REFERENCE_ONLY'||r.copyright_review!=='per_item_HOLD_NASA_origin_and_any_repackaged_asset','publication or rights state '+i);
 }
 bad(a.rows[6]?.commons_catalog_master_width_px!==800||a.rows[6]?.conditional_staged_width_px!==800,'LRO: no upscale 800px source');
 bad(a.rows[4]?.commons_catalog_url!=='https://commons.wikimedia.org/wiki/File:Apollo_Command_Module_Main_Control_Panel.gif','technical GIF identity');
 return errors;
}
module.exports={validate};
