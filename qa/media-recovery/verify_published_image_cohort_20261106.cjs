'use strict';
// 2026-11-06 offline WordPress-published-cohort image benchmark gate.
// Read-only. No browser collection, asset copying, cache, or WordPress writes.
const manifest=require('./published_cohort_manifest_20261106.json');
const {evaluate}=require('./measure_cold_wire_pairs_20261106.cjs');
function validateManifest(m){
 const e=[],ck=(yes,s)=>{if(!yes)e.push(s);};
 if(!m||typeof m!=='object')return {ok:false,errors:['manifest absent'],byURL:new Map()};
 ck(m.schema==='fv-wordpress-published-post-manifest-v1','schema');
 ck(m.site==='https://finalvestige.com'&&m.captured_utc==='2026-11-06','site/date');
 ck(m.current_content_recensus_complete===true&&m.fresh_recensus_progress===66,'fresh 66-post recensus required');
 const rows=m.articles;if(!Array.isArray(rows)||rows.length!==66)return {ok:false,errors:['expected exactly 66 articles',...e],byURL:new Map()};
 const byURL=new Map(),ids=[],legacy=[];let total=0,legacyTotal=0,externals=0;
 for(const [i,r] of rows.entries()){
  if(!r||typeof r!=='object'){e.push('missing article '+i);continue;}
  ck(Number.isSafeInteger(r.id)&&r.id>0,'post ID '+i);
  ck(typeof r.url==='string'&&/^https:\/\/finalvestige\.com\/20\d{2}\/\d{2}\/\d{2}\/[a-z0-9-]+\/$/.test(r.url),'canonical URL '+i);
  ck(typeof r.slug==='string'&&r.url?.endsWith('/'+r.slug+'/'),'slug/URL '+i);
  ck(typeof r.modified_wp==='string'&&!Number.isNaN(Date.parse(r.modified_wp))&&r.fresh_modified_wp===r.modified_wp,'WP version '+i);
  ck(Number.isSafeInteger(r.fresh_inline_img_count)&&r.fresh_inline_img_count>=0&&r.fresh_inline_img_count<=100,'image count '+i);
  ck(Number.isSafeInteger(r.fresh_external_img_count)&&r.fresh_external_img_count>=0&&r.fresh_external_img_count<=r.fresh_inline_img_count,'external count '+i);
  ck(r.inline_img_count===r.fresh_inline_img_count,'old/new count drift '+i);
  ck(!byURL.has(r.url)&&!ids.includes(r.id),'duplicate article '+i);
  byURL.set(r.url,r);ids.push(r.id);
  if(Number.isInteger(r.fresh_inline_img_count)){total+=r.fresh_inline_img_count;if(r.id<1900){legacy.push(r.id);legacyTotal+=r.fresh_inline_img_count;}}
  if(Number.isInteger(r.fresh_external_img_count))externals+=r.fresh_external_img_count;
 }
 ck(ids.length===66&&ids.every((x,i)=>i===0||ids[i-1]<x),'sorted unique IDs');
 ck(legacy.length===61,'legacy 61');
 ck(JSON.stringify(ids)===JSON.stringify(m.current_66_post_ids),'current cohort IDs');
 ck(JSON.stringify(legacy)===JSON.stringify(m.legacy_61_post_ids),'legacy cohort IDs');
 ck(total===361&&m.fresh_total_inline_images===361,'fresh 361 inline images');
 ck(legacyTotal===355&&m.fresh_legacy_inline_images===355,'fresh legacy 355 images');
 ck(externals===294&&m.fresh_total_external_images===294,'fresh 294 external images');
 ck(m.wordpress_writes===0&&m.browser_verified===false,'evidence must be read-only');
 return {ok:e.length===0,errors:e,byURL};
}
function verify(input,m=manifest){
 const guard=validateManifest(m),errors=[...guard.errors];
 const reject=()=>({ok:false,errors,measured:null,sitewide_claim_allowed:false,claim_76_percent_supported:false});
 if(!guard.ok)return reject();
 if(!input||typeof input!=='object'){errors.push('browser evidence absent');return reject();}
 const n=input.published_cohort_size;
 if(n!==61&&n!==66){errors.push('cohort must be 61 or 66');return reject();}
 const allowed=new Set(m.articles.filter(r=>n===66||r.id<1900).map(r=>r.url));
 const pages=input.expected_page_urls,pairs=input.pairs;
 if(!Array.isArray(pages)||!pages.length||!Array.isArray(pairs)){errors.push('pages and pairs required');return reject();}
 if(pages.length>n||new Set(pages).size!==pages.length)errors.push('duplicate/overlong page list');
 if(pages.some(x=>!allowed.has(x)))errors.push('nonmember published page');
 if(pairs.length!==pages.length)errors.push('pair count mismatch');
 const profiles=new Set(),sources=new Set(),seen=new Set();
 for(const [i,p] of pairs.entries()){
  if(!p||typeof p!=='object'){errors.push('bad pair '+i);continue;}
  const a=guard.byURL.get(p.page_url);
  if(!a||!allowed.has(p.page_url)){errors.push('pair nonmember '+i);continue;}
  if(seen.has(p.page_url))errors.push('duplicate pair '+a.id);
  seen.add(p.page_url);
  if(!pages.includes(p.page_url))errors.push('pair outside expected URLs '+a.id);
  for(const side of ['before','after']){
   const run=p[side],tag=a.id+' '+side;
   if(!run||typeof run!=='object'||!Array.isArray(run.dom_images)||!Array.isArray(run.image_requests)){errors.push(tag+' missing DOM/network arrays');continue;}
   const count=a.fresh_inline_img_count,dom=run.dom_images,req=run.image_requests,slots=new Set(),urls=new Set();
   if(dom.length!==count)errors.push(tag+' missing published inline image count (expected '+count+', got '+dom.length+')');
   for(const d of dom){
    if(!d||typeof d!=='object'||typeof d.slot!=='string'){errors.push(tag+' malformed DOM image');continue;}
    const v=d.slot.match(/^(\d+):(\d+)$/);
    if(!v||Number(v[1])!==a.id||Number(v[2])>=count){errors.push(tag+' wrong post/index slot '+d.slot);continue;}
    if(slots.has(d.slot))errors.push(tag+' duplicate image slot '+d.slot);
    slots.add(d.slot);urls.add(d.current_src);
   }
   for(let j=0;j<count;j++)if(!slots.has(a.id+':'+j))errors.push(tag+' missing image slot '+j);
   for(const r of req){if(!r||typeof r!=='object'||!urls.has(r.url))errors.push(tag+' orphan network request');else sources.add(r.wire_source);}
   if(count===0&&(req.length!==0||run.zero_image_page_verified!==true))errors.push(tag+' empty article needs zero-image attestation');
   profiles.add(JSON.stringify([run.browser,run.browser_version,run.device_profile,run.viewport_width,run.viewport_height,run.dpr,run.network_profile]));
  }
 }
 if(sources.size>1)errors.push('mixed wire sources across cohort');
 if(profiles.size>1)errors.push('mixed browser/network profiles across cohort');
 if(seen.size!==pages.length)errors.push('unobserved/duplicate pages');
 if(errors.length)return reject();
 const measured=evaluate(input);
 if(!measured.ok)return {...measured,sitewide_claim_allowed:false,claim_76_percent_supported:false};
 const complete=pages.length===n&&pages.every(x=>allowed.has(x)),sitewide=n===66&&complete;
 return {...measured,manifest_scope:'frozen 2026-11-06 authenticated WordPress published-post census; refresh before claiming a later current site-wide result',
  stored_inline_slots_verified:pairs.reduce((s,p)=>s+p.before.dom_images.length,0),
  complete_cohort:complete,historical_61_cohort_only:n===61,
  sitewide_claim_allowed:sitewide,
  claim_76_percent_supported:sitewide&&measured.measured.saving_percent>=76,
  reason:sitewide?'all 66 published posts in frozen November 6 manifest':complete?'61 historical posts, NOT entire current 66-post site':'sample only; no site-wide claim'};
}
if(typeof module!=='undefined')module.exports={verify,validateManifest};
if(typeof require==='function'&&require.main===module){
 const fs=require('node:fs');
 if(process.argv.length!==3){console.error('Usage: node verify_published_image_cohort_20261106.cjs EVIDENCE.json');process.exit(2);}
 const result=verify(JSON.parse(fs.readFileSync(process.argv[2],'utf8')));
 console.log(JSON.stringify(result,null,2));if(!result.ok)process.exitCode=1;
}
