'use strict';
const { test }=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const { validate }=require('./validate_archimedes_268_20261116.cjs');
const evidence=JSON.parse(fs.readFileSync(path.join(__dirname,'archimedes_268_ten_image_rights_geometry_20261116.json'),'utf8'));
const changed=(fn)=>{const x=structuredClone(evidence);fn(x);return x};
test('baseline has zero unauthorized releases',()=>assert.equal(validate(evidence).ok,true));
for(let i=0;i<10;i++)test('source slot '+i+' stays pinned',()=>{
  assert.equal(evidence.rows[i].slot,'268:'+i);
  assert.match(evidence.rows[i].authored_url,/^https:\/\//);
  assert.equal(evidence.rows[i].release,'HOLD');
});
const attacks=[
  ['fake HTTP',(a)=>a.rows[0].guest_http_status=200],
  ['fake decode',(a)=>a.rows[1].guest_decoded=true],
  ['fake currentSrc',(a)=>a.rows[2].guest_current_src='https://finalvestige.com/fake.jpg'],
  ['fake wire bytes',(a)=>a.rows[3].guest_transfer_bytes=1024],
  ['fake binary hash',(a)=>a.rows[4].original_binary_sha256='abcdef'],
  ['false matching crop',(a)=>a.rows[5].pixel_crop_match_verified=true],
  ['cache approval',(a)=>a.rows[6].cache_approved=true],
  ['WordPress write approval',(a)=>a.rows[7].wordpress_write_approved=true],
  ['release flip',(a)=>a.rows[8].release='READY'],
  ['960px cap',(a)=>a.rows[6].proposed_review_dimensions.width=1280],
  ['665px upscale',(a)=>a.rows[0].proposed_review_dimensions.width=960],
  ['aspect ratio mismatch',(a)=>a.rows[9].proposed_review_dimensions.height=1200],
  ['license claim removed',(a)=>a.rows[3].project_bank_license=null],
  ['invented item license',(a)=>a.rows[1].item_license='CC-BY-3.0'],
  ['non-HTTPS image',(a)=>a.rows[2].view_url='http://test.invalid/a.jpg'],
  ['revision mismatch',(a)=>a.post.contexts_equal_revision=false],
  ['fake optimization claim',(a)=>a.program_baseline.claimed_savings_percent_unmeasured=0],
  ['false response attributes',(a)=>a.rows[2].view_has_width_height=true],
];
for (const [name,fn] of attacks) test('reject '+name,()=>assert.equal(validate(changed(fn)).ok,false));
