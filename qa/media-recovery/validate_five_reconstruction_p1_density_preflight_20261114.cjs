'use strict';
// Independent P1 readiness gate: no browser collector, CMS writes or media operations.
const FROZEN = [
 [39,34,'bceca0bd-a16f-44f7-be08-16376fbf08ca.png',2892087],
 [40,35,'377e08da-e121-4f57-9174-1548343402b3.png',2552136],
 [41,36,'a44f673d-a8a8-4c83-9f29-7e24dd55156b.png',2498247],
 [42,37,'c1237ffd-4a47-4988-8254-e3b021069e72.png',2488823],
 [43,38,'01340c2e-1165-4ca0-aa96-87398a83d13a.png',2836245]
];
function validate(a) {
 const check=(x,message)=>{if(!x)throw Error('HOLD: '+message);};
 const fields=(x,names,label)=>check(x && !Array.isArray(x) && typeof x==='object' && Object.keys(x).sort().join('|')===names.slice().sort().join('|'),label+' unknown/missing keys');
 fields(a,['schema','audit_date_pt','scope','historical_context','cohort','policy','items'],'root');
 check(a.schema==='fv-media-five-reconstruction-p1-conditional-width-v1'&&a.audit_date_pt==='2026-11-14'&&a.scope==='FIVE FIRST_PARTY RECONSTRUCTION IMAGES; POST_SOURCE_READ_ONLY','record identity');
 const h=a.historical_context,c=a.cohort,p=a.policy;
 fields(h,['frozen_posts','frozen_inline_images','recent_published_posts_20261114','historical_reported_broken_unverified','proposed_76pct_network_reduction_measured'],'history');
 check(h.frozen_posts===61&&h.frozen_inline_images===355&&h.recent_published_posts_20261114===66&&h.historical_reported_broken_unverified===42&&h.proposed_76pct_network_reduction_measured===false,'historic cohorts are not actual failures/savings');
 fields(c,['images','posts','no_wordpress_subsizes','original_stored_bytes','true_wire_bytes_measured'],'cohort');
 check(c.images===5&&c.posts===5&&c.no_wordpress_subsizes===5&&c.original_stored_bytes===13267538&&c.true_wire_bytes_measured===false,'stored bytes are not wire bytes');
 fields(p,['max_derivative_width_px','no_upscale','preserve_ai_reconstruction_label','no_new_archive_photo_substitution','wp_production_write','media_download_or_rehost_approval','release_or_merge','subscription_spend_usd','site_qa_browser_collector_pr','follow_existing_six_p0_first'],'policy');
 check(p.max_derivative_width_px===960&&p.no_upscale===true&&p.preserve_ai_reconstruction_label===true&&p.no_new_archive_photo_substitution===true&&p.wp_production_write===false&&p.media_download_or_rehost_approval===false&&p.release_or_merge===false&&p.subscription_spend_usd===0&&p.site_qa_browser_collector_pr===154&&p.follow_existing_six_p0_first===true,'release and ownership safeguards');
 check(Array.isArray(a.items)&&a.items.length===5,'exactly five originals');
 let total=0;
 for(let i=0;i<5;i++){
  const r=a.items[i],[mid,pid,file,bytes]=FROZEN[i],url='https://finalvestige.com/wp-content/uploads/2026/08/'+file;
  fields(r,['media_id','post_id','post_title','post_url','post_modified','media_original_url','post_img_src','post_img_alt','post_img_width_attr_px','post_img_height_attr_px','post_figcaption','media_description','source_kind','native_width_px','native_height_px','original_stored_bytes','wordpress_derivative_count','conditional_derivative','verification','release'],'row '+i);
  check(r.media_id===mid&&r.post_id===pid&&r.media_original_url===url&&r.post_img_src===url&&r.original_stored_bytes===bytes,'exact media ID URL size post '+i);
  check(typeof r.post_title==='string'&&r.post_title.length>8&&r.post_url.startsWith('https://finalvestige.com/2026/08/16/')&&/^2026-10-29T/.test(r.post_modified),'post metadata '+i);
  check(r.post_img_width_attr_px===1024&&r.post_img_height_attr_px===576&&r.native_width_px===1672&&r.native_height_px===941&&r.wordpress_derivative_count===0,'authored/native/WordPress geometry '+i);
  check(r.source_kind==='AI_ASSISTED_RECONSTRUCTION_NOT_DOCUMENTARY_PHOTOGRAPH'&&typeof r.post_img_alt==='string'&&r.post_img_alt.length>20&&r.post_figcaption.startsWith('AI-assisted historical reconstruction')&&r.media_description.includes('Historical reconstruction, not a documentary photograph.'),'non-documentary label and alt '+i);
  const d=r.conditional_derivative,v=r.verification;
  fields(d,['width_px','height_px','format_candidates','production_ready','rights_reviewed','visual_scene_parity_reviewed','quality_reviewed','css_width_at_1x_max_px','css_width_at_2x_max_px','css_width_at_3x_max_px','actual_rendered_css_width_px','actual_device_pixel_ratio','encoded_derivative_bytes','visitor_encoded_transfer_bytes'],'derivative '+i);
  check(d.width_px===960&&d.height_px===Math.round(r.native_height_px*960/r.native_width_px)&&d.width_px<=r.native_width_px,'no upscale 960x540 '+i);
  check(JSON.stringify(d.format_candidates)==='["webp","avif"]'&&d.production_ready===false&&d.rights_reviewed===false&&d.visual_scene_parity_reviewed===false&&d.quality_reviewed===false,'rights/quality HOLD '+i);
  check(d.css_width_at_1x_max_px===960&&d.css_width_at_2x_max_px===480&&d.css_width_at_3x_max_px===320&&d.actual_rendered_css_width_px===null&&d.actual_device_pixel_ratio===null,'CSS/DPR unknown '+i);
  check(d.encoded_derivative_bytes===null&&d.visitor_encoded_transfer_bytes===null,'not benchmarked '+i);
  fields(v,['method','origin_http_status','guest_browser_status','web_retriever_result','binary_received','exact_source_hash'],'verification '+i);
  check(v.method==='AUTHENTICATED_WP_EDIT_SOURCE_AND_MEDIA_DETAILS'&&v.origin_http_status===null&&v.guest_browser_status===null&&v.web_retriever_result==='TOOL_IMAGE_NOT_ACCESSIBLE_NOT_HTTP_PROOF'&&v.binary_received===false&&v.exact_source_hash===null&&r.release==='HOLD','do not invent HTTP or approvals '+i);
  total+=bytes;
 }
 check(total===c.original_stored_bytes,'count and bytes');
 return {ok:true,rows:5,stored_original_bytes:total,geometry:'960x540',wire_savings_measured:false,disposition:'HOLD'};
}
module.exports={validate};
if(require.main===module){
 try{const fs=require('node:fs'),path=require('node:path');const a=JSON.parse(fs.readFileSync(path.join(__dirname,'five_reconstruction_p1_density_preflight_20261114.json'),'utf8'));console.log(JSON.stringify(validate(a)));}
 catch(e){console.error(e.message);process.exitCode=1;}
}
