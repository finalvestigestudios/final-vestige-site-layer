'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const crypto=require('node:crypto');
const {blobSha,loadPinned,inventory,sourceMatches,assess,PINNED}=require('./slot_parity_61_20261117.cjs');
const batches=[52,59,49,56,54,49,31,5], groupSizes=[8,8,8,8,8,8,8,5];
function fixture(){
 let id=1000,num=0;
 return batches.map((count,idx)=>{
   const n=groupSizes[idx],part={batch:idx+1,post_count:n,image_count:count,posts:[],images:[]};
   for(let j=0;j<n;j++){
     const k=Math.floor(count/n)+(j<count%n?1:0),p={id:id++,url:`https://finalvestige.com/test-${id}/`,modified:'2026-10-30T10:00:00',images:k};
     part.posts.push(p);
     for(let s=0;s<k;s++){
       const isExternal=num++<288,source_url=`https://${isExternal?'source.example.test':'finalvestige.com'}/images/${p.id}-${s}.jpg`;
       part.images.push({key:`${p.id}:${s}`,post_id:p.id,slot:s,source_url,source_kind:isExternal?'external':'first_party',post_url:p.url,modified:p.modified,broken_in_browser:null,actual_http_status:null,allowed_to_localize:false,target_max_width_px:960});
     }
   }return part;
 });
}
const sha=crypto.createHash('sha256').update('fixture').digest('hex');
function page(p,bytes){return {post_id:p.id,url:p.url,revision:p.modified,screenshot_sha256:sha,screenshot_reviewed:true,scrolled_to_end:true,lazy_images_settled:true,network_complete:true,slots:p.rows.map((r,i)=>({key:r.key,authored_url:r.source_url,current_src:r.source_url,request_url:r.source_url,request_id:`req-${r.key}`,http_status:200,mime:'image/jpeg',decoded:true,natural_width:640,natural_height:480,wire_bytes:bytes,from_cache:false,from_service_worker:false,from_prefetch:false}))};}
function capture(inv,ids=null,before=3000,after=600){const posts=[...inv.posts.values()].filter(p=>!ids||ids.includes(p.id));return {schema:'fv-siteqa-image-slot-parity-v1',environment:{collector:'Site QA #154',browser:'Chromium',session:'logged_out',cache_disabled:true,service_workers_bypassed:true,viewport_width:390,viewport_height:844,dpr:2},before:posts.map(p=>page(p,before)),after:posts.map(p=>page(p,after))};}
const clone=x=>structuredClone(x);
function bad(desc,mutate){test(desc,()=>{const parts=fixture(),inv=inventory(parts),c=capture(inv,[[...inv.posts.keys()][0]]);mutate(c,parts);assert.throws(()=>assess(parts,c))});}
test('frozen source blob SHA matches Git object format',()=>assert.equal(blobSha('hello\n'),'ce013625030ba8dba906f756967f9e9ca394464a'));
test('eight immutable Git blob pins are 40 hex chars',()=>assert.ok(PINNED.length===8&&PINNED.every(x=>/^[a-f0-9]{40}$/.test(x))));
test('reject missing source files before ever assessing capture',()=>assert.throws(()=>loadPinned([]),/eight pinned/));
test('valid synthetic 61 post/355 slot/288 offsite source inventory',()=>{const a=inventory(fixture());assert.equal(a.posts.size,61);assert.equal(a.slots,355);assert.equal(a.offsite,288)});
test('without guest evidence, never invent missing images or sitewide savings',()=>{const r=assess(fixture());assert.equal(r.status,'NO_GUEST_CAPTURE');assert.equal(r.reduction_percent,null);assert.equal(r.visitor_broken_images_confirmed,null);assert.equal(r.sitewide_76_percent_verified,false)});
test('valid synthetic subset reports only measured subset, never 76% sitewide',()=>{const f=fixture(),a=inventory(f),r=assess(f,capture(a,[[...a.posts.keys()][0]],3000,500));assert.equal(r.status,'MEASURED_SUBSET_NOT_SITEWIDE');assert.equal(r.reduction_percent,83.33);assert.equal(r.sitewide_76_percent_verified,false)});
test('synthetic complete 355-slot pair is still self reported, not certified',()=>{const f=fixture(),a=inventory(f),r=assess(f,capture(a));assert.equal(r.status,'ALL_355_SELF_REPORTED_REVIEW_REQUIRED');assert.equal(r.paired_slots,355);assert.equal(r.reduction_percent,80);assert.equal(r.sitewide_76_percent_verified,false)});
test('legitimate Jetpack resized source path retained',()=>assert.equal(sourceMatches('https://i2.wp.com/source.example.test/images/test.jpg?w=960&ssl=1','https://source.example.test/images/test.jpg'),true));
test('unrecognized Jetpack source domain rejected',()=>assert.equal(sourceMatches('https://i0.wp.com/evil.example/photo.jpg?ssl=1','https://source.example.test/photo.jpg'),false));
test('unrecognized Jetpack query operation rejected',()=>assert.equal(sourceMatches('https://i0.wp.com/source.example.test/a.jpg?redirect=evil','https://source.example.test/a.jpg'),false));
test('frozen inventory cannot claim a previously observed HTTP success',()=>{const f=fixture();f[0].images[0].actual_http_status=200;assert.throws(()=>inventory(f),/unsupported image/)});
test('frozen inventory cannot silently drop an authored image',()=>{const f=fixture();f[0].images.pop();f[0].image_count--;assert.throws(()=>inventory(f))});
test('frozen inventory cannot silently mislabel a third party source',()=>{const f=fixture();f[0].images[0].source_kind='first_party';assert.throws(()=>inventory(f),/snapshot drift/)});
bad('reject dropped after image even if review flag says true',c=>c.after[0].slots.pop());
bad('reject 404 original still presented as complete',c=>c.before[0].slots[0].http_status=404);
bad('reject HTTP 200 image that does not decode',c=>c.after[0].slots[0].decoded=false);
bad('reject HTML masquerading as an image',c=>c.after[0].slots[0].mime='text/html');
bad('reject a changed source URL under same image key',c=>c.after[0].slots[0].authored_url='https://different.example/file.jpg');
bad('reject valid image URL from unrelated host with forged authored URL',c=>{c.after[0].slots[0].current_src='https://unrelated.example/img.jpg';c.after[0].slots[0].request_url=c.after[0].slots[0].current_src;});
bad('reject missing screenshot integrity fingerprint',c=>c.before[0].screenshot_sha256=null);
bad('reject screenshot not actually reviewed',c=>c.after[0].screenshot_reviewed=false);
bad('reject stale article revision after optimization',c=>c.after[0].revision='2026-11-17T11:00:00');
bad('reject cache-labelled image bytes',c=>c.before[0].slots[0].from_cache=true);
bad('reject unknown natural dimensions',c=>c.after[0].slots[0].natural_width=0);
bad('reject duplicate image request ID reused across slots',c=>c.after[0].slots[1].request_id=c.after[0].slots[0].request_id);
bad('reject duplicate slot key with displaced image',c=>c.after[0].slots[1].key=c.after[0].slots[0].key);
bad('reject negative CDP received bytes',c=>c.before[0].slots[0].wire_bytes=-1);
bad('reject untracked service worker image delivery',c=>c.after[0].slots[0].from_service_worker=true);
bad('reject incomplete lazy-image settling',c=>c.after[0].lazy_images_settled=false);
bad('reject fabricated Site QA collector label',c=>c.environment.collector='non-browser');
bad('reject missing paired after page',c=>c.after=[]);
bad('reject corrupted source post URL',(_,f)=>f[0].images[0].post_url='https://elsewhere.test/');


