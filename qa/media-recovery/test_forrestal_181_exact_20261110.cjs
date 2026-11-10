"use strict";
const {test}=require("node:test"),assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path");
const {validateBatch,validateCoverage}=require("./validate_forrestal_181_exact_20261110.cjs");
const read=p=>JSON.parse(fs.readFileSync(path.join(__dirname,p),"utf8"));
const b=read("forrestal_289_six_retriever_dvids_20261110.json"), i=read("parts/03.json"),n=read("coverage_181_exact_pr1703_20261110.json"),o=read("coverage_175_exact_pr1703_20261110.json");
const cp=x=>JSON.parse(JSON.stringify(x));
test("six true source URLs and observed retriever state",()=>assert.deepEqual(validateBatch(b,i),[]));
test("181/288 ledger and all unrelated positions immutable",()=>assert.deepEqual(validateCoverage(n,b,o),[]));
const batchMut=[
["fake visitor 403",x=>x.rows[4].retrieval.guest_http_status=403],
["fake loaded 200",x=>x.rows[1].retrieval.guest_http_status=200],
["fake wire bytes",x=>x.rows[0].retrieval.guest_wire_bytes=1000],
["invent natural pixels",x=>x.rows[2].retrieval.guest_decoded_px=[640,516]],
["false cache proof",x=>x.rows[3].retrieval.uncached_guest_verified=true],
["change published URL",x=>x.rows[1].stored_url="https://changed.invalid/photo.jpg"],
["alter original alt",x=>x.rows[3].stored_alt="false"],
["lie about tool success",x=>x.rows[4].retrieval.outcome="IMAGE_RENDERED"],
["license bypass",x=>x.rows[2].candidate.rights_cleared=true],
["binary match invented",x=>x.rows[0].candidate.exact_binary_match_sha256="abc"],
["source-photo substitution",x=>x.rows[1].candidate.relationship="PUBLISHED_SOURCE_CATALOG"],
["2021 photo mistaken for 1967",x=>x.rows[4].candidate.chronology_note="1967 fire"],
["2013 photo mistaken for 1967",x=>x.rows[5].candidate.chronology_note="1967 fire"],
["mis-sized memorial",x=>x.rows[5].candidate.conditional_960px=[960,540]],
["wrong provenance",x=>x.rows[4].candidate.catalog_id="different"],
["unapproved WP upload",x=>x.rows[5].permissions.wordpress_upload=true],
["unapproved cache",x=>x.rows[0].permissions.cache=true],
["unapproved editor edit",x=>x.rows[1].permissions.post_block_edit=true],
["unapproved expenditure",x=>x.spend_usd=1]
];
for(const [name,m] of batchMut)test("reject "+name,()=>{let x=cp(b);m(x);assert.notDeepEqual(validateBatch(x,i),[]);});
const ledgerMut=[
["inflated research",x=>x.counts.researched_unique=182],
["fabricated 76 percent",x=>x.counts.wire_reduction_76_percent_measured=true],
["fabricated 42 broken",x=>x.counts.reported_42_broken_browser_confirmed=true],
["old slot changed",x=>x.rows.find(r=>r.slot==="285:5").origin_host="changed.invalid"],
["original URL changed",x=>x.rows.find(r=>r.slot==="289:2").stored_url="https://changed.invalid"],
["fabricated visitor status",x=>x.rows.find(r=>r.slot==="289:5").guest_http_status=200],
["rights bypass",x=>x.rows.find(r=>r.slot==="289:4").cache_authorized=true],
["duplicate slot",x=>x.rows.find(r=>r.slot==="289:1").slot="289:0"],
["wrong batch SHA",x=>x.rows.find(r=>r.slot==="289:3").evidence[0].blob_sha="bad"],
["evidence removed",x=>x.rows.find(r=>r.slot==="289:0").evidence=[]],
["wrong P0",x=>x.original_six_p0_guest_queue.reverse()]
];
for(const [name,m] of ledgerMut)test("reject ledger "+name,()=>{let x=cp(n);m(x);assert.notDeepEqual(validateCoverage(x,b,o),[]);});
