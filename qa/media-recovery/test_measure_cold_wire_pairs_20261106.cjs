'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const {evaluate}=require('./measure_cold_wire_pairs_20261106.cjs');
function fixture(){
 const url='https://finalvestige.com/2026/08/20/they-buried-the-dead-apart-okeechobee-1928/';
 const img='https://www.floridamemory.com/fpc/prints/pr04493.jpg';
 function capture(bytes){return {guest_browser_verified:true,cache_disabled:true,service_worker_bypassed:true,scrolled_to_bottom:true,all_images_loaded:true,capture_complete:true,browser:'Chrome',browser_version:'131',device_profile:'mobile',viewport_width:390,viewport_height:844,dpr:3,network_profile:'4G',captured_at:'2026-11-06T14:00:00Z',image_requests:[{url:img,status:200,from_cache:false,content_type:'image/jpeg',wire_bytes:bytes,wire_source:'chrome_har_entry_transferSize'}],dom_images:[{slot:'432:0',current_src:img,complete:true,natural_width:600,natural_height:463}]};}
 return {schema:'fv-cold-image-wire-pairs-v1',published_cohort_size:66,expected_page_urls:[url],pairs:[{page_url:url,before:capture(100000),after:capture(24000)}]};
}
test('76% on one page is sample-only and never a site-wide claim',()=>{const r=evaluate(fixture());assert.equal(r.ok,true);assert.equal(r.measured.saving_percent,76);assert.equal(r.sitewide_claim_allowed,false);assert.equal(r.claim_76_percent_supported,false);});
const mutations=[
 ['browser not verified','before.guest_browser_verified',false],
 ['warm cache','before.cache_disabled',false],
 ['service worker','before.service_worker_bypassed',false],
 ['not scrolled','before.scrolled_to_bottom',false],
 ['incomplete capture','before.capture_complete',false],
 ['lazy images missing','after.all_images_loaded',false],
 ['network 404','after.image_requests.0.status',404],
 ['network 304','after.image_requests.0.status',304],
 ['zero TAO transfer','before.image_requests.0.wire_bytes',0],
 ['CMS storage not network','before.image_requests.0.wire_source','cms_storage_bytes'],
 ['different wire units','after.image_requests.0.wire_source','cdp_loadingFinished_encodedDataLength'],
 ['cached image','after.image_requests.0.from_cache',true],
 ['decode failed','after.dom_images.0.natural_width',0],
 ['no matching network request','after.dom_images.0.current_src','https://example.com/unobserved.jpg'],
 ['viewport mismatch','after.viewport_width',1200],
 ['incorrect MIME','after.image_requests.0.content_type','text/html'],
 ['insecure request','after.image_requests.0.url','http://example.org/abc.jpg'],
 ['empty DOM image set','after.dom_images',[]],
 ['changed image slots','after.dom_images.0.slot','432:1'],
 ['bad timestamp','after.captured_at','not-a-date'],
 ['missing before capture','before',null]
];
function set(root,path,value){const parts=path.split('.');let p=root.pairs[0];for(let i=0;i<parts.length-1;i++)p=p[parts[i]];p[parts.at(-1)]=value;}
for(const [label,path,value]of mutations)test('reject: '+label,()=>{const x=fixture();set(x,path,value);assert.equal(evaluate(x).ok,false);});
test('reject missing page',()=>{const x=fixture();x.pairs=[];assert.equal(evaluate(x).ok,false);});
test('reject duplicate image URL',()=>{const x=fixture();x.pairs[0].after.image_requests.push({...x.pairs[0].after.image_requests[0]});assert.equal(evaluate(x).ok,false);});
test('reject URL mismatch',()=>{const x=fixture();x.pairs[0].page_url='https://example.org/';assert.equal(evaluate(x).ok,false);});
test('61-page site-wide denominator is not inferred from a one-page sample',()=>{const x=fixture();x.published_cohort_size=61;assert.equal(evaluate(x).sitewide_claim_allowed,false);});
test('negative savings are reported as negative rather than coerced',()=>{const x=fixture();x.pairs[0].after.image_requests[0].wire_bytes=200000;const r=evaluate(x);assert.equal(r.ok,true);assert.equal(r.measured.saving_percent,-100);});
test('only a full 66-page cohort may support site-wide 76% threshold',()=>{
 const x=fixture(),one=x.pairs[0];x.expected_page_urls=[];x.pairs=[];
 for(let i=0;i<66;i++){const page='https://finalvestige.com/article-'+i+'/';x.expected_page_urls.push(page);x.pairs.push({...structuredClone(one),page_url:page});}
 const r=evaluate(x);assert.equal(r.ok,true);assert.equal(r.sitewide_claim_allowed,true);assert.equal(r.claim_76_percent_supported,true);
});

test('explicitly verified empty-image article is allowed within a page cohort',()=>{
 const x=fixture(),empty=structuredClone(x.pairs[0]);
 empty.page_url='https://finalvestige.com/article-with-no-images/';
 for(const stage of ['before','after']){empty[stage].image_requests=[];empty[stage].dom_images=[];empty[stage].zero_image_page_verified=true;}
 x.expected_page_urls.push(empty.page_url);x.pairs.push(empty);
 const r=evaluate(x);assert.equal(r.ok,true);assert.equal(r.measured.before_wire_bytes,100000);
});
test('unverified empty image list cannot silently qualify',()=>{
 const x=fixture();x.pairs[0].after.image_requests=[];x.pairs[0].after.dom_images=[];
 assert.equal(evaluate(x).ok,false);
});
test('empty cohort transfer cannot yield division by zero savings',()=>{
 const x=fixture();for(const phase of ['before','after']){x.pairs[0][phase].image_requests=[];x.pairs[0][phase].dom_images=[];x.pairs[0][phase].zero_image_page_verified=true;}
 assert.equal(evaluate(x).ok,false);
});
test('reject invalid browser viewport numeric type',()=>{const x=fixture();x.pairs[0].after.viewport_width='390';assert.equal(evaluate(x).ok,false);});
