// Source-only structural QA for optional Issue 06. Run: node --test dispatch/r363/release_check.test.mjs
import {readFileSync} from 'node:fs';
import {test} from 'node:test';
import assert from 'node:assert/strict';
const root = new URL('.', import.meta.url);
const read = name => readFileSync(new URL(name, root), 'utf8');
const md = read('ISSUE06_OPTIONAL.md'), txt = read('ISSUE06_OPTIONAL.txt'), html = read('ISSUE06_OPTIONAL.html');
const cta = 'https://finalvestige.com/2026/11/02/change-blindness/', doi = 'https://doi.org/10.3758/BF03208840';
test('original Issue06 remains optional and unsent',()=>{for (const f of [md,txt,html]) assert.match(f,/UNSENT|DO NOT SEND/i);assert.match(md,/NOT_ADOPTED/);});
test('exact subject and preheader parity',()=>{for(const f of [md,txt,html]){assert.ok(f.includes('Seven days of noticing. One thing you probably missed.'));assert.ok(f.includes("A fieldbook log, a door experiment, and a better question than 'did it work?'"));}});
test('primary destination is existing live article, not signup or merchant',()=>{for(const f of [md,txt,html]){assert.ok(f.includes(cta));assert.ok(!/affiliate\.inspire3|zen12\.com|hypnosislive\.com|\[\[APPROVED_/.test(f));}});
test('accuracy claim is qualified',()=>{for(const f of [md,txt,html]){assert.ok(/seven of fifteen|7\/15/i.test(f));assert.ok(f.includes(doi));}});
test('mandatory hard stop retained in all variants',()=>{for(const f of [md,txt,html]){assert.ok(f.includes('[[VALID_POSTAL_ADDRESS_REQUIRED]]'));assert.ok(f.includes('[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]'));}});
test('email-safe HTML avoids dynamic scripts and images',()=>{assert.match(html,/lang="en"/);assert.match(html,/role="presentation"/);assert.match(html,/name="viewport"/);assert.ok(!/<script|<form|<img|<iframe|onclick=|<style/i.test(html));});
test('source links are not commercial CTAs',()=>{assert.ok(html.includes('Primary research'));assert.ok(html.includes('Editorial Standards'));assert.equal((html.match(new RegExp(cta.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'),'g'))??[]).length,1);});
test('no sales / efficacy claims',()=>{for(const f of [md,txt,html])assert.ok(!/guaranteed (results|income)|clinically proven|one hour of meditation in twelve minutes/i.test(f));});
