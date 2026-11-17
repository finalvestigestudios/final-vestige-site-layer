'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { classifySource, parseCsv, reconcile } = require('./reconcile_proxy_census_20261103.cjs');
const read = x => JSON.parse(fs.readFileSync(path.join(__dirname, x), 'utf8'));
const parts = Array.from({length:8},(_,i)=>read('parts/'+String(i+1).padStart(2,'0')+'.json'));
const audit = read('proxy_origin_census_delta_20261103.json');
const copy = x => structuredClone(x);
const csv = () => {
  const images=parts.flatMap(p=>p.images);
  const lines=['post_id,stored_img_src_count,offsite_src_count'];
  for(const p of parts.flatMap(x=>x.posts)) {
    const rows=images.filter(x=>x.post_id===p.id);
    let off=rows.filter(x=>classifySource(x.source_url).offsite_origin).length;
    // Recorded 2026-10-30 Site QA counts; exact published differences verified separately.
    if(p.id===285||p.id===291)off--;
    lines.push([p.id,rows.length,off].join(','));
  }
  return lines.join('\n')+'\n';
};
test('reconciles pinned 61 posts, 355 slots and both post-level differences',()=>{
  const r=reconcile(parts,csv(),audit);
  assert.equal(r.posts,61);assert.equal(r.slots,355);
  assert.equal(r.siteqa_offsite,286);assert.equal(r.media_offsite,288);
  assert.deepEqual(r.delta_rows.map(x=>x.post_id),[285,291]);
  assert.equal(r.browser_verified_broken_count,null);
  assert.equal(r.weight_reduction_percent,null);
  assert.equal(r.publish_authorized,false);
});
test('original from outside FV through i0.wp.com is external',()=>{
  assert.equal(classifySource(audit.delta_rows[0].exact_current_source_url).upstream_host,'text-message.blogs.archives.gov');
  assert.equal(classifySource(audit.delta_rows[1].exact_current_source_url).upstream_host,'squawkpoint.com');
  assert.equal(classifySource(audit.delta_rows[0].exact_current_source_url).offsite_origin,true);
});
test('genuine FV Jetpack proxy remains first party',()=>{
  assert.equal(classifySource('https://i0.wp.com/finalvestige.com/wp-content/uploads/a.png?ssl=1').offsite_origin,false);
  assert.equal(classifySource('https://finalvestige.com/example.jpg').offsite_origin,false);
});
test('lookalike and encoded hostile proxy route are not first party',()=>{
  assert.equal(classifySource('https://i1.wp.com/finalvestige.com.evil.org/example.jpg').offsite_origin,true);
  assert.equal(classifySource('https://i2.wp.com/www.finalvestige.com.evil.org/x.png').offsite_origin,true);
});
test('invalid Jetpack upstream path is rejected',()=>{
  assert.throws(()=>classifySource('https://i0.wp.com/wp-content/uploads/x.png'));
  assert.throws(()=>classifySource('https://i0.wp.com/'));
  assert.throws(()=>classifySource('https://i0.wp.com/%2Fmalformed/foo'));
});
test('unsafe source protocol and userinfo blocked',()=>{
  assert.throws(()=>classifySource('javascript:alert(1)'));
  assert.throws(()=>classifySource('https://user:pass@i0.wp.com/finalvestige.com/img.jpg'));
});
test('duplicate CSV post is rejected',()=>assert.throws(()=>parseCsv(csv()+ '291,6,5\n')));
test('tampered third post count is rejected',()=>{
 const changed=csv().replace('432,7,7','432,7,6');
 assert.throws(()=>reconcile(parts,changed,audit));
});
test('fake visitor HTTP or broken claim is rejected',()=>{
 const x=copy(parts);x[2].images.find(i=>i.key==='285:1').actual_http_status=404;
 assert.throws(()=>reconcile(x,csv(),audit));
});
test('post source URL drift must invalidate audit',()=>{
 const x=copy(parts);x[2].images.find(i=>i.key==='285:1').source_url='https://i0.wp.com/finalvestige.com/a.jpg';
 assert.throws(()=>reconcile(x,csv(),audit));
});
test('wrong per-item source candidate rejected',()=>{
 const a=copy(audit);a.delta_rows[0].exact_current_source_url='https://i0.wp.com/example.com/foo.jpg';
 assert.throws(()=>reconcile(parts,csv(),a));
});
test('rights, cache and dimension approvals fail closed',()=>{
 for(const [field,value] of [['rights_clearance','CLEAR'],['wordpress_upload_authorized',true],['wordpress_edit_authorized',true],['output_max_width_px',1200],['intrinsic_source_width_px',1200],['pixel_identity_verified',true],['guest_browser_http_status',200]]) {
  const a=copy(audit);a.delta_rows[0][field]=value;
  assert.throws(()=>reconcile(parts,csv(),a),field);
 }
});
test('new image slot or missing post fails denominator gate',()=>{
 const x=copy(parts);x[0].images.push({...x[0].images[0],key:'621:99',slot:99});x[0].image_count++;
 assert.throws(()=>reconcile(x,csv(),audit));
});
