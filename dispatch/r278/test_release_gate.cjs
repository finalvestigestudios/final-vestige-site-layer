'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {evaluateLedger,requiredGlobal,requiredMerchant}=require('./release_gate.cjs');
const data=JSON.parse(fs.readFileSync(path.join(__dirname,'proof_ledger.json'),'utf8'));
let pass=0;
function test(title,fn){fn();pass++;console.log('PASS '+String(pass).padStart(2,'0')+' '+title);}
function reject(name,mutate){
 let snap=structuredClone(data); mutate(snap);
 test(name,()=>assert.equal(evaluateLedger(snap).status,'INVALID_SOURCE_SNAPSHOT'));
}
test('baseline hard hold',()=>assert.equal(evaluateLedger(data).status,'HOLD_NO_SEND'));
test('six issues never ready',()=>assert.deepEqual(Object.values(evaluateLedger(data).issue_states),['HOLD_SEND','HOLD_SEND','HOLD_MERCHANT_AND_SEND','HOLD_SEND','HOLD_MERCHANT_AND_SEND','HOLD_SEND']));
test('financial results not computable',()=>assert.equal(evaluateLedger(data).reported_paid_revenue,'NOT_COMPUTABLE'));
test('evidence always unauthenticated',()=>assert.equal(evaluateLedger(data).proof_is_provider_authenticated,false));
test('no automated founder approval',()=>assert.equal(evaluateLedger(data).founder_permission_to_send,false));
reject('default-on drift',x=>x.read_only_wordpress.email_new_posts_by_default=true);
reject('newsletter disabled',x=>x.read_only_wordpress.newsletter_enabled=false);
reject('excerpt drift',x=>x.read_only_wordpress.email_format='excerpt');
reject('fewer issues',x=>x.editorial_campaign.issue_count=5);
reject('issue-role drift',x=>x.editorial_campaign.commercial=[1,3,5]);
reject('false actual eligible count',x=>x.read_only_wordpress.counts.actual_eligible_recipients=3);
reject('impossible confirmation total',x=>x.read_only_wordpress.counts.diagnostic_confirmed=22);
reject('campaign state changed',x=>x.state='READY');
reject('campaign hold changed',x=>x.editorial_campaign.all_issues_hold=false);
for(const k of requiredGlobal) reject('unverified claimed gate '+k,x=>x.gate[k]=true);
for(const key of ['03','05']) {
 reject('active offer link '+key,x=>x.commercial[key].activated_link='https://example.org/');
 for(const k of requiredMerchant) reject('unverified claimed '+key+' '+k,x=>x.commercial[key][k]=true);
}
for(const k of ['attributable_paid_orders','gross_revenue','refunds','fees','net_realized_revenue','net_per_1000_qualified_human_sessions'])
 reject('unverified financial claim '+k,x=>x.metrics[k]=0);
console.log('TOTAL PASS '+pass+' / '+pass);
