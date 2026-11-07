"use strict";
function validate(a){
 const e=[],err=x=>e.push(x);
 const names=["New_London_School_explosion.jpg","New_London_School_before_explosion.webp","INP_Photos_of_New_London_School_explosion.jpg","INP_Photos_of_New_London_School_explosion_(1).jpg","INP_Photos_of_New_London_School_explosion_(2).jpg","New_London_School_Explosion_Memorial_-_46699056584.jpg"];
 const widths=[760,960,2861,2457,2457,3840],heights=[609,685,2244,1950,1862,2160];
 if(a.schema!=="FV-media-217-v1"||a.post?.id!==217||a.post?.inventory_blob_sha!=="0f3dfe398a76838049cebba7cb773d5c5a0c8c69")err("source provenance");
 if(a.counts?.images!==6||a.counts?.offsite!==6||a.counts?.independent_source_families!==4||a.counts?.confirmed_broken!==0||a.counts?.actually_tested_guest!==0)err("source counts");
 if(!Array.isArray(a.images)||a.images.length!==6)return {ok:false,errors:[...e,"six images"]};
 a.images.forEach((v,i)=>{
  const src="https://commons.wikimedia.org/wiki/Special:Redirect/file/"+names[i]+"?width=1280";
  if(v.key!=="217:"+i||v.post_id!==217||v.slot!==i||v.stored_source_url!==src||!v.stored_alt)err("slot/source/alt "+i);
  if(v.catalog_original?.width!==widths[i]||v.catalog_original?.height!==heights[i])err("native catalog geometry "+i);
  const w=Math.min(960,widths[i]),h=Math.round(heights[i]*w/widths[i]);
  if(v.safe_preview?.width!==w||v.safe_preview?.height!==h||v.safe_preview?.no_upscale!==true||v.safe_preview?.crop!==false)err("preview safety "+i);
  if(!v.catalog_url?.startsWith("https://commons.wikimedia.org/wiki/File:")||!v.primary_or_origin_record_url?.startsWith("https://"))err("provenance URL "+i);
  if(!v.provenance?.credit||!v.provenance?.rights||v.provenance?.rights_republication_cleared!==false)err("rights "+i);
  if(!v.visual_integrity||v.wp_recovery?.replacement_authorized!==false||v.wp_recovery?.wp_media_id!==null||v.wp_recovery?.master_sha256!==null||v.wp_recovery?.derivative_made!==false)err("unsafe staging "+i);
  if(!v.browser||Object.values(v.browser).some(x=>x!==null)||v.retriever?.actual_origin_http_status!==null)err("unsupported browser/origin status "+i);
 });
 for(let i=2;i<5;i++)if(a.images[i].provenance.lineage!=="INP-plate")err("newspaper parent/crop "+i);
 if(a.images[0].provenance.date_record!=="1937-03-17"||!a.images[0].visual_integrity.includes("precedes"))err("AP date conflict");
 if(a.images[5].provenance.date_record!=="2016-07-05"||!a.images[5].provenance.rights.includes("CC BY-SA 2.0"))err("modern memorial license");
 if(a.performance?.reported_42_broken_proven!==false||a.performance?.claimed_76_percent_wire_saved_measured!==false||a.performance?.cold_browser_image_bytes!==null)err("invented performance");
 if(a.performance?.oversized_wp_originals_count_historical!==13||a.performance?.oversized_wp_originals_stored_bytes_historical!==43522829)err("oversize storage cohort");
 if(a.related_authoritative_source?.rights_rehosting_cleared!==false||!a.related_authoritative_source?.relationship?.includes("NOT exact replacement"))err("archival substitution risk");
 if(Object.values(a.prohibitions||{}).some(x=>x!==true)||a.site_qa_handoff?.no_duplicate_collector!==true)err("authorized scope");
 return {ok:e.length===0,errors:e};
}
module.exports={validate};
