'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const {coldNetworkProvenance}=require('./cdp_cold_cache_provenance_20261113.cjs');
const {classifyImages}=require('./browser_probe_core.cjs');
const src='https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg';
const policy={cache_disabled_acknowledged:true,service_worker_bypass_acknowledged:true,
 monitor_started_before_navigation:true};
function caseData(status=404,mutate=()=>{}){
 const raw={type:'Image',request_id:'image-418',url:src,status,
 mime_type:status===200?'image/jpeg':'text/html',encodedDataLength:512,
 request_will_be_sent_observed:true,response_received_observed:true,
 loading_finished_observed:true,loading_failed_observed:false,
 served_from_cache_observed:false,from_disk_cache:false,from_service_worker:false};
 mutate(raw);
 const req={...raw,...coldNetworkProvenance(raw,policy)};
 const visible=status===200;
 const rend={index:0,src,currentSrc:src,alt:'Scotch Cap aftermath',
 complete:true,naturalWidth:visible?960:0,naturalHeight:visible?540:0};
 const original=[{key:'418:2',source_url:src,alt:'Scotch Cap aftermath'}];
 return classifyImages(original,[rend],[req],true)[0];
}
test('completed 404 is reviewable as browser-broken only with full cold provenance',()=>{
 const row=caseData(404);
 assert.equal(row.result,'confirmed_broken_in_probe_browser');
 assert.equal(row.verified_broken_in_browser,true);
});
test('completed 200 image is considered loaded only with full cold provenance',()=>{
 const row=caseData(200);
 assert.equal(row.result,'loaded_in_probe_browser');
 assert.equal(row.verified_broken_in_browser,false);
});
for(const [title,mutator] of [
 ['partial request (no finish)',r=>{delete r.loading_finished_observed}],
 ['cache event',r=>{r.served_from_cache_observed=true}],
 ['disk-cache image',r=>{r.from_disk_cache=true}],
 ['service-worker image',r=>{r.from_service_worker=true}],
 ['failed load event',r=>{r.loading_failed_observed=true}]
]){
 test('cached or incomplete 404 never counts: '+title,()=>{
  const row=caseData(404,mutator);
  assert.notEqual(row.result,'confirmed_broken_in_probe_browser');
  assert.equal(row.verified_broken_in_browser,null);
 });
 test('cached or incomplete 200 never proves image loaded: '+title,()=>{
  const row=caseData(200,mutator);
  assert.notEqual(row.result,'loaded_in_probe_browser');
  assert.equal(row.verified_broken_in_browser,null);
 });
}
