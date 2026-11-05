'use strict';
// Pure offline validator; never fetches or edits content.
function validate(a){
 function check(t,m){if(!t)throw new Error(m)}
 const base='https://finalvestige.com/wp-content/uploads/2026/08/';
 const originals=['edit-017-v01-malbone-tunnel-generalpunger-original.jpg','edit-017-v02-nypl-5003296-original.jpg'];
 const med=['edit-017-v01-malbone-tunnel-generalpunger-original-768x576.jpg','edit-017-v02-nypl-5003296-original-768x519.jpg'];
 const lg=['edit-017-v01-malbone-tunnel-generalpunger-original-1024x768.jpg','edit-017-v02-nypl-5003296-original-1024x692.jpg'];
 const alts=['View into the Malbone Street Tunnel from the southbound platform at Prospect Park, showing the surviving curved tunnel alignment.','1903 map of the Brooklyn Rapid Transit street railway and rapid-transit network.'];
 const px=[[4000,3000],[5667,3831]], cb=[[960,720],[960,649]], b=[4798395,5553669];
 check(a&&a.schema==='fv-media-malbone621-wp-virtual-renditions-v1','schema');
 const p=a.post;
 check(p&&p.id===621&&p.url==='https://finalvestige.com/2026/08/23/six-miles-an-hour-malbone-street-wreck/'&&p.status==='publish'&&p.modified==='2026-09-09T12:03:35','post');
 check(p.inline_images===6&&p.stored_img_missing_dimensions===6&&p.stored_img_srcset_count===0,'HTML audit');
 check(a.wp_originals_stored_bytes===10352064&&a.guest_transferred_bytes===null&&a.guest_trace_sha256===null,'storage vs wire');
 check(a.sitewide_broken_42==='BROWSER_UNVERIFIED'&&a.reduction_76_percent==='WIRE_UNMEASURED','performance claim');
 check(a.approved_to_publish===false&&a.staging_gate==='PENDING_BROWSER_PROVEN_RIGHTS_ITEM_IDENTITY_AND_VISUAL_CHECK','staging');
 check(Array.isArray(a.images)&&a.images.length===2,'two images');
 let sum=0;
 for(let i=0;i<2;i++){
  const e=a.images[i];
  check(e.image_key===`621:${i}`&&e.media_id===1257+i,'slot identity');
  check(e.exact_published_src===base+originals[i]&&e.wp_source_url===e.exact_published_src,'exact original URL');
  check(e.alt===alts[i],'ALT preserved');
  check(JSON.stringify(e.wp_dimensions)===JSON.stringify(px[i])&&e.wp_filesize_bytes===b[i]&&e.wp_mime==='image/jpeg','WP metadata');
  check(e.registered_sizes_virtual===true&&e.html_width===null&&e.html_height===null&&e.html_srcset===false,'stored HTML and virtual state');
  const m=e.intermediate_768,l=e.intermediate_1024;
  check(m&&m.url===base+med[i]&&JSON.stringify(m.dimensions)===JSON.stringify([768,i===0?576:519])&&m.virtual===true&&m.actual_http_status===null&&m.guest_decodes===null,'768 virtual candidate');
  check(l&&l.url===base+lg[i]&&JSON.stringify(l.dimensions)===JSON.stringify([1024,i===0?768:692])&&l.virtual===true&&l.actual_http_status===null&&l.guest_decodes===null,'1024 virtual candidate');
  check(JSON.stringify(e.candidate_derivative_960)===JSON.stringify(cb[i])&&e.no_upscale===true,'960 sizing');
  check(cb[i][0]<=960&&cb[i][0]<=px[i][0]&&cb[i][1]<=px[i][1]&&Math.abs(cb[i][0]/cb[i][1]-px[i][0]/px[i][1])<0.004,'aspect/no-upscale');
  check(e.provenance&&e.provenance.rights==='HOLD'&&e.provenance.description.length>45&&e.provenance.checklist.length===4,'item-level rights hold');
  for(const k of ['original_sha256','guest_current_src','guest_http_status','guest_decode_ok','guest_encoded_transfer_bytes'])check(e[k]===null,'not browser/binary measured '+k);
  for(const k of ['rights_cleared','cache_authorized','wp_upload_authorized','post_edit_authorized'])check(e[k]===false,'release hold '+k);
  sum+=e.wp_filesize_bytes;
 }
 check(sum===a.wp_originals_stored_bytes,'stored sum');
 return {valid:true,count:2,stored_bytes:sum,status:'HOLD'};
}
module.exports={validate};
