'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {loadSnapshot}=require('./validate_inventory.cjs'),{validateThresher}=require('./validate_thresher.cjs');
const census=loadSnapshot().parts.flatMap(x=>x.images),template=JSON.parse(fs.readFileSync(path.join(__dirname,'thresher_nhhc_20261030.json'),'utf8'));
const clone=()=>JSON.parse(JSON.stringify(template));
test('positive: all seven original sources, six NHHC matches and safe no-upscale sizes',()=>{
 const result=validateThresher(clone(),census);assert.equal(result.ok,true,result.errors.join(' / '));assert.equal(result.originals_under_960,5);
});
const cases=[
 ['invented 42 successes',x=>x.reported_42_broken_status='VERIFIED'],
 ['invented 76% savings',x=>x.reported_76_percent_weight_savings='76%'],
 ['imaginary browser run',x=>x.guest_browser_run_executed=true],
 ['source URL swap',x=>x.rows[1].source_url=x.rows[0].source_url],
 ['altered historical alt',x=>x.rows[2].stored_alt='generic submarine'],
 ['fake commons page',x=>x.rows[5].commons_file_page=x.rows[4].commons_file_page],
 ['arbitrary host',x=>x.rows[3].commons_file_page='https://attacker.example/File:watertight_door.jpg'],
 ['swapped NHHC accession',x=>x.rows[5].catalog_id='NH 97557'],
 ['invented Trieste official accession',x=>x.rows[4].catalog_id='NH 97520'],
 ['fake NHHC link',x=>x.rows[6].nhhc_record_url='https://example.test'],
 ['upscaled original 578 to 960',x=>x.rows[2].proposed_width_px=960],
 ['distorted aspect ratio',x=>x.rows[0].proposed_height_px=500],
 ['fictional original pixel size',x=>x.rows[0].original_commons_width_px=8000],
 ['falsified 200 HTTP',x=>x.rows[0].guest_browser_http_status=200],
 ['falsified broken browser count',x=>x.rows[2].confirmed_broken_in_browser=true],
 ['fabricated transfer bytes',x=>x.rows[0].guest_browser_transfer_bytes=1234],
 ['fabricated percentage saving',x=>x.rows[1].measured_weight_reduction_pct=76],
 ['fake original hash',x=>x.rows[0].source_asset_hash_sha256='f'.repeat(64)],
 ['fabricated CMS media ID',x=>x.rows[1].wp_media_id=100],
 ['copyright clearance assumed',x=>x.rows[0].reuse_cleared=true],
 ['unapproved WordPress media upload',x=>x.rows[0].wp_media_upload_authorized=true],
 ['unapproved Gutenberg edit',x=>x.rows[0].wp_post_edit_authorized=true],
 ['missing slot',x=>x.rows.splice(0,1)],
 ['duplicate slot',x=>x.rows[1].image_key='220:0'],
 ['ledger count altered',x=>x.verified_nhhc_catalog_crosswalks=7]
];
for(const [label,mutate]of cases)test('reject '+label,()=>{const c=clone();mutate(c);assert.equal(validateThresher(c,census).ok,false,label)});
