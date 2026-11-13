#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),assert=require('node:assert/strict'),path=require('node:path');
const root=__dirname,read=n=>fs.readFileSync(path.join(root,n),'utf8');
const a=read('ZEN12_A_TEXT_REVIEW.html'),b=read('ZEN12_B_OPTIONAL_FILM_REVIEW.html');
const hub=read('MIND_HUB_REVIEW.html'),poster=read('ZEN12_42S_POSTER.svg'),vtt=read('ZEN12_42S_CAPTIONS.vtt');
const matrix=JSON.parse(read('CLAIM_SOURCE_AND_RELEASE.json'));
let count=0;function ok(pred,what){assert.ok(pred,what);count++}
for(const [name,html] of [['A',a],['B',b],['Hub',hub]]){
ok(html.startsWith('<!doctype html>'),name+' html document');
ok(/<html lang="en">/.test(html),name+' lang');
ok(/name="viewport"/.test(html),name+' responsive');
ok(/name="robots" content="noindex,nofollow"/.test(html),name+' unpublished');
ok(!/<script\b|<iframe\b|<form\b|<input\b|<video\b|<audio\b|<[^>]+\sautoplay(?:[ =/>])|<link\b[^>]+rel="preload"/i.test(html),name+' no scripts/forms/media');
ok(/focus-visible/.test(html),name+' focus indicator');
ok(/prefers-reduced-motion/.test(html),name+' reduced-motion');
ok(!/https?:\/\/(?:www\.)?(?:payhip\.com|affiliates\.inspire3\.com)\/.*(?:ref|aff|tracking)/i.test(html),name+' no issued earning links');
}
for(const [name,html] of [['A',a],['B',b]]){
ok(/<button type="button" disabled aria-disabled="true">/.test(html),name+' native purchase disable');
ok(/Prospective affiliate disclosure/.test(html),name+' earnings disclosure');
ok(html.indexOf('Prospective affiliate disclosure')<html.indexOf('Seller checkout unavailable'),name+' disclosure before button');
ok(/merchant approval pending|partner approval pending/.test(html),name+' missing approval');
ok(/Beginner is the first six levels and 24 MP3s/.test(html),name+' tier A');
ok(/Premium is the complete twelve-level, 48-MP3 program/.test(html),name+' full tier');
ok(/Advanced is the final six levels and 24 MP3s/.test(html),name+' tier C');
ok(/seller's Zen12 sample page says that the visitor will also receive its newsletter/.test(html),name+' consent separation');
ok(!/<a[^>]*href=["'][^"']*(?:aff_id|ref=|hop=|affiliate)/i.test(html),name+' no active earning');
}
ok(b.replace(/<figure class="optional-film">[\s\S]*?<\/figure>/,'')===a.replace('B — Optional Film','A — Text Only'),'A/B identical non-film copy');
ok(b.includes('ZEN12_42S_POSTER.svg')&&b.includes('ZEN12_42S_CAPTIONS.vtt'),'B film sources');
ok(poster.includes('A SAMPLE IS NOT A STUDY')&&!/<script\b|<foreignObject\b|<image\b/i.test(poster),'safe original poster');
ok(vtt.startsWith('WEBVTT')&&(vtt.match(/-->/g)||[]).length===6,'six caption segments');
ok(matrix.gates&&Object.keys(matrix.gates).length===18&&Object.values(matrix.gates).every(v=>v===false),'18 commercial gates closed');
ok(matrix.sources.length>=12&&matrix.claims.length>=12,'claim/source volume');
ok(hub.includes('/focus/')&&hub.includes('puysegurs-animal-magnetism-files'),'hub actual live links');
const mut=[
a.replace('disabled aria-disabled="true"','aria-disabled="true"'),
a.replace('Prospective affiliate disclosure','Marketing information'),
a.replace('seller\'s Zen12 sample page says that the visitor will also receive its newsletter','seller sample is free'),
a+'<script>evil()</script>', a+'<form method="GET"></form>',
a.replace('48-MP3 program','24-MP3 program'),
a.replace('<button type="button"','<a href="https://example.com/buy"'),
a.replace('If you purchase through an approved earning link','After you purchase through our link')
];
function safe(x){return /<button type="button" disabled aria-disabled="true">/.test(x)&&/Prospective affiliate disclosure/.test(x)&&/seller's Zen12 sample page says that the visitor will also receive its newsletter/.test(x)&&!/script\b|<form\b/i.test(x)&&/48-MP3 program/.test(x)&&!/<a href="https:\/\/example\.com\/buy"/.test(x)&&/If you purchase through an approved earning link/.test(x)}
mut.forEach((m,i)=>ok(!safe(m),'mutation '+i+' rejected'));
process.stdout.write('PASS '+count+' source/negative assertions (native Node)\\n');
