'use strict';
/**
 * Derive strict negative cache evidence from a COMPLETE CDP Image request
 * lifecycle. Network.responseReceived does not carry a trustworthy
 * "fromMemoryCache:false" boolean; silence alone is not negative evidence.
 * Never infer a cold transfer from a partial capture or unacknowledged
 * Network.setCacheDisabled / Network.setBypassServiceWorker commands.
 * Offline pure helper. No requests, file writes, WP mutations or caching.
 */
function coldNetworkProvenance(r,policy){
 const completed=!!(r&&r.type==='Image'&&typeof r.request_id==='string'&&r.request_id.trim()&&
  r.request_will_be_sent_observed===true&&r.response_received_observed===true&&
  r.loading_finished_observed===true&&r.loading_failed_observed!==true&&
  Number.isInteger(r.status)&&r.status>=100&&r.status<=599&&
  Number.isSafeInteger(r.encodedDataLength)&&r.encodedDataLength>=0);
 const configured=!!(policy&&policy.cache_disabled_acknowledged===true&&
  policy.service_worker_bypass_acknowledged===true&&
  policy.monitor_started_before_navigation===true);
 const served=r?.served_from_cache_observed===true||r?.was_cached===true;
 const disk=r?.from_disk_cache===true,worker=r?.from_service_worker===true;
 const cold=completed&&configured&&!served&&!disk&&!worker;
 return {cold_event_chain_complete:completed,cold_policy_verified:configured,
  was_cached:served?true:cold?false:null,
  from_disk_cache:disk?true:cold?false:null,
  from_memory_cache:cold?false:null,
  from_service_worker:worker?true:cold?false:null,
  cold_network_transfer_proven:cold};
}
module.exports={coldNetworkProvenance};
