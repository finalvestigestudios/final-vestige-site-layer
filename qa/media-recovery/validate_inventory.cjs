'use strict';
/** Offline, read-only validation of 61-post site media audit. No network/WordPress writes. */
const fs=require('node:fs'),path=require('node:path');
function validateSnapshot(s){
 const errors=[],check=(v,m)=>{if(!v)errors.push(m)};
 const keys=new Set(),posts=new Set(),counts={},hosts={};let n=0,dims=0;
 check(s.parts.length===8,"parts");
 for(let i=0;i<s.parts.length;i++){
  const b=s.parts[i];check(b.batch===i+1,`batch ${i}`);check(b.post_count===b.posts.length,`post size ${i}`);check(b.image_count===b.images.length,`image size ${i}`);
  for(const p of b.posts){check(!posts.has(p.id),`duplicate post ${p.id}`);posts.add(p.id)}
 }
 for(const b of s.parts)for(const im of b.images){
  n++;check(!keys.has(im.key),`duplicate image ${im.key}`);keys.add(im.key);
  check(im.key===`${im.post_id}:${im.slot}`,`key mismatch ${im.key}`);
  check(im.broken_in_browser===null&&im.actual_http_status===null,`invented browser status ${im.key}`);
  check(im.allowed_to_localize===false&&im.target_max_width_px===960,`unsafe localization ${im.key}`);
  const match=String(im.source_url).match(/^https?:\/\/([^/?#]+)/i);
  check(!!match&&match[1].toLowerCase()===im.source_host.toLowerCase(),`invalid origin URL ${im.key}`);
  counts[im.source_kind]=(counts[im.source_kind]||0)+1;hosts[im.source_host]=(hosts[im.source_host]||0)+1;
  if(!im.width_px||!im.height_px)dims++;
 }
 check(posts.size===s.summary.post_count&&n===s.summary.inline_img_count,`total mismatch ${posts.size},${n}`);
 for(const [kind,count]of Object.entries(s.summary.origin_counts))check((counts[kind]||0)===count,`kind mismatch ${kind}`);
 check((counts.wikimedia_redirect||0)+(counts.external||0)===s.summary.raw_external_ref_count,`external counts`);
 check(dims===s.summary.missing_explicit_width_or_height,"dimension count");
 const targetHost=Object.fromEntries(s.summary.origin_host_counts.map(x=>[x.host,x.count]));
 check(Object.keys(targetHost).length===Object.keys(hosts).length&&Object.keys(hosts).every(k=>hosts[k]===targetHost[k]),"origin hosts");
 check(s.summary.browser_verified_broken_images===null&&s.summary.founder_reported_42_broken_images==="unverified browser status","42-browser unsupported");
 check(s.summary.reported_76_percent_weight_reduction==="not independently measured"&&s.summary.original_bytes_not_actual_page_weight===true,"76-percent unsupported");
 for(const c of s.sources){check(keys.has(c.image_key)&&c.wp_upload_authorized===false&&c.post_change_authorized===false&&c.output_max_width_px===960&&!!c.rights_review,`candidate gate ${c.image_key}`)}
 for(const v of s.viewer){check(keys.has(v.image_key)&&v.browser_http_status===null&&v.verified_broken_in_browser===null,`viewer gate ${v.image_key}`)}
 check(s.oversize.length===s.summary.original_media_over_1_5MiB,`oversize count`);
 for(const o of s.oversize){check(o.original_bytes>1.5*1024*1024&&o.browser_transfer_bytes===null&&o.approved_for_recompression===false,`oversize gate ${o.media_id}`)}
 return {ok:errors.length===0,errors,metrics:{published_posts:posts.size,stored_images:n,offsite:s.summary.raw_external_ref_count,origins:counts,hosts:Object.keys(hosts).length,candidate_records:s.sources.length,viewer_spotchecks:s.viewer.length,oversize_originals:s.oversize.length,missing_dimensions:dims}};
}
function loadSnapshot(root=__dirname){const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));return{summary:read('summary_20261030.json'),parts:Array.from({length:8},(_,i)=>read('parts/'+String(i+1).padStart(2,'0')+'.json')),sources:read('source_record_candidates_20261030.json'),viewer:read('viewer_spotchecks_20261030.json'),oversize:read('oversize_originals_20261030.json')}}
if(require.main===module){try{const result=validateSnapshot(loadSnapshot());console.log(JSON.stringify(result,null,2));if(!result.ok)process.exitCode=1}catch(err){console.error('MEDIA_QA_DATA_ERROR '+err.message);process.exitCode=2}}
module.exports={validateSnapshot,loadSnapshot};
