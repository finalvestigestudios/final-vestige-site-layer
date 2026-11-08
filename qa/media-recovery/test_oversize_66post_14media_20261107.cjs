'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const input=require('./oversize_66post_14media_20261107.json'),{validate}=require('./validate_oversize_66post_14media_20261107.cjs');
const copy=()=>JSON.parse(JSON.stringify(input));
test('read-only 66/361, 118/14, 45,553,777-byte snapshot passes',()=>assert.equal(validate(input).ok,true));
const bad=[
['invented 404',x=>x.media[0].guest_http_status=404],['browser success invented',x=>x.media[0].browser_decoded=true],['wire transfer invented',x=>x.media[0].visitor_transfer_bytes=9000],
['invented savings',x=>x.performance_and_release.measured_wire_delta_percent=76],['42 broken falsely verified',x=>x.performance_and_release.reported_broken_count_42_verified=true],
['unauthorized license',x=>x.media[0].rights_approved=true],['unauthorized hosting',x=>x.media[0].rehost_approved=true],['uploads',x=>x.performance_and_release.uploads=1],
['post writes',x=>x.performance_and_release.post_writes=1],['downloads',x=>x.performance_and_release.image_downloads=1],['spend',x=>x.performance_and_release.spend_usd=1],
['wrong 66 census',x=>x.cohort.published_posts=61],['wrong media count',x=>x.cohort.image_media_items=113],['duplicate media',x=>x.media[1].id=x.media[0].id],
['wrong bytes',x=>x.media[0].original_bytes--],['unsupported upsize',x=>x.media[0].conditional_max_960.width=1280],
['aspect ratio drift',x=>x.media[0].conditional_max_960.height--],['source origin swap',x=>x.media[0].source_url='https://example.com/test.jpg'],
['fabricated Vasa direct original',x=>x.media.find(y=>y.id===388).source_match_method='stored exact original img src'],['false PNG subsize',x=>x.media.find(y=>y.id===39).wp_subsizes_metadata_present=true],
['false newly published NOAA ref',x=>x.media.find(y=>y.id===2148).published_raw_inline_post_ids=[34]],['wrong NOAA catalog',x=>x.media.find(y=>y.id===2148).authority='https://example.org'],
['missing published post',x=>x.posts_checked.pop()],['false reference',x=>x.media.find(y=>y.id===405).published_raw_inline_post_ids=[9999]]];
for(const [name,mutate] of bad)test('fail closed: '+name,()=>{const x=copy();mutate(x);assert.equal(validate(x).ok,false);});
