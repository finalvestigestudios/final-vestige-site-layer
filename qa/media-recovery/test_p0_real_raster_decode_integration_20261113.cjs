'use strict';
/** Synthetic self-authored images only; no third-party downloads or publication. */
const test=require('node:test'),assert=require('node:assert/strict'),{spawnSync}=require('node:child_process');
const {verifyP0SourceMasterEvidence,verifyP0ReviewEvidence,sha256,gitBlobSha}=require('./verify_p0_review_evidence_20261112.cjs');
const {fullyDecodedJpegWebpGeometry:decode}=require('./verify_image_pixels_pillow_20261113.cjs');
const png=Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+ip1sAAAAASUVORK5CYII=','base64');
function synthetic(fmt,orientation=1){
 const py="import sys, io\nfrom PIL import Image\na=Image.new('RGB',(2,1),(128,45,190))\nb=io.BytesIO()\nkw={}\nif sys.argv[1]=='JPEG':\n e=Image.Exif();e[274]=int(sys.argv[2]);kw['exif']=e\na.save(b,format=sys.argv[1],**kw)\nsys.stdout.buffer.write(b.getvalue())";
 const p=spawnSync('python3',['-I','-B','-c',py,fmt,String(orientation)],{encoding:null,timeout:5000,maxBuffer:8192});
 return p.status===0&&!p.error?p.stdout:null;
}
const jpg=synthetic('JPEG'),webp=synthetic('WEBP'),rotated=synthetic('JPEG',6);
const HAS_PIL=Buffer.isBuffer(jpg)&&Buffer.isBuffer(webp);
function masterFixture(bytes,w=2,h=1){
 const hash=sha256(bytes),asset='f'.repeat(64);
 return {review:{source_master_sha256:hash,source_master_provenance:'AUTHORIZED_ORIGINAL_MASTER_BYTES',asset_sha256:asset,
 geometry:{native_width:w,native_height:h,output_width:w,output_height:h}},
 artifacts:{source_master_asset:bytes,rights_review_text:JSON.stringify({source_master_sha256:hash,
 source_master_reuse_permission_verified:true,item_level_reuse_permission_verified:true,asset_sha256:asset})}};
}
function candidateFixture(bytes,w=2,h=1){
 const catalog='https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/';
 const asset='https://www.history.uscg.mil/assets/synthetic-test.jpg',hash=sha256(bytes);
 const rights=JSON.stringify({slot:'418:1',candidate_catalog:catalog,asset_url:asset,asset_sha256:hash,
 item_level_reuse_permission_verified:true,credit_and_restrictions_recorded:true,replacement_mode:'SAME_PHOTO',
 review_basis_url:catalog,attribution_text:'Synthetic fixture only, not a historic asset'});
 const review={slot:'418:1',candidate_catalog:catalog,asset_url:asset,asset_sha256:hash,
 rights_review_git_blob_sha:gitBlobSha(rights),replacement_mode:'SAME_PHOTO',geometry:{output_width:w,output_height:h}};
 const capture={slot:'418:1',screenshot_sha256:sha256(png)};
 const captureText=JSON.stringify(capture);
 return {packet:{...capture,capture_git_blob_sha:gitBlobSha(captureText)},review,
 artifacts:{capture_text:captureText,screenshot_png:png,rights_review_text:rights,candidate_asset:bytes}};
}
function reviewOnly(r){assert.equal(r.verified,true);assert.equal(r.production_write_allowed,false);assert.equal(r.third_party_cache_allowed,false);}
test('full JPEG pixel raster verified',{skip:!HAS_PIL},()=>assert.deepEqual(decode(jpg),{width:2,height:1,format:'jpeg'}));
test('full WebP pixel raster verified',{skip:!HAS_PIL},()=>assert.deepEqual(decode(webp),{width:2,height:1,format:'webp'}));
test('JPEG source master byte/decode review eligibility only',{skip:!HAS_PIL},()=>{const f=masterFixture(jpg);reviewOnly(verifyP0SourceMasterEvidence(f.review,f.artifacts));});
test('WebP source master byte/decode review eligibility only',{skip:!HAS_PIL},()=>{const f=masterFixture(webp);reviewOnly(verifyP0SourceMasterEvidence(f.review,f.artifacts));});
test('JPEG candidate byte/decode review eligibility only',{skip:!HAS_PIL},()=>{const f=candidateFixture(jpg);reviewOnly(verifyP0ReviewEvidence(f.packet,f.review,f.artifacts));});
test('WebP candidate byte/decode review eligibility only',{skip:!HAS_PIL},()=>{const f=candidateFixture(webp);reviewOnly(verifyP0ReviewEvidence(f.packet,f.review,f.artifacts));});
test('EXIF rotated file held for visual review',{skip:!HAS_PIL},()=>assert.equal(decode(rotated),null));
test('truncated JPEG master fails even if SHA matches truncated bytes',{skip:!HAS_PIL},()=>{const f=masterFixture(jpg.subarray(0,jpg.length-8));assert.equal(verifyP0SourceMasterEvidence(f.review,f.artifacts).verified,false);});
test('false source-master native geometry denied',{skip:!HAS_PIL},()=>{const f=masterFixture(webp,1,1);assert.equal(verifyP0SourceMasterEvidence(f.review,f.artifacts).reason,'DECLARED_NATIVE_GEOMETRY_DIFFERS_FROM_MASTER_BYTES');});
test('missing decoder fails closed',{skip:!HAS_PIL},()=>{
 const old=process.env.PATH;try{process.env.PATH='/__absent__';const f=masterFixture(jpg);assert.equal(verifyP0SourceMasterEvidence(f.review,f.artifacts).reason,'SOURCE_MASTER_FULL_RASTER_DECODE_REQUIRED');}
 finally{process.env.PATH=old;}
});
