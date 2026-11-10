"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path");
const {validateCosmos}=require("./validate_cosmos_279_six_20261110.cjs");
const root=path.join(__dirname);
const audit=JSON.parse(fs.readFileSync(path.join(root,"cosmos_279_six_live_primary_rights_20261110.json"),"utf8"));
const prev=JSON.parse(fs.readFileSync(path.join(root,"coverage_257_exact_pr1703_20261110.json"),"utf8"));
const next=JSON.parse(fs.readFileSync(path.join(root,"coverage_263_exact_pr1703_20261110.json"),"utf8"));
const copy=x=>JSON.parse(JSON.stringify(x));
let passed=0;
function test(name,fn){fn();passed++;console.log("PASS",name)}
test("committed data passes fail-closed validation",()=>assert.equal(validateCosmos(audit,next,prev).ok,true,JSON.stringify(validateCosmos(audit,next,prev).errors)));
test("six precise changes",()=>assert.deepEqual(validateCosmos(audit,next,prev).changed,["279:0","279:1","279:2","279:3","279:4","279:5"]));
test("reject claimed guest 404",()=>{let a=copy(audit);a.rows[5].guest_http_status=404;assert.equal(validateCosmos(a,next,prev).ok,false)});
test("reject fabricated transferred bytes",()=>{let a=copy(audit);a.rows[0].guest_transfer_bytes=100;assert.equal(validateCosmos(a,next,prev).ok,false)});
test("reject unsupported 76 percent savings",()=>{let n=copy(next);n.counts.wire_reduction_76_percent_measured=true;assert.equal(validateCosmos(audit,n,prev).ok,false)});
test("reject source URL substitution",()=>{let a=copy(audit);a.rows[3].original_url="https://example.org/replacement.jpg";assert.equal(validateCosmos(a,next,prev).ok,false)});
test("reject copied/unlicensed assets",()=>{let a=copy(audit);a.rows[0].cache_authorized=true;assert.equal(validateCosmos(a,next,prev).ok,false)});
test("reject unauthorized WordPress upload",()=>{let n=copy(next);n.rows.find(r=>r.slot==="279:0").wordpress_media_upload_authorized=true;assert.equal(validateCosmos(audit,n,prev).ok,false)});
test("reject unrelated changes",()=>{let n=copy(next);n.rows.find(r=>r.slot==="101:1").origin_host="forged.host";assert.equal(validateCosmos(audit,n,prev).ok,false)});
test("reject unsupported 960px enlargement",()=>{let a=copy(audit);a.rows[4].conditional_max960_px=[960,1437];assert.equal(validateCosmos(a,next,prev).ok,false)});
test("reject wrong collage scene",()=>{let a=copy(audit);a.rows[3].source_scene_description="Contains an aircraft";assert.equal(validateCosmos(a,next,prev).ok,false)});
test("reject broken research count",()=>{let n=copy(next);n.counts.researched_unique=264;assert.equal(validateCosmos(audit,n,prev).ok,false)});
test("reject source evidence SHA corruption",()=>{let n=copy(next);n.rows.find(r=>r.slot==="279:3").evidence[0].blob_sha="0".repeat(40);assert.equal(validateCosmos(audit,n,prev).ok,false)});
test("reject fabricated origin status",()=>{let a=copy(audit);a.rows[1].origin_http_status=200;assert.equal(validateCosmos(a,next,prev).ok,false)});
test("reject invented rights clearance",()=>{let n=copy(next);n.rows.find(r=>r.slot==="279:2").candidate_sources[0].item_rights_cleared=true;assert.equal(validateCosmos(audit,n,prev).ok,false)});
console.log(passed+"/"+passed+" native Node test cases passed");

