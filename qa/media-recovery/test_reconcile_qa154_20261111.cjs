'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {census,proxyOrigin,reconcile}=require('./reconcile_qa154_20261111.cjs');
const c=fs.readFileSync(path.join(__dirname,'fixtures','siteqa154_frozen_census_20261030.csv'),'utf8');
const u=JSON.parse(fs.readFileSync(path.join(__dirname,'offsite_upstream_288_20261109.json'),'utf8'));
const a=JSON.parse(fs.readFileSync(path.join(__dirname,'qa154_286_288_proxy_crosswalk_20261111.json'),'utf8'));
const clone=()=>structuredClone(u);
test('61-post original/QA totals and exact two-post difference',()=>{
 const x=reconcile(c,u);assert.deepEqual([x.qa_posts,x.qa_inline,x.qa_offsite,x.origin_offsite,x.delta],[61,355,286,288,2]);
 assert.deepEqual(x.post_differences,[{post_id:285,qa_offsite:5,origin_offsite:6,delta:1},{post_id:291,qa_offsite:5,origin_offsite:6,delta:1}]);
});
test('two exception slots have external origins despite Jetpack delivery',()=>{
 assert.deepEqual(reconcile(c,u).candidates.map(x=>[x.slot,x.third_party_origin]),[['285:1','www.squawkpoint.com'],['291:0','text-message.blogs.archives.gov']]);
});
test('machine audit matches exact frozen URLs and zero visitor proof',()=>{
 for(const x of reconcile(c,u).candidates){const y=a.exception_slots.find(i=>i.slot===x.slot);assert.equal(y.stored_url,x.stored_url);
 assert.equal(y.guest_status,null);assert.equal(y.guest_decode,null);assert.equal(y.copyright_cleared,false);
 assert.equal(y.wordpress_write_authorized,false);}
});
test('archival contractor authorship stays on rights hold',()=>{
 assert.match(a.exception_slots.find(x=>x.slot==='291:0').rights,/contractor/i);
 assert.equal(a.exception_slots.find(x=>x.slot==='291:0').copyright_cleared,false);
});
test('no claimed guest failures or 76% savings',()=>{
 assert.equal(a.methodology.guest_broken_42_confirmed,false);assert.equal(a.methodology.claimed_transfer_76_percent_measured,false);
});
test('reject malformed or duplicated census',()=>{
 assert.throws(()=>reconcile(c.replace('post_id,','post,'),u));assert.throws(()=>reconcile(c+'\n285,6,5',u));
});
test('reject missing/duplicated origin slots',()=>{
 let x=clone();x.rows.pop();assert.throws(()=>reconcile(c,x));
 x=clone();x.rows[1]=x.rows[0];assert.throws(()=>reconcile(c,x));
});
test('reject invented visitor result',()=>{
 let x=clone();x.rows.find(r=>r.slot==='285:1').visitor_http=200;assert.throws(()=>reconcile(c,x));
});
test('reject silent upload and cache rights grants',()=>{
 let x=clone();x.rows.find(r=>r.slot==='291:0').release.mirror=true;assert.throws(()=>reconcile(c,x));
});
test('reject relabelling a third-party target as first-party',()=>{
 let x=clone();x.rows.find(r=>r.slot==='291:0').origin_host='finalvestige.com';assert.throws(()=>reconcile(c,x));
});
test('reject unexplained further post delta',()=>assert.throws(()=>reconcile(c.replace('432,7,7','432,7,6'),u)));
test('extract proxy target not delivery hostname',()=>assert.equal(proxyOrigin('https://i0.wp.com/www.squawkpoint.com/photo.jpg?ssl=1'),'www.squawkpoint.com'));
test('deny production changes',()=>assert.equal(Object.values(a.restrictions).every(Boolean),true));
test('frozen QA CSV totals still valid',()=>{
 const rows=census(c);assert.equal(rows.length,61);assert.equal(rows.reduce((s,x)=>s+x.total,0),355);
});
