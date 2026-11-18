'use strict';
// Offline integrity gate. No web calls, CMS modifications or image downloads.
const fs=require('node:fs');const path=require('node:path');const crypto=require('node:crypto');
const validate=function validate(a){
 const need=(b,msg)=>{if(!b)throw Error("HOLD "+msg)};
 need(a&&a.schema==="fv-media-qa154-286to288-v1","schema");
 need(a.siteqa_snapshot?.blob==="76aa63ffaa299a6e6878edc1b66e637fa6f058ab","old source");
 need(a.siteqa_snapshot.posts===61&&a.siteqa_snapshot.slots===355&&a.siteqa_snapshot.offsite===286,"old counts");
 need(a.media_snapshot?.cohort_posts===61&&a.media_snapshot.cohort_slots===355&&a.media_snapshot.cohort_offsite===288,"cohort counts");
 need(a.media_snapshot.all_posts===66&&a.media_snapshot.all_slots===361&&a.media_snapshot.all_offsite===294,"current counts");
 const pins=["698b613c41e792b2e0100547a07f4b519c0a908a","1c8cd5d1fd015705c0937d68471fb54546ed2f67","32210de4d0f46ae2547d604d9f1d02769e98bd32","0d5bf91705d7b9956ac7097ebb896c9b142afc51","c0d54c30769b0276a143c2f77b897202d818105f","38718a55ce8fb52eb09cf04765c444a9df1255c9","8cdd86e25bbc6aff1654eeff3fc65f3f42b1e4af","d2c1716c99ff9886e6dac60c6a42926c801be7f4","0248e5d62e589dd6cfc0ec543b5c22a7c14128ea"];
 need(Array.isArray(a.media_snapshot.source_slices)&&a.media_snapshot.source_slices.length===9,"slices");
 pins.forEach((sha,i)=>need(a.media_snapshot.source_slices[i].blob===sha&&a.media_snapshot.source_slices[i].path===`qa/media-recovery/live_66_view_slice_${i+1}_20261117.json`,"pin "+i));
 need(Array.isArray(a.changed_post_counts)&&a.changed_post_counts.length===2,"changed posts");
 const ids=a.changed_post_counts.map(p=>p.id).sort((x,y)=>x-y);need(ids.join(",")==="285,291","affected IDs");
 for(const p of a.changed_post_counts){
  need(p.modified>"2026-10-30"&&p.old_offsite===5&&p.new_offsite===6&&p.image_slots===6&&p.delta===1,"changed post count/revision");
  need(/^https:\/\/finalvestige\.com\//.test(p.post_url)&&Array.isArray(p.current_images)&&p.current_images.length===6,"post/source identity");
  const keys=new Set();
  for(const im of p.current_images){
   need(typeof im.slot==="string"&&im.slot.startsWith(p.id+":")&&!keys.has(im.slot),"unique image slot");keys.add(im.slot);
   need(typeof im.published_url==="string"&&im.published_url.startsWith("https://")&&typeof im.origin_url==="string"&&im.origin_url.startsWith("https://"),"exact URLs");
   need(["third_party_direct","third_party_jetpack"].includes(im.route)&&im.guest_status===null&&im.guest_decode===null&&im.guest_bytes===null,"classification/visitor unknown");
   need(im.rights==="HOLD"&&im.replacement_approved===false&&im.max_width===960&&im.no_upscale===true,"rights/geometry HOLD");
  }
  for(let i=0;i<6;i++)need(keys.has(`${p.id}:${i}`),"slot coverage");
 }
 need(a.reported_42_broken_guest_confirmed===null&&a.claimed_76_percent_wire_savings_verified===false&&a.visitor_bytes===null&&a.rights_rehosting_authorized===false&&a.wordpress_writes===0,"no invented success/production action");
 return {passed:true,affected_post_ids:ids,third_party_count_delta:2,exact_current_urls:12};
};
function blobSha(raw){const b=Buffer.from(raw,'utf8');return crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex');}
function verifySourceBlobs(a,root){const pairs=[[a.siteqa_snapshot.path,a.siteqa_snapshot.blob],...a.media_snapshot.source_slices.map(x=>[x.path,x.blob])];for(const [p,sha] of pairs){const f=fs.readFileSync(path.join(root,p),'utf8');if(blobSha(f)!==sha)throw Error('HOLD source blob '+p);}}
module.exports={validate,blobSha,verifySourceBlobs};
if(require.main===module){try{const file=process.argv[2]||path.join(__dirname,'qa154_286to288_delta_20261117_2227.json');const a=JSON.parse(fs.readFileSync(file,'utf8'));const r=validate(a);if(process.argv[3])verifySourceBlobs(a,process.argv[3]);console.log(JSON.stringify(r,null,2));}catch(e){console.error(e.message);process.exitCode=1;}}
