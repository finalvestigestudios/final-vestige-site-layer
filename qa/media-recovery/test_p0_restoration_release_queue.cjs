'use strict';
const{test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const{validateP0}=require('./validate_p0_restoration_release_queue.cjs');
const directory=__dirname;
const baseline=JSON.parse(fs.readFileSync(path.join(directory,'p0_restoration_release_queue_20261101.json'),'utf8'));
const parts=Array.from({length:8},(_,i)=>JSON.parse(fs.readFileSync(
 path.join(directory,'parts',String(i+1).padStart(2,'0')+'.json'),'utf8')));
const clone=x=>JSON.parse(JSON.stringify(x));
test('exact 10-target, 355-slot source audit is valid and claims no guest failures',()=>{
 const r=validateP0(baseline,parts);assert.equal(r.ok,true,JSON.stringify(r.errors));
 assert.equal(r.checked_slots,10);assert.equal(r.checked_census_images,355);
 assert.equal(r.rights_approved_assets,0);
});
test('HTML double-quoted ALT can contain an apostrophe without truncation',()=>{
 const c=parts.flatMap(x=>x.images).find(x=>x.key==='268:3');
 assert.ok(c.alt.includes("Heiberg's early twentieth-century"));
 assert.equal(baseline.wordpress_live_readback.posts.find(x=>x.id===268).image_count,10);
});
function reject(name,mutate,reason){
 test(name,()=>{
  const b=clone(baseline),p=clone(parts);mutate(b,p);
  const r=validateP0(b,p);assert.equal(r.ok,false,'must fail closed');
  if(reason)assert.ok(r.errors.some(x=>x.startsWith(reason)),JSON.stringify(r.errors));
 });
}
reject("invented visitor 404 rejected",(b,p)=>{b.rows[0].guest_browser.http_status=404},"invented_visitor_measurement:285:5:http_status");
reject("invented visitor broken flag rejected",(b,p)=>{b.rows[0].guest_browser.visibly_broken=true},"invented_visitor_measurement");
reject("retriever status not origin HTTP",(b,p)=>{b.rows[0].source_viewer.origin_http_status=404},"retriever_mistaken_for_browser");
reject("retriever wrapper cannot claim 200",(b,p)=>{b.rows[0].source_viewer.retriever_wrapper_error_code=200},"viewer_evidence_changed");
reject("viewer 404 cannot be rewritten to 403",(b,p)=>{b.rows[0].source_viewer.result='RETRIEVER_FETCH_403';b.rows[0].source_viewer.retriever_wrapper_error_code=403},"viewer_evidence_changed");
reject("old viewer result cannot be marked rechecked",(b,p)=>{b.rows[3].source_viewer.rechecked_this_sprint=true},"retriever_mistaken_for_browser");
reject("unverified claim of 42 broken rejected",(b,p)=>{b.claims.reported_broken_42_browser_verified=true},"unsupported_site_wide_claim");
reject("invented broken-site count rejected",(b,p)=>{b.claims.confirmed_site_wide_broken_count=42},"unsupported_site_wide_claim");
reject("invented 76pct claim rejected",(b,p)=>{b.claims.claimed_76pct_transfer_reduction_measured=true;b.claims.measured_transfer_reduction_percent=76},"unsupported_site_wide_claim");
reject("original storage not wire bytes",(b,p)=>{b.oversized_media.real_visitor_transfer_bytes=43522829},"original_storage_is_not_wire_bytes");
reject("frozen denominators pinned",(b,p)=>{b.frozen_census.offsite_source_references=286},"source_census_not_frozen");
reject("stored original URL cannot change",(b,p)=>{b.rows[0].current_published_source_url='https://fakesite.example.org/a.jpg'},"source_identity_mismatch:285:5");
reject("historical ALT cannot change",(b,p)=>{b.rows[0].current_published_alt='Another photo'},"source_identity_mismatch:285:5");
reject("article permalink cannot change",(b,p)=>{b.rows[0].post_url='https://finalvestige.com/not-it/'},"source_identity_mismatch:285:5");
reject("priority ordering and keys pinned",(b,p)=>{[b.rows[0],b.rows[1]]=[b.rows[1],b.rows[0]]},"priority_or_key_changed");
reject("missing queue member fails",(b,p)=>{b.rows.pop()},"priority_queue_not_ten");
reject("duplicated queue member fails",(b,p)=>{b.rows[3].image_key=b.rows[2].image_key},"duplicate_priority_image_key");
reject("readback must cover 30 images",(b,p)=>{b.wordpress_live_readback.all_image_slots_checked=29},"cms_readback_scope_missing");
reject("live post image count pinned",(b,p)=>{b.wordpress_live_readback.posts[0].image_count=9},"cms_source_attestation_invalid");
reject("tampered frozen file source detected",(b,p)=>{p.flatMap(x=>x.images).find(x=>x.key==='285:5').source_url='https://somewhere.example.org/different.jpg'},"source_identity_mismatch:285:5");
reject("frozen source SHA pinned",(b,p)=>{b.rows[0].source_census_blob_sha='f'.repeat(40)},"unpinned_frozen_source_record");
reject("official archive catalog exact URL pinned",(b,p)=>{b.rows[0].candidate.archive_record_url='https://aggregator.example.org/another'},"archival_record_substituted:285:5");
reject("unverified same-topic photo cannot be binary matched",(b,p)=>{b.rows[8].candidate.binary_identity_verified=true},"archival_source_or_rights_unverified:285:2");
reject("master hash cannot be invented",(b,p)=>{b.rows[0].candidate.original_master_sha256='f'.repeat(64)},"archival_source_or_rights_unverified:285:5");
reject("image rights cannot be assumed",(b,p)=>{b.rows[2].candidate.reproduction_rights_review='APPROVED'},"archival_source_or_rights_unverified:418:1");
reject("caching needs release approval",(b,p)=>{b.rows[0].approval.media_cache_authorized=true},"unapproved_production_action:285:5");
reject("WordPress upload forbidden",(b,p)=>{b.rows[0].approval.wordpress_upload_authorized=true},"unapproved_production_action:285:5");
reject("Gutenberg post edit forbidden",(b,p)=>{b.rows[0].approval.wordpress_post_edit_authorized=true},"unapproved_production_action:285:5");
reject("homepage design unchanged",(b,p)=>{b.rows[0].approval.homepage_design_changed=true},"unapproved_production_action:285:5");
reject("unknown master cannot get invented 960px resize",(b,p)=>{b.rows[1].geometry.conditional_960px_width=960;b.rows[1].geometry.conditional_960px_height=720},"hypothetical_geometry_unjustified:407:1");
reject("Commons 819px photo cannot upscale",(b,p)=>{b.rows[0].geometry.conditional_960px_width=960;b.rows[0].geometry.conditional_960px_height=720},"catalog_geometry_mismatch:285:5");
reject("aspect ratio of NARA alternative preserved",(b,p)=>{b.rows[8].geometry.conditional_960px_height=640},"catalog_geometry_mismatch:285:2");
reject("stored HTML dimensions not arbitrary output",(b,p)=>{b.rows[5].geometry.conditional_960px_height=720},"hypothetical_geometry_unjustified:407:3");
reject("no invented transfer bytes",(b,p)=>{b.rows[0].guest_browser.encoded_transfer_bytes=250000},"invented_visitor_measurement:285:5:encoded_transfer_bytes");
reject("release cannot bypass rights",(b,p)=>{b.rows[0].approval.replacement_ready=true},"unapproved_production_action:285:5");
