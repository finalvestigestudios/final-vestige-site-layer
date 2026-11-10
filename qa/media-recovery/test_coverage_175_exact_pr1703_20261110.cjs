"use strict";
const {test}=require("node:test"),assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path");
const {validate}=require("./validate_coverage_175_exact_pr1703_20261110.cjs");
const full=JSON.parse(fs.readFileSync(path.join(__dirname,"coverage_175_exact_pr1703_20261110.json"),"utf8"));
const copy=()=>JSON.parse(JSON.stringify(full));
test("175 exact slots and prior rows immutable",()=>assert.deepEqual(validate(full),[]));
test("last Courrières source included and not browser classified",()=>{assert.equal(full.rows.find(r=>r.slot==="425:8").evidence.length,1);assert.equal(full.rows.find(r=>r.slot==="425:8").guest_broken,null);});
for(const [label,mut] of [
["falsify 76 percent",a=>a.counts.wire_reduction_76_percent_measured=true],
["claim broken 42",a=>a.counts.reported_42_broken_browser_confirmed=true],
["invent HTTP 404",a=>a.rows.find(r=>r.slot==="425:1").guest_http_status=404],
["invent bytes",a=>a.rows.find(r=>r.slot==="425:3").guest_wire_bytes=24000],
["rehost rights bypass",a=>a.rows.find(r=>r.slot==="425:6").rights_cleared=true],
["cache bypass",a=>a.rows.find(r=>r.slot==="425:8").cache_authorized=true],
["unapproved WP upload",a=>a.rows.find(r=>r.slot==="425:2").wordpress_media_upload_authorized=true],
["inaccurate geometry",a=>a.rows.find(r=>r.slot==="425:3").candidate_sources[0].conditional_960px=[960,1200]],
["source changed",a=>a.rows.find(r=>r.slot==="425:4").stored_url="https://other.example/photo.jpg"],
["old evidence changed",a=>a.rows.find(r=>r.slot==="285:5").origin_host="changed.example"],
["duplicate row",a=>a.rows[1].slot=a.rows[0].slot],
["missing new evidence",a=>a.rows.find(r=>r.slot==="425:5").evidence=[]],
["wrong count",a=>a.counts.researched_unique=176],
["tamper source pin",a=>a.rows.find(r=>r.slot==="425:7").evidence[0].blob_sha="bad"],
["change P0 queue",a=>a.original_six_p0_guest_queue.reverse()]
])test("reject "+label,()=>{const x=copy();mut(x);assert.notDeepEqual(validate(x),[]);});
