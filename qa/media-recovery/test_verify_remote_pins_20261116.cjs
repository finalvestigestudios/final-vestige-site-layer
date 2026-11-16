'use strict';
const test=require('node:test');const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');
const {validate}=require('./verify_remote_pins_20261116.cjs');
const original=JSON.parse(fs.readFileSync(path.join(__dirname,'remote_pinned_blob_custody_20261116.json'),'utf8'));
const clone=()=>JSON.parse(JSON.stringify(original));
function rejects(title,mutate){test(title,()=>{const x=clone();mutate(x);assert.throws(()=>validate(x),/HOLD:/)})}
test('live GitHub read-only 14-blob custody data remains a non-execution hold',()=>{
 const x=validate(clone());assert.equal(x.remote_blobs_verified,14);assert.equal(x.declared_tests_pending,123);
 assert.equal(x.visitor_http_status,null);assert.equal(x.production_writes,0);
});
rejects('reject claimed suite execution',x=>x.native_node_suites_executed=true);
rejects('reject fabricated visitor HTTP',x=>x.actual_http_statuses_collected=true);
rejects('reject invented 42 broken',x=>x.confirmed_broken_image_count=42);
rejects('reject invented 76% transfer',x=>x.visitor_bandwidth_savings_percent=76);
rejects('reject unapproved WordPress write',x=>x.wordpress_writes=1);
rejects('reject media download',x=>x.media_downloads=1);
rejects('reject paid action',x=>x.subscription_spend_usd=1);
rejects('reject replaced fetched hash',x=>x.suites[0].files[0].fetched_blob_sha='a'.repeat(40));
rejects('reject replaced manifest pin',x=>x.suites[0].files[0].git_blob_sha='b'.repeat(40));
rejects('reject false match boolean',x=>x.suites[0].files[0].match=false);
rejects('reject path traversal',x=>x.suites[0].files[0].name='../outside.cjs');
rejects('reject duplicate file',x=>x.suites[0].files[0].name=x.suites[1].files[0].name);
rejects('reject missing pinned source',x=>x.suites[0].files.pop());
rejects('reject wrong suite expected tests',x=>x.suites[0].expected_tests=34);
rejects('reject skipped suite',x=>x.suites.pop());
rejects('reject premature successful native gate',x=>x.gate='PASS');
rejects('reject malformed inspected revision',x=>x.inspected_commit='latest');
