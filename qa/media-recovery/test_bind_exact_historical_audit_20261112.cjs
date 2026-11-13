'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const {createHash}=require('node:crypto');
const {bindExactHistoricalAudit,gitBlobSha,MAX_AUDIT_BYTES}=require('./bind_exact_historical_audit_20261112.cjs');
const raw=Buffer.from('{"schema":"fixture","rows":[{"slot":"285:5","src":"https://example.org/old.jpg"}]}');
const expected=createHash('sha1').update(Buffer.from(`blob ${raw.length}\0`)).update(raw).digest('hex');
const good=()=>bindExactHistoricalAudit(raw,expected,expected);
test('raw Git blob SHA-1 matches independent Node crypto computation',()=>assert.equal(gitBlobSha(raw),expected));
test('unchanged authenticated bytes parse exact frozen record',()=>assert.deepEqual(good(),{ok:true,reason:null,audit:JSON.parse(raw.toString()),verified_git_blob_sha:expected}));
test('claimed correct SHA cannot authenticate mutated same-length source URL',()=>{
 const altered=Buffer.from(raw.toString().replace('old.jpg','new.jpg'));
 assert.equal(altered.length,raw.length);
 assert.equal(bindExactHistoricalAudit(altered,expected,expected).reason,'RAW_GIT_BLOB_SHA_MISMATCH_OR_INVALID_BYTES');
});
test('reformatted equivalent JSON bytes fail: freeze is byte-exact',()=>{
 const altered=Buffer.from(JSON.stringify(JSON.parse(raw.toString()),null,2));
 assert.equal(bindExactHistoricalAudit(altered,expected,expected).ok,false);
});
test('fake claimed SHA fails even for authentic bytes',()=>assert.equal(bindExactHistoricalAudit(raw,'0'.repeat(40),expected).ok,false));
test('missing expected SHA fails closed',()=>assert.equal(bindExactHistoricalAudit(raw,expected,'').ok,false));
test('untrusted parsed object cannot bypass raw authentication',()=>assert.equal(bindExactHistoricalAudit(JSON.parse(raw.toString()),expected,expected).ok,false));
test('string input cannot masquerade as Git blob bytes',()=>assert.equal(bindExactHistoricalAudit(raw.toString(),expected,expected).ok,false));
test('empty buffer rejected',()=>assert.equal(bindExactHistoricalAudit(Buffer.alloc(0),expected,expected).ok,false));
test('oversize raw input rejected without crypto processing',()=>assert.equal(bindExactHistoricalAudit(Buffer.alloc(MAX_AUDIT_BYTES+1),expected,expected).ok,false));
test('verified invalid UTF-8 fails strict decode',()=>{
 const invalid=Buffer.from([0xff,0xfe]),sha=gitBlobSha(invalid);
 assert.equal(bindExactHistoricalAudit(invalid,sha,sha).reason,'RAW_AUDIT_JSON_INVALID');
});
test('verified invalid JSON fails closed',()=>{
 const invalid=Buffer.from('{bad'),sha=gitBlobSha(invalid);
 assert.equal(bindExactHistoricalAudit(invalid,sha,sha).reason,'RAW_AUDIT_JSON_INVALID');
});
test('verified JSON scalar is not historical audit object',()=>{
 const scalar=Buffer.from('42'),sha=gitBlobSha(scalar);
 assert.equal(bindExactHistoricalAudit(scalar,sha,sha).reason,'RAW_AUDIT_OBJECT_REQUIRED');
});
test('verified JSON array is not historical audit object',()=>{
 const arr=Buffer.from('[]'),sha=gitBlobSha(arr);
 assert.equal(bindExactHistoricalAudit(arr,sha,sha).reason,'RAW_AUDIT_OBJECT_REQUIRED');
});
test('single-byte mutation fails despite unchanged length and claimed SHA',()=>{
 const changed=Buffer.from(raw);changed[changed.length-2]^=1;
 assert.equal(bindExactHistoricalAudit(changed,expected,expected).ok,false);
});
