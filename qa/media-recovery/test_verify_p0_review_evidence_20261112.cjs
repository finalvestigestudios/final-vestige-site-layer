'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const {verifyP0ReviewEvidence,gitBlobSha,sha256}=require('./verify_p0_review_evidence_20261112.cjs');
function fixture(){
 const p={slot:'418:1',post_id:418,published_original_src:'https://media.defense.gov/x.jpg',siteqa_pr:154,guest:{cdp_request_id:'req-1'},screenshot_sha256:null};
 const r={slot:'418:1',candidate_catalog:'https://www.history.uscg.mil/a',asset_url:'https://media.defense.gov/a.jpg',asset_sha256:null,rights_review_git_blob_sha:null,replacement_mode:'SAME_PHOTO'};
 const screenshot=Buffer.concat([Buffer.from('89504e470d0a1a0a','hex'),Buffer.alloc(48,2)]);
 const asset=Buffer.from('SYNTHETIC_ASSET_BYTES_NOT_A_REAL_IMAGE');
 p.screenshot_sha256=sha256(screenshot);r.asset_sha256=sha256(asset);
 const rights={slot:p.slot,candidate_catalog:r.candidate_catalog,asset_url:r.asset_url,asset_sha256:r.asset_sha256,item_level_reuse_permission_verified:true,credit_and_restrictions_recorded:true,replacement_mode:r.replacement_mode,review_basis_url:'https://www.history.uscg.mil/a',attribution_text:'U.S. Coast Guard official archive'};
 const a={screenshot_png:screenshot,candidate_asset:asset,rights_review_text:JSON.stringify(rights)};
 r.rights_review_git_blob_sha=gitBlobSha(a.rights_review_text);
 a.capture_text=JSON.stringify(p);
 p.capture_git_blob_sha=gitBlobSha(a.capture_text);
 return {p,r,a};
}
test('byte-identical synthetic fixture admits review ONLY, never a write',()=>{const {p,r,a}=fixture();const x=verifyP0ReviewEvidence(p,r,a);assert.equal(x.verified,true);assert.equal(x.production_write_allowed,false);assert.equal(x.third_party_cache_allowed,false);});
test('missing packet bytes HOLD',()=>{const {p,r}=fixture();assert.equal(verifyP0ReviewEvidence(p,r).verified,false);});
test('changed screenshot after signing HOLD',()=>{const {p,r,a}=fixture();a.screenshot_png=Buffer.from(a.screenshot_png);a.screenshot_png[30]^=1;assert.match(verifyP0ReviewEvidence(p,r,a).reason,/HASH_MISMATCH/);});
test('different capture with unchanged Git pointer HOLD',()=>{const {p,r,a}=fixture();a.capture_text=a.capture_text.replace('req-1','req-2');assert.equal(verifyP0ReviewEvidence(p,r,a).verified,false);});
test('signed capture from different slot HOLD',()=>{const {p,r,a}=fixture();const j=JSON.parse(a.capture_text);j.slot='418:2';a.capture_text=JSON.stringify(j);p.capture_git_blob_sha=gitBlobSha(a.capture_text);assert.match(verifyP0ReviewEvidence(p,r,a).reason,/NOT_BYTE_BOUND/);});
test('mutated rights note after signing HOLD',()=>{const {p,r,a}=fixture();a.rights_review_text=a.rights_review_text.replace('official archive','private donor');assert.match(verifyP0ReviewEvidence(p,r,a).reason,/HASH_MISMATCH/);});
test('signed rights cannot approve another source asset',()=>{const {p,r,a}=fixture();const j=JSON.parse(a.rights_review_text);j.asset_url='https://unrelated.example/another.jpg';a.rights_review_text=JSON.stringify(j);r.rights_review_git_blob_sha=gitBlobSha(a.rights_review_text);assert.match(verifyP0ReviewEvidence(p,r,a).reason,/RIGHTS_RECORD/);});
test('rights review must affirm reuse and credit even when signed',()=>{const {p,r,a}=fixture();const j=JSON.parse(a.rights_review_text);j.item_level_reuse_permission_verified=false;a.rights_review_text=JSON.stringify(j);r.rights_review_git_blob_sha=gitBlobSha(a.rights_review_text);assert.match(verifyP0ReviewEvidence(p,r,a).reason,/RIGHTS_RECORD/);});
test('candidate asset bytes must match SHA-256',()=>{const {p,r,a}=fixture();a.candidate_asset=Buffer.from('SYNTHETIC_DIFFERENT_ASSET');assert.match(verifyP0ReviewEvidence(p,r,a).reason,/HASH_MISMATCH/);});
test('no screenshot PNG magic HOLD',()=>{const {p,r,a}=fixture();a.screenshot_png=Buffer.alloc(40);p.screenshot_sha256=sha256(a.screenshot_png);const {capture_git_blob_sha,...rest}=p;a.capture_text=JSON.stringify(rest);p.capture_git_blob_sha=gitBlobSha(a.capture_text);assert.match(verifyP0ReviewEvidence(p,r,a).reason,/INVALID_ARTIFACT_BYTES/);});
test('no rights record can be inferred from booleans',()=>{const {p,r,a}=fixture();a.rights_review_text='';assert.equal(verifyP0ReviewEvidence(p,r,a).verified,false);});
test('fabricated Git blob strings without bytes HOLD',()=>{const {p,r,a}=fixture();a.capture_text=null;assert.equal(verifyP0ReviewEvidence(p,r,a).verified,false);});
