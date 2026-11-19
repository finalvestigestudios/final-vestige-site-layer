'use strict';
// Source-only WP VIEW audit validator. Never fetches remote URLs or writes WordPress.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const DIR = __dirname;
function readCensus(dir=DIR) {
  const slices = Array.from({length:9},(_,i)=>JSON.parse(fs.readFileSync(path.join(dir, 'live_66_view_slice_'+(i+1)+'_20261117.json'),'utf8')));
  const rollup = JSON.parse(fs.readFileSync(path.join(dir,'live_66_source_census_rollup_20261117_1624pt.json'),'utf8'));
  return {slices,rollup};
}
function checkGitBlobs(dir=DIR,rollup) {
  assert.equal(rollup.input_parts.length,9);
  for(let i=0;i<9;i++){
    const item=rollup.input_parts[i];
    assert.equal(item.path,'qa/media-recovery/live_66_view_slice_'+(i+1)+'_20261117.json');
    const bytes=fs.readFileSync(path.join(dir,path.basename(item.path)));
    const sha=crypto.createHash('sha1').update(Buffer.from('blob '+bytes.length+'\0')).update(bytes).digest('hex');
    assert.equal(sha,item.blob_sha,'Git blob identity mismatch: '+item.path);
  }
}
function checkSource(x) {
  assert.match(x.authored_view_src,/^https:\/\//,'missing HTTPS img src');
  const u=new URL(x.authored_view_src);
  let host=u.hostname.toLowerCase(),route,origin;
  if(/^i[012]\.wp\.com$/.test(host)){
    const embedded=u.pathname.replace(/^\/+/,'');
    host=embedded.split('/')[0].toLowerCase();
    origin='https://'+embedded;
    route=['finalvestige.com','www.finalvestige.com'].includes(host)?'first_party_jetpack':'third_party_jetpack';
  } else {
    origin=x.authored_view_src;
    route=['finalvestige.com','www.finalvestige.com'].includes(host)?'first_party_direct':'third_party_direct';
  }
  assert.equal(x.origin_host,host,'origin host mismatch');
  assert.equal(x.source_origin_url,origin,'derived origin path mismatch');
  assert.equal(x.route_type,route,'source class mismatch');
  assert.equal(x.visitor_http_status,null,'WP VIEW cannot claim guest HTTP');
  assert.equal(x.visitor_decode,null,'WP VIEW cannot claim image decoding');
  assert.equal(x.visitor_wire_bytes,null,'WP VIEW cannot claim network bytes');
  assert.equal(x.replacement_approved,false,'rehost/replacement not approved');
  assert.equal(x.rights_rehosting,'HOLD','rights not cleared');
  for(const dim of ['width_attr','height_attr']) if(x[dim]!==null) assert.ok(Number.isFinite(x[dim])&&x[dim]>0,'invalid dimension');
}
function verify(slices,rollup) {
  assert.equal(slices.length,9);
  assert.equal(rollup.schema,'fv-live-66-view-census-rollup-v1');
  assert.equal(rollup.production_writes,0);
  const posts=[],images=[];
  for(let i=0;i<slices.length;i++) {
    const s=slices[i];
    assert.equal(s.schema,'fv-66-view-slice-v1');
    assert.equal(s.slice,i+1);
    assert.equal(s.listing_total,66);
    assert.equal(s.production_writes,0);
    assert.equal(s.posts.length,i===8?2:8);
    posts.push(...s.posts);images.push(...s.images);
  }
  assert.equal(posts.length,66);
  assert.equal(new Set(posts.map(p=>p.id)).size,66,'duplicate post');
  assert.equal(images.length,361);
  assert.deepEqual(images.length,rollup.totals.image_slots);
  assert.equal(rollup.totals.posts,66);
  const kinds={},hosts={};let dimless=0,nonresponsive=0,wider=0,dups=0,thirdParty=0;
  for(const x of images) {
    checkSource(x);
    kinds[x.route_type]=(kinds[x.route_type]||0)+1;
    hosts[x.origin_host]=(hosts[x.origin_host]||0)+1;
    if(!x.width_attr||!x.height_attr)dimless++;
    if(!x.has_srcset||!x.has_sizes)nonresponsive++;
    if(x.width_attr>960)wider++;
    if(x.route_type.startsWith('third_party'))thirdParty++;
  }
  for(const p of posts) {
    assert.equal(p.list_modified,p.view_modified,'snapshot drift '+p.id);
    const owned=images.filter(x=>x.post_id===p.id);
    assert.equal(owned.length,p.image_slots,'slot count '+p.id);
    assert.ok(owned.every((im,i)=>im.slot===i),'slot numbering '+p.id);
    assert.equal(owned.filter(x=>x.route_type.startsWith('third_party')).length,p.third_party_slots,'third-party count '+p.id);
    const prior=new Set();
    for(const im of owned){if(prior.has(im.authored_view_src))dups++;prior.add(im.authored_view_src);}
  }
  assert.equal(thirdParty,294);
  assert.equal(rollup.totals.external_origin_slots,thirdParty);
  assert.deepEqual(rollup.totals.route_types,kinds);
  assert.equal(rollup.totals.missing_explicit_width_or_height,dimless);
  assert.equal(rollup.totals.missing_srcset_or_sizes,nonresponsive);
  assert.equal(rollup.totals.authored_width_over_960,wider);
  assert.equal(rollup.totals.duplicate_visible_src_within_same_post,dups);
  assert.equal(rollup.totals.distinct_source_hosts,Object.keys(hosts).length);
  for(const h of rollup.source_hosts) assert.equal(hosts[h.host],h.count,'host frequency mismatch '+h.host);
  assert.equal(rollup.source_hosts.length,Object.keys(hosts).length);
  const old=posts.filter(p=>p.id<1000),later=posts.filter(p=>p.id>=1000);
  assert.deepEqual({posts:old.length,image_slots:old.reduce((n,p)=>n+p.image_slots,0),external_origin_slots:old.reduce((n,p)=>n+p.third_party_slots,0)},rollup.historical_worklist_61);
  assert.equal(old.length,61);assert.equal(old.reduce((n,p)=>n+p.image_slots,0),355);
  assert.equal(old.reduce((n,p)=>n+p.third_party_slots,0),288);
  assert.equal(later.length,5);assert.equal(later.reduce((n,p)=>n+p.image_slots,0),6);
  assert.equal(later.reduce((n,p)=>n+p.third_party_slots,0),6);
  assert.equal(rollup.reported_broken_42.guest_confirmed_count,null);
  assert.equal(rollup.bandwidth_reduction_claim.verified_percent,null);
  assert.equal(rollup.oversized_library_originals.measured_user_wire_bytes,null);
  assert.equal(rollup.replacement_controls.max_target_width_px,960);
  assert.equal(rollup.replacement_controls.upscale,false);
  assert.equal(rollup.replacement_controls.rehost_or_wordpress_media_upload,'not authorized');
  for(const priority of rollup.priority_image_slots) {
    const [pid,slot]=priority.slot_id.split(':').map(Number);
    const actual=images.find(im=>im.post_id===pid&&im.slot===slot);
    assert.ok(actual,'missing P0 slot '+priority.slot_id);
    assert.equal(priority.view_url,actual.authored_view_src);
    assert.equal(priority.derived_origin_url,actual.source_origin_url);
    assert.equal(priority.guest_http_status,null);
    assert.equal(priority.cached_replacement_authorized,false);
  }
  return {posts:posts.length,images:images.length,external:thirdParty,hosts:Object.keys(hosts).length,missing_dimensions:dimless};
}
if(require.main===module) {
  const {slices,rollup}=readCensus();
  checkGitBlobs(DIR,rollup);
  process.stdout.write(JSON.stringify(verify(slices,rollup))+'\n');
}
module.exports={readCensus,checkGitBlobs,checkSource,verify};
