'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {validate}=require('./validate_coverage_93_20261109.cjs');
const m=JSON.parse(fs.readFileSync(path.join(__dirname,'coverage_93_exact_reconciliation_20261109.json'),'utf8'));
const c=JSON.parse(fs.readFileSync(path.join(__dirname,'offsite_upstream_288_20261109.json'),'utf8'));
const clone=x=>JSON.parse(JSON.stringify(x));
test('93 unique sources; exact 96 evidence records; three overlaps',()=>{const v=validate(m,c);assert.equal(v.distinct,93);assert.equal(v.pending,195);assert.equal(v.evidence_count,96);});
for(const [name,mutate] of Object.entries({
 'duplicate slot':x=>x.rows[1].slot=x.rows[0].slot,
 'alter source url':x=>x.rows[0].stored_url+='?changed=1',
 'forge visitor 404':x=>x.rows[0].guest_http_status=404,
 'forge visitor decode':x=>x.rows[0].guest_decoded_px=[960,720],
 'forge visitor bytes':x=>x.rows[0].guest_transfer_bytes=300,
 'forge visitor failure':x=>x.rows[0].guest_broken=true,
 'pretend rights clearance':x=>x.rows[0].rights_cleared=true,
 'allow image downloads':x=>x.rows[0].asset_download_authorized=true,
 'allow media cache':x=>x.rows[0].cdn_cache_authorized=true,
 'allow WP upload':x=>x.rows[0].wordpress_upload_authorized=true,
 'allow WP blocks':x=>x.rows[0].post_block_rewrite_authorized=true,
 'invent weight saving':x=>x.counts.image_transfer_savings_pct=76,
 'miscount research':x=>x.counts.researched_distinct=94,
 'hide duplicated evidence':x=>x.rows.find(r=>r.slot==='418:5').research_evidence.pop(),
 'invent overlap slot':x=>x.overlap_slots[2]='407:1',
 'replace primary audit SHA':x=>x.sources[0].git_blob_sha='0'.repeat(40),
 'break item SHA custody':x=>x.rows[0].research_evidence[0].git_blob_sha='0'.repeat(40),
 'alter source post id':x=>x.rows[0].post_id=999,
 'claim catalog exact match':x=>{const r=x.rows.find(r=>r.archival_candidates.length);r.archival_candidates[0].exact_image_match_verified=true;},
 'invent catalog rights':x=>{const r=x.rows.find(r=>r.archival_candidates.length);r.archival_candidates[0].item_rights_cleared=true;},
 'upscale catalog geometry':x=>{const r=x.rows.find(r=>r.archival_candidates.some(a=>a.claimed_960px_from_catalog));r.archival_candidates.find(a=>a.claimed_960px_from_catalog).claimed_960px_from_catalog=[1920,1080];},
 'drop researched slot':x=>x.rows.pop(),
 'inject foreign slot':x=>x.rows[0].slot='999:999'
}))test('reject '+name,()=>{const x=clone(m);mutate(x);assert.throws(()=>validate(x,c));});
