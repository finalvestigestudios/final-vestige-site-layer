#!/usr/bin/env node
/**
 * Offline, read-only quality gate for the FV "Two Timelines" draft.
 * Usage from repository root:
 *   node scripts/editorial/check-two-timelines-evidence-gate.mjs
 * No network, dependency, WordPress or account access.
 * This exercises the exact pure comparison functions extracted from draft HTML.
 * It cannot replace production-browser, real-theme or assistive-technology QA.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';
import vm from 'node:vm';

const here=path.dirname(fileURLToPath(import.meta.url));
const file=path.resolve(here,'../../docs/editorial/library/the-two-timelines-chronology-conflict-desk-2026-11-17.html');
const html=fs.readFileSync(file,'utf8');
const match=html.match(/<script>([\s\S]*?)<\/script>/);
assert.ok(match,'One inline script must exist');
const script=match[1];
assert.equal((html.match(/<script>/g)||[]).length,1,'Only one script supported');
new vm.Script(script,{filename:'two-timelines-inline.js'}); // parse-only; never execute DOM code here
const start=script.indexOf('function parseMinute(');
const end=script.indexOf('function compare(){',start);
assert.ok(start>0 && end>start,'Expected pure function boundary');
const api=vm.runInNewContext('(()=>{'+script.slice(start,end)+'return {parseMinute,interval,classifyPair,pairResults,pairDescription};})()', {},{timeout:1000});
const r={source:'Primary record A',original:'09:00 UTC',kind:'Event occurrence',url:'https://www.nasa.gov/',
  basis:'utc',start:'1967-01-27 09:00',end:'1967-01-27 09:02',
  qualification:'NASA source + explicit clock rationale; test-only hypothetical values'};
const s={...r,source:'Primary record B'};
const tests=[
 ['overlap',()=>api.classifyPair(r,s)==='overlap'],
 ['separate',()=>api.classifyPair(r,{...s,start:'1967-01-27 09:03',end:'1967-01-27 09:04'})==='separate'],
 ['boundary-inclusive',()=>api.classifyPair(r,{...s,start:'1967-01-27 09:02'})==='overlap'],
 ['event-is-not-transmission',()=>api.classifyPair(r,{...s,kind:'Message transmission or receipt'})==='different'],
 ['event-is-not-publication',()=>api.classifyPair(r,{...s,kind:'Publication or release'})==='different'],
 ['absent-original-before-kind-classification',()=>api.classifyPair(r,{...s,original:'',kind:'Publication or release'})==='unknown'],
 ['absent-source-before-kind-classification',()=>api.classifyPair(r,{...s,source:'',kind:'Publication or release'})==='unknown'],
 ['missing-clock-note',()=>api.classifyPair(r,{...s,qualification:''})==='unknown'],
 ['missing-title',()=>api.classifyPair(r,{...s,source:''})==='unknown'],
 ['unknown-kind',()=>api.classifyPair(r,{...s,kind:'Unclear'})==='unknown'],
 ['unverified-clock',()=>api.classifyPair(r,{...s,basis:'unverified'})==='unknown'],
 ['inverted-window',()=>api.classifyPair(r,{...s,start:'1967-01-28 09:00'})==='unknown'],
 ['calendar-invalid',()=>api.parseMinute('1967-02-29 09:00')===null],
 ['leap-day',()=>api.parseMinute('1968-02-29 09:00')!==null],
 ['25-hour-invalid',()=>api.parseMinute('1967-01-27 25:00')===null],
 ['pair-count',()=>api.pairResults([r,s,{...r,source:'Primary record C'}]).length===3],
 ['non-contradiction-label',()=>api.pairDescription({type:'different'}).includes('DIFFERENT ACTIONS')],
 ['no-duplicate-static-ids',()=>{const a=html.match(/id="[^"]+"/g)||[];return new Set(a).size===a.length}],
 ['static-source-note',()=>html.includes('Source check: November 17, 2026')],
 ['original-non-documentary-svg',()=>html.includes('not historical testimony')&&html.includes('tt-apollo-desc')],
 ['responsive-breakpoints',()=>html.includes('@media(max-width:760px)')&&html.includes('@media(max-width:390px)')],
 ['no-external-script',()=>!/<script[^>]*src=/i.test(html)],
 ['re-number-after-removal',()=>script.includes('b.remove();renumber();')],
 ['same-story-cross-link',()=>html.includes('/free-resources/the-same-story-twice/')]
];
let passed=0;
for(const [name,test] of tests){assert.ok(test(),name);passed++;}
const receiptCode=script.slice(script.indexOf('function receipt(){'),script.indexOf('root.querySelector("#tt-add")'));
assert.ok(receiptCode.includes('function receipt(){'),'receipt function found');
const receipt=vm.runInNewContext('(()=>{'+script.slice(start,end)+
  'function rows(){return '+JSON.stringify([r,s])+';}'+
  'const root={querySelector:()=>({value:"Test event"})};'+receiptCode+
  'return receipt();})()', {},{timeout:1000});
assert.ok(receipt.includes('\n## Pairwise result\n'),'Markdown output has actual newlines');
assert.ok(receipt.includes('Record URL: https://www.nasa.gov/'),'URI preserved');
assert.ok(receipt.includes('WINDOWS OVERLAP'),'Pairwise result exported');
passed+=3;
console.log(JSON.stringify({status:'pass',passed,source:file,scope:'offline extracted comparator and export; NOT production browser acceptance'},null,2));
