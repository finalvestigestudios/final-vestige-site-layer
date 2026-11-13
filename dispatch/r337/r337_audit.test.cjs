'use strict';
const { test }=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const read=f=>fs.readFileSync(path.join(__dirname,f),'utf8');
const md=read('issue04-apollo1.md'),html=read('issue04-apollo1.html'),txt=read('issue04-apollo1.txt');
const ledger=read('PRIMARY_SOURCE_SENTENCE_LEDGER.md'),funnel=read('SIX_ISSUE_DECISIONS.md'),guide=read('README.md');
const subj='Apollo 1: five minutes to open the hatch',pre='The surviving timeline tells a harder story than a single spark.';
const dest='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
for(const [label,data] of [['md',md],['html',html],['txt',txt]]){
 test(label+' subject accurate',()=>assert.ok(data.includes(subj)));
 test(label+' proposed preheader present',()=>assert.ok(data.includes(pre)));
 test(label+' one approved first-party destination',()=>assert.ok(data.includes(dest)));
 test(label+' unsent review only',()=>assert.match(data,/UNSENT/i));
 test(label+' precise 17.7 seconds contextualized',()=>assert.match(data,/17.7 seconds/));
 test(label+' estimate of five minutes stated',()=>assert.match(data,/five minutes/i));
 test(label+' no direct earning link',()=>assert.doesNotMatch(data,/hoplink|clickbank\.net|\?hop=|utm_campaign=/i));
 test(label+' no unsupported meditation efficacy',()=>assert.doesNotMatch(data,/12 minutes = 1 hour|guaranteed productivity|brain reprogramming is proven/i));
}
test('HTML has semantic language',()=>assert.match(html,/<html lang="en">/));
test('HTML table layout and inline style',()=>{assert.match(html,/role="presentation"/);assert.match(html,/style="font:/)});
test('HTML single main CTA',()=>assert.equal((html.match(/Read The Hatch Opened Inward/g)||[]).length,1));
test('HTML no scripting or images',()=>assert.doesNotMatch(html,/<script|<img/i));
test('No fabricated postal/unsubscribe placeholders',()=>assert.doesNotMatch(html,/\[\[VALID_POSTAL|\[\[JETPACK_UNSUBSCRIBE/i));
test('Source ledger has both actual chronology timestamps',()=>{assert.match(ledger,/23:31:04.7/);assert.match(ledger,/23:31:22.4/)});
test('Uncertainty on cause preserved',()=>assert.match(ledger,/no proven single ignition source/i));
test('Campaign commercial lanes blocked',()=>assert.match(funnel,/HOLD_MERCHANT/));
test('Revenue not inferred from clicks',()=>assert.match(funnel,/not settled sales/i));
test('No production approval implied',()=>assert.match(guide,/not adopted/i));
