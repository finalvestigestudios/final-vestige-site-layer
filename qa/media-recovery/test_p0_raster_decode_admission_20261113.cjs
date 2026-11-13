'use strict';
/** Offline regression: matching bytes, hashes and plausible dimensions are not a decoded raster. */
const test=require('node:test'),assert=require('node:assert/strict');
const {verifyP0SourceMasterEvidence,verifyP0ReviewEvidence,sha256,gitBlobSha}=
 require('./verify_p0_review_evidence_20261112.cjs');
const png=Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+ip1sAAAAASUVORK5CYII=','base64');
// SOI + plausible SOF + SOS + a few meaningless bytes + EOI; no compressed image.
const fakeJpeg=Buffer.from('ffd8ffc0000b080001000101011100ffda000201000000ffd9','hex');
// Valid-looking RIFF/WebP VP8X dimensions, but no VP8/VP8L compressed image payload.
const fakeWebp=Buffer.alloc(30);
fakeWebp.write('RIFF',0,'ascii');fakeWebp.writeUInt32LE(22,4);
fakeWebp.write('WEBP',8,'ascii');fakeWebp.write('VP8X',12,'ascii');
fakeWebp.writeUInt32LE(10,16);
const fakeSha='f'.repeat(64);
function masterFixture(bytes){
 const hash=sha256(bytes);
 const review={source_master_sha256:hash,source_master_provenance:'AUTHORIZED_ORIGINAL_MASTER_BYTES',
  asset_sha256:fakeSha,geometry:{native_width:1,native_height:1,output_width:1,output_height:1}};
 const rights={source_master_sha256:hash,source_master_reuse_permission_verified:true,
  item_level_reuse_permission_verified:true,asset_sha256:fakeSha};
 return {review,artifacts:{source_master_asset:bytes,rights_review_text:JSON.stringify(rights)}};
}
function candidateFixture(bytes){
 const catalog='https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/';
 const assetUrl='https://www.history.uscg.mil/assets/proposed.jpg',hash=sha256(bytes);
 const rights={slot:'418:1',candidate_catalog:catalog,asset_url:assetUrl,asset_sha256:hash,
  item_level_reuse_permission_verified:true,credit_and_restrictions_recorded:true,
  replacement_mode:'SAME_PHOTO',review_basis_url:catalog,
  attribution_text:'United States Coast Guard archival photograph'};
 const rightsText=JSON.stringify(rights);
 const review={slot:'418:1',candidate_catalog:catalog,asset_url:assetUrl,asset_sha256:hash,
  rights_review_git_blob_sha:gitBlobSha(rightsText),replacement_mode:'SAME_PHOTO',
  geometry:{output_width:1,output_height:1}};
 const capture={slot:'418:1',screenshot_sha256:sha256(png)};
 const captureText=JSON.stringify(capture);
 const packet={...capture,capture_git_blob_sha:gitBlobSha(captureText),screenshot_sha256:sha256(png)};
 return {packet,review,artifacts:{capture_text:captureText,screenshot_png:png,
  rights_review_text:rightsText,candidate_asset:bytes}};
}
function hold(value,reason){
 assert.equal(value.verified,false);assert.equal(value.reason,reason);
 assert.equal(value.production_write_allowed,false);
 assert.equal(value.third_party_cache_allowed,false);
}
test('full-raster PNG source master is a review-only admission (not production permission)',()=>{
 const f=masterFixture(png),x=verifyP0SourceMasterEvidence(f.review,f.artifacts);
 assert.equal(x.verified,true);assert.equal(x.source_master_raster_decode_verified,true);
 assert.equal(x.production_write_allowed,false);assert.equal(x.third_party_cache_allowed,false);
});
test('forged JPEG source master: matching hash and claimed 1x1 cannot prove raster decode',()=>{
 const f=masterFixture(fakeJpeg);
 hold(verifyP0SourceMasterEvidence(f.review,f.artifacts),'SOURCE_MASTER_FULL_RASTER_DECODE_REQUIRED');
});
test('forged WebP VP8X source master: matching hash and header dimensions still HOLD',()=>{
 const f=masterFixture(fakeWebp);
 hold(verifyP0SourceMasterEvidence(f.review,f.artifacts),'SOURCE_MASTER_FULL_RASTER_DECODE_REQUIRED');
});
test('full-raster PNG candidate remains eligible for review only',()=>{
 const f=candidateFixture(png),x=verifyP0ReviewEvidence(f.packet,f.review,f.artifacts);
 assert.equal(x.verified,true);assert.equal(x.production_write_allowed,false);
 assert.equal(x.third_party_cache_allowed,false);
});
test('forged JPEG replacement candidate cannot reach review eligibility',()=>{
 const f=candidateFixture(fakeJpeg);
 hold(verifyP0ReviewEvidence(f.packet,f.review,f.artifacts),'CANDIDATE_FULL_RASTER_DECODE_REQUIRED');
});
test('forged WebP replacement candidate cannot reach review eligibility',()=>{
 const f=candidateFixture(fakeWebp);
 hold(verifyP0ReviewEvidence(f.packet,f.review,f.artifacts),'CANDIDATE_FULL_RASTER_DECODE_REQUIRED');
});
