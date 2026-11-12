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
const {verifiedPngGeometry}=require('./png_decode_guard_20261112.cjs');

// Decode-checked PNG before staging review; JPEG/WebP remain structural-only.
function jpegGeometry(b){
 if(!Buffer.isBuffer(b)||b.length<16||b[0]!==0xff||b[1]!==0xd8)return null;
 let i=2,w=0,h=0,hadSof=false,sos=false;
 while(i+3<b.length){
  if(b[i++]!==0xff)return null;
  while(i<b.length&&b[i]===0xff)i++;
  const marker=b[i++];
  if(marker===0xd9)break;
  if(marker===0xd8||marker===0x00||marker===0x01||(marker>=0xd0&&marker<=0xd7))continue;
  if(i+2>b.length)return null;
  const n=b.readUInt16BE(i);if(n<2||i+n>b.length)return null;
  const sof=[0xc0,0xc1,0xc2,0xc3,0xc5,0xc6,0xc7,0xc9,0xca,0xcb,0xcd,0xce,0xcf].includes(marker);
  if(sof){
   if(n<8)return null;
   h=b.readUInt16BE(i+3);w=b.readUInt16BE(i+5);hadSof=true;
  }
  if(marker===0xda){sos=true;break;}
  i+=n;
 }
 // Metadata only. Browser decode and EXIF orientation still require visual review.
 return hadSof&&sos&&w>0&&h>0&&
  b.lastIndexOf(Buffer.from([0xff,0xd9]))>i?{width:w,height:h,format:'jpeg'}:null;
}
function webpGeometry(b){
 if(!Buffer.isBuffer(b)||b.length<30||b.toString('ascii',0,4)!=='RIFF'||
    b.toString('ascii',8,12)!=='WEBP'||b.readUInt32LE(4)+8!==b.length)return null;
 const t=b.toString('ascii',12,16),n=b.readUInt32LE(16);
 if(n>b.length-20)return null;
 let w=0,h=0;
 if(t==='VP8X'&&n>=10){w=1+b.readUIntLE(24,3);h=1+b.readUIntLE(27,3);}
 else if(t==='VP8L'&&n>=5&&b[20]===0x2f){
  w=1+(b[21]|((b[22]&63)<<8));
  h=1+((b[22]>>6)|(b[23]<<2)|((b[24]&15)<<10));
 }else if(t==='VP8 '&&n>=10&&b[23]===0x9d&&b[24]===0x01&&b[25]===0x2a){
  w=b.readUInt16LE(26)&0x3fff;h=b.readUInt16LE(28)&0x3fff;
 }
 return w>0&&h>0?{width:w,height:h,format:'webp'}:null;
}
function imageGeometry(b){return verifiedPngGeometry(b)||jpegGeometry(b)||webpGeometry(b);}

function verifyP0ReviewEvidence(packet,review,artifacts){
  if(!packet||!review||!artifacts)return denied('MISSING_BYTE_BOUND_ARTIFACTS');
  const {capture_text,screenshot_png,rights_review_text,candidate_asset}=artifacts;
  if(typeof capture_text!=='string'||!Buffer.isBuffer(screenshot_png)||
     typeof rights_review_text!=='string'||!Buffer.isBuffer(candidate_asset))
    return denied('ARTIFACT_TYPES_UNVERIFIED');
  if(!capture_text||!rights_review_text||candidate_asset.length<1)
    return denied('MISSING_OR_INVALID_ARTIFACT_BYTES');
  if(gitBlobSha(capture_text)!==packet.capture_git_blob_sha||
     sha256(screenshot_png)!==packet.screenshot_sha256||
     gitBlobSha(rights_review_text)!==review.rights_review_git_blob_sha||
     sha256(candidate_asset)!==review.asset_sha256)
    return denied('ARTIFACT_HASH_MISMATCH');
  const screen=verifiedPngGeometry(screenshot_png);
  if(!screen)return denied('MISSING_OR_INVALID_ARTIFACT_BYTES');
  const assetShape=imageGeometry(candidate_asset);
  if(!assetShape||!Number.isSafeInteger(review.geometry?.output_width)||
     !Number.isSafeInteger(review.geometry?.output_height)||
     assetShape.width!==review.geometry.output_width||
     assetShape.height!==review.geometry.output_height)
    return denied('ASSET_FORMAT_OR_OUTPUT_GEOMETRY_UNVERIFIED');
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
