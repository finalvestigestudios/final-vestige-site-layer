'use strict';
// Offline-only validator of the November 15, 2026 read-only WordPress CMS snapshot.
// Does not request URLs, modify CMS content, or establish browser HTTP status.
function validate(a) {
  const e=[];
  const need=(ok,why)=>{if(!ok)e.push(why);};
  need(a && a.schema==='fv-media-wp66-132-oversized-current-view-v1','schema');
  if(!a||typeof a!=='object') return {ok:false,errors:e};
  const expected=a.published_post_ids_expected,seen=a.post_ids_read,rows=a.records;
  need(Array.isArray(expected)&&expected.length===66&&new Set(expected).size===66,'66 published IDs');
  need(Array.isArray(seen)&&seen.length===66&&new Set(seen).size===66&&Array.isArray(expected)&&seen.every(id=>expected.includes(id)),'66 complete unique post reads');
  need(a.cms_img_tags_read===361,'361 WordPress VIEW img tags');
  need(a.media_attachments_read===132,'132 image attachments');
  need(a.media_total_original_stored_bytes===90403013,'90,403,013 original storage bytes');
  need(a.threshold_strictly_greater_than_bytes===1500000,'strict decimal 1.5MB threshold');
  need(a.oversize_count===20&&Array.isArray(rows)&&rows.length===20,'20 oversized originals');
  need(a.oversize_total_stored_bytes===64385752,'64,385,752 oversized original storage bytes');
  need(a.method==='authenticated_read_only_wp_media_metadata_and_post_view_markup','source method');
  need(a.guest_http_audit_performed===false&&a.visitor_wire_reduction_percent===null&&a.reported_42_broken_guest_verified===null,'do not invent guest failures or a 76% wire saving');
  need(a.production_changes===0,'no production writes');
  if(!Array.isArray(rows)) return {ok:false,errors:e};
  need(new Set(rows.map(x=>x.attachment_id)).size===rows.length,'unique media IDs');
  let uses=0,nonempty=0,missingSrcset=0,noSub=0;const observed=new Set();
  for(const r of rows) {
    need(Number.isInteger(r.attachment_id)&&r.attachment_id>0,'media ID');
    need(typeof r.media_original_url==='string'&&r.media_original_url.startsWith('https://finalvestige.com/wp-content/uploads/'),'first-party original URL');
    need(Number.isInteger(r.stored_original_bytes)&&r.stored_original_bytes>1500000,'original stored bytes above threshold');
    need(Number.isInteger(r.native_width)&&r.native_width>0&&Number.isInteger(r.native_height)&&r.native_height>0,'native dimensions');
    const w=Math.min(960,r.native_width),h=Math.max(1,Math.round(r.native_height*w/r.native_width));
    need(r.conditional_review_width===w&&r.conditional_review_height===h,'960px no-upscale proportional geometry');
    need(r.rights_status==='HOLD_UNVERIFIED'&&r.cache_authorized===false&&r.wp_upload_authorized===false&&r.post_rewrite_authorized===false,'rights and no-production holds');
    need(Array.isArray(r.subsize_names),'CMS subsize list');
    if(Array.isArray(r.subsize_names)&&r.subsize_names.length===0)noSub++;
    need(Array.isArray(r.published_inline_uses),'inline use list');
    if(!Array.isArray(r.published_inline_uses))continue;
    if(r.published_inline_uses.length)nonempty++;
    for(const u of r.published_inline_uses) {
      uses++;if(u.srcset_present!==true)missingSrcset++;
      const key=r.attachment_id+':'+u.post_id+':'+u.image_index;
      need(!observed.has(key),'duplicate image-slot use');observed.add(key);
      need(Number.isInteger(u.post_id)&&Array.isArray(expected)&&expected.includes(u.post_id),'known published parent');
      need(typeof u.post_url==='string'&&u.post_url.startsWith('https://finalvestige.com/'),'article URL');
      need(typeof u.wp_view_img_src==='string'&&u.wp_view_img_src.startsWith('https://'),'actual WordPress VIEW src URL');
      const fname=typeof r.media_original_url==='string'?r.media_original_url.split('/').pop():'';
      need(Boolean(fname)&&u.wp_view_img_src.includes('/'+fname+'?'),'image URL maps to exact original filename');
      need(Number.isInteger(u.image_index)&&u.image_index>=0,'image slot index');
      need(typeof u.srcset_present==='boolean'&&typeof u.sizes_present==='boolean','responsive markup observed as booleans');
      need(u.guest_current_src===null&&u.guest_http_status===null&&u.guest_transferred_bytes===null,'browser and transfer unknown');
    }
  }
  need(rows.reduce((n,x)=>n+x.stored_original_bytes,0)===a.oversize_total_stored_bytes,'stored byte sum');
  need(nonempty===11&&uses===11,'exact 11 published inline oversized assets/uses');
  need(rows.length-nonempty===9,'exact 9 originals not in published inline tags');
  need(new Set(rows.flatMap(r=>r.published_inline_uses.map(u=>u.post_id))).size===8,'8 published posts using originals');
  need(noSub===5&&missingSrcset===5,'5 no-subsize/no-srcset reconstruction PNGs');
  return {ok:e.length===0,errors:e};
}
module.exports={validate};
if(require.main===module){
  const fs=require('node:fs'),path=require('node:path');
  const file=process.argv[2]||path.join(__dirname,'wp66_132media_20oversized_inline_exposure_20261115.json');
  const result=validate(JSON.parse(fs.readFileSync(file,'utf8')));
  console.log(JSON.stringify(result));
  if(!result.ok)process.exitCode=1;
}
