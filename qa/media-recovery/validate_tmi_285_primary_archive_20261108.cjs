'use strict';
const orig={
 "285:5":"https://images.saymedia-content.com/.image/ar_16:9,c_fill,cs_srgb,fl_progressive,q_auto:eco,w_1200/MTg5ODU1MTM1NjYzNDAwNjM2/the-china-syndrome-blockbuster-movie-becomes-eerie-prophecy.jpg",
 "285:2":"https://blog.ucsusa.org/wp-content/uploads/2022/10/DBD-42-Figure-4-tmi-panel.jpg"
};
function validate(a){
 const errors=[],bad=s=>errors.push(s);
 if(a?.schema!=='fv-tmi285-primary-publisher-identity-v1')bad('schema');
 if(a?.frozen_source_blob!=='49183f66f880f7c4dfd363acca906876877f2e5e')bad('source_blob');
 if(a?.historical_42_broken!=='UNVERIFIED_GUEST'||a?.claimed_76pct_transfer!=='UNMEASURED'||a?.visitor_broken_total!==null)bad('unsupported_metrics');
 if(a?.publication_authorized!==false||a?.wp_media_write_authorized!==false||a?.assets_downloaded!==0)bad('production_hold');
 if(!Array.isArray(a?.records)||a.records.length!==2)return {ok:false,errors:[...errors,'row_count']};
 const map=Object.fromEntries(a.records.map(r=>[r.slot,r]));
 if(Object.keys(map).length!==2)bad('duplicate_slot');
 for(const [key,src] of Object.entries(orig)){
   const r=map[key];if(!r){bad('missing_'+key);continue}
   if(r.published_src!==src)bad('source_integrity_'+key);
   if(r.browser_status!==null||r.browser_bytes!==null||r.browser_decode!==null)bad('fabricated_browser_'+key);
   if(r.retriever?.is_origin_http!==false||r.retriever?.is_browser_http!==false)bad('confused_wrapper_'+key);
   if(r.candidate?.max_width!==960||r.candidate?.no_upscale!==true||r.candidate?.binary_sha256!==null)bad('staging_gate_'+key);
   if(r.candidate?.replacement_editor_approved!==false||r.candidate?.wordpress_action!=='HOLD')bad('not_approved_'+key);
 }
 const p=map['285:5']?.candidate||{},q=map['285:2']?.candidate||{};
 if(p.file_page!=='https://commons.wikimedia.org/wiki/File:Three_mile_island_062010.jpg'||p.master_url!=='https://upload.wikimedia.org/wikipedia/commons/0/09/Three_mile_island_062010.jpg'||p.publisher_links_direct_master!==true)bad('primary_record');
 if(p.publisher_article!=='https://discover.hubpages.com/entertainment/The-China-Syndrome-Blockbuster-Movie-Becomes-Eerie-Prophecy')bad('publisher');
 if(p.license_evidence!=='COMMONS_CREATOR_PD_SELF'||p.author!=='Marque1313')bad('rights');
 if(JSON.stringify(p.native_px)!=='[819,614]'||JSON.stringify(p.proposed_px)!=='[819,614]'||p.keep_full_frame!==true)bad('no_upscale_or_crop');
 if(!p.crop_warning?.includes('16:9')||!p.date_discrepancy?.includes('June 16')||!p.scene?.includes('NOT 1979'))bad('history_integrity');
 if(q.file_page!==null||q.master_url!==null||q.native_px!==null||q.proposed_px!==null||q.license_evidence!=='NO_EXACT_PANEL_PHOTO_RIGHTS')bad('ucs_unsourced');
 if(q.not_equivalent_reason!=='NRC schematic is not the published documentary panel photograph')bad('false_image_equivalence');
 if(map['285:2']?.retriever?.redirect_target!=='https://blog.ucs.org/wp-content/uploads/2022/10/DBD-42-Figure-4-tmi-panel.jpg')bad('ucs_redirect');
 return {ok:errors.length===0,errors};
}
module.exports={validate};
if(require.main===module){const fs=require('node:fs');const data=JSON.parse(fs.readFileSync(process.argv[2]||__dirname+'/tmi_285_primary_archive_20261108.json','utf8'));const result=validate(data);console.log(JSON.stringify(result));if(!result.ok)process.exitCode=1}
