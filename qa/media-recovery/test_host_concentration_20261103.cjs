'use strict';
const assert=require('node:assert/strict');
const {buildHostConcentration,loadPinnedParts}=require('./audit_host_concentration_20261103.cjs');
const path=require('node:path');
const original=loadPinnedParts(__dirname);
const clone=()=>JSON.parse(JSON.stringify(original));
let n=0;
function passes(name,fn){fn();n++;process.stdout.write('PASS '+name+'\n');}
function fails(name,mutate){const corpus=clone();mutate(corpus);assert.throws(()=>buildHostConcentration(corpus),undefined,name);n++;process.stdout.write('PASS rejects '+name+'\n');}
const a=buildHostConcentration(original);
passes('61 posts, 355 inline slots',()=>{assert.equal(a.source_count.posts,61);assert.equal(a.source_count.stored_inline_image_refs,355);});
passes('288 external upstream references, 67 first-party',()=>{assert.equal(a.source_count.recorded_external_origins,288);assert.equal(a.source_count.first_party_direct+a.source_count.first_party_jetpack,67);});
passes('118 Wikimedia Special Redirect original sources in 20 posts',()=>{
 const h=a.hosts.find(h=>h.source_host==='commons.wikimedia.org');
 assert.equal(h.stored_reference_count,118);assert.equal(h.distinct_post_count,20);
});
passes('80 recorded source hosts, not final CDP network destinations',()=>assert.equal(a.source_count.distinct_stored_source_hosts,80));
passes('36 entirely external-source posts',()=>assert.equal(a.source_count.all_external_posts,36));
passes('17 entirely single-external-host posts',()=>assert.equal(a.source_count.fully_single_external_host_posts,17));
passes('Hebgen 407 eight direct USGS S3 refs',()=>{let p=a.posts.find(x=>x.post_id===407);assert.equal(p.single_external_source_host,'d9-wret.s3.us-west-2.amazonaws.com');assert.equal(p.stored_image_count,8);});
passes('Florida Memory 432 seven upstream refs',()=>{let p=a.posts.find(x=>x.post_id===432);assert.equal(p.single_external_source_host,'www.floridamemory.com');assert.equal(p.stored_image_count,7);});
passes('Jetpack proxy host 9 URLs not automatically first-party',()=>assert.equal(a.hosts.find(h=>h.source_host==='i0.wp.com').stored_reference_count,9));
passes('browser and weight claims remain unverified',()=>{
 assert.equal(a.caveats.browser_broken_42,'UNVERIFIED');assert.equal(a.caveats.wire_weight_savings_76_percent,'UNMEASURED');
 assert.ok(a.hosts.every(h=>h.origin_http_status===null&&h.guest_browser_broken_verified===false));
});
fails('lost part',c=>c.pop());
fails('wrong frozen batch',c=>c[0].batch=9);
fails('lost image slot',c=>c[0].images.pop());
fails('duplicated slot',c=>c[1].images[0].key=c[0].images[0].key);
fails('unknown article',c=>c[0].images[0].post_id=123456);
fails('post URL drift',c=>c[0].images[0].post_url='https://example.com/post');
fails('source host mismatch',c=>c[0].images[0].source_host='example.com');
fails('source URL invalid',c=>c[0].images[0].source_url='data:image/png;base64,test');
fails('non-http URL',c=>c[0].images[0].source_url='ftp://example.com/photo.jpg');
fails('source classification drift',c=>c[0].images[0].source_kind='unknown');
fails('external census mutation',c=>c[0].images[7].source_kind='first_party');
fails('duplicate post',c=>c[1].posts[0].id=c[0].posts[0].id);
fails('source key mismatch',c=>c[0].images[0].key='some-other-key');
process.stdout.write('PASS '+n+'/'+n+' host-topology assertions; offline assertions complete; native Node CI status depends on runner\n');
