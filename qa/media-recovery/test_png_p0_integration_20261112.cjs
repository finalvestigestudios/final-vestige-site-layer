'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),zlib=require('node:zlib');
const {verifyP0ReviewEvidence,sha256,gitBlobSha}=require('./verify_p0_review_evidence_20261112.cjs');
const tiny=Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+ip1sAAAAASUVORK5CYII=','base64');
const table=Array.from({length:256},(_,i)=>{let c=i;for(let j=0;j<8;j++)c=c&1?0xedb88320^(c>>>1):c>>>1;return c>>>0;});
function chunk(tag,data){
 const b=Buffer.alloc(data.length+12);b.writeUInt32BE(data.length);b.write(tag,4);data.copy(b,8);
 let c=0xffffffff;for(let i=4;i<b.length-4;i++)c=table[(c^b[i])&255]^(c>>>8);
 b.writeUInt32BE((c^0xffffffff)>>>0,b.length-4);return b;
}
function invalidButSignedPng(payload){return Buffer.concat([tiny.subarray(0,33),chunk('IDAT',payload),tiny.subarray(tiny.length-12)]);}
function fixture(){
 const p={slot:'418:1',post_id:418,published_original_src:'https://media.defense.gov/exact.jpg',screenshot_sha256:null};
 const r={candidate_catalog:'https://www.history.uscg.mil/item',asset_url:'https://media.defense.gov/asset.png',asset_sha256:null,replacement_mode:'SAME_PHOTO',geometry:{output_width:1,output_height:1}};
 const rights={slot:p.slot,candidate_catalog:r.candidate_catalog,asset_url:r.asset_url,asset_sha256:null,item_level_reuse_permission_verified:true,credit_and_restrictions_recorded:true,replacement_mode:r.replacement_mode,review_basis_url:r.candidate_catalog,attribution_text:'U.S. Coast Guard archive test'};
 const a={screenshot_png:Buffer.from(tiny),candidate_asset:Buffer.from(tiny)};
 function sign(){
  p.screenshot_sha256=sha256(a.screenshot_png);r.asset_sha256=sha256(a.candidate_asset);
  rights.asset_sha256=r.asset_sha256;a.rights_review_text=JSON.stringify(rights);
  r.rights_review_git_blob_sha=gitBlobSha(a.rights_review_text);
  a.capture_text=JSON.stringify(p);p.capture_git_blob_sha=gitBlobSha(a.capture_text);
 }
 sign();return {p,r,a,sign};
}
test('byte-authenticated baseline synthetic raster permits review, not production',()=>{
 const f=fixture(),x=verifyP0ReviewEvidence(f.p,f.r,f.a);
 assert.equal(x.verified,true);assert.equal(x.production_write_allowed,false);assert.equal(x.third_party_cache_allowed,false);
});
test('CRC-valid corrupt deflate in signed SCREENSHOT cannot clear staging review',()=>{
 const f=fixture();f.a.screenshot_png=invalidButSignedPng(Buffer.from('INVALID_ZLIB'));f.sign();
 const x=verifyP0ReviewEvidence(f.p,f.r,f.a);
 assert.equal(x.verified,false);assert.equal(x.reason,'MISSING_OR_INVALID_ARTIFACT_BYTES');
});
test('CRC-valid corrupt deflate in signed CANDIDATE cannot clear staging review',()=>{
 const f=fixture();f.a.candidate_asset=invalidButSignedPng(Buffer.from('INVALID_ZLIB'));f.sign();
 const x=verifyP0ReviewEvidence(f.p,f.r,f.a);
 assert.equal(x.verified,false);assert.equal(x.reason,'ASSET_FORMAT_OR_OUTPUT_GEOMETRY_UNVERIFIED');
});
test('valid zlib but invalid filter in signed candidate is held',()=>{
 const f=fixture();f.a.candidate_asset=invalidButSignedPng(zlib.deflateSync(Buffer.from([5,255,255])));f.sign();
 assert.equal(verifyP0ReviewEvidence(f.p,f.r,f.a).verified,false);
});
