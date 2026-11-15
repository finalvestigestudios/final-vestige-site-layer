'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const SOURCE_SHAS = Object.freeze({"cross":"8526557c7a5138e1ca22a347e3f9839503d48b2c","navy7":"86d4ed137fb27a2db7b77f11077461936fa53736","primary18":"ac51e43f9c300e7b19820b6c7f17bdb02db93718","coastal12":"7980bde96151c418e082f3cc3add077477c9ba48","pelee4":"bca94b9db11d804af03a5b0809a036d7a9e967ed","molasses4":"4cfde7163cb3b909a494e5e2fea5a8a3a0767ade","usgs8":"f20f95ab80d63418909dafb22b984d94bd10a4f2"});
const REQUIRED_OVERLAPS = Object.freeze(['418:1','418:2','418:5']);
function validate(m,c) {
  assert.equal(m.schema,'fv-media-exact-source-coverage-v2');
  assert.equal(m.frozen_census.git_blob_sha,'92a904c8da1ace1f972b2f00adf1a4847dde2b99');
  assert.equal(c.schema,'fv-media-80-host-upstream-v1');
  assert.equal(c.rows.length,288);
  assert.equal(m.rows.length,93);
  assert.deepEqual(m.overlap_slots,REQUIRED_OVERLAPS);
  assert.deepEqual(m.counts,{researched_distinct:93,unresearched:195,total_upstream:288,source_records:96,overlapping_evidence_records:3,guest_browser_confirmed_broken:0,guest_browser_confirmed_loaded:0,oversized_wp_originals:15,oversized_wp_stored_original_bytes:47096779,image_transfer_savings_pct:null,unverified_historical_broken_report:42});
  assert.equal(m.sources.length,7);
  const all = new Map(c.rows.map(r=>[r.slot,r]));
  const evidenceCount = Object.create(null);
  for(const s of m.sources){assert.equal(s.git_blob_sha,SOURCE_SHAS[s.batch]);assert.equal(s.ref.startsWith('media/')||s.ref.startsWith('qa/'),true);evidenceCount[s.batch]=0;}
  const seen = new Set(), multiple = [];
  for(const r of m.rows){
    assert.equal(seen.has(r.slot),false,'duplicate slot: '+r.slot);seen.add(r.slot);
    const src=all.get(r.slot);assert.ok(src,'slot missing: '+r.slot);
    assert.equal(r.post_id,src.post_id);assert.equal(r.post_url,src.post_url);
    assert.equal(r.stored_url,src.stored_url);assert.equal(r.upstream_origin_host,src.origin_host);
    assert.ok(/^https:\/\//.test(r.stored_url));
    for(const key of ['guest_http_status','guest_decoded_px','guest_transfer_bytes','guest_broken'])assert.equal(r[key],null,key+' must remain UNKNOWN');
    for(const key of ['rights_cleared','asset_download_authorized','cdn_cache_authorized','wordpress_upload_authorized','post_block_rewrite_authorized'])assert.equal(r[key],false,key+' forbidden');
    assert.ok(Array.isArray(r.research_evidence)&&r.research_evidence.length>=1);
    if(r.research_evidence.length>1)multiple.push(r.slot);
    for(const e of r.research_evidence){
      assert.equal(e.git_blob_sha,SOURCE_SHAS[e.batch],'untracked source blob');
      assert.ok(m.sources.some(s=>s.batch===e.batch&&s.ref===e.ref&&s.path===e.path));
      evidenceCount[e.batch]++;
    }
    assert.ok(Array.isArray(r.archival_candidates));
    for(const a of r.archival_candidates){
      assert.ok(/^https:\/\//.test(a.catalog_url));
      assert.equal(a.exact_image_match_verified,false);
      assert.equal(a.item_rights_cleared,false);
      assert.equal(a.from_batch in SOURCE_SHAS,true);
      if(a.claimed_960px_from_catalog!==null){
        assert.equal(a.claimed_960px_from_catalog.length,2);
        const [w,h]=a.claimed_960px_from_catalog;
        assert.ok(Number.isInteger(w)&&w>0&&w<=960&&Number.isInteger(h)&&h>0);
        if(a.native_catalog_px){
          const [nw,nh]=a.native_catalog_px;
          assert.ok(w<=nw&&h<=nh,'upscale forbidden');
          assert.ok(Math.abs(w/h-nw/nh)<0.025,'aspect drift');
        }
      }
    }
  }
  assert.deepEqual(multiple,REQUIRED_OVERLAPS);
  for(const s of m.sources)assert.equal(evidenceCount[s.batch],s.source_rows,'source evidence lost: '+s.batch);
  assert.equal(seen.size+c.rows.filter(r=>!seen.has(r.slot)).length,288);
  return {distinct:seen.size,pending:288-seen.size,overlap:multiple,evidence_count:Object.values(evidenceCount).reduce((a,b)=>a+b,0)};
}
if(require.main===module){
 const root=path.resolve(__dirname,'..','..');
 const m=JSON.parse(fs.readFileSync(path.join(__dirname,'coverage_93_exact_reconciliation_20261109.json'),'utf8'));
 const c=JSON.parse(fs.readFileSync(path.join(__dirname,'offsite_upstream_288_20261109.json'),'utf8'));
 process.stdout.write(JSON.stringify(validate(m,c))+'\n');
}
module.exports={validate};
