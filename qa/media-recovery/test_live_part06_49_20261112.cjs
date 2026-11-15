'use strict';
/* Offline native Node regression suite. No HTTP, media binaries, or WordPress writes. */
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {validate}=require('./validate_live_part06_49_20261112.cjs');
const audit=JSON.parse(fs.readFileSync(path.join(__dirname,'live_part06_8posts_49_images_20261112.json')));
const registry=JSON.parse(fs.readFileSync(path.join(__dirname,'coverage_288_exact_pr1703_20261110.json')));
function clone(){return JSON.parse(JSON.stringify(audit));}
function reject(name,modify,pattern){
  test(name,()=>{const a=clone();modify(a);const r=validate(a,registry);assert.equal(r.ok,false);assert.match(r.errors.join('|'),pattern);});
}
test('exact frozen 49-row audit validates without browser claims',()=>{const r=validate(audit,registry);assert.equal(r.ok,true,r.errors.join('; '));assert.equal(r.counts.images,49);assert.equal(r.counts.missing_both_dimensions,43);});
reject('source URL change under same slot',a=>{a.rows[0].live_source_url='https://example.org/not-the-original.jpg';},/live_src_mismatch/);
reject('source changed on both fields still denied by frozen registry',a=>{a.rows[0].source_url='https://example.org/replace.jpg';a.rows[0].live_source_url=a.rows[0].source_url;},/frozen_registry_src_mismatch/);
reject('ALT modification denied',a=>{a.rows[0].live_alt='Different photo';},/live_alt_mismatch/);
reject('ALT equality flag cannot conceal drift',a=>{a.rows[0].original_alt='Other';},/live_alt_mismatch/);
reject('wrong source host denied',a=>{a.rows[0].host='example.com';},/origin_host_mismatch/);
reject('duplicate image slot denied',a=>{a.rows[1].slot=a.rows[0].slot;},/duplicate_slot/);
reject('post reassignment denied',a=>{a.rows[0].post_id=999;},/foreign_post_slot/);
reject('post count modification denied',a=>{a.posts.pop();},/post_cohort_or_order_changed/);
reject('partial intrinsic HTML dimension denied',a=>{a.rows[0].html_width_px=960;},/invalid_dimension_pair/);
reject('negative width denied',a=>{a.rows[0].html_width_px=-1;a.rows[0].html_height_px=540;},/invalid_dimension_pair/);
reject('unverified srcset claim denied',a=>{a.rows[0].literal_srcset=true;},/unverified_srcset/);
reject('false current guest 404 denied',a=>{a.rows[0].guest_origin_http_status=404;},/fabricated_guest_evidence/);
reject('false wire bytes denied',a=>{a.rows[0].guest_transferred_bytes=1200;},/fabricated_guest_evidence/);
reject('browser success inferred from retriever wrapper denied',a=>{a.rows[0].guest_image_failure_confirmed=false;},/fabricated_guest_evidence/);
reject('unauthorized cache denied',a=>{a.rows[0].cache_authorized=true;},/unsafe_release_flag/);
reject('unauthorized WordPress upload denied',a=>{a.rows[0].wordpress_upload_authorized=true;},/unsafe_release_flag/);
reject('candidate rights overclaim denied',a=>{a.rows[0].archive_candidates[0].rights_cleared=true;},/candidate_unapproved_release/);
reject('960 width cap denied',a=>{a.rows[0].archive_candidates[0].conditional_960px=[1280,700];},/unsafe_960_derivative/);
reject('zero height denied',a=>{a.rows[0].archive_candidates[0].conditional_960px=[960,0];},/unsafe_960_derivative/);
reject('reported 42 treated confirmed denied',a=>{a.policy.historical_42_broken_browser_verified=true;},/scope_or_claim_invariant/);
reject('76 percent measured claim denied',a=>{a.policy.claimed_76_percent_network_weight_saving_measured=true;},/scope_or_claim_invariant/);
reject('reclassified source kind denied',a=>{a.rows[0].origin_kind='first_party';},/source_kind_mismatch/);
reject('changed count summary denied',a=>{a.counts.commons_redirects=0;},/count_mismatch/);
reject('unpublished post not a current-page audit',a=>{a.posts[0].status='draft';},/post_invalid/);
