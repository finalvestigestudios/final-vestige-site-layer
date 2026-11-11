// Offline source-review checks for the R287 original-six HTML/plain assets.
// Never imports WordPress or an email sender. Run: node dispatch/r287/test_original_review.mjs
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';
const root=path.dirname(fileURLToPath(import.meta.url));
const ledger=JSON.parse(fs.readFileSync(path.join(root,'source-ledger.json'),'utf8'));
assert.equal(ledger.issues.length,6);
assert.deepEqual(ledger.mix,{editorial:4,commercial_reserved:2});
let checks=2;
for(const e of ledger.issues){
 const html=fs.readFileSync(path.join(root,'issue-'+String(e.number).padStart(2,'0')+'.html'),'utf8');
 const txt=fs.readFileSync(path.join(root,'issue-'+String(e.number).padStart(2,'0')+'.txt'),'utf8');
 for(const [name,predicate] of [
  ['subject',html.includes(e.subject)&&txt.includes(e.subject)],
  ['preheader',html.includes(e.preheader)&&txt.includes(e.preheader)],
  ['unsent',html.includes('DO NOT SEND')&&txt.includes('DO NOT EMAIL')],
  ['postal marker',html.includes('[[VALID_POSTAL_ADDRESS_REQUIRED]]')&&txt.includes('[[VALID_POSTAL_ADDRESS_REQUIRED]]')],
  ['unsub marker',html.includes('[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]')&&txt.includes('[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]')],
  ['email safe structure',html.includes('role="presentation"')&&!/<script|<form|<iframe|<img/i.test(html)],
  ['no active merchant',!/href="[^"]*(APPROVED_|\[\[|ref=|checkout)/i.test(html)],
  ['one editorial route or disabled merchant',e.kind==='editorial'?html.includes('href="'+e.primary_cta+'"'):!html.includes('href="'+e.primary_cta+'"')],
  ['release hold',e.release_status==='HOLD_UNSENT']]){
  assert.ok(predicate,'issue '+e.number+' '+name);checks++;
 }
}
for(const k of ['partner_acceptance','email_channel_permission','affiliate_earning_url_verified','postal_address_verified','unsubscribe_received_verified','offer_guide_urls_verified_live','founder_final_approval']){assert.equal(ledger[k],false);checks++;}
console.log('R287 offline source checks PASS: '+checks+'/'+checks+'. NO email sends or provider preview performed.');
