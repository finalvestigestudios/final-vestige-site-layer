'use strict';
/** Offline, read-only metadata validator. No external image requests or WordPress writes. */
function audit(x){
 const errors=[],check=(ok,why)=>{if(!ok)errors.push(why)};
 check(x?.schema==='fv-navy-thresher-post220-catalog-v1','schema');
 check(x?.source_post?.id===220&&x?.source_post?.status==='publish'&&x?.source_post?.live_image_count===7,'post');
 check(typeof x?.source_post?.modified==='string'&&x.source_post.modified.length>8,'modified');
 check(x?.count===7&&Array.isArray(x.records)&&x.records.length===7,'row_count');
 check(x?.official_exact_subject_catalogs===6&&x?.secondary_only_items===1,'identity_counts');
 check(x?.browser_evidence_available===false&&x?.actual_broken_image_count===null&&x?.production_images_repaired===0&&x?.sitewide_wire_reduction_percent===null,'unsupported_sitewide_claim');
 check(x?.inventory_context?.alleged_broken_count_unverified===42&&x?.inventory_context?.claimed_76_percent_wire_savings==='UNMEASURED','false_42_or_76_claim');
 const names=['USS_Thresher_(SSN-593)_bow.jpg','USS_Thresher_(SSN-593)_launching.jpg','USS_Skylark_(ASR-20).jpg','USS_Thresher_(SSN-593)_watertight_door.jpg','Bathyscaphe_Trieste2_2.jpg','USS_Thresher_(SSN-593)_brass_pipe.jpg','USS_Thresher_(SSN-593)_rudder_sunk.jpg'];
 const ids=['NH 97545','NH 97552','NH 97310','NH 97567',null,'NH 97570','NH 97557'];
 const widths=[4918,740,578,740,1700,739,740],heights=[6136,574,737,532,1349,574,576];
 for(let i=0;i<7;i++){
  const r=x?.records?.[i]; if(!r){errors.push('missing:'+i);continue}
  const key='220:'+i;
  check(r.image_key===key,'key:'+i);
  check(r.commons_filename===names[i],'file:'+i);
  const expected='https://commons.wikimedia.org/wiki/Special:Redirect/file/'+names[i];
  check(typeof r.current_published_source_url==='string'&&r.current_published_source_url.startsWith(expected)&&(!r.current_published_source_url.includes('?')||r.current_published_source_url===expected+'?width=1280'),'source:'+i);
  check(typeof r.current_published_alt==='string'&&r.current_published_alt.length>25,'alt:'+i);
  check(r.commons_file_page==='https://commons.wikimedia.org/wiki/File:'+names[i],'catalog_identity:'+i);
  check(r.official_navy_catalog_id===ids[i]&&r.same_subject_primary_catalog_caption_verified===(i!==4),'navy_identity:'+i);
  check((i===4&&r.official_navy_catalog_url===null)||(i!==4&&typeof r.official_navy_catalog_url==='string'&&r.official_navy_catalog_url.startsWith('https://www.history.navy.mil/')),'official_url:'+i);
  const p=r.commons_original_pixels,d=r.proposed_derivative_pixels;
  check(p?.width===widths[i]&&p?.height===heights[i],'pixels:'+i);
  check(d?.width===Math.min(960,widths[i])&&d?.height===Math.round(heights[i]*Math.min(960,widths[i])/widths[i]),'derivative:'+i);
  check(typeof r.photographic_chronology_note==='string'&&r.photographic_chronology_note.length>18,'chronology:'+i);
  check(r.rights?.item_specific_review==='HOLD'&&r.rights?.localization_permission_granted_by_this_audit===false,'rights:'+i);
  const b=r.guest_browser;
  check(b?.current_src===null&&b?.http_status===null&&b?.decoded_natural_width===null&&b?.decoded_natural_height===null&&b?.cdp_transfer_bytes===null&&b?.verified_broken===null,'fabricated_guest_status:'+i);
  const a=r.release;
  check(a?.candidate_only===true&&a?.binary_downloaded===false&&a?.wp_media_upload===false&&a?.wp_post_edit===false&&a?.public_publish===false,'publication_gate:'+i);
 }
 return {ok:errors.length===0,errors,results:{rows:x?.records?.length,exact_primary:6,secondary_unresolved:1}};
}
if(typeof module!=='undefined')module.exports={audit};
