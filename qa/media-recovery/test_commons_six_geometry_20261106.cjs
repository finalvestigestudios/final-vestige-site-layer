'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {validateSix}=require('./validate_commons_six_geometry_20261106.cjs');
const load=name=>JSON.parse(fs.readFileSync(path.join(__dirname,name),'utf8'));
const base=load('commons_six_native_geometry_20261106.json');
const shards=[load('commons_redirect_20261106_shard01.json'),load('commons_redirect_20261106_shard03.json')];
const clone=()=>structuredClone(base);
test('six source-matched candidates have safe preview geometry',()=>assert.deepEqual(validateSix(clone(),shards),{ok:true,errors:[]}));
test('original Commons Archimedes 665px never enlarged to requested 1280px',()=>{
 const r=base.rows.find(x=>x.key==='268:0');
 assert.deepEqual(r.catalog_dimensions_native_px,[665,448]);
 assert.equal(r.requested_width_parameter_px,1280);
 assert.deepEqual(r.proposed_preview_dimensions_no_upscale_px,[665,448]);
});
function rejects(label,mutate){test(label,()=>{const a=clone();mutate(a);assert.equal(validateSix(a,shards).ok,false);});}
rejects('no fabricated visitor HTTP failure',a=>a.rows[0].browser_http=404);
rejects('no 665-to-960 upscaling',a=>a.rows[0].proposed_preview_dimensions_no_upscale_px[0]=960);
rejects('no skewed historical photographs',a=>a.rows[1].proposed_preview_dimensions_no_upscale_px[1]++);
rejects('no assumed copyright clearance',a=>a.rows[1].license_release_approved=true);
rejects('no invented browser verification',a=>a.rows[1].browser_render_verified=true);
rejects('no foreign source used as exact match',a=>a.rows[2].exact_stored_src='https://elsewhere.org/fake.jpg');
rejects('no substituted Commons title',a=>a.rows[2].commons_file_page_candidate='https://commons.wikimedia.org/wiki/File:Other.jpg');
rejects('no dropped audit row',a=>a.rows.pop());
rejects('no fabricated licensing field',a=>a.rows[1].license_verified=true);
rejects('no unauthorized caching',a=>a.rows[4].media_caching_allowed=true);
rejects('no WordPress writes',a=>a.release.wordpress_writes=1);
rejects('no untrusted provenance URL',a=>a.rows[3].catalog_evidence_url='https://elsewhere.org');
