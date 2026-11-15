'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const {gitBlobSha,classify,readQaCsv,reconcile}=require('./reconcile_qa154_census_20261112.cjs');
const csv='post_id,stored_img_src_count,offsite_src_count\n285,2,1\n291,1,1\n';
const rows=[
 {post_id:285,slot:'285:0',source_url:'https://finalvestige.com/a.jpg',offsite_historical_registry:false,source_equal:true,alt_equal:true},
 {post_id:285,slot:'285:1',source_url:'https://i0.wp.com/www.squawkpoint.com/a.jpg?ssl=1',offsite_historical_registry:true,source_equal:true,alt_equal:true},
 {post_id:291,slot:'291:0',source_url:'https://text-message.blogs.archives.gov/a.jpg',offsite_historical_registry:true,source_equal:true,alt_equal:true}
];
const ledger=()=>JSON.stringify({rows,counts:{historical_offsite_positions:2}});
test('Git blob encoding is standard',()=>assert.equal(gitBlobSha('hello\n'),'ce013625030ba8dba906f756967f9e9ca394464a'));
test('QA classifier: first-party URL',()=>assert.equal(classify('https://finalvestige.com/a.jpg'),'first_party'));
test('QA classifier: Jetpack only when proxying FV',()=>assert.equal(classify('https://i0.wp.com/finalvestige.com/a.jpg'),'jetpack_proxy'));
test('QA classifier: remote Jetpack is external',()=>assert.equal(classify('https://i0.wp.com/www.squawkpoint.com/a.jpg'),'external'));
test('QA classifier: Commons redirect',()=>assert.equal(classify('https://commons.wikimedia.org/wiki/Special:Redirect/file/abc'),'redirect_image'));
test('QA classifier: Google drive thumbnail',()=>assert.equal(classify('https://drive.google.com/thumbnail?id=123'),'drive_thumbnail'));
test('QA classifier: non-HTTP',()=>assert.equal(classify('data:image/png;base64,hello'),'non_http'));
test('QA CSV rejects duplicate posts',()=>assert.throws(()=>readQaCsv(csv+'285,1,0\n')));
test('QA CSV rejects malformed rows',()=>assert.throws(()=>readQaCsv(csv+'invalid\n')));
test('synthetic baseline reconciles without pinned hashes',()=>{const x=reconcile(csv,ledger(),{enforcePins:false});assert.equal(x.status,'RECONCILED_POST_LEVEL_SOURCE_COUNT_DISAGREEMENT');assert.equal(x.counts.offsite_difference,0);assert.equal(x.differences.length,0);});
test('synthetic one-post offsite mismatch is found, without attributing a slot',()=>{const x=reconcile(csv.replace('285,2,1','285,2,0'),ledger(),{enforcePins:false});assert.equal(x.differences.length,1);assert.equal(x.differences[0].post_id,285);assert.equal(x.differences[0].source_slots_for_custody_recheck.length,2);assert.equal(x.differences[0].source_slots_for_custody_recheck[1].actual_guest_http_status,null);});
test('pin check fails closed against a synthetic ledger',()=>assert.equal(reconcile(csv,ledger()).status,'HOLD'));
test('wrong media offsite flag rejected',()=>{const j=JSON.parse(ledger());j.rows[1].offsite_historical_registry=false;assert.equal(reconcile(csv,JSON.stringify(j),{enforcePins:false}).reason,'CLASSIFIER_AND_MEDIA_FLAG_DISAGREE');});
test('duplicate slot rejected',()=>{const j=JSON.parse(ledger());j.rows[1].slot='285:0';assert.equal(reconcile(csv,JSON.stringify(j),{enforcePins:false}).reason,'BAD_MEDIA_ROW_OR_SLOT');});
test('source identity drift rejected',()=>{const j=JSON.parse(ledger());j.rows[1].source_equal=false;assert.equal(reconcile(csv,JSON.stringify(j),{enforcePins:false}).reason,'BAD_MEDIA_ROW_OR_SLOT');});
test('missing post rejected',()=>{const j=JSON.parse(ledger());j.rows.pop();assert.equal(reconcile(csv,JSON.stringify(j),{enforcePins:false}).reason,'POST_SET_MISMATCH');});
