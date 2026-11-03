'use strict';
function validate(a){
 let e=[];const bad=x=>e.push(x);
 if(!a||a.schema!=='fv-silver-bridge-six-v1') return ['schema'];
 if(a.wp_live?.id!==258||a.wp_live?.status!=='publish'||a.pinned_source_blob!=='6df3251e5a67a971d87a516a1ba4a0cc32f51f96d')bad('pin');
 const expected=["https://commons.wikimedia.org/wiki/Special:Redirect/file/Silver%20Bridge%2C%201928.jpg","https://www-d.ntsb.gov/investigations/PublishingImages/80267-img.jpg","https://www.fhwa.dot.gov/highwayhistory/images/national_bridge_inspection_standards/bridge_inspection_1_thumb.jpg","https://www.fhwa.dot.gov/highwayhistory/images/national_bridge_inspection_standards/bridge_inspection_1B.jpg","https://www.fhwa.dot.gov/highwayhistory/images/national_bridge_inspection_standards/bridge_inspection_4.jpg","https://commons.wikimedia.org/wiki/Special:Redirect/file/Silver%20Bridge%20-%20DPLA%20-%209fc0bcf07698072f128124fc79edd1c7%20%28page%202%29.jpg"],checks=["retriever_inaccessible_no_origin_status","retriever_inaccessible_no_origin_status","viewer_displayed","viewer_displayed","viewer_displayed","retriever_inaccessible_no_origin_status"];
 if(!Array.isArray(a.images)||a.images.length!==6)return [...e,'slot count'];
 a.images.forEach((x,i)=>{
  if(x.key!=='258:'+i||x.source_url!==expected[i]||!x.alt)bad('source '+i);
  const o=x.original_observation||{},c=x.candidate||{};
  if(o.method!=='web_open_independent_retriever'||o.result!==checks[i]||o.origin_http_status!==null||o.guest_browser_status!==null||o.decode_verified!==null||o.encoded_transfer_bytes!==null)bad('network proof '+i);
  if(x.target_max_width_px!==960||c.rights_cleared!==false||c.wp_upload_approved!==false||c.exact_bytes_or_crop_verified!==false)bad('unsafe release '+i);
  if(typeof c.catalog_url!=='string'||!c.catalog_url.startsWith('https://')||(c.url!==null&&!c.url?.startsWith('https://')))bad('candidate URL '+i);
  if(typeof c.rights_note!=='string'||!c.rights_note||!c.kind)bad('rights/source '+i);
  if(c.original_intrinsic_px===null && c.conditional_derivative_px!==null)bad('invented pixels '+i);
  if(c.original_intrinsic_px!==null){
   const p=c.original_intrinsic_px,d=c.conditional_derivative_px;
   if(!Array.isArray(p)||!Array.isArray(d)||p.length!==2||d.length!==2||[...p,...d].some(v=>!Number.isInteger(v)||v<=0)||d[0]>960||d[0]>p[0]||d[1]>p[1]||Math.abs(p[0]/p[1]-d[0]/d[1])>0.004)bad('dimensions '+i);
  }
 });
 if(a.images[0].candidate.original_intrinsic_px?.join('x')!=='286x154'||a.images[0].candidate.conditional_derivative_px?.join('x')!=='286x154')bad('tiny source cannot upscale');
 if(a.images[5].candidate.original_intrinsic_px?.join('x')!=='3296x2080'||a.images[5].candidate.conditional_derivative_px?.join('x')!=='960x606')bad('DPLA dimensions');
 if(!a.images[5].candidate.rights_note.includes('INCONCLUSIVE'))bad('DPLA license not verified');
 if(a.images[1].candidate.url!=='https://www-s.ntsb.gov/investigations/PublishingImages/80267-img.jpg'||a.images[1].candidate.candidate_displayed!==true)bad('NTSB candidate mismatch');
 if(a.images[3].candidate.candidate_displayed!==true||a.images[4].candidate.candidate_displayed!==true)bad('FHWA candidate mismatch');
 let t=a.totals||{};
 if(t.slots!==6||t.source_viewer_displayed!==3||t.source_retriever_inaccessible!==3||t.official_alternative_displayed!==3||t.browser_confirmed_broken!==0||t.wp_repairs!==0||t.measured_reduction_percent!==null)bad('invented results');
 let b=a.baseline||{};
 if(b.articles!==61||b.stored_image_slots!==355||b.external_origins!==288||b.over_1_5MiB_wp_originals!==13||b.reported_42_broken!=='NOT_BROWSER_VERIFIED'||b.reported_76_percent!=='NOT_MEASURED')bad('unsupported census');
 return e;
}
module.exports={validate};
