'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const crypto=require('node:crypto');
const {blobSha,loadPinned,inventory,sourceMatches,validRedirectChain,assess,PINNED}=require('./slot_parity_61_20261117.cjs');
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
function page(p,bytes){return {post_id:p.id,url:p.url,revision:p.modified,screenshot_sha256:sha,screenshot_reviewed:true,scrolled_to_end:true,lazy_images_settled:true,network_complete:true,slots:p.rows.map((r,i)=>({key:r.key,authored_url:r.source_url,current_src:r.source_url,request_url:r.source_url,request_id:`req-${r.key}`,http_status:200,mime:'image/jpeg',decoded:true,natural_width:640,natural_height:480,raster_width_px:640,raster_height_px:480,
      raster_probe:'decoded_network_payload',raster_sha256:sha,wire_bytes:bytes,from_cache:false,from_service_worker:false,from_prefetch:false}))};}
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
 c.after[0].slots[1].wire_bytes=1;
 assert.throws(()=>assess(parts,c),/Conflicting shared network request/);
});
test('reject fake shared GET when MIME, dimensions or actual URL disagree',()=>{
 for(const [field,value] of [['mime','image/webp'],['natural_width',123],['current_src','https://different.example/img.jpg']]) {
  const {parts,c}=duplicateSourceCapture();
  c.after[0].slots[1][field]=value;
  assert.throws(()=>assess(parts,c));
 }
});
bad('reject HTTP 204 no-content response masquerading as a decoded image',c=>c.after[0].slots[0].http_status=204);
bad('reject HTTP 206 partial-content without a range-transfer ledger',c=>c.after[0].slots[0].http_status=206);
bad('reject HTTP 201 created response as a cold image GET',c=>c.after[0].slots[0].http_status=201);
bad('reject zero transferred bytes for alleged cold decoded image',c=>c.after[0].slots[0].wire_bytes=0);

test('allow documented HTTP 302 chain with unchanged authored DOM image',()=>{
 const f=fixture(),inv=inventory(f),id=[...inv.posts.keys()][0],c=capture(inv,[id]),s=c.after[0].slots[0];
 s.request_url='https://cdn.example.test/final.jpg';s.redirect_chain=[{from_url:s.current_src,to_url:s.request_url,http_status:302}];
 assert.equal(assess(f,c).status,'MEASURED_SUBSET_NOT_SITEWIDE');
});
test('same image URL with no redirect remains accepted',()=>assert.equal(validRedirectChain('https://a.test/a','https://a.test/a'),true));
test('changed actual response URL requires a chain',()=>assert.equal(validRedirectChain('https://a.test/a','https://b.test/b'),false));
test('reject unrelated hop origin',()=>assert.equal(validRedirectChain('https://a.test/a','https://b.test/b',[{from_url:'https://x.test/x',to_url:'https://b.test/b',http_status:301}]),false));
test('reject redirect to different endpoint than final response',()=>assert.equal(validRedirectChain('https://a.test/a','https://b.test/b',[{from_url:'https://a.test/a',to_url:'https://c.test/c',http_status:302}]),false));
test('reject non-redirect hop status 200',()=>assert.equal(validRedirectChain('https://a.test/a','https://b.test/b',[{from_url:'https://a.test/a',to_url:'https://b.test/b',http_status:200}]),false));
test('reject insecure redirect to HTTP',()=>assert.equal(validRedirectChain('https://a.test/a','http://b.test/b',[{from_url:'https://a.test/a',to_url:'http://b.test/b',http_status:302}]),false));
test('reject seven-hop chain',()=>assert.equal(validRedirectChain('https://a.test/0','https://a.test/7',Array.from({length:7},(_,i)=>({from_url:'https://a.test/'+i,to_url:'https://a.test/'+(i+1),http_status:302}))),false));
test('reject redirect cycle',()=>assert.equal(validRedirectChain('https://a.test/0','https://a.test/2',[{from_url:'https://a.test/0',to_url:'https://a.test/1',http_status:301},{from_url:'https://a.test/1',to_url:'https://a.test/0',http_status:302},{from_url:'https://a.test/0',to_url:'https://a.test/2',http_status:302}]),false));
test('shared request ID with inconsistent redirects fails',()=>{
 const {parts,c}=duplicateSourceCapture();
 for(const s of c.after[0].slots.slice(0,2)){s.request_url='https://cdn.example.test/final.jpg';s.redirect_chain=[{from_url:s.current_src,to_url:s.request_url,http_status:302}];}
 c.after[0].slots[1].redirect_chain[0].http_status=301;
 assert.throws(()=>assess(parts,c),/Conflicting shared network request/);
});


