'use strict';
const fs=require('node:fs');
function validate(a){
 const errors=[]; const wrong=(x,msg)=>{if(x)errors.push(msg);};
 if(!a||a.schema!=='fv-oversize-66-post-14-media-20261107'||!Array.isArray(a.media))return {ok:false,errors:['schema']};
 const c=a.cohort||{},p=a.prior_captured_cohort||{},r=a.performance_and_release||{},m=a.media;
 wrong(c.published_posts!==66||c.published_inline_img_src!==361||c.image_media_items!==118||c.oversize_items!==14||c.oversize_threshold_bytes_exclusive!==1572864||c.oversize_stored_original_bytes!==45553777,'cohort');
 wrong(p.image_media_items!==113||p.oversize_items!==13||p.oversize_stored_original_bytes!==43522829,'prior');
 wrong(!Array.isArray(a.posts_checked)||a.posts_checked.length!==66||new Set(a.posts_checked).size!==66,'post census');
 const ids=[39,40,41,42,43,293,382,388,389,405,482,1257,1258,2148];
 wrong(m.length!==14||new Set(m.map(x=>x.id)).size!==14||ids.some(id=>!m.some(x=>x.id===id)),'media ids');
 wrong(m.reduce((sum,x)=>sum+x.original_bytes,0)!==45553777,'real stored bytes');
 wrong(m.filter(x=>x.published_raw_inline_post_ids.length).length!==10,'matched published originals');
 wrong(m.filter(x=>!x.published_raw_inline_post_ids.length).map(x=>x.id).sort((a,b)=>a-b).join(',')!=='293,405,482,2148','unmapped scope');
 for(const x of m){
  wrong(x.original_bytes<=1572864||!Number.isInteger(x.original_bytes),'size '+x.id);
  wrong(!x.source_url.startsWith('https://finalvestige.com/wp-content/uploads/2026/'),'origin '+x.id);
  wrong(!Number.isInteger(x.width)||!Number.isInteger(x.height)||x.width<=0||x.height<=0,'geometry '+x.id);
  const w=Math.min(960,x.width),h=Math.round(x.height*w/x.width);
  wrong(x.conditional_max_960?.width!==w||x.conditional_max_960?.height!==h,'no-upscale/aspect '+x.id);
  wrong(x.rights_approved!==false||x.rehost_approved!==false||x.guest_http_status!==null||x.browser_decoded!==null||x.visitor_transfer_bytes!==null,'unsupported status/rights '+x.id);
  wrong(!Array.isArray(x.published_raw_inline_post_ids)||x.published_raw_inline_post_ids.some(i=>!a.posts_checked.includes(i)),'published lookup '+x.id);
 }
 for(let j=34;j<=38;j++){const x=m.find(x=>x.id===j+5);wrong(!x||x.featured_post_id!==j||x.wp_subsizes_metadata_present!==false||x.published_raw_inline_post_ids.join(',')!==String(j),'PNG hero '+j);}
 for(const id of [382,388,389]){const x=m.find(x=>x.id===id);wrong(!x||x.source_match_method!=='stored Jetpack src basename'||x.published_raw_inline_post_ids.join(',')!=='299','Vasa method '+id);}
 wrong(m.find(x=>x.id===2148)?.original_bytes!==2030948||m.find(x=>x.id===2148)?.authority!=='https://www.noaa.gov/noaa-collections/photo-library/wea00739jpg','new NOAA');
 wrong(r.reported_broken_count_42_verified!==false||r.reported_76_percent_wire_reduction_verified!==false||r.measured_wire_delta_percent!==null||r.guest_broken_count!==null,'fabricated performance');
 wrong(r.rights_clearance!==false||r.uploads!==0||r.post_writes!==0||r.image_downloads!==0||r.homepage_changes!==0||r.spend_usd!==0,'release holds');
 return {ok:!errors.length,errors,metrics:{media_items:14,stored_original_bytes:45553777,matched_published:10,unmatched_other_surfaces_unknown:4,delta_media_items:1,delta_stored_original_bytes:2030948}};
}
module.exports={validate};
if(require.main===module){if(!process.argv[2])throw Error('Usage: node validate_oversize_66post_14media_20261107.cjs <audit.json>');const result=validate(JSON.parse(fs.readFileSync(process.argv[2],'utf8')));console.log(JSON.stringify(result,null,2));if(!result.ok)process.exitCode=1;}
