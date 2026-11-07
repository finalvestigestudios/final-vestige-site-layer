'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const data=require('./navy_five_gap_closure_20261106.json');
const {validateBatch}=require('./validate_navy_five_gap_closure_20261106.cjs');
const clone=v=>JSON.parse(JSON.stringify(v));
const tests=[
  [
    "baseline valid",
    "x=>{}"
  ],
  [
    "fabricated visitor broken",
    "x=>x.records[0].evidence.visitor_broken=true"
  ],
  [
    "faked origin 404",
    "x=>x.records[1].evidence.published_origin_http_status=404"
  ],
  [
    "faked guest 200",
    "x=>x.records[0].evidence.guest_http_status=200"
  ],
  [
    "faked wire bytes",
    "x=>x.records[1].evidence.guest_cold_wire_bytes=9500"
  ],
  [
    "premature rehosting",
    "x=>x.records[0].rights.can_rehost=true"
  ],
  [
    "unauthorized WP write",
    "x=>x.records[0].actions.wordpress_written=true"
  ],
  [
    "unverified output generated",
    "x=>x.records[0].primary_candidate.preview_candidate.output_generated=true"
  ],
  [
    "unsafe 1280px",
    "x=>x.records[0].primary_candidate.preview_candidate.width=1280"
  ],
  [
    "wrong preview aspect",
    "x=>x.records[1].primary_candidate.preview_candidate.height=200"
  ],
  [
    "claim false 76%",
    "x=>x.baseline.measured_savings_percent=76"
  ],
  [
    "claim 42 confirmed",
    "x=>x.baseline.visitor_verified_broken_count=42"
  ],
  [
    "alternative promoted",
    "x=>x.records[3].primary_candidate={catalog_id:\"NH 68705\"}"
  ],
  [
    "1969 misdated",
    "x=>x.records[3].alternatives[0].date=\"1968-01-23\""
  ],
  [
    "fake catalogue id verified",
    "x=>x.results.exact_binary_verified=4"
  ],
  [
    "wrong frozen original URL",
    "x=>x.records[0].original_src=x.records[1].original_src"
  ],
  [
    "row missing",
    "x=>x.records.pop()"
  ],
  [
    "excess record",
    "x=>x.records.push(clone(x.records[0]))"
  ],
  [
    "missing attribution gate",
    "x=>x.records[2].rights.clearance=\"PUBLIC_DOMAIN_VERIFIED\""
  ],
  [
    "unknown-pixel pretended known",
    "x=>x.records[2].primary_candidate.preview_candidate={width:960,height:960}"
  ],
  [
    "wrong baseline SHA",
    "x=>x.baseline.ledger_blob_sha=\"0\".repeat(40)"
  ]
];
for(const [name,mutator] of tests){
 test(name,()=>{const v=clone(data);const fn=Function('return ('+mutator+')')();fn(v);const result=validateBatch(v);assert.equal(result.ok,name==='baseline valid',JSON.stringify(result.errors));});
}
