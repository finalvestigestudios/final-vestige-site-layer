'use strict';
function validate(a,sourceRows){
 const errors=[],bad=(x)=>errors.push(x);
 if(a.schema!=='fv.media_recovery.forrestal_289_primary_source_recheck.v1')bad('schema');
 if(a.date!=='2026-11-02'||a.post_id!==289)bad('scope');
 if(!/^https:\/\/finalvestige\.com\//.test(a.post_url||''))bad('post');
 if(a.source_blob_sha!=='49183f66f880f7c4dfd363acca906876877f2e5e')bad('source-blob');
 if(!Array.isArray(sourceRows)||sourceRows.length!==6)bad('source-row-count');
 if(!Array.isArray(a.image_entries)||a.image_entries.length!==6)bad('entry-count');
 const s=new Map((sourceRows||[]).map(x=>[x.key,x])),seen=new Set(),status={DISPLAYED:0,RETRIEVER_403:0};
 for(const e of (a.image_entries||[])){
  if(seen.has(e.key))bad('duplicate:'+e.key);seen.add(e.key);
  const orig=s.get(e.key);
  if(!orig||orig.source_url!==e.published_src||orig.alt!==e.published_alt||orig.post_url!==e.article_url)bad('frozen-src-alt:'+e.key);
  if(!/^289:[0-5]$/.test(e.key||'')||e.source_kind!=='external'||e.external_origin!==true)bad('origin:'+e.key);
  const r=e.retriever||{},b=e.visitor_browser||{};
  if(r.method!=='web.open exact published image URL'||r.observed_on!=='2026-11-02')bad('retriever-evidence:'+e.key);
  if(!Object.prototype.hasOwnProperty.call(status,r.observation))bad('retriever-enum:'+e.key);
  else status[r.observation]++;
  if((r.observation==='DISPLAYED'&&r.retriever_wrapper_status!==null)||(r.observation==='RETRIEVER_403'&&r.retriever_wrapper_status!==403))bad('retriever-status:'+e.key);
  for(const k of ['request_id','http_status','current_src','natural_width_px','transfer_bytes','visual_failure'])if(b[k]!==null)bad('fabricated-browser:'+e.key+':'+k);
  if(e.same_image_replacement_approved!==false||e.wordpress_media_upload_authorized!==false||e.wordpress_post_edit_authorized!==false)bad('unsafe-replacement:'+e.key);
 }
 if(status.DISPLAYED!==5||status.RETRIEVER_403!==1||a.image_entries[4]?.key!=='289:4'||a.image_entries[4]?.retriever?.observation!=='RETRIEVER_403')bad('source-check-counts');
 if(!/2021/.test(a.image_entries[4]?.chronology||'')||!/2013/.test(a.image_entries[5]?.chronology||''))bad('modern-photo-chronology');
 const base=a.baseline||{};
 if(base.articles!==61||base.published_image_slots!==355||base.offsite_origin_refs!==288||base.wp_originals_over_1_5_mib!==13||base.reported_42_broken_verified!==false||base.claimed_76_percent_wire_reduction_measured!==false||base.production_repaired_images!==0)bad('baseline-claims');
 const m=a.summary||{};
 if(m.exact_published_source_checks!==6||m.independent_viewer_displayed!==5||m.independent_retriever_403!==1||m.visitor_broken_confirmed!==0||m.candidates_from_authoritative_primary_catalogs!==3)bad('summary');
 if(!Array.isArray(a.replacement_candidates)||a.replacement_candidates.length!==3)bad('candidate-count');
 const byId=new Map((a.replacement_candidates||[]).map(c=>[c.candidate_id,c]));
 if(byId.size!==3)bad('candidate-unique');
 for(const c of(a.replacement_candidates||[])){
  if(!/^https:\/\//.test(c.catalog_url||'')||!c.for_image_key||c.identical_binary_sha256_verified!==false||c.source_bytes_transferred!==null)bad('candidate-source:'+c.candidate_id);
  if(c.max_target_width_px!==960||!c.no_upscale||!Number.isInteger(c.conditional_width_px)||!Number.isInteger(c.conditional_height_px)||c.conditional_width_px>960||c.conditional_width_px>c.catalog_original_width_px)bad('geometry:'+c.candidate_id);
  if(Math.abs(c.conditional_height_px-Math.round(c.catalog_original_height_px*c.conditional_width_px/c.catalog_original_width_px))>0)bad('aspect:'+c.candidate_id);
  if(c.rights?.item_specific_review_required!==true||c.rights?.wordpress_rehosting_cleared!==false||c.rights?.nonendorsement_and_credit_required_for_staging_review!==true)bad('rights:'+c.candidate_id);
 }
 const d=byId.get('DVIDS-6947585');
 if(!d||d.for_image_key!=='289:4'||d.virin!=='210811-N-SG189-1105'||d.catalog_url!=='https://www.dvidshub.net/image/6947585/farrier-firefighting-school'||!a.image_entries[4]?.published_src.includes(d.virin+'.JPG')||d.conditional_width_px!==960||d.conditional_height_px!==639||d.created_date!=='2021-08-11'||d.published_filename_virin_match!==true||d.rights.catalog_marked_public_domain!==true||d.rights.official_dvids_public_use_notice!=='https://www.dvidshub.net/about/copyright'||d.action!=='HOLD_FOR_VISITOR_NETWORK_EVIDENCE_AND_RIGHTS_REVIEW')bad('dvids-identity');
 for(const id of ['NHHC-USN-1124785','NHHC-USN-1124802']){
  const c=byId.get(id);if(!c||c.scene_class!=='different_1967_firefighting_scene_editor_approval_required'||c.action!=='ALTERNATE_SCENE_ONLY_DO_NOT_AUTOSWAP'||c.rights.catalog_marked_public_domain!==false)bad('NHHC-alternate:'+id);
 }
 for(const [key,value] of Object.entries(a.controls||{}))if(value!==false)bad('unsafe-control:'+key);
 if((a.staging_plan||[]).length<5)bad('staging');
 return errors;
}
module.exports={validate};
