'use strict';
/** Offline byte-bound review admission. Does not fetch, scrape, cache, upload, or approve media. */
const crypto=require('node:crypto');
const {isDeepStrictEqual}=require('node:util');
const sha256=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const gitBlobSha=bytes=>{
  const data=Buffer.isBuffer(bytes)?bytes:Buffer.from(bytes,'utf8');
  return crypto.createHash('sha1').update('blob '+data.length+'\0').update(data).digest('hex');
};
const denied=reason=>({verified:false,reason,production_write_allowed:false,third_party_cache_allowed:false});
const pngSignature=Buffer.from('89504e470d0a1a0a','hex');
function verifyP0ReviewEvidence(packet,review,artifacts){
  if(!packet||!review||!artifacts)return denied('MISSING_BYTE_BOUND_ARTIFACTS');
  const {capture_text,screenshot_png,rights_review_text,candidate_asset}=artifacts;
  if(typeof capture_text!=='string'||!Buffer.isBuffer(screenshot_png)||
     typeof rights_review_text!=='string'||!Buffer.isBuffer(candidate_asset))
    return denied('ARTIFACT_TYPES_UNVERIFIED');
  if(!capture_text||screenshot_png.length<24||!screenshot_png.subarray(0,8).equals(pngSignature)||
     !rights_review_text||candidate_asset.length<1)
    return denied('MISSING_OR_INVALID_ARTIFACT_BYTES');
  if(gitBlobSha(capture_text)!==packet.capture_git_blob_sha||
     sha256(screenshot_png)!==packet.screenshot_sha256||
     gitBlobSha(rights_review_text)!==review.rights_review_git_blob_sha||
     sha256(candidate_asset)!==review.asset_sha256)
    return denied('ARTIFACT_HASH_MISMATCH');
  let capture,rights;
  try{capture=JSON.parse(capture_text);rights=JSON.parse(rights_review_text);}
  catch{return denied('ARTIFACT_JSON_INVALID');}
  const packetWithoutBlob={...packet};delete packetWithoutBlob.capture_git_blob_sha;
  if(!isDeepStrictEqual(capture,packetWithoutBlob))return denied('CAPTURE_PACKET_NOT_BYTE_BOUND');
  if(rights.slot!==packet.slot||rights.candidate_catalog!==review.candidate_catalog||
     rights.asset_url!==review.asset_url||rights.asset_sha256!==review.asset_sha256||
     rights.item_level_reuse_permission_verified!==true||
     rights.credit_and_restrictions_recorded!==true||
     rights.replacement_mode!==review.replacement_mode||
     typeof rights.review_basis_url!=='string'||!rights.review_basis_url.startsWith('https://')||
     typeof rights.attribution_text!=='string'||rights.attribution_text.trim().length<12)
    return denied('RIGHTS_RECORD_NOT_BOUND_TO_ASSET');
  return {verified:true,reason:null,production_write_allowed:false,third_party_cache_allowed:false,
    verified_capture_blob_sha:packet.capture_git_blob_sha,
    verified_rights_blob_sha:review.rights_review_git_blob_sha,
    verified_asset_sha256:review.asset_sha256};
}
module.exports={verifyP0ReviewEvidence,gitBlobSha,sha256};
