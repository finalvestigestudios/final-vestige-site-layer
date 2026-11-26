'use strict';
// This module is read-only. It does not probe HTTP, download images, edit CMS content, or clear reuse rights.
const EXPECTED = Object.freeze([
  ['432:0','/fpc/prints/pr04493.jpg','PR04493','4144'],
  ['432:1','/fpc/reference/rc17068.jpg','RC17068','38362'],
  ['432:2','/fpc/reference/rc10673.jpg','RC10673','33289'],
  ['432:3','/fpc/general/n031889.jpg','N031889','141398'],
  ['432:4','/fpc/reference/rc04344.jpg','RC04344','27848'],
  ['432:5','/fpc/reference/rc07668.jpg','RC07668','30741'],
  ['432:6','/fpc/msf/MSF-PB11548-001.jpg','MSF-PB11548-001','340182']
]);
const SOURCE_BLOB='948bc1b65b42799aa40cfdb810ddf6ffd80886b6';
const CANDIDATE_BLOB='f737816bb8e7cf36b69834d8e3ed28d2839d8d9d';
const POST_URL='https://finalvestige.com/2026/08/20/they-buried-the-dead-apart-okeechobee-1928/';
const die=m=>{throw Error(m)};
function exactHttps(url,host,pathname){
  if(typeof url!=='string'||url.length>2048)return false;
  try{const u=new URL(url);return u.protocol==='https:'&&u.hostname===host&&u.pathname===pathname&&u.search===''&&u.hash===''&&!u.port&&!u.username&&!u.password;}catch{return false;}
}
function verify(a){
  if(!a||a.schema!=='fv-florida432-redirect-v1'||a.post_id!==432||a.post_url!==POST_URL||a.historical_cohort!=='61-post-20261030'||a.historical_source_blob!==SOURCE_BLOB||a.candidate_crosswalk_blob!==CANDIDATE_BLOB||!Array.isArray(a.slots)||a.slots.length!==7)die('Unpinned or incomplete Florida Memory cohort');
  if(a.guest_broken_confirmed!==null||a.origin_http_500_confirmed!==false||a.claimed_42_broken_verified!==false||a.claimed_76_percent_wire_savings_verified!==false||a.rehost_approved!==false||a.wordpress_production_write_approved!==false)die('Unverified production or performance claim');
  const found=new Set();
  for(const row of a.slots){
    if(!row||typeof row.key!=='string'||found.has(row.key))die('Duplicate/invalid slot');
    const expected=EXPECTED.find(x=>x[0]===row.key);
    if(!expected)die('Unexpected historical slot');
    const [key,path,accession,item]=expected;
    if(!exactHttps(row.stored_original,'www.floridamemory.com',path)||!exactHttps(row.redirect_target,'floridamemory.com',path)||!exactHttps(row.archival_record,'www.floridamemory.com',`/items/show/${item}`)||row.accession!==accession)die('Unverified media URL, canonical redirect or catalog ID');
    if(!row.origin_probe||row.origin_probe.kind!=='RETRIEVER_REDIRECT_WRAPPER_ERROR'||row.origin_probe.retriever_reported_code!==500||row.origin_probe.origin_final_http_status!==null||row.origin_probe.redirect_observed!==true||row.origin_probe.visitor_http_status!==null||row.origin_probe.browser_decode!==null||row.origin_probe.actual_transfer_bytes!==null)die('False HTTP 500 or visitor/byte attribution');
    if(row.origin_probe.target_retriever_accessible!==false||row.origin_probe.mode!=='public_web_retriever_not_browser')die('Invalid wrapper provenance');
    if(row.catalog_match_basis!=='archival_id_and_source_path_prior_snapshot'||row.exact_raster_verified!==false||row.native_width_px!==null||row.native_height_px!==null||row.derivative_width_px!==null||row.derivative_height_px!==null||row.target_max_width_px!==960||row.no_upscale!==true||row.rights_clearance!=='HOLD'||row.can_rehost!==false||row.can_edit_wordpress!==false)die('Unsupported asset identity, rights or geometry');
    if(row.metadata_review!=='EDITOR_REVIEW'||row.catalog_date!== (key==='432:6'?'2001':key==='432:3'?'1928':null))die('Metadata chronology is unverified or corrupted');
    found.add(key);
  }
  if(found.size!==EXPECTED.length)die('Missing slot');
  return {status:'HOLD_GUEST_CHROMIUM_AND_RIGHTS',slots:7,origin_redirect_wrappers:7,verified_origin_http_500:0,guest_confirmed_failures:0,approved_rehosts:0,percent_76_verified:false};
}
module.exports={verify,EXPECTED};