const {preservesPixelGeometry}=require('./slot_parity_61_20261117.cjs');
const geom=(w,h)=>({natural_width:w,natural_height:h,raster_width_px:w,raster_height_px:h});
test('visual parity: 4K photo to <=960px proportional derivative',()=>assert.equal(preservesPixelGeometry(geom(4000,3000),geom(960,720)),true));
test('visual parity: historical portrait 4918x6136 to 769x960',()=>assert.equal(preservesPixelGeometry(geom(4918,6136),geom(769,960)),true));
test('visual parity: preserve small original 600x463 without upscale',()=>assert.equal(preservesPixelGeometry(geom(600,463),geom(600,463)),true));
test('visual parity: wide panorama 4000x400 to 960x96',()=>assert.equal(preservesPixelGeometry(geom(4000,400),geom(960,96)),true));
test('visual parity: reject same-ratio 64x48 placeholder for 1200x900 photograph',()=>assert.equal(preservesPixelGeometry(geom(1200,900),geom(64,48)),false));
test('visual parity: reject invalid or excessive reported dimensions',()=>{assert.equal(preservesPixelGeometry(geom(640,480),geom(0,0)),false);assert.equal(preservesPixelGeometry(geom(640,480),geom(100001,100001)),false);});
bad('integration: decoded 1x1 after image cannot claim high bandwidth reduction',c=>{c.after[0].slots[0].natural_width=1;c.after[0].slots[0].natural_height=1;});
bad('integration: tiny proportional after image cannot claim high savings',c=>{c.after[0].slots[0].natural_width=64;c.after[0].slots[0].natural_height=48;});
bad('integration: aspect-drift after image must hold despite valid status and bytes',c=>{c.after[0].slots[0].natural_width=640;c.after[0].slots[0].natural_height=640;});
bad('integration: small source image may not silently lose half its pixels',c=>{c.before[0].slots[0].natural_width=200;c.before[0].slots[0].natural_height=100;c.after[0].slots[0].natural_width=100;c.after[0].slots[0].natural_height=50;});

test('960px safeguard: 1280px derivative from 4K original must HOLD despite same crop',()=>assert.equal(preservesPixelGeometry(geom(4000,3000),geom(1280,960)),false));
test('960px safeguard: proper 960x720 derivative from 4K original passes',()=>assert.equal(preservesPixelGeometry(geom(4000,3000),geom(960,720)),true));
test('no-upscale safeguard: 600x463 archival preview must not become 900x694',()=>assert.equal(preservesPixelGeometry(geom(600,463),geom(900,694)),false));
test('no-upscale safeguard: original smaller than 960px must not be enlarged to limit',()=>assert.equal(preservesPixelGeometry(geom(200,100),geom(960,480)),false));
test('portrait 960px width with >960px height is valid (width, not longest-edge cap)',()=>assert.equal(preservesPixelGeometry(geom(1500,3000),geom(960,1920)),true));
test('small original preserved exactly needs no unnecessary upscaling',()=>assert.equal(preservesPixelGeometry(geom(200,100),geom(200,100)),true));
bad('integration: optimistic 960x720 upscaled replacement of 640x480 is not savings parity',c=>{c.after[0].slots[0].natural_width=960;c.after[0].slots[0].natural_height=720;});
bad('integration: 4K original reduced only to 1280px fails strict 960px derivative ceiling',c=>{c.before[0].slots[0].natural_width=4000;c.before[0].slots[0].natural_height=3000;c.after[0].slots[0].natural_width=1280;c.after[0].slots[0].natural_height=960;});

test('density-adjusted 960px DOM width must not conceal 1920px encoded file',()=>{
 const a={natural_width:960,natural_height:540,raster_width_px:1920,raster_height_px:1080};
 assert.equal(preservesPixelGeometry(geom(4000,3000),a),false);
});
test('a real 960px file can have density-adjusted naturalWidth 480',()=>{
 const a={natural_width:480,natural_height:360,raster_width_px:960,raster_height_px:720};
 assert.equal(preservesPixelGeometry(geom(4000,3000),a),true);
});
test('normal genuine 960x720 encoded derivative passes',()=>assert.equal(preservesPixelGeometry(geom(4000,3000),geom(960,720)),true));
test('missing binary raster dimensions cannot certify image optimization',()=>assert.equal(preservesPixelGeometry(geom(4000,3000),{natural_width:960,natural_height:720}),false));
test('DOM and binary aspect ratios cannot silently diverge',()=>assert.equal(preservesPixelGeometry(geom(4000,3000),{natural_width:480,natural_height:360,raster_width_px:960,raster_height_px:960}),false));
test('file raster cannot be smaller than natural CSS geometry',()=>assert.equal(preservesPixelGeometry(geom(4000,3000),{natural_width:960,natural_height:720,raster_width_px:480,raster_height_px:360}),false));
bad('integration: encoded raster over 960 HOLD even if DOM naturalWidth is 640',c=>{c.after[0].slots[0].raster_width_px=1280;c.after[0].slots[0].raster_height_px=960;});
bad('integration: DOM-only probe cannot substitute actual decoded response payload',c=>{c.after[0].slots[0].raster_probe='DOM_naturalWidth';});
bad('integration: absent binary response SHA256 cannot certify dimensions',c=>{c.after[0].slots[0].raster_sha256=null;});
bad('integration: same request ID with contradictory raster geometry rejected',c=>{c.after[0].slots[1].request_id=c.after[0].slots[0].request_id;c.after[0].slots[1].raster_width_px=959;});
bad('integration: density correction cannot hide encoded image upscaling',c=>{
 const x=c.before[0].slots[0],y=c.after[0].slots[0];
 x.natural_width=480;x.natural_height=360;x.raster_width_px=480;x.raster_height_px=360;
 y.natural_width=480;y.natural_height=360;y.raster_width_px=960;y.raster_height_px=720;
});