function duplicateSourceCapture(){
 const parts=fixture();
 // This models the two identical published image URLs on Teton 291:2/291:5,
 // without conflating two independently fetched URLs.
 const p=parts[0].posts[0];
 parts[0].images[1].source_url=parts[0].images[0].source_url;
 const inv=inventory(parts);
 const c=capture(inv,[p.id],3000,600);
 for(const phase of ['before','after']) {
   const [a,b]=c[phase][0].slots;
   b.request_id=a.request_id;
 }
 return {parts,c,slotCount:p.images};
}
test('one cold shared GET can display two DOM image slots and counts wire bytes once',()=>{
 const {parts,c,slotCount}=duplicateSourceCapture();
 const out=assess(parts,c);
 assert.equal(out.paired_slots,slotCount);
 assert.equal(out.before_image_bytes,(slotCount-1)*3000);
 assert.equal(out.after_image_bytes,(slotCount-1)*600);
 assert.equal(out.reduction_percent,80);
 assert.equal(out.sitewide_76_percent_verified,false);
});
test('same currentSrc with two real distinct network GETs charges both transfers',()=>{
 const {parts,c,slotCount}=duplicateSourceCapture();
 for(const phase of ['before','after']) c[phase][0].slots[1].request_id='separate-get';
 const out=assess(parts,c);
 assert.equal(out.before_image_bytes,slotCount*3000);
 assert.equal(out.after_image_bytes,slotCount*600);
});
test('reject fake shared GET when transferred byte counts disagree',()=>{
 const {parts,c}=duplicateSourceCapture();
 c.after[0].slots[1].wire_bytes=0;
 assert.throws(()=>assess(parts,c),/Conflicting shared network request/);
});
test('reject fake shared GET when MIME, dimensions or actual URL disagree',()=>{
 for(const [field,value] of [['mime','image/webp'],['natural_width',123],['current_src','https://different.example/img.jpg']]) {
  const {parts,c}=duplicateSourceCapture();
  c.after[0].slots[1][field]=value;
  assert.throws(()=>assess(parts,c));
 }
});
