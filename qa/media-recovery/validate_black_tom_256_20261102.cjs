'use strict';
/** Strict read-only post-256 catalog/rights/geometry attestation. Does not fetch media. */
const EXPECT=[{"key":"256:0","src":"https://commons.wikimedia.org/wiki/Special:Redirect/file/Black%20Tom%20explosion%20-%201916.jpg?width=1280","alt":"Destroyed warehouses, rail infrastructure and scattered debris at the Black Tom ammunition terminal after the July 30, 1916 explosion.","catalog_url":"https://commons.wikimedia.org/wiki/File:Black_Tom_explosion_-_1916.jpg","record":"http://www.njcu.edu/programs/jchistory/Pages/B_Pages/Black_Tom_Explosion.htm","master":[800,528]},{"key":"256:1","src":"https://commons.wikimedia.org/wiki/Special:Redirect/file/Map%20of%20Black%20Tom%20Island%2C%20Jersey%20City%2C%20New%20Jersey%20-%20showing%20area%20damaged%20by%20explosion%20and%20fire%2C%20July%2030th%201916.%20LOC%202010588272.jpg?width=1280","alt":"1916 Sanborn map of Black Tom Island showing ammunition warehouses, railroad tracks, wharves and the area damaged by the explosion and fire.","catalog_url":"https://commons.wikimedia.org/wiki/File:Map_of_Black_Tom_Island,_Jersey_City,_New_Jersey_-_showing_area_damaged_by_explosion_and_fire,_July_30th_1916._LOC_2010588272.jpg","record":"https://www.loc.gov/item/2010588272/","master":[8385,11736]},{"key":"256:2","src":"https://commons.wikimedia.org/wiki/Special:Redirect/file/Black%20Tom%20explosion%20-%20firefighters%20-%201916.jpg?width=1280","alt":"Firefighters working amid wreckage at Black Tom on the day after the 1916 explosion.","catalog_url":"https://commons.wikimedia.org/wiki/File:Black_Tom_explosion_-_firefighters_-_1916.jpg","record":"http://www.njcu.edu/programs/jchistory/Pages/B_Pages/Black_Tom_Explosion.htm","master":[800,537]},{"key":"256:3","src":"https://commons.wikimedia.org/wiki/Special:Redirect/file/Black%20Tom%20explosion%20-%20Men%20on%20pier%20-%201916.jpg?width=1280","alt":"Men standing on the damaged Black Tom pier amid the aftermath of the 1916 explosion.","catalog_url":"https://commons.wikimedia.org/wiki/File:Black_Tom_explosion_-_Men_on_pier_-_1916.jpg","record":"http://www.njcu.edu/programs/jchistory/Pages/B_Pages/Black_Tom_Explosion.htm","master":[800,545]},{"key":"256:4","src":"https://commons.wikimedia.org/wiki/Special:Redirect/file/Diving%20at%20Black%20Tom%20LCCN2014702309.jpg?width=1280","alt":"A diver preparing to recover unexploded ammunition from the water at Black Tom after the 1916 explosion.","catalog_url":"https://commons.wikimedia.org/wiki/File:Diving_at_Black_Tom_LCCN2014702309.jpg","record":"https://www.loc.gov/item/2014702309/","master":[5766,4141]},{"key":"256:5","src":"https://commons.wikimedia.org/wiki/Special:Redirect/file/Girl%20with%20relics%20from%20the%20Black%20Tom%20Explosion.png?width=1280","alt":"A young girl holding three shells reportedly found about a mile and a half from Black Tom after the 1916 explosion.","catalog_url":"https://commons.wikimedia.org/wiki/File:Girl_with_relics_from_the_Black_Tom_Explosion.png","record":"https://chroniclingamerica.loc.gov/lccn/sn83045462/1916-08-02/ed-1/seq-4/","master":[412,720]},{"key":"256:6","src":"https://commons.wikimedia.org/wiki/Special:Redirect/file/Black%20Tom%20explosion%20-%20electrical%20poles%20-%201916.jpg?width=1280","alt":"Wreckage and damaged utility poles at Black Tom after the July 1916 explosion.","catalog_url":"https://commons.wikimedia.org/wiki/File:Black_Tom_explosion_-_electrical_poles_-_1916.jpg","record":"http://www.njcu.edu/programs/jchistory/Pages/B_Pages/Black_Tom_Explosion.htm","master":[800,535]}];
const SOURCE_SHA='9b16b828342a9ac338f3e65610fd3d8d508355e9';
function inspect(a){
 const e=[];
 if(a?.schema_version!==1||a?.audit_date!=='2026-11-02')e.push('bad_audit_identity');
 const s=a?.source_inventory;
 if(s?.post_id!==256||s?.part_git_blob_sha!==SOURCE_SHA||s?.source_image_count!==7||
  s?.post_url!=='https://finalvestige.com/2026/08/18/the-torch-never-reopened/'||s?.exact_alt_and_url_from_frozen_census!==true)e.push('frozen_source_not_pinned');
 const o=a?.observation_limitations;
 if(o?.catalog_html_pages_read!==7||o?.exact_stored_redirect_urls_tested_by_independent_tool!==7||
  o?.redirect_urls_not_accessible_via_tool!==7||o?.guest_browser_checks!==0||
  o?.verified_browser_broken_count!==null||o?.origin_http_responses!==null||o?.no_public_outage_claim!==true)e.push('unsupported_browser_or_redirect_claim');
 const c=a?.sitewide_context;
 if(c?.published_investigations!==61||c?.source_image_slots!==355||c?.external_origin_slots!==288||
  c?.oversized_wp_originals_over_1_5_MiB!==13||c?.reported_42_broken_guest_verified!==false||
  c?.claimed_76_percent_weight_savings_guest_measured!==false||c?.production_replacements_this_sprint!==0)e.push('unsupported_sitewide_claim');
 const release=a?.rights_and_release;
 if(release?.all_item_rights_hold!==true||release?.media_downloads_allowed!==false||
  release?.first_party_cache_release!==false||release?.production_wp_writes_allowed!==false||
  release?.homepage_design_modifications_allowed!==false||release?.spend_allowed!==false)e.push('unauthorized_release');
 if(!Array.isArray(a?.rows)||a.rows.length!==7)return [...new Set([...e,'seven_rows_required'])];
 const seen=new Set();
 for(let i=0;i<7;i++){
  const r=a.rows[i],x=EXPECT[i];
  if(!r||seen.has(r.image_key)||r.image_key!==x.key||r.post_id!==256||r.slot!==i||
    r.stored_original_source_url!==x.src||r.stored_original_alt!==x.alt||
    r.archived_source_part_blob_sha!==SOURCE_SHA)e.push('row_frozen_identity_mismatch:'+i);
  if(r)seen.add(r.image_key);
  const ob=r?.independent_source_retriever;
  if(ob?.checked_on!=='2026-11-02'||ob?.result!=='TOOL_URL_NOT_ACCESSIBLE_NO_ORIGIN_STATUS'||
    ob?.origin_http_status!==null||ob?.visitor_http_status!==null||ob?.redirect_final_url!==null||ob?.bytes_transferred!==null)e.push('invented_origin_http:'+i);
  const cat=r?.catalog;
  if(cat?.catalog_page_url!==x.catalog_url||cat?.primary_record_url!==x.record||
    cat?.html_catalog_page_read!==true||cat?.same_commons_file_title_as_stored_source!==true||
    cat?.decoded_binary_identity_verified!==false||cat?.original_binary_sha256!==null||
    cat?.original_binary_downloaded!==false||cat?.master_dimensions_from_downloaded_binary_px!==null||
    JSON.stringify(cat?.master_dimensions_from_catalog_px)!==JSON.stringify(x.master))e.push('invalid_archival_identity:'+i);
  const rights=r?.rights;
  if(rights?.assessment!=='HOLD_ITEM_LEVEL_REVIEW'||rights?.credit_required!==true||
     rights?.license_for_mirroring_approved!==false)e.push('rights_hold_violated:'+i);
  const d=r?.conditional_derivative,w=Math.min(960,x.master[0]),h=Math.round(x.master[1]*w/x.master[0]);
  if(d?.max_width_px!==960||JSON.stringify(d?.target_dimensions_px)!==JSON.stringify([w,h])||
     d?.no_upscale!==true||d?.aspect_ratio_preserved!==true||d?.derivative_created!==false||
     d?.source_binary_needed_before_final_sizing!==true)e.push('invalid_derivative_geometry:'+i);
  const b=r?.browser;
  for(const k of ['actual_get_status','final_url','current_src','natural_width_px','natural_height_px','mime_type','request_id','uncached_transfer_bytes','visibly_broken'])
    if(b?.[k]!==null)e.push('invented_browser_measurement:'+i+':'+k);
  const auth=r?.authorization;
  if(auth?.replacement_ready!==false||auth?.first_party_wordpress_cache_authorized!==false||
     auth?.wordpress_post_rewrite_authorized!==false)e.push('unauthorized_wordpress_action:'+i);
 }
 return [...new Set(e)];
}
module.exports={inspect,EXPECT,SOURCE_SHA};
