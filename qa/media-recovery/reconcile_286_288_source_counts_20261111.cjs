'use strict';
// Cross-branch historical source count reconciliation; no network or WordPress writes.
function hold(x){throw Error('HOLD:'+x)}
function parseCsv(t){
 if(typeof t!=='string')hold('csv');
 const lines=t.trim().split(/\r?\n/);
 if(lines.shift()!=='post_id,stored_img_src_count,offsite_src_count')hold('header');
 const m=new Map();
 for(const s of lines){
  if(!/^\d+,\d+,\d+$/.test(s))hold('row');
  const [id,images,offsite]=s.split(',').map(Number);
  if(!id||offsite>images||m.has(id))hold('duplicate_or_invalid');
  m.set(id,{images,offsite});
 }return m;
}
function reconcile(csv,ledger,audit,expected={posts:61,inline:355,qa:286,media:288}){
 const qa=parseCsv(csv);
 if(qa.size!==expected.posts||qa.size<2||!ledger||!Array.isArray(ledger.rows)||ledger.rows.length!==expected.media)hold('cohort');
 if([...qa.values()].reduce((n,r)=>n+r.images,0)!==expected.inline||[...qa.values()].reduce((n,r)=>n+r.offsite,0)!==expected.qa)hold('totals');
 const count=new Map(),used=new Set();
 for(const r of ledger.rows){
  if(typeof r.slot!=='string'||!/^\d+:\d+$/.test(r.slot)||used.has(r.slot))hold('slot');
  if(!qa.has(r.post_id)||+r.slot.split(':')[0]!==r.post_id)hold('article_slot_binding');
  if(typeof r.stored_url!=='string'||!r.stored_url.startsWith('https://'))hold('url');
  if(r.visitor_http!=null||r.visitor_wire_bytes!=null||r.visitor_broken!=null)hold('fabricated_guest');
  used.add(r.slot);count.set(r.post_id,(count.get(r.post_id)||0)+1);
 }
 const d=[...qa].map(([id,r])=>({post_id:id,siteqa:r.offsite,media:count.get(id)||0})).filter(x=>x.siteqa!==x.media).sort((a,b)=>a.post_id-b.post_id);
 if(d.length!==2||d[0].post_id!==285||d[1].post_id!==291||d.some(x=>x.media-x.siteqa!==1))hold('unexpected_deltas');
 if(!audit||!Array.isArray(audit.rows)||audit.rows.length!==2)hold('audit');
 for(const [i,slot] of ['285:1','291:0'].entries()){
  const e=audit.rows.find(x=>x.slot===slot),r=ledger.rows.find(x=>x.slot===slot);
  if(!e||!r||e.post_id!==r.post_id||e.exact_published_src!==r.stored_url||d[i].post_id!==e.post_id||d[i].siteqa!==e.siteqa_offsite||d[i].media!==e.media_offsite)hold('source_identity');
  const m=/^https:\/\/(i[012]\.wp\.com)\/([^/?#]+)\//.exec(e.exact_published_src);
  if(!m||m[1]!==e.transport_host||m[2]!==e.underlying_origin||m[2]==='finalvestige.com')hold('not_external_origin');
  if(e.origin_http_status!=null||e.guest_http_status!=null||e.guest_wire_bytes!=null||e.native_px!==null||e.conditional_960px!==null)hold('invented_measurements');
  if(e.maximum_derivative_width!==960||e.never_upscale!==true||e.rights_cleared!==false||e.rehost_authorized!==false||e.exact_photo_identity_proven!==false)hold('rights_or_visual_gate');
 }
 if(!audit.release||Object.values(audit.release).length!==7||Object.values(audit.release).some(x=>x!==false))hold('unsafe_release');
 return {status:'RECONCILED_HISTORICAL_SOURCE_COUNT_ONLY',posts:qa.size,siteqa_offsite:expected.qa,media_offsite:expected.media,other_posts_equal:qa.size-2,differences:d,guest_http_verified:0};
}
module.exports={parseCsv,reconcile};
if(require.main===module){
 try{const fs=require('node:fs');if(process.argv.length!==5)hold('usage csv ledger audit');
 console.log(JSON.stringify(reconcile(fs.readFileSync(process.argv[2],'utf8'),JSON.parse(fs.readFileSync(process.argv[3],'utf8')),JSON.parse(fs.readFileSync(process.argv[4],'utf8'))),null,2));}
 catch(e){console.error(e.message);process.exitCode=2;}
}
