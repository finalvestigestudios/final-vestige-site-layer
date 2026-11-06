'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const manifest=require('./published_cohort_manifest_20261106.json');
const {verify,validateManifest}=require('./verify_published_image_cohort_20261106.cjs');
const clone=x=>JSON.parse(JSON.stringify(x));
function capture(a,bytes){
 const urls=Array.from({length:a.fresh_inline_img_count},(_,i)=>'https://assets.example.org/'+a.id+'-'+i+'.jpg');
 return {guest_browser_verified:true,cache_disabled:true,service_worker_bypassed:true,
  scrolled_to_bottom:true,all_images_loaded:true,capture_complete:true,
  browser:'Chrome',browser_version:'131',device_profile:'mobile',
  viewport_width:390,viewport_height:844,dpr:3,network_profile:'4G',
  captured_at:'2026-11-06T19:00:00Z',zero_image_page_verified:urls.length===0,
  image_requests:urls.map(url=>({url,status:200,from_cache:false,content_type:'image/jpeg',
   wire_bytes:bytes,wire_source:'chrome_har_entry_transferSize'})),
  dom_images:urls.map((current_src,i)=>({slot:a.id+':'+i,current_src,
   complete:true,natural_width:960,natural_height:540}))};
}
function fixture(rows=manifest.articles,cohort=66){
 return {schema:'fv-cold-image-wire-pairs-v1',published_cohort_size:cohort,
  expected_page_urls:rows.map(a=>a.url),
  pairs:rows.map(a=>({page_url:a.url,before:capture(a,100000),after:capture(a,24000)}))};
}
test('manifest contains exactly 66 real public published routes and 361 freshly recensused image slots',()=>{
 assert.equal(validateManifest(manifest).ok,true);
 assert.equal(manifest.fresh_total_external_images,294);
 assert.equal(manifest.fresh_legacy_inline_images,355);
});
test('synthetic complete 66 article fixture supports an EXAMPLE 76% threshold, not a production claim',()=>{
 const x=verify(fixture());
 assert.equal(x.ok,true);
 assert.equal(x.sitewide_claim_allowed,true);
 assert.equal(x.claim_76_percent_supported,true);
 assert.equal(x.stored_inline_slots_verified,361);
 assert.equal(x.measured.saving_percent,76);
});
const mutations=[
 ['fabricated expected article URL',x=>{x.expected_page_urls[0]='https://finalvestige.com/fake/';}],
 ['fabricated pair article URL',x=>{x.pairs[0].page_url='https://finalvestige.com/fake/';}],
 ['missing original image slot',x=>{x.pairs[0].before.dom_images=[];}],
 ['substitute image from another article',x=>{x.pairs[0].after.dom_images[0].slot='999:0';}],
 ['out-of-range image index',x=>{x.pairs[0].after.dom_images[0].slot='34:999';}],
 ['missing page capture',x=>{x.pairs.pop();}],
 ['duplicate expected page',x=>{x.expected_page_urls[0]=x.expected_page_urls[1];}],
 ['orphaned image request not in article DOM',x=>{x.pairs[0].before.image_requests.push({url:'https://other.example.org/extra.jpg',status:200,from_cache:false,content_type:'image/jpeg',wire_bytes:1,wire_source:'chrome_har_entry_transferSize'});}],
 ['mixed wire-byte sources across different pages',x=>{x.pairs[1].before.image_requests[0].wire_source='cdp_loadingFinished_encodedDataLength';}],
 ['mixed viewport across articles',x=>{x.pairs[1].after.viewport_width=1200;}],
 ['HTTP 404',x=>{x.pairs[1].after.image_requests[0].status=404;}],
 ['cache hit',x=>{x.pairs[1].before.image_requests[0].from_cache=true;}],
 ['failed image decode',x=>{x.pairs[1].after.dom_images[0].natural_width=0;}],
 ['false empty-post attestation',x=>{x.pairs.find(p=>p.page_url.includes('/change-blindness/')).before.zero_image_page_verified=false;}],
 ['foreign image on zero-image post',x=>{x.pairs.find(p=>p.page_url.includes('/change-blindness/')).before.dom_images.push({slot:'1922:0',current_src:'https://example.org/p.jpg',complete:true,natural_width:1,natural_height:1});}]
];
for(const [label,mutate] of mutations)test('REJECT '+label,()=>{
 const x=clone(fixture());mutate(x);const result=verify(x);
 assert.equal(result.ok,false,label);
 assert.equal(result.sitewide_claim_allowed,false,label);
});
test('valid one-page fixture is a sample and cannot support a site-wide claim',()=>{
 const x=verify(fixture(manifest.articles.slice(0,1)));
 assert.equal(x.ok,true);assert.equal(x.sitewide_claim_allowed,false);
});
test('complete historical 61 articles are NOT all 66 current published articles',()=>{
 const x=verify(fixture(manifest.articles.filter(a=>a.id<1900),61));
 assert.equal(x.ok,true);assert.equal(x.complete_cohort,true);
 assert.equal(x.historical_61_cohort_only,true);
 assert.equal(x.sitewide_claim_allowed,false);
 assert.equal(x.claim_76_percent_supported,false);
});
test('tampered manifest post image count cannot authorize a claim',()=>{
 const m=clone(manifest);m.articles[0].fresh_inline_img_count=99;
 assert.equal(validateManifest(m).ok,false);
});
test('tampered manifest duplicate URL cannot authorize a claim',()=>{
 const m=clone(manifest);m.articles[1].url=m.articles[0].url;
 assert.equal(validateManifest(m).ok,false);
});
test('tampered manifest missing fresh 66/66 readback fails',()=>{
 const m=clone(manifest);m.fresh_recensus_progress=64;
 assert.equal(validateManifest(m).ok,false);
});
test('source row of a cached 304 request cannot be promoted to measured savings',()=>{
 const x=fixture();x.pairs[0].after.image_requests[0].status=304;
 assert.equal(verify(x).sitewide_claim_allowed,false);
});
test('omitting any published article from claimed full cohort fails even when 76% simulated',()=>{
 const x=fixture();x.expected_page_urls.pop();x.pairs.pop();
 const result=verify(x);assert.equal(result.ok,true);
 assert.equal(result.sitewide_claim_allowed,false);
});
