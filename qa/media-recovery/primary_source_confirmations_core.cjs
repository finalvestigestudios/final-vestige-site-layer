'use strict';
/** Provenance validator; deliberately separates official records from visitor HTTP evidence. */
function validatePrimaryEvidence(queue,doc){
 const failures=[],bad=s=>failures.push(s),a=queue&&queue.rows,b=doc&&doc.entries;
 if(!Array.isArray(a)||!Array.isArray(b))return{ok:false,errors:['missing queue/entries'],summary:null};
 const map=new Map(a.map(x=>[x.image_key,x])),seen=new Set();let usgs=0,nasa=0;
 if(doc.schema_version!==1||doc.review_date!=='2026-10-30'||b.length!==6)bad('schema/count');
 for(let i=0;i<b.length;i++){
  const e=b[i],tag='row '+String(i)+' '+String(e.image_key),q=map.get(e.image_key);
  if(seen.has(e.image_key))bad(tag+' duplicated key');seen.add(e.image_key);
  if(!q||q.post_id!==e.post_id||q.exact_stored_url!==e.exact_stored_url)bad(tag+' P0 source mismatch');
  if(typeof e.exact_stored_url!=='string'||!e.exact_stored_url.startsWith('https://'))bad(tag+' unsafe source URL');
  if(e.proof_tier==='exact_archive_original_url'){
   usgs++;
   if(e.authority!=='USGS'||e.post_id!==407||
     !e.official_catalog_url.startsWith('https://www.usgs.gov/media/images/')||
     !e.exact_stored_url.startsWith('https://d9-wret.s3.us-west-2.amazonaws.com/')||
     e.official_original_url!==e.exact_stored_url||e.web_image_viewer_rendered!==true||
     e.catalog_rights_statement!=='Public Domain (item page)')bad(tag+' USGS archive original claim unsupported');
   if(e.catalog_id!==e.exact_stored_url.split('/').pop())bad(tag+' USGS filename mismatch');
  }else if(e.proof_tier==='nasa_official_gallery_id'){
   nasa++;
   const id=(e.exact_stored_url.match(/^https:\/\/images-assets\.nasa\.gov\/image\/([^/]+)\/\1~large\.jpg$/)||[])[1];
   if(e.authority!=='NASA'||e.post_id!==434||
     e.official_catalog_url!=='https://www.nasa.gov/gallery/apollo-1/'||
     !['S67-15717','S66-58038','S67-21294'].includes(id)||
     e.catalog_id!==id||e.official_original_url!==null||e.web_image_viewer_rendered!==false)
     bad(tag+' NASA gallery ID claim unsupported');
  }else bad(tag+' unknown evidence tier');
  if(!e.required_credit||!e.catalog_date||!e.description)bad(tag+' missing credit/context');
  if(e.source_http_status!==null||e.web_viewer_http_status!==null||e.visitor_browser_http_status!==null||
    e.visitor_natural_width_px!==null||e.visitor_image_transfer_bytes!==null||e.verified_broken_in_browser!==null)
    bad(tag+' unverified HTTP/browser status');
  if(e.image_sha256!==null||e.binary_identity_verified!==false||e.expected_savings_percent!==null)
    bad(tag+' fabricated binary/performance evidence');
  if(e.rights_review_complete!==false||e.wordpress_media_id!==null||e.wordpress_media_upload_authorized!==false||
    e.wordpress_post_edit_authorized!==false)bad(tag+' unauthorized rights/WordPress change');
  if(e.maximum_width_px!==960||e.never_upscale!==true||e.preserve_aspect_ratio!==true||
    e.source_intrinsic_dimensions_px!==null||e.target_dimensions_px!==null)
    bad(tag+' unverified intrinsic or unsafe dimensions');
 }
 if(usgs!==3||nasa!==3)bad('expected 3+3 institutional split');
 if(queue.counts.image_slots!==43||queue.counts.offsite!==36||queue.counts.source_record_mapped!==16)bad('queue baseline changed; re-audit');
 if(doc.counts?.new_institutional_matches!==6||doc.counts?.exact_usgs_original_url_matches!==3||
    doc.counts?.nasa_gallery_id_matches!==3||doc.counts?.original_image_viewer_rendered!==3||
    doc.counts?.confirmed_broken_in_browser!==null||doc.counts?.measured_weight_reduction!==null)bad('summary counts invalid');
 return{ok:failures.length===0,errors:failures,summary:{new_catalog_matches:b.length,USGS_exact_source_matches:usgs,NASA_gallery_matches:nasa,
  total_offsite_p0_with_official_candidate:queue.counts.source_record_mapped+b.length,
  offsite_p0_still_unmapped:queue.counts.offsite-(queue.counts.source_record_mapped+b.length),
  confirmed_visitor_broken:null,measured_savings_percent:null}};
}
module.exports={validatePrimaryEvidence};
