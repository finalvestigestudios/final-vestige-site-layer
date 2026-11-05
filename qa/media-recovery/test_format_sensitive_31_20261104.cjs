'use strict';
// Native Node checkout regression suite: all media/network fields remain unverified.
// No image downloads, local asset modification, WordPress writes or scraping.
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {validate}=require('./validate_format_sensitive_31_20261104.cjs');
const d=__dirname;
const raw=fs.readFileSync(path.join(d,'format_sensitive_31_sitewide_20261104.json'),'utf8');
const root=JSON.parse(raw),large=JSON.parse(fs.readFileSync(path.join(d,'large_first_party_20261101.json'),'utf8'));
const parts=Array.from({length:8},(_,i)=>{const name='qa/media-recovery/parts/'+String(i+1).padStart(2,'0')+'.json';return{name,raw:fs.readFileSync(path.join(d,'parts',String(i+1).padStart(2,'0')+'.json'),'utf8')}});
const clone=()=>JSON.parse(raw),mutate=(f)=>{const v=clone();f(v);return validate(v,parts,large)};
test('exact frozen 355-source 31-sensitive cohort passes every gate',()=>{
 const r=validate(root,parts,large);assert.deepEqual(r.errors,[]);assert.equal(r.ok,true);
 assert.deepEqual(r.types,{png:28,gif:2,svg:1});
});
test('slot counts cannot be silently truncated',()=>{const r=mutate(x=>x.rows.pop());assert.equal(r.ok,false)});
test('URL changes cannot pretend to be pinned WordPress source',()=>{const r=mutate(x=>x.rows[0].original_url='https://other.example/fake.png');assert.equal(r.ok,false)});
test('false original ALT cannot be published as archived',()=>{const r=mutate(x=>x.rows[0].original_alt='Different description');assert.equal(r.ok,false)});
test('fabricated HTTP 404 is rejected',()=>{const r=mutate(x=>x.rows[0].actual_guest_browser_http_status=404);assert.equal(r.ok,false)});
test('fabricated decode failure is rejected',()=>{const r=mutate(x=>x.rows[0].actual_guest_browser_decode_ok=false);assert.equal(r.ok,false)});
test('fabricated transferred bytes are rejected',()=>{const r=mutate(x=>x.rows[0].actual_browser_transfer_bytes=0);assert.equal(r.ok,false)});
test('fabricated CLS is rejected',()=>{const r=mutate(x=>x.rows[0].actual_lab_cls=0);assert.equal(r.ok,false)});
test('unverified binary cannot be called browser broken',()=>{const r=mutate(x=>x.rows[0].broken_original_in_browser=true);assert.equal(r.ok,false)});
test('cache/rehost permission cannot be silently granted',()=>{const r=mutate(x=>x.rows[0].rehost_or_cache_approved=true);assert.equal(r.ok,false)});
test('production WordPress writes cannot be permitted',()=>{const r=mutate(x=>x.rows[0].production_write_approved=true);assert.equal(r.ok,false)});
test('rights review cannot be automatically declared complete',()=>{const r=mutate(x=>x.rows[0].rights_status='CLEARED');assert.equal(r.ok,false)});
test('output bigger than 960px cannot be authorized',()=>{const r=mutate(x=>x.rows.find(q=>q.first_party_oversized_wordpress_original).max_width_conditional_px=1280);assert.equal(r.ok,false)});
test('invented dimensions on unmeasured archival graphics fail',()=>{const r=mutate(x=>x.rows.find(q=>!q.first_party_oversized_wordpress_original).max_width_conditional_px=960);assert.equal(r.ok,false)});
test('wrong original media storage bytes fail provenance gate',()=>{
 const r=mutate(x=>x.rows.find(q=>q.first_party_oversized_wordpress_original).first_party_oversized_wordpress_original.media_original_storage_bytes=1);assert.equal(r.ok,false)
});
test('reported 42 browser failures cannot become confirmed',()=>{const r=mutate(x=>x.inventory.reported_broken_42='CONFIRMED');assert.equal(r.ok,false)});
test('76pct savings cannot become measured',()=>{const r=mutate(x=>x.inventory.claimed_76pct_image_wire_reduction='VERIFIED');assert.equal(r.ok,false)});
test('existing Site QA P0 order remains unchanged',()=>{const r=mutate(x=>x.priorities.reverse());assert.equal(r.ok,false)});
test('stale census blob SHA is rejected',()=>{
 const pp=parts.map(x=>({...x}));pp[0].raw=pp[0].raw+'\n';const r=validate(root,pp,large);assert.equal(r.ok,false);
});
test('archival record with invented cleared reuse rights fails closed',()=>{
 const r=mutate(x=>x.rows.find(q=>q.catalog_candidate).catalog_candidate.reuse_rights_status='public domain');assert.equal(r.ok,false);
});
