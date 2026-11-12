import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {validEvidence,assessEdition,assessCampaign} from './release_gate.mjs';
const data=JSON.parse(fs.readFileSync(new URL('./evidence.json',import.meta.url),'utf8'));
const now=data.date_utc;
const proof=(type,url,checked_at=now)=>({proof_id:'proof_test_001',type,url,checked_at,verified:true});
test('canonical six remain HOLD; 4 editorial, two commercial',()=>{
 const x=assessCampaign(data.editions,{},now);
 assert.equal(x.mix_valid,true);assert.equal(x.send_allowed,false);assert.ok(x.results.every(r=>r.status==='HOLD_UNSENT'));
});
test('every issue separately requires FTC purpose review, actual preview and postal/unsubscribe evidence',()=>{
 for(const e of data.editions){const b=assessEdition(e,{},now).blockers;
 assert.ok(b.includes('NO_FTC_PRIMARY_PURPOSE_WITNESS'));
 assert.ok(b.includes('NO_NATIVE_EMAIL_PREVIEW_WITNESS'));
 for(const k of ['postal','unsubscribe','inbox','eligible_email'])assert.ok(b.includes('MISSING_OR_EXPIRED_'+k));
 }
});
test('product-specific commercial proof is not inherited from general site opt-in',()=>{
 for(const e of [data.editions[2],data.editions[4]]){const b=assessEdition(e,{},now).blockers;
 assert.ok(b.includes('MISSING_OR_EXPIRED_email_permission'));
 assert.ok(b.includes('NO_ACCOUNT_SPECIFIC_EMAIL_PERMISSION'));
 assert.ok(b.includes('NO_ADJACENT_AFFILIATE_DISCLOSURE'));
 assert.ok(b.includes('NO_APPROVED_PUBLISHED_WARMUP_GUIDE'));
 }
});
test('sources are constrained to canonical HTTPS domains',()=>{
 assert.equal(validEvidence(proof('sales_page','https://zen12.com/'),'sales_page',now),true);
 for(const bad of ['http://zen12.com/','https://zen12.com.attacker.org/','https://example.com/']){
 assert.equal(validEvidence(proof('sales_page',bad),'sales_page',now),false); }
 assert.equal(validEvidence(proof('email_permission','https://inspire3.com/'),'email_permission',now),false);
});
test('stale or future proof invalidates readiness',()=>{
 assert.equal(validEvidence(proof('sales_page','https://zen12.com/','2026-11-01T00:00:00Z'),'sales_page',now),false);
 assert.equal(validEvidence(proof('sales_page','https://zen12.com/','2026-11-13T00:00:00Z'),'sales_page',now),false);
});
test('duplicate issues, altered allocation, source mutation, live affiliate link never authorize sending',()=>{
 assert.equal(assessCampaign([data.editions[0],...data.editions.slice(0,5)],{},now).mix_valid,false);
 assert.ok(assessEdition({...data.editions[0],kind:'commercial-review-pending'},{},now).blockers.some(x=>x.includes('allocation')));
 assert.ok(assessEdition({...data.editions[0],source_blob:'x'},{},now).blockers.some(x=>x.includes('identity')));
 assert.ok(assessEdition({...data.editions[2],affiliate_link:'https://zen12.com/?aff=fake'},{},now).blockers.includes('NO_LIVE_AFFILIATE_LINKS_ALLOWED_IN_DRAFT'));
});
