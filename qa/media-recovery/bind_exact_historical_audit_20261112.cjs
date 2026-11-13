'use strict';
/**
 * Authenticate exact frozen Git audit bytes before parsing.
 * A caller-provided 40-character Git blob SHA is not evidence of those bytes.
 * Offline, bounded, read-only; no WordPress or browser operations.
 */
const {createHash}=require('node:crypto');
const {TextDecoder}=require('node:util');
const MAX_AUDIT_BYTES=16*1024*1024;
const SHA40=/^[0-9a-f]{40}$/;
function gitBlobSha(raw){
 if(!Buffer.isBuffer(raw)||raw.length<1||raw.length>MAX_AUDIT_BYTES)return null;
 return createHash('sha1').update(Buffer.from(`blob ${raw.length}\0`,'utf8')).update(raw).digest('hex');
}
function bindExactHistoricalAudit(raw,claimedSha,expectedSha){
 const fail=reason=>({ok:false,reason,audit:null,verified_git_blob_sha:null});
 if(!SHA40.test(expectedSha||'')||claimedSha!==expectedSha)
   return fail('UNTRUSTED_EXPECTED_OR_CLAIMED_BLOB_SHA');
 const measured=gitBlobSha(raw);
 if(!measured||measured!==expectedSha)return fail('RAW_GIT_BLOB_SHA_MISMATCH_OR_INVALID_BYTES');
 let parsed;
 try{parsed=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(raw));}
 catch{return fail('RAW_AUDIT_JSON_INVALID');}
 if(!parsed||typeof parsed!=='object'||Array.isArray(parsed))
   return fail('RAW_AUDIT_OBJECT_REQUIRED');
 return {ok:true,reason:null,audit:parsed,verified_git_blob_sha:measured};
}
module.exports={bindExactHistoricalAudit,gitBlobSha,MAX_AUDIT_BYTES};
