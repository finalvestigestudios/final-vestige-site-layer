'use strict';
// Run: node qa/media-recovery/test_cross_ledger_43_source_15_oversize_20261109.cjs
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {validate}=require('./validate_cross_ledger_43_source_15_oversize_20261109.cjs');
const ledger=JSON.parse(fs.readFileSync(path.join(__dirname,'cross_ledger_43_source_15_oversize_20261109.json'),'utf8'));
const deepClone=x=>JSON.parse(JSON.stringify(x));
const tests=[
  {name:"forged_browser",mutate:d=>d.source_rows[0].retriever.guest_http=200},
  {name:"forged_broken",mutate:d=>d.source_rows[0].retriever.visitor_broken=true},
  {name:"wrapper_vs_origin",mutate:d=>d.source_rows[0].retriever.origin_http=404},
  {name:"swapped_wrapper",mutate:d=>d.source_rows[0].retriever.result=d.source_rows[1].retriever.result},
  {name:"swapped_originals",mutate:d=>d.source_rows[0].stored_source_url=d.source_rows[1].stored_source_url},
  {name:"unauthorized_cache",mutate:d=>d.source_rows[0].release.cache=true},
  {name:"rights_fabrication",mutate:d=>d.source_rows[0].candidate.item_rights_cleared=true},
  {name:"binary_match_fabrication",mutate:d=>d.source_rows[0].candidate.exact_binary_match=true},
  {name:"catalog_substitution",mutate:d=>d.source_rows[0].candidate.catalog_url="https://example.org/photo"},
  {name:"foreign_post_binding",mutate:d=>d.source_rows[0].post_id=999},
  {name:"duplicate_slot",mutate:d=>d.source_rows[1].slot=d.source_rows[0].slot},
  {name:"source_sha_changed",mutate:d=>d.source_groups[0].source_blob_sha="f".repeat(40)},
  {name:"row_added_browser_verified",mutate:d=>d.source_rows[0].browser_verified=true},
  {name:"oversize_wire_fabricated",mutate:d=>d.oversized_media_rows[0].browser_transfer_bytes=1000},
  {name:"oversize_release_fabricated",mutate:d=>d.oversized_media_rows[0].derivative_authorized=true},
  {name:"oversize_bad_threshold",mutate:d=>d.oversized_media_rows[0].stored_original_bytes=1499999},
  {name:"oversize_large_width",mutate:d=>d.oversized_media_rows[0].conditional_960px=[1920,1280]},
  {name:"claimed_76_percent",mutate:d=>d.counts.proposed_76pct_wire_saving_proven=true},
  {name:"claimed_42_confirmed",mutate:d=>d.historical_inventory.reported_broken_42_guest_confirmed=true},
  {name:"incorrect_stored_bytes",mutate:d=>d.counts.oversized_original_stored_bytes=47096778},
  {name:"cross_group_priority",mutate:d=>d.source_rows[6].priority="P0"},
  {name:"new_unknown_candidate_dimension",mutate:d=>d.source_rows[0].candidate.conditional_960px=[961,720]},
];
assert.equal(validate(ledger).pass,true,JSON.stringify(validate(ledger).errors));
let passed=1;
for(const t of tests){const copy=deepClone(ledger);t.mutate(copy);const result=validate(copy);assert.equal(result.pass,false,'bad evidence accepted: '+t.name);passed++;}
console.log('PASS '+passed+'/'+(tests.length+1)+' immutable-source / fake-browser / rights / source geometry checks');
