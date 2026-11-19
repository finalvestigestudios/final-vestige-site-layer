'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {validateAudit}=require('./validate_live_twelve_post_view_20261117.cjs');
const raw=JSON.parse(fs.readFileSync(path.join(__dirname,'live_twelve_post_view_crosswalk_20261117_1026pt.json'),'utf8'));
const cases=["positive","fabricated_http","fake_wire","fake_rights","fake_derivative_width","missing_image","duplicate_slot","changed_origin","changed_proxy","fake_source_count","fake_76","fake_broken42","bad_post_revision","missing_p0","wrong_66","unknown_dimensions","changed_host_count"];
function mutate(a,name){switch(name){
 case 'fabricated_http':a.posts[0].images[0].guest_http_status=200;break;
 case 'fake_wire':a.posts[0].images[0].guest_transferred_bytes=400;break;
 case 'fake_rights':a.posts[0].images[0].rights_for_copying_approved=true;break;
 case 'fake_derivative_width':a.posts[0].images[0].allowed_max_derivative_width_px=1600;break;
 case 'missing_image':a.posts[0].images.pop();break;
 case 'duplicate_slot':a.posts[0].images[1].key=a.posts[0].images[0].key;break;
 case 'changed_origin':a.posts[0].images[0].underlying_host='evil.example';break;
 case 'changed_proxy':a.posts[0].images[0].published_src='https://i0.wp.com/evil.test/image.jpg?ssl=1';break;
 case 'fake_source_count':a.summary.image_families.external_direct=12;break;
 case 'fake_76':a.summary.sitewide_76_percent_verified=true;break;
 case 'fake_broken42':a.summary.guest_broken_42_confirmed=42;break;
 case 'bad_post_revision':a.posts[0].modified='fake';break;
 case 'missing_p0':a.summary.p0_keys.pop();break;
 case 'wrong_66':a.site_publish_inventory.ids_and_modified.pop();break;
 case 'unknown_dimensions':a.posts[0].images[0].width_attribute_px=-4;break;
 case 'changed_host_count':a.summary.distinct_underlying_hosts=80;break;
}}
for(const name of cases){test(name,()=>{const a=structuredClone(raw);mutate(a,name);if(name==='positive'){const r=validateAudit(a);assert.equal(r.status,'HOLD_GUEST_BROWSER_AND_RIGHTS');assert.equal(r.images,77)}else assert.throws(()=>validateAudit(a));});}
