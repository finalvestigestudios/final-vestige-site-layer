#!/usr/bin/env node
'use strict';
// Offline consumer. Never fetch images, write WordPress, or certify a 76% sitewide improvement.
const fs = require('node:fs');
const crypto = require('node:crypto');
const PINNED = Object.freeze([
  '948bc1b65b42799aa40cfdb810ddf6ffd80886b6',
  '48e1ebf07207e948ba5802e714eb39659d2e1c1d',
  '49183f66f880f7c4dfd363acca906876877f2e5e',
  '6df3251e5a67a971d87a516a1ba4a0cc32f51f96',
  '9b16b828342a9ac338f3e65610fd3d8d508355e9',
  '0f3dfe398a76838049cebba7cb773d5c5a0c8c69',
  '21095161e633aba093b74c0ead9936c9f6186d00',
  '5659ec243c188928be3f89c0f96354b660608ca2'
]);
const isObject = x => x !== null && typeof x === 'object' && !Array.isArray(x);
const integer = (x,min=0) => Number.isSafeInteger(x) && x>=min;
function fail(msg) { throw new Error(msg); }
function validUrl(x) { try {const u = new URL(x);return u.protocol==='https:' && !u.username && !u.password && typeof x==='string';}catch{return false;} }
function sourceMatches(current, authored) {
  if(current===authored)return true;
  try {
    const a=new URL(authored), u=new URL(current);
    if(!/^i[0-3]\.wp\.com$/.test(u.hostname)||u.protocol!=='https:')return false;
    if(decodeURIComponent(u.pathname)!==`/${a.hostname}${decodeURIComponent(a.pathname)}`)return false;
    // Known Jetpack resizing controls; unknown URL transformations are a source-identity HOLD.
    const controls=new Set(['ssl','resize','w','h','fit','crop','quality','strip','zoom']);
    for(const [k,v] of a.searchParams)if(u.searchParams.get(k)!==v)return false;
    return [...u.searchParams.keys()].every(k=>controls.has(k)||a.searchParams.has(k));
  } catch {return false;}
}
function validRedirectChain(start,end,chain) {
  if(start===end)return chain===undefined||(Array.isArray(chain)&&chain.length===0);
  if(!Array.isArray(chain)||chain.length<1||chain.length>6)return false;
  const visited=new Set([start]);let current=start;
  for(const hop of chain) {
    if(!isObject(hop)||!validUrl(hop.from_url)||!validUrl(hop.to_url)||
      hop.from_url!==current||![301,302,303,307,308].includes(hop.http_status)||
      visited.has(hop.to_url))return false;
    visited.add(hop.to_url);current=hop.to_url;
  }
  return current===end;
}
function blobSha(raw) {const b=Buffer.from(raw,'utf8');return crypto.createHash('sha1').update(`blob ${b.length}\0`).update(b).digest('hex');}
function loadPinned(paths) {
  if(!Array.isArray(paths)||paths.length!==8)fail('Exactly eight pinned source files required');
  return paths.map((p,i)=>{
    if(typeof p!=='string'||!/\/0[1-8]\.json$/.test(p)||!p.endsWith(`/${String(i+1).padStart(2,'0')}.json`))fail('Unexpected part path or order');
    const raw=fs.readFileSync(p,'utf8');
    if(blobSha(raw)!==PINNED[i])fail(`Immutable source Git blob mismatch for part ${i+1}`);
    return JSON.parse(raw);
  });
}
function inventory(parts) {
  if(!Array.isArray(parts)||parts.length!==8)fail('Expected eight historical source parts');
  const posts=new Map(), seenKeys=new Set(), seenBatches=new Set();let imageCount=0,offsite=0;
  parts.forEach((part,i)=>{
    if(!isObject(part)||part.batch!==i+1||seenBatches.has(part.batch)||!Array.isArray(part.posts)||!Array.isArray(part.images)||part.post_count!==part.posts.length||part.image_count!==part.images.length)fail('Invalid part counts or batch order');
    seenBatches.add(part.batch);
    for(const p of part.posts) {
      if(!integer(p.id,1)||posts.has(p.id)||!integer(p.images)||!validUrl(p.url)||typeof p.modified!=='string'||!p.modified)fail('Invalid/duplicate post metadata');
      posts.set(p.id,{...p, rows:[]});
    }
    for(const im of part.images) {
      const p=posts.get(im.post_id);
      if(!p||!integer(im.slot)||im.key!==`${im.post_id}:${im.slot}`||seenKeys.has(im.key)||im.post_url!==p.url||im.modified!==p.modified||!validUrl(im.source_url)||im.broken_in_browser!==null||im.actual_http_status!==null||im.allowed_to_localize!==false||im.target_max_width_px!==960)fail('Invalid/unsupported image source assertion');
      const off=['external','wikimedia_redirect'].includes(im.source_kind);
      if(!off && !['first_party','jetpack_proxy'].includes(im.source_kind))fail('Unrecognized source family');
      if(off)offsite++;
      seenKeys.add(im.key);p.rows.push(im);imageCount++;
    }
  });
  if(posts.size!==61||imageCount!==355||offsite!==288)fail('Historical 61/355/288 snapshot drift');
  for(const p of posts.values()){
    if(p.rows.length!==p.images)fail(`Missing authored image slots for post ${p.id}`);
    const slots=new Set(p.rows.map(r=>r.slot));
    for(let i=0;i<p.images;i++)if(!slots.has(i))fail(`Gap in source slots for post ${p.id}`);
  }
  return {posts,slots:imageCount,offsite};
}
function validatePage(p,which,inv) {
  if(!isObject(p)||!integer(p.post_id,1)||!inv.posts.has(p.post_id))fail(`Unknown ${which} post`);
  const original=inv.posts.get(p.post_id);
  if(p.url!==original.url||p.revision!==original.modified)fail(`Source URL/revision drift in ${which} ${p.post_id}`);
  if(!Array.isArray(p.slots)||p.slots.length!==original.images)fail(`Missing image slot(s) in ${which} ${p.post_id}`);
  if(p.scrolled_to_end!==true||p.lazy_images_settled!==true||p.network_complete!==true||p.screenshot_reviewed!==true||!(/^[a-f0-9]{64}$/).test(p.screenshot_sha256||''))fail(`Incomplete visual/page evidence in ${which} ${p.post_id}`);
  const slots=new Map(),reqs=new Map();let bytes=0;
  for(const r of p.slots) {
    if(!isObject(r)||typeof r.key!=='string'||slots.has(r.key))fail(`Duplicate/invalid ${which} image slot`);
    const expected=original.rows.find(x=>x.key===r.key);
    if(!expected||r.authored_url!==expected.source_url)fail(`Unmatched source image identity in ${which} ${r.key}`);
    if(!validUrl(r.current_src)||!validUrl(r.request_url)||!sourceMatches(r.current_src,expected.source_url)||!validRedirectChain(r.current_src,r.request_url,r.redirect_chain)||typeof r.request_id!=='string'||!r.request_id)fail(`Unmatched ${which} network request`);
    if(r.http_status!==200||typeof r.mime!=='string'||!/^image\//i.test(r.mime)||r.decoded!==true||!integer(r.natural_width,1)||!integer(r.natural_height,1)||!integer(r.wire_bytes,1)||r.from_cache!==false||r.from_service_worker!==false||r.from_prefetch!==false)fail(`Broken/missing/cached image in ${which} ${r.key}`);
    // Chromium may serve the same decoded URL to multiple DOM image slots from one
    // network request, even with HTTP cache disabled. Count that request once.
    const previous=reqs.get(r.request_id);
    if(previous) {
      for(const field of ['current_src','request_url','http_status','mime','wire_bytes',
        'natural_width','natural_height','from_cache','from_service_worker','from_prefetch']) {
        if(r[field]!==previous[field])fail(`Conflicting shared network request in ${which} ${r.key}: ${field}`);
      }
    } else {
      reqs.set(r.request_id,r);
      bytes+=r.wire_bytes;
      if(!Number.isSafeInteger(bytes))fail('Unsafe image wire-byte sum');
    }
    if(previous&&JSON.stringify(r.redirect_chain||[])!==JSON.stringify(previous.redirect_chain||[]))fail(`Conflicting shared network request in ${which} ${r.key}: redirect_chain`);
    slots.set(r.key,r);
  }
  return {id:p.post_id,slots,bytes};
}
function assess(parts,capture=null) {
  const inv=inventory(parts);
  const base={schema:'fv-61-slot-parity-report-v1',historical_posts:61,historical_image_slots:355,historical_offsite_authored:288,source_blobs:PINNED,visitor_broken_images_confirmed:null,sitewide_76_percent_verified:false,production_change_authorized:false};
  if(capture===null||capture===undefined)return {...base,status:'NO_GUEST_CAPTURE',paired_posts:0,paired_slots:0,before_image_bytes:null,after_image_bytes:null,reduction_percent:null};
  const e=capture.environment;
  if(!isObject(capture)||capture.schema!=='fv-siteqa-image-slot-parity-v1'||!isObject(e)||e.collector!=='Site QA #154'||e.browser!=='Chromium'||e.session!=='logged_out'||e.cache_disabled!==true||e.service_workers_bypassed!==true||!integer(e.viewport_width,1)||!integer(e.viewport_height,1)||!Number.isFinite(e.dpr)||e.dpr<=0||!Array.isArray(capture.before)||!Array.isArray(capture.after)||capture.before.length!==capture.after.length||capture.before.length===0||capture.before.length>61)fail('Invalid/uncold/unpaired Site QA guest capture');
  const groups=[];
  for(const phase of ['before','after']){
    const found=new Map();
    for(const p of capture[phase]){const v=validatePage(p,phase,inv);if(found.has(v.id))fail(`Duplicate ${phase} post`);found.set(v.id,v);}
    groups.push(found);
  }
  const [before,after]=groups;let beforeBytes=0,afterBytes=0,slots=0;
  for(const [id,b] of before){const a=after.get(id);if(!a)fail(`Missing after post ${id}`);for(const [key] of b.slots)if(!a.slots.has(key))fail(`Lost after image ${key}`);beforeBytes+=b.bytes;afterBytes+=a.bytes;slots+=b.slots.size;}
  if(!Number.isSafeInteger(beforeBytes)||!Number.isSafeInteger(afterBytes)||beforeBytes===0)fail('Unsafe/zero baseline image-byte total');
  const complete=before.size===61&&slots===355;
  return {...base,status:complete?'ALL_355_SELF_REPORTED_REVIEW_REQUIRED':'MEASURED_SUBSET_NOT_SITEWIDE',paired_posts:before.size,paired_slots:slots,before_image_bytes:beforeBytes,after_image_bytes:afterBytes,reduction_percent:Math.round((1-afterBytes/beforeBytes)*10000)/100,sitewide_76_percent_verified:false,caveat:'Collector-supplied screenshot hashes/review flags and identity assertions are NOT independently verified; obtain independent trace and visual review before any sitewide claim or replacement.'};
}
module.exports={PINNED,blobSha,loadPinned,inventory,sourceMatches,validRedirectChain,assess};
if(require.main===module){try{const args=process.argv.slice(2);if(args.length<8||args.length>9)fail('Usage: node slot_parity_61_20261117.cjs parts/01.json ... parts/08.json [SiteQA-slot-capture.json]');const parts=loadPinned(args.slice(0,8));const cap=args[8]?JSON.parse(fs.readFileSync(args[8],'utf8')):null;process.stdout.write(JSON.stringify(assess(parts,cap),null,2)+'\n');}catch(e){console.error('HOLD: '+e.message);process.exitCode=1;}}
