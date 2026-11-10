#!/usr/bin/env node
'use strict';
// R258 native: node mind/r258/test_r258.cjs
// Static source QA only, no network, no WordPress, no transaction.
const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const root=__dirname;
const base={
 article:fs.readFileSync(path.join(root,'THE-FACE-THAT-CHANGED-WHEN-YOU-TURNED-IT-UPRIGHT-UNPUBLISHED.md'),'utf8'),
 matrix:fs.readFileSync(path.join(root,'CLAIM-PROOF-REVENUE-AND-QA-GATES.json'),'utf8'),
 plan:fs.readFileSync(path.join(root,'CONVERSION-FIRST-SINGLE-OFFER-VIDEO-QA-ACCEPTANCE.md'),'utf8')
};
function check(x){
 const m=JSON.parse(x.matrix),s=m.sources,c=m.claims,g=m.commercial_gates;
 assert.equal(m.status,'UNPUBLISHED_HARD_HOLD');
 assert.equal(m.commercial_activation,false);
 assert.equal(m.partner_publisher_approval,'NOT_VERIFIED');
 assert.equal(s.length,15);assert.equal(c.length,13);assert.equal(g.length,16);
 assert.equal(new Set(s.map(z=>z.id)).size,15);
 assert.equal(new Set(c.map(z=>z.id)).size,13);
 assert.equal(new Set(g.map(z=>z.id)).size,16);
 assert.ok(g.every(z=>z.state==='HARD_HOLD'&&z.proof&&z.proof.length>20));
 assert.ok(s.every(z=>/^https:\/\//.test(z.url)));
 const ids=new Set(s.map(z=>z.id));
 assert.ok(c.every(z=>z.refs.length&&z.refs.every(id=>ids.has(id))));
 const prohibited=c.filter(z=>z.status.includes('PROHIBITED')||z.status.includes('UNSUBSTANTIATED'));
 assert.ok(prohibited.length>=4);
 assert.equal(c.find(z=>z.id==='C07').status,'seller_efficacy_UNSUBSTANTIATED');
 assert.equal(c.find(z=>z.id==='C09').status,'NOT_VERIFIED_must_not_assert');
 assert.match(x.article,/1980/);
 assert.match(x.article,/Thompson/);
 assert.match(x.article,/Bartlett/);
 assert.match(x.article,/Psalta/);
 assert.match(x.article,/Puységur/);
 assert.match(x.article,/source notes and verification/i);
 assert.match(x.article,/copyright ownership and image permissions/i);
 assert.match(x.article,/No affiliate recommendation or earning link/i);
 assert.doesNotMatch(x.article,/<script|<iframe|href=["']https?:\/\/(?:www\.)?zen12\.com/i);
 assert.doesNotMatch(x.article,/guaranteed (?:results|benefit|cure)|99% of (?:people|viewers) (?:fail|are fooled)/i);
 assert.match(x.plan,/Net revenue per 1,000/i);
 assert.match(x.plan,/26\/26 unsafe mutations rejected/i);
 assert.match(x.plan,/NOT COMPUTABLE/i);
 assert.match(x.plan,/preload="none"/i);
 assert.match(x.plan,/If you purchase through this link, Final Vestige may earn a commission at no additional cost to you/i);
 assert.match(x.plan,/NOT LIVE/);
 assert.match(x.plan,/NOT VERIFIED/);
 assert.match(x.plan,/no new form/i);
 assert.match(x.plan,/Grok retains creator/i);
 assert.match(x.plan,/Mind hub PR #172/i);
 assert.match(x.plan,/no invented values/i);
 assert.equal(m.video_status,'LOCAL_INSPECTED_NOT_HOSTED_NOT_LIVE');
 assert.equal(m.attribution_contract.unknowns.includes('NOT COMPUTABLE'),true);
 return 'R258 BASELINE PASS: 15 sources, 13 scoped claims, 16 HARD_HOLD gates';
}
console.log(check(base));
const cases=[
 ['claim without source',o=>{let m=JSON.parse(o.matrix);m.claims[0].refs=['UNKNOWN'];o.matrix=JSON.stringify(m)}],
 ['commercial turned on',o=>{let m=JSON.parse(o.matrix);m.commercial_activation=true;o.matrix=JSON.stringify(m)}],
 ['fake affiliate acceptance',o=>{let m=JSON.parse(o.matrix);m.partner_publisher_approval='ACCEPTED';o.matrix=JSON.stringify(m)}],
 ['one gate approved',o=>{let m=JSON.parse(o.matrix);m.commercial_gates[0].state='APPROVED';o.matrix=JSON.stringify(m)}],
 ['duplicate gate ID',o=>{let m=JSON.parse(o.matrix);m.commercial_gates[1].id=m.commercial_gates[0].id;o.matrix=JSON.stringify(m)}],
 ['false product efficacy',o=>{let m=JSON.parse(o.matrix);m.claims.find(c=>c.id==='C07').status='proven';o.matrix=JSON.stringify(m)}],
 ['invented CTA evidence',o=>o.plan=o.plan.replace('NOT COMPUTABLE','REVENUE VERIFIED')],
 ['remove FTC disclosure',o=>o.plan=o.plan.replace('If you purchase through this link, Final Vestige may earn a commission at no additional cost to you','Free health outcomes guaranteed')],
 ['fake Thatcher stat',o=>o.article+='\n99% of people are fooled by this test.'],
 ['remove photo rights guard',o=>o.article=o.article.replace('copyright ownership and image permissions','public image reuse welcome')],
 ['added unlicensed merchant link',o=>o.article+='\n<a href="https://zen12.com/secret/">Get it</a>'],
 ['fake merchant sale',o=>{let m=JSON.parse(o.matrix);m.video_status='PAID_SALES_VERIFIED';o.matrix=JSON.stringify(m)}]
];
let passed=0;
for(const [name,mut] of cases){
 const x={...base};mut(x);
 try{check(x);throw new Error('UNREJECTED: '+name)}
 catch(e){if(e.message.startsWith('UNREJECTED'))throw e;passed++}
}
console.log(passed+'/'+cases.length+' independent unsafe mutations REJECTED');
console.log('Static tests do not certify native browser/WP/checkout/sales.');
