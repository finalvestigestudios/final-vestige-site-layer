'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const {verifyP0SourceMasterEvidence:check,sha256}=require('./verify_p0_review_evidence_20261112.cjs');
const png=Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+ip1sAAAAASUVORK5CYII=','base64');
const fakeSha='f'.repeat(64);
function fixture(){
 const hash=sha256(png);
 const review={source_master_sha256:hash,source_master_provenance:'AUTHORIZED_ORIGINAL_MASTER_BYTES',
  asset_sha256:fakeSha,geometry:{native_width:1,native_height:1,output_width:1,output_height:1}};
 const rights={source_master_sha256:hash,source_master_reuse_permission_verified:true,
  item_level_reuse_permission_verified:true,asset_sha256:fakeSha};
 return {review,artifacts:{source_master_asset:Buffer.from(png),rights_review_text:JSON.stringify(rights)},rights};
}
function audit(mutator,reason){
 const f=fixture();mutator(f);f.artifacts.rights_review_text=JSON.stringify(f.rights);
 const got=check(f.review,f.artifacts);assert.equal(got.verified,false);assert.equal(got.reason,reason);
 assert.equal(got.production_write_allowed,false);assert.equal(got.third_party_cache_allowed,false);
}
test('signed source-master raster passes byte-bound REVIEW only',()=>{
 const f=fixture(),x=check(f.review,f.artifacts);
 assert.equal(x.verified,true);assert.equal(x.source_master_raster_decode_verified,true);
 assert.deepEqual(x.source_master_dimensions,[1,1]);
 assert.equal(x.production_write_allowed,false);assert.equal(x.third_party_cache_allowed,false);
});
test('no master bytes is a HOLD',()=>audit(f=>delete f.artifacts.source_master_asset,'SOURCE_MASTER_BYTES_REQUIRED'));
test('review hash cannot differ from source master bytes',()=>audit(f=>{f.review.source_master_sha256='a'.repeat(64)},'SOURCE_MASTER_SHA_OR_PROVENANCE_MISMATCH'));
test('rights master digest must bind to bytes',()=>audit(f=>{f.rights.source_master_sha256='a'.repeat(64)},'SOURCE_MASTER_RIGHTS_NOT_BYTE_BOUND'));
test('master cannot be read from an unauthorized provenance',()=>audit(f=>{f.review.source_master_provenance='UNKNOWN'},'SOURCE_MASTER_SHA_OR_PROVENANCE_MISMATCH'));
test('reuse rights for original master must be present',()=>audit(f=>{f.rights.source_master_reuse_permission_verified=false},'SOURCE_MASTER_RIGHTS_NOT_BYTE_BOUND'));
test('derivative rights and original master rights are separate',()=>audit(f=>{f.rights.item_level_reuse_permission_verified=false},'SOURCE_MASTER_RIGHTS_NOT_BYTE_BOUND'));
test('declared master native geometry must match actual bytes',()=>audit(f=>{f.review.geometry.native_width=819},'DECLARED_NATIVE_GEOMETRY_DIFFERS_FROM_MASTER_BYTES'));
test('signed output >960 pixels cannot be admitted',()=>audit(f=>{f.review.geometry.output_width=961},'DERIVATIVE_OVER_960_OR_UPSCALED_FROM_MASTER'));
test('signed output may not upscale even below 960',()=>audit(f=>{f.review.geometry.output_width=2},'DERIVATIVE_OVER_960_OR_UPSCALED_FROM_MASTER'));
test('truncated PNG master cannot pass',()=>audit(f=>{f.artifacts.source_master_asset=f.artifacts.source_master_asset.subarray(0,32);
 f.review.source_master_sha256=sha256(f.artifacts.source_master_asset);f.rights.source_master_sha256=f.review.source_master_sha256},'SOURCE_MASTER_IMAGE_FORMAT_UNVERIFIED'));
test('missing rights JSON cannot silently pass',()=>{const f=fixture();f.artifacts.rights_review_text='not-json';
 const x=check(f.review,f.artifacts);assert.equal(x.reason,'SOURCE_MASTER_RIGHTS_JSON_INVALID');});
