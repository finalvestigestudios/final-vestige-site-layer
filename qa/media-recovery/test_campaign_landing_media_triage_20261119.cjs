'use strict';
const {test}=require('node:test');const assert=require('node:assert/strict');
const {validate}=require('./validate_campaign_landing_media_triage_20261119.cjs');
const evidence=require('./campaign_landing_media_triage_20261119.json');
const copy=()=>JSON.parse(JSON.stringify(evidence));
test('baseline audit is conservatively valid',()=>assert.deepEqual(validate(evidence),[]));
const cases=[
 ['invented mobile LCP',x=>x.priority_posts[0].mobile.lcp_ms=700],
 ['invented screenshot',x=>x.priority_posts[0].mobile.screenshot_sha256='fake'],
 ['claimed guest 404 from publisher 404',x=>x.priority_posts[0].known_origin_http_404[0].guest_broken_confirmed=true],
 ['fabricated guest HTTP',x=>x.priority_posts[0].known_origin_http_404[0].guest_response=404],
 ['fabricated 76 percent evidence',x=>x.claimed_76_percent_all_image_transfer_verified=true],
 ['fabricated 42 broken evidence',x=>x.reported_failures_42_guest_verified=true],
 ['invented video referral attribution',x=>x.window.video_or_social_campaign_attribution=true],
 ['negative WordPress views',x=>x.priority_posts[0].views_30d=-1],
 ['wrong URL on 404',x=>x.priority_posts[0].known_origin_http_404[0].exact_url='http://invalid.test'],
 ['fake first-party page',x=>x.priority_posts[0].url='https://unrelated.example/'],
 ['counterfeit image census',x=>x.source_custody.source_snapshot_blob_sha='0'.repeat(40)],
 ['fake media caching approval',x=>x.release_policy.cached_rehosting=true],
 ['unlicensed candidate rehosting',x=>x.official_candidates[0].rehosting_approved=true],
 ['stored bytes treated as downloads',x=>x.priority_posts.find(p=>p.post_id===621).large_originals[0].guest_original_download_confirmed=true],
 ['altered image origin counts',x=>x.priority_posts.find(p=>p.post_id===1917).direct_external++],
 ['missing zero-image control',x=>x.priority_posts=x.priority_posts.filter(p=>p.post_id!==1922)],
 ['duplicate post',x=>x.priority_posts.push(x.priority_posts[0])]
];for(const [name,mutation] of cases)test('reject '+name,()=>{const x=copy();mutation(x);assert.ok(validate(x).length>0)});
