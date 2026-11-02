'use strict';
/** Pure, fail-closed source-custody validator. No networking or WordPress writes. */
const TMI='https://images.saymedia-content.com/.image/ar_16:9,c_fill,cs_srgb,fl_progressive,q_auto:eco,w_1200/MTg5ODU1MTM1NjYzNDAwNjM2/the-china-syndrome-blockbuster-movie-becomes-eerie-prophecy.jpg';
const USGS='https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/media/images/EarthquakeLake3.jpg';
function validate(d){
 const fail=(message)=>{throw Error('RECOVERY_EVIDENCE_REJECTED '+message)};
 if(d?.schema!=='fv.media_recovery.high_value_same_scene_crosswalk.v1'||d.audit_date!=='2026-11-02')fail('schema_or_date');
 const b=d.baseline;
 if(!b||b.published_articles!==61||b.stored_image_slots!==355||b.offsite_origin_refs!==288||b.wordpress_originals_over_1_5_mib!==13||b.reported_broken_42_browser_verified!==false||b.claimed_76_percent_wire_reduction_measured!==false||b.production_repairs!==0)fail('sitewide_claim');
 if(!Array.isArray(d.entries)||d.entries.length!==2||d.entries[0].image_key!=='285:5'||d.entries[1].image_key!=='407:3')fail('source_slots');
 for(const row of d.entries){
  if(row.wordpress_media_upload_authorized!==false||row.wordpress_post_edit_authorized!==false||row.retriever.visitor_http_status!==null||row.retriever.visitor_natural_width!==null||row.retriever.visitor_transfer_bytes!==null)fail('publication_or_fabricated_browser_evidence_'+row.image_key);
  if(!row.published_url.startsWith('https://')||!row.article_url.startsWith('https://finalvestige.com/'))fail('url_scheme_or_article');
  if(row.geometry.no_upscale!==true||row.geometry.max_derived_width_px!==960||row.geometry.conditional_derived_width_px>960||row.geometry.conditional_derived_width_px<=0||row.geometry.conditional_derived_height_px<=0)fail('upscale_or_dimensions');
  if(row.rights.item_rights_cleared_for_wordpress_upload!==false||!Array.isArray(row.required_before_repair)||!row.required_before_repair.length)fail('rights_gate');
 }
 const [t,h]=d.entries;
 if(t.published_url!==TMI||t.retriever.observation!=='retriever_404_not_browser_404'||t.retriever.wrapper_status!==404)fail('tmi_retriever');
 if(!t.source_chain.publisher_current_image.includes('/.image/MTg5ODU1MTM1NjYzNDAwNjM2/')||t.source_chain.original_creator_file!=='https://upload.wikimedia.org/wikipedia/commons/0/09/Three_mile_island_062010.jpg'||t.source_chain.publisher_current_image_viewer!=='displayed'||t.source_chain.original_creator_file_viewer!=='displayed'||t.source_chain.same_apparent_scene!=='visually_inspected_matching_composition_not_hash_verified'||t.source_chain.same_bytes_verified!==false)fail('tmi_scene_identity');
 if(t.rights.catalog_assertion.indexOf('public domain')<0||t.rights.publisher_processed_derivative_rights_assumed!==false||t.rights.not_a_1979_accident_photograph!==true||!t.rights.exact_master_photo_date.includes('unresolved'))fail('tmi_rights_date');
 if(t.geometry.catalog_original_width_px!==819||t.geometry.catalog_original_height_px!==614||t.geometry.conditional_derived_width_px!==819||t.geometry.conditional_derived_height_px!==614||t.decision!=='HIGH_CONFIDENCE_SAME_SCENE_ORIGINAL_FOR_STAGING_REVIEW_ONLY')fail('tmi_size_or_decision');
 if(h.published_url!==USGS||h.source_chain.catalog_original_link!==USGS||h.source_chain.catalog_original_same_as_published!==true||h.retriever.observation!=='exact_published_source_displayed_2026_11_02'||h.retriever.wrapper_status!==null)fail('hebgen_source');
 if(!h.rights.creator_credit.includes('Mrs. Steven W. Nile')||!h.rights.catalog_assertion.includes('Public Domain')||h.geometry.viewer_rendered_width_px!==1000||h.geometry.viewer_rendered_height_px!==745||h.geometry.conditional_derived_width_px!==960||h.geometry.conditional_derived_height_px!==715||h.geometry.dimensions_not_visitor_decode!==true||h.decision!=='RETRIEVER_POSITIVE_KEEP_SOURCE_BROWSER_VERIFY_NOT_REPLACE')fail('hebgen_provenance_or_geometry');
 const c=d.common_controls;if(!c)fail('controls');
 for(const k of ['no_unlicensed_scraping','no_binary_downloads','no_wordpress_production_writes','no_homepage_design_changes','no_site_qa_pr_changes','no_subscription_spend'])if(c[k]!==true)fail('controls_'+k);
 if(c.all_reported_guest_http_statuses!==null)fail('claimed_guest_status');
 return {ok:true,verified_records:2,browser_verified_failures:0,publication_authorized:false};
}
module.exports={validate};
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path');
 const d=JSON.parse(fs.readFileSync(path.join(__dirname,'p0_same_scene_2010_tmi_hebgen_20261102.json'),'utf8'));
 console.log(JSON.stringify(validate(d)));
}
