'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {validate,hostInfo}=require('./validate_host_blast_radius_20261106.cjs');
const original=JSON.parse(fs.readFileSync(path.join(__dirname,'host_blast_radius_verified_20261106.json'),'utf8'));
const copy=()=>structuredClone(original);
function rejects(name,change){
 test(name,()=>{const a=copy();change(a);assert.equal(validate(a).ok,false);});
}
test('66 published/65 image-bearing posts and 361 images in 81 upstream groups',()=>{
 const r=validate(copy());assert.deepEqual(r.errors,[]);
 assert.equal(r.metrics.posts,66);assert.equal(r.metrics.image_bearing_posts,65);
 assert.equal(r.metrics.images,361);assert.equal(r.metrics.host_count,81);
});
test('image references grouped without losing any URLs',()=>assert.equal(original.groups.reduce((n,g)=>n+g.source_references,0),361));
test('zero-image published post 1922 included only in sitewide denominator',()=>{
 assert.deepEqual(original.zero_image_post_ids,[1922]);
 assert.equal(new Set(original.groups.flatMap(g=>g.affected_post_ids)).size,65);
});
test('Wikimedia Commons exposure is 124 image references across 24 posts',()=>{
 const g=original.groups.find(x=>x.upstream_host==='commons.wikimedia.org');
 assert.equal(g.source_references,124);assert.equal(g.affected_post_ids.length,24);
});
test('Jetpack request host unwrapped to correct original provider',()=>{
 assert.equal(hostInfo('https://i0.wp.com/text-message.blogs.archives.gov/a.jpg?ssl=1').upstream,'text-message.blogs.archives.gov');
});
test('no insecure, malformed or credentialed URL accepted',()=>{
 assert.throws(()=>hostInfo('http://example.org/img.jpg'));
 assert.throws(()=>hostInfo('https://user@example.org/img.jpg'));
 assert.throws(()=>hostInfo('https://i0.wp.com/invalid/image.jpg'));
});
rejects('invented browser success',a=>a.groups[0].guest_browser_http=200);
rejects('invented 42 failures',a=>a.rights_and_release.reported_broken_42='VERIFIED');
rejects('invented 76% savings',a=>a.rights_and_release.claimed_76_percent_reduction='MEASURED');
rejects('unlicensed rehosting',a=>a.groups[0].rehost_permission='GRANTED');
rejects('forbidden WordPress production write',a=>a.rights_and_release.wordpress_production_writes_allowed=true);
rejects('unsafe 1920-pixel resize',a=>a.rights_and_release.optimization_max_width_px=1920);
rejects('zero-image post removed',a=>a.zero_image_post_ids=[123]);
rejects('missing origin group',a=>a.groups.pop());
rejects('host tally mismatch',a=>a.groups[0].source_references+=10);
rejects('invented P0 404',a=>a.p0_source_urls[0].visitor_http=404);
rejects('wrapper mislabelled as browser status',a=>a.retrieval_observations[0].browser_origin_status=404);
rejects('wrong provider for image sample',a=>a.groups[0].exact_source_samples[0].url='https://unrelated.example.org/photo.jpg');
rejects('missing source SHA',a=>a.sources.legacy_parts[0].blob_sha='not-a-sha');
rejects('duplicate host group',a=>a.groups[1].upstream_host=a.groups[0].upstream_host);
