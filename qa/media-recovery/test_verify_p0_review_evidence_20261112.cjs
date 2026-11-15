'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const {verifyP0ReviewEvidence,gitBlobSha,sha256}=require('./verify_p0_review_evidence_20261112.cjs');
function fixture(){
 const p={slot:'418:1',post_id:418,published_original_src:'https://media.defense.gov/x.jpg',siteqa_pr:154,guest:{cdp_request_id:'req-1'},screenshot_sha256:null};
 const r={slot:'418:1',candidate_catalog:'https://www.history.uscg.mil/a',asset_url:'https://media.defense.gov/a.jpg',asset_sha256:null,rights_review_git_blob_sha:null,replacement_mode:'SAME_PHOTO'};
 const png=Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+ip1sAAAAASUVORK5CYII=','base64');
 const screenshot=Buffer.from(png),asset=Buffer.from(png);
 r.geometry={output_width:1,output_height:1};
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

function signUpdated(f){
 f.p.screenshot_sha256=sha256(f.a.screenshot_png);
 f.r.asset_sha256=sha256(f.a.candidate_asset);
 const rights=JSON.parse(f.a.rights_review_text);
 rights.asset_sha256=f.r.asset_sha256;
 f.a.rights_review_text=JSON.stringify(rights);
 f.r.rights_review_git_blob_sha=gitBlobSha(f.a.rights_review_text);
 const {capture_git_blob_sha,...capture}=f.p;
 f.a.capture_text=JSON.stringify(capture);
 f.p.capture_git_blob_sha=gitBlobSha(f.a.capture_text);
 return f;
}
test('candidate bytes are verified as an actual supported image structure',()=>{
 const f=fixture();assert.equal(verifyP0ReviewEvidence(f.p,f.r,f.a).verified,true);
});
test('signed arbitrary text masquerading as a candidate asset is rejected',()=>{
 const f=fixture();f.a.candidate_asset=Buffer.from('<html>not an image</html>');
 signUpdated(f);assert.match(verifyP0ReviewEvidence(f.p,f.r,f.a).reason,/ASSET_FORMAT/);
});
test('signed SVG is not treated as a safe raster candidate',()=>{
 const f=fixture();f.a.candidate_asset=Buffer.from('<svg xmlns="http://www.w3.org/2000/svg"></svg>');
 signUpdated(f);assert.match(verifyP0ReviewEvidence(f.p,f.r,f.a).reason,/ASSET_FORMAT/);
});
test('valid raster with falsely asserted different dimensions is held',()=>{
 const f=fixture();f.r.geometry.output_width=960;
 assert.match(verifyP0ReviewEvidence(f.p,f.r,f.a).reason,/OUTPUT_GEOMETRY/);
});
test('valid PNG screenshot with changed and re-signed CRC cannot pass',()=>{
 const f=fixture();f.a.screenshot_png=Buffer.from(f.a.screenshot_png);
 f.a.screenshot_png[33]^=1;signUpdated(f);
 assert.match(verifyP0ReviewEvidence(f.p,f.r,f.a).reason,/INVALID_ARTIFACT_BYTES/);
});
test('signed PNG screenshot lacking IDAT/IEND cannot pass',()=>{
 const f=fixture();f.a.screenshot_png=Buffer.from(f.a.screenshot_png.subarray(0,33));
 signUpdated(f);assert.match(verifyP0ReviewEvidence(f.p,f.r,f.a).reason,/INVALID_ARTIFACT_BYTES/);
});
test('PNG candidate with corrupted image chunk is held even with matching SHA',()=>{
 const f=fixture();f.a.candidate_asset=Buffer.from(f.a.candidate_asset);
 f.a.candidate_asset[47]^=1;signUpdated(f);
 assert.match(verifyP0ReviewEvidence(f.p,f.r,f.a).reason,/ASSET_FORMAT/);
});
test('truncated signed candidate is not admitted',()=>{
 const f=fixture();f.a.candidate_asset=Buffer.from(f.a.candidate_asset.subarray(0,35));
 signUpdated(f);assert.match(verifyP0ReviewEvidence(f.p,f.r,f.a).reason,/ASSET_FORMAT/);
});
test('signed JPEG without valid SOF/SOS/EOI image structure is rejected',()=>{
 const f=fixture();f.a.candidate_asset=Buffer.from([0xff,0xd8,0xff,0xd9]);
 signUpdated(f);assert.match(verifyP0ReviewEvidence(f.p,f.r,f.a).reason,/ASSET_FORMAT/);
});
test('unsupported/empty image geometry fails closed',()=>{
 const f=fixture();delete f.r.geometry;
 assert.match(verifyP0ReviewEvidence(f.p,f.r,f.a).reason,/ASSET_FORMAT/);
});
test('real synthetic one-pixel JPEG passes structural dimensions and hashes',()=>{
 const f=fixture();f.a.candidate_asset=Buffer.from(['/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAsICAoIBwsKCQoNDAsNERwSEQ8PESIZ','GhQcKSQrKigkJyctMkA3LTA9MCcnOEw5PUNFSElIKzZPVU5GVEBHSEX/2wBDAQwN','DREPESESEiFFLicuRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVF','RUVFRUVFRUVFRUVFRUX/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAA','AAAAAAAAAAb/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFAEBAAAAAAAAAAAAAAAA','AAAABf/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AJYAqMf/2Q=='].join(''),'base64');
 signUpdated(f);assert.equal(verifyP0ReviewEvidence(f.p,f.r,f.a).verified,true);
});
test('real synthetic one-pixel lossless WebP passes structural dimensions and hashes',()=>{
 const f=fixture();f.a.candidate_asset=Buffer.from('UklGRh4AAABXRUJQVlA4TBEAAAAvAAAAAAdQqH7Ur/+BiOh/AAA=','base64');
 signUpdated(f);assert.equal(verifyP0ReviewEvidence(f.p,f.r,f.a).verified,true);
});
