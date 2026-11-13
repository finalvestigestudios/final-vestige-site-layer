'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const {coldNetworkProvenance}=require('./cdp_cold_cache_provenance_20261113.cjs');
const raw=()=>({type:'Image',request_id:'request-17',status:404,
 request_will_be_sent_observed:true,response_received_observed:true,
 loading_finished_observed:true,loading_failed_observed:false,
 served_from_cache_observed:false,from_disk_cache:false,from_service_worker:false});
const policy=()=>({cache_disabled_acknowledged:true,
 service_worker_bypass_acknowledged:true,monitor_started_before_navigation:true});
function hold(name,mutateRaw,mutatePolicy){
 test(name,()=>{
  const r=raw(),p=policy();mutateRaw?.(r);mutatePolicy?.(p);
  const v=coldNetworkProvenance(r,p);
  assert.equal(v.cold_network_transfer_proven,false);
  assert.notEqual(v.from_memory_cache,false);
  assert.notEqual(v.was_cached,false);
 });
}
test('complete uncached 404 image CDP lifecycle gets four explicit false flags',()=>{
 const r=coldNetworkProvenance(raw(),policy());
 assert.equal(r.cold_network_transfer_proven,true);
 for(const key of ['was_cached','from_disk_cache','from_memory_cache','from_service_worker'])
  assert.equal(r[key],false,key);
});
test('complete uncached 200 image accepted',()=>{
 const r=raw();r.status=200;assert.equal(coldNetworkProvenance(r,policy()).cold_network_transfer_proven,true);
});
hold('missing requestWillBeSent cannot forge cold',r=>{delete r.request_will_be_sent_observed});
hold('missing responseReceived cannot forge cold',r=>{delete r.response_received_observed});
hold('missing loadingFinished cannot forge cold',r=>{delete r.loading_finished_observed});
hold('loadingFailed cannot certify completed image transfer',r=>{r.loading_failed_observed=true});
hold('Network.requestServedFromCache is not cold',r=>{r.served_from_cache_observed=true});
hold('cached request remains held even if was_cached asserted',r=>{r.was_cached=true});
hold('disk cache response rejected',r=>{r.from_disk_cache=true});
hold('service worker response rejected',r=>{r.from_service_worker=true});
hold('request without Image resource type rejected',r=>{r.type='Document'});
hold('missing request identity rejected',r=>{r.request_id=''});
hold('bad response HTTP status rejected',r=>{r.status=700});
hold('unacknowledged disable-cache command rejects',null,p=>{p.cache_disabled_acknowledged=false});
hold('unacknowledged service worker bypass rejects',null,p=>{delete p.service_worker_bypass_acknowledged});
hold('monitor started after navigation rejects',null,p=>{p.monitor_started_before_navigation=false});
test('confirmed cached outcome stays positive without inventing cache subtype',()=>{
 const r=raw();r.served_from_cache_observed=true;
 const v=coldNetworkProvenance(r,policy());
 assert.equal(v.was_cached,true);assert.equal(v.from_memory_cache,null);
 assert.equal(v.from_disk_cache,null);assert.equal(v.cold_network_transfer_proven,false);
});
test('partial network with explicit disk cached retains positive cache evidence',()=>{
 const r=raw();delete r.loading_finished_observed;r.from_disk_cache=true;
 const v=coldNetworkProvenance(r,policy());
 assert.equal(v.from_disk_cache,true);assert.equal(v.cold_event_chain_complete,false);
});
