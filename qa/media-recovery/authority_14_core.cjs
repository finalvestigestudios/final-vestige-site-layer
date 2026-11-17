'use strict';
// Repository-only catalog checks, with fail-closed WordPress and visitor-network fields.
const typeCounts={commons:6,publisher:4,nasa_mirror:2,usgs:1,context:1};
const file=s=>decodeURIComponent(s.split('?')[0].split('/').pop()).replace(/^File:/,'').replaceAll('_',' ');
function audit14(q,p,d){
 const errors=[],bad=x=>errors.push(x),Q=new Map(q?.rows?.map(x=>[x.image_key,x])||[]),old=new Set(p?.entries?.map(x=>x.image_key)||[]),seen=new Set(),counts={};
 if(d?.schema_version!==1||d.review_date!=='2026-10-30'||d.prior_commit_sha!=='f7ec47fc22ed8b838315e52934e111b5579601a6'||d.entries?.length!==14)bad('schema/count/base');
 for(const x of d.entries||[]){
  const k=x.image_key,t=x.evidence_type,orig=Q.get(k);counts[t]=(counts[t]||0)+1;
  if(seen.has(k)||old.has(k))bad(k+' duplicate/existing');seen.add(k);
  if(!orig||orig.exact_stored_url!==x.source_url_exact||orig.post_id!==x.post_id||orig.article_url!==x.article_url||orig.official_record_url)bad(k+' input source mismatch');
  if(!Object.hasOwn(typeCounts,t)||!x.source_url_exact?.startsWith('https://')||!x.record_url?.startsWith('https://')||!x.credit||!x.license_observed)bad(k+' source/licensing evidence absent');
  if(t==='commons'){
   if(!x.source_url_exact.startsWith('https://commons.wikimedia.org/wiki/Special:Redirect/file/')||
      !x.record_url.startsWith('https://commons.wikimedia.org/wiki/File:')||
      file(x.source_url_exact)!==file(x.record_url))bad(k+' Commons canonical mismatch');
   if(k==='268:0'){
    if(JSON.stringify(x.source_pixel_dimensions_catalog)!=='[665,448]'||!x.license_observed.includes('PD-US'))bad(k+' small file rights gate');
   }else if(!x.license_observed.includes('CC BY 2.0')||!x.flickr_id)bad(k+' Flickr license gate');
  }else if(t==='publisher'){
   if(x.post_id!==268||!x.source_url_exact.includes('/assets/img/')||
      !x.record_url.startsWith('https://archimedespalimpsest.org/about/')||
      file(x.source_url_exact)!==file(x.publisher_expected_file)||!['imaging_x8.jpg','imagecapture-capture2b.jpg','imaging_x12.jpg','imaging_x9.jpg'].some(f=>file(f)===file(x.source_url_exact)))bad(k+' publisher exact image mismatch');
  }else if(t==='nasa_mirror'){
   const id=x.source_url_exact.match(/^https:\/\/images-assets\.nasa\.gov\/image\/([^/]+)\/\1~large\.jpg$/)?.[1];
   if(!id||x.post_id!==434||x.nasa_id!==id||x.nasa_image_date!=='2017-01-24'||!x.record_url.startsWith('https://commons.wikimedia.org/wiki/File:Apollo_1_Tribute_'))bad(k+' NASA archival ID/date');
  }else if(t==='usgs'){
   if(k!=='418:5'||x.record_url!=='https://www.usgs.gov/media/images/damage-hilo-tsunami-struck-april-fools-day-1946'||!x.archive_original_url?.startsWith('https://d9-wret.s3.us-west-2.amazonaws.com/')||file(x.archive_original_url)!==file(x.source_url_exact)||!x.source_url_exact.includes('/styles/full_width/'))bad(k+' USGS filename/original mismatch');
  }else if(t==='context'&&(k!=='418:4'||x.record_url!=='https://www.hawaiimagazine.com/three-tsunamis-that-changed-hilo-and-hawaiis-big-island/'))bad(k+' NOAA contextual evidence mismatch');
  if(x.candidate_source_identified!==(t!=='context'))bad(k+' overstated source identity');
  if(x.source_pixel_dimensions_catalog===null){
   if(x.calculated_nonupscaled_dimensions_px!==null)bad(k+' assumed natural dimensions');
  }else {
   const [w,h]=x.source_pixel_dimensions_catalog,z=x.calculated_nonupscaled_dimensions_px;
   if(t!=='commons'||![w,h].every(n=>Number.isInteger(n)&&n>0)||!Array.isArray(z)||z[0]!==Math.min(960,w)||z[1]!==Math.round(h*z[0]/w))bad(k+' unsafe target/no-upscale');
  }
  if(x.proposed_width_max_px!==960||x.live_site_http_status!==null||x.live_site_natural_width_px!==null||x.live_site_wire_bytes!==null||x.confirmed_broken!==null||x.measured_weight_saving_pct!==null||x.original_binary_sha256!==null||x.rights_verified!==false||x.wp_media_id!==null||x.wp_upload_approved!==false||x.wp_post_edit_approved!==false)bad(k+' fabricated measurement or unauthorized release');
 }
 for(const [t,n] of Object.entries(typeCounts))if(counts[t]!==n)bad('tier '+t+' count');
 if(q?.counts?.image_slots!==43||q.counts.offsite!==36||q.counts.source_record_mapped!==16||p?.entries?.length!==6||d.baseline?.previous_identity_candidates!==22||d.summary?.new_source_identity_candidates!==13||d.summary?.context_only!==1||d.summary?.candidate_coverage!==35||d.summary?.remaining_unmatched!==1||d.summary?.visitor_broken_count!==null||d.summary?.measured_savings_percent!==null)bad('baseline/summary claims');
 return {ok:errors.length===0,errors,counts:{researched:seen.size,new_candidates:13,source_candidates:35,unmatched:1,verified_broken:null,measured_savings:null}};
}
module.exports={audit14};
