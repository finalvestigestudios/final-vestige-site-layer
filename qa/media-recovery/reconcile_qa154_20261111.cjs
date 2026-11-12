'use strict';
// Source-only audit. No network, browser or WordPress requests.
function census(csv){
 const lines=String(csv).trim().split(/\r?\n/);
 if(lines.shift()!=='post_id,stored_img_src_count,offsite_src_count')throw Error('header');
 const seen=new Set();
 return lines.map(line=>{
  const a=line.split(',');
  if(a.length!==3||a.some(x=>!/^\d+$/.test(x)))throw Error('row');
  const [id,total,offsite]=a.map(Number);
  if(seen.has(id)||offsite>total)throw Error('duplicate_or_count');
  seen.add(id);return {id,total,offsite};
 });
}
function proxyOrigin(url){
 const m=String(url).match(/^https?:\/\/i[012]\.wp\.com\/([^/?#]+)/i);
 return m&&/^[a-z0-9.-]+\.[a-z]{2,}$/i.test(m[1])?m[1].toLowerCase():null;
}
function reconcile(csv,register){
 const a=census(csv), rows=register?.rows;
 if(a.length!==61||a.reduce((n,x)=>n+x.total,0)!==355||a.reduce((n,x)=>n+x.offsite,0)!==286)throw Error('qa_cohort');
 if(!Array.isArray(rows)||rows.length!==288||register.counts?.offsite_origin_slots!==288)throw Error('register_cohort');
 const seen=new Set(),posts=new Map();
 for(const r of rows){
  if(!r||!/^\d+:\d+$/.test(r.slot)||seen.has(r.slot)||Number(r.slot.split(':')[0])!==r.post_id||!/^https?:\/\//.test(r.stored_url))throw Error('slot_or_url');
  seen.add(r.slot);posts.set(r.post_id,(posts.get(r.post_id)||0)+1);
 }
 if([...posts.keys()].some(id=>!a.some(x=>x.id===id)))throw Error('unknown_post');
 const diffs=a.filter(x=>(posts.get(x.id)||0)!==x.offsite)
  .map(x=>({post_id:x.id,qa_offsite:x.offsite,origin_offsite:posts.get(x.id)||0,delta:(posts.get(x.id)||0)-x.offsite}))
  .sort((x,y)=>x.post_id-y.post_id);
 if(diffs.length!==2||diffs[0].post_id!==285||diffs[0].delta!==1||diffs[1].post_id!==291||diffs[1].delta!==1)throw Error('unexpected_discrepancy');
 const candidates=['285:1','291:0'].map(slot=>{
  const x=rows.find(x=>x.slot===slot),origin=proxyOrigin(x.stored_url);
  if(!origin||x.origin_host!==origin||x.delivery_host!=='i0.wp.com'||x.kind!=='external'||
     x.visitor_http!==null||x.visitor_broken!==null||x.visitor_wire_bytes!==null||
     x.release?.mirror!==false||x.release?.cache!==false||x.release?.wordpress_upload!==false)throw Error('proxy_rights_or_status:'+slot);
  return {slot,stored_url:x.stored_url,delivery_host:x.delivery_host,third_party_origin:origin,guest_http:null,guest_broken:null};
 });
 return {qa_posts:61,qa_inline:355,qa_offsite:286,origin_offsite:288,delta:2,post_differences:diffs,candidates,
  exclusion_cause_proven:false,guest_failures_confirmed:false};
}
if(typeof require!=='undefined'&&require.main===module){
 const fs=require('node:fs');if(process.argv.length!==4)throw Error('usage: node reconcile_qa154_20261111.cjs census.csv origin.json');
 console.log(JSON.stringify(reconcile(fs.readFileSync(process.argv[2],'utf8'),JSON.parse(fs.readFileSync(process.argv[3],'utf8'))),null,2));
}
module.exports={census,proxyOrigin,reconcile};
