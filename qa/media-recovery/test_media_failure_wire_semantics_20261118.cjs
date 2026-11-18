"use strict";
const test=require("node:test"),assert=require("node:assert/strict");
const {assessImageWire}=require("./media_failure_wire_semantics_20261118.cjs");
const base=()=>({request_id:"12.3",from_cache:false,from_service_worker:false,
 transfer_metric:"CDP_ENCODED_DATALENGTH",transfer_bytes:200,http_status:200,
 mime:"image/jpeg",decoded:true,natural_width:960,natural_height:640});
test("before genuine 404 HTML counts broken, not image bytes",()=>{
 const m={...base(),http_status:404,mime:"text/html",decoded:false,natural_width:0,natural_height:0,transfer_bytes:122};
 assert.deepEqual(assessImageWire(m,"before"),{errors:[],counted_bytes:0,broken:true,origin_error:true});
});
test("before failed 404 image MIME still excludes error bytes",()=>{
 const m={...base(),http_status:404,decoded:false,natural_width:0,natural_height:0,transfer_bytes:90};
 assert.equal(assessImageWire(m,"before").counted_bytes,0);
 assert.deepEqual(assessImageWire(m,"before").errors,[]);
});
test("before 404 with zero encodedDataLength is measured, not invented bytes",()=>{
 const m={...base(),http_status:404,mime:"text/plain",decoded:false,natural_width:0,natural_height:0,transfer_bytes:0};
 assert.deepEqual(assessImageWire(m,"before").errors,[]);
 assert.equal(assessImageWire(m,"before").counted_bytes,0);
});
test("before 200 empty corrupt image is broken and has zero image bytes",()=>{
 const m={...base(),decoded:false,natural_width:0,natural_height:0,transfer_bytes:0};
 assert.deepEqual(assessImageWire(m,"before").errors,[]);
 assert.equal(assessImageWire(m,"before").broken,true);
});
test("before corrupt positive 200 image payload counts transferred image bytes",()=>{
 const m={...base(),decoded:false,natural_width:0,natural_height:0};
 assert.equal(assessImageWire(m,"before").counted_bytes,200);
 assert.equal(assessImageWire(m,"before").broken,true);
});
test("after 200 decoded image counts real wire bytes",()=>{
 assert.deepEqual(assessImageWire(base(),"after"),{errors:[],counted_bytes:200,broken:false,origin_error:false});
});
test("after 404 is never accepted as recovered",()=>{
 const m={...base(),http_status:404,mime:"text/html",decoded:false,natural_width:0,natural_height:0};
 const x=assessImageWire(m,"after");assert.ok(x.errors.includes("response"));assert.ok(x.errors.includes("broken_after"));
});
test("after corrupt 200 rejects regardless of transfer",()=>{
 const m={...base(),decoded:false,natural_width:0,natural_height:0};
 assert.ok(assessImageWire(m,"after").errors.includes("broken_after"));
});
test("before 200 HTML masquerading as image is rejected",()=>{
 const m={...base(),mime:"text/html"};
 assert.ok(assessImageWire(m,"before").errors.includes("response"));
});
test("before 404 falsely marked decoded is rejected",()=>{
 const m={...base(),http_status:404,mime:"text/html"};
 const x=assessImageWire(m,"before");assert.ok(x.errors.includes("response"));assert.ok(x.errors.includes("decoded_error"));
});
test("decoded 200 with zero transfer is rejected",()=>{
 const x=assessImageWire({...base(),transfer_bytes:0},"before");assert.ok(x.errors.includes("unmeasured_wire"));
});
test("unknown bytes or negative bytes are not zero-byte evidence",()=>{
 for(const n of [null,undefined,-1,1.5,"0"]){const m={...base(),http_status:404,mime:"text/html",decoded:false,natural_width:0,natural_height:0,transfer_bytes:n};assert.ok(assessImageWire(m,"before").errors.includes("unmeasured_wire"));}
});
test("cache and service-worker responses cannot justify byte savings",()=>{
 for(const field of ["from_cache","from_service_worker"]){assert.ok(assessImageWire({...base(),[field]:true},"after").errors.includes("unmeasured_wire"));}
});
test("no-response transport failure status zero is on hold",()=>{
 const m={...base(),http_status:0,decoded:false,natural_width:0,natural_height:0,transfer_bytes:0};
 assert.ok(assessImageWire(m,"before").errors.includes("response"));
});
test("non-image 500 HTML after is on hold",()=>{
 const m={...base(),http_status:500,mime:"text/html",decoded:false,natural_width:0,natural_height:0};
 assert.ok(assessImageWire(m,"after").errors.includes("response"));
});
test("404 JSON error document is allowed only before and excluded",()=>{
 const m={...base(),http_status:404,mime:"application/problem+json",decoded:false,natural_width:0,natural_height:0};
 assert.deepEqual(assessImageWire(m,"before").errors,[]);
 assert.ok(assessImageWire(m,"after").errors.includes("broken_after"));
});
