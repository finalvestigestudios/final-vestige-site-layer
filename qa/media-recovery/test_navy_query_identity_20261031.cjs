'use strict';
/** Regression against the actual 61-post snapshot. No HTTP, media or CMS writes. */
const {test}=require('node:test'),assert=require('node:assert/strict');
const {loadSnapshot}=require('./validate_inventory.cjs');
const {sameSource}=require('./browser_probe_core.cjs');
const ledger=require('./navy_query_identity_20261031.json');
const snapshot=loadSnapshot();
const all=snapshot.parts.flatMap(p=>p.images);
const canonicalPath=u=>String(u).split('?')[0];

test('site-wide query-image census is grounded in the fixed 355-image snapshot',()=>{
 assert.equal(snapshot.summary.post_count,61);
 assert.equal(all.length,355);
 assert.equal(all.filter(x=>x.source_url.includes('?')).length,126);
 assert.equal(ledger.scope.query_bearing_stored_urls,126);
 const p=new Map();
 for(const im of all){
  const k=canonicalPath(im.source_url),rows=p.get(k)||[];
  rows.push(im.source_url);p.set(k,rows);
 }
 const groups=[...p].filter(([u,a])=>new Set(a).size>1);
 assert.equal(groups.length,1);
 assert.equal(groups[0][0],ledger.shared_endpoint);
 assert.equal(groups[0][1].length,6);
});
test('all six distinct Navy source URLs are exact snapshot images, not invented substitutes',()=>{
 assert.equal(ledger.rows.length,6);
 const keys=new Set();
 for(const row of ledger.rows){
  assert.equal(keys.has(row.image_key),false);keys.add(row.image_key);
  const im=all.find(x=>x.key===row.image_key);
  assert.ok(im);
  assert.equal(row.stored_url,im.source_url);
  assert.equal(row.stored_alt,im.alt);
  assert.equal(row.post_url,im.post_url);
  assert.equal(canonicalPath(row.stored_url),ledger.shared_endpoint);
 }
});
test('historically distinct Navy image selectors can never be classified as same source',()=>{
 const a=ledger.rows.map(r=>r.stored_url);
 for(let i=0;i<a.length;i++)for(let j=i+1;j<a.length;j++)
  assert.equal(sameSource(a[i],a[j]),false);
 assert.equal(new Set(a).size,6);
});
test('Navy download rendition can change without losing image= archival identity',()=>{
 const src=ledger.rows[0].stored_url;
 const small=src.replace('rendition=cq5dam.web.1280.1280.jpeg','rendition=cq5dam.web.960.960.jpeg');
 assert.equal(sameSource(src,small),true);
 assert.equal(sameSource(small,ledger.rows[1].stored_url),false);
});
test('Navy catalog ID on each primary record is a literal component of the image selector',()=>{
 for(const r of ledger.rows){
  assert.ok(r.official_primary_record_url.startsWith('https://www.history.navy.mil/'));
  assert.ok(r.official_catalog_id_supported);
  const clean=x=>x.toLowerCase().replaceAll(' ','');
  assert.ok(clean(r.archive_encoded_image_selector).includes(clean(r.official_catalog_id)));
 }
});
test('every catalog candidate is a rights-gated, <=960px, non-upscaling plan only',()=>{
 for(const r of ledger.rows){
  assert.equal(r.proposed_max_width_px,960);
  assert.equal(r.no_upscale,true);
  assert.equal(r.preserve_aspect_ratio,true);
  assert.equal(r.proposed_exact_dimensions_px,null);
  assert.equal(r.original_file_binary_sha256,null);
  assert.equal(r.rights_clearance_for_republication,false);
  assert.equal(r.wp_media_upload_authorized,false);
  assert.equal(r.wp_article_rewrite_authorized,false);
  assert.equal(r.current_visitor_http_status,null);
  assert.equal(r.verified_broken_in_visitor_browser,null);
  assert.equal(r.current_visitor_transfer_bytes,null);
 }
 assert.equal(ledger.production_writes,false);
});
test('42 broken and 76 percent saved remain unsupported, not asserted audit outcomes',()=>{
 assert.equal(ledger.scope.founder_report_verification,'NOT_VERIFIED');
 assert.equal(ledger.scope.claimed_savings_verification,'NOT_MEASURED');
 assert.equal(ledger.scope.confirmed_broken_browser_image_count,null);
});
