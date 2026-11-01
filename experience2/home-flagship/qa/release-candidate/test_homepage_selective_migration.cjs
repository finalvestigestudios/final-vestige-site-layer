'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const os=require('node:os');
const cp=require('node:child_process');
const {assemble}=require('./assemble_homepage_migration.cjs');
const {attest,SHA}=require('./verify_homepage_migration.cjs');
const fragmentPath=process.env.FV_RELEASE_FRAGMENT;
if(!fragmentPath) throw new Error('FV_RELEASE_FRAGMENT must name the independently reviewed WordPress content-only fragment');
const fragment=fs.readFileSync(fragmentPath,'utf8');
const fragmentSha=SHA(fragment);
const marginTags=Array.from({length:72},(_,i)=>`<span class="fv-margin-strip__item" style="--i:${i}">Archive record ${i}</span>`).join('\n');
const MARGIN_BLOCK=`<!-- wp:html -->\n<div class="fv-margin-strip" role="region" aria-label="Hidden in the Margins">${marginTags}</div>\n<!-- /wp:html -->`;
const HERO=`<!-- wp:html -->\n<section class="fv-studios-hero" aria-labelledby="fv-studios-title">\n<h1 id="fv-studios-title">Find what others miss.</h1><p>Original hero, to be replaced only here.</p>\n<style>.fv-studios-hero{background:#070b0a}</style>\n</section>\n<!-- /wp:html -->`;
const CTA=`<!-- wp:html -->\n<section class="fv-focus-cta"><h2>Seven Day Focus Fieldbook</h2><a href="/focus/">Get the fieldbook</a><a href="/focus/">Learn more</a></section>\n<!-- /wp:html -->`;
const JETPACK=`<!-- wp:group --><div><p>Weekly Dispatch</p><!-- wp:jetpack/subscriptions {"className":"is-style-split"} /--></div><!-- /wp:group -->`;
const FEED=`<!-- wp:query {"query":{"postType":"post"}} --><section class="archive-feed">Recent investigations</section><!-- /wp:query -->`;
const SCHEMA=`<!-- wp:html -->\n<script type="application/ld+json">{"@type":"Organization","name":"Final Vestige Studios"}</script>\n<!-- /wp:html -->`;
const legacy=[MARGIN_BLOCK,HERO,CTA,JETPACK,FEED,SCHEMA].join('\n');
const opts={expectedLegacySha:SHA(legacy),expectedFragmentSha:fragmentSha};
const run=(l=legacy,f=fragment,o=opts)=>assemble(l,f,o);
const candidate=run().candidate;
const attestCandidate=(s=candidate)=>attest(legacy,s,{expectedLegacySha:SHA(legacy)});

test('selectively replaces only one old hero, preserving every other Gutenberg byte',()=>{
 const {candidate:c,receipt:r}=run();
 assert.equal(c,legacy.replace(HERO,'<!-- wp:html -->\n'+fragment.trim()+'\n<!-- /wp:html -->'));
 assert.ok(!c.includes('fv-studios-hero'));
 assert.equal((c.match(/<h1\b/g)||[]).length,1);
 assert.equal(r.preserved_margin_items,72);assert.equal(r.original_jetpack_blocks,1);
 assert.equal(r.original_focus_links,2);assert.equal(r.chapter_anchors,7);
});
test('all 72 original history spans remain identical and unique',()=>{
 for(let i=0;i<72;i++) assert.equal(candidate.split(`<span class="fv-margin-strip__item" style="--i:${i}">Archive record ${i}</span>`).length,2);
});
test('Jetpack Gutenberg and Focus Fieldbook CTA remain unchanged and correctly located',()=>{
 assert.ok(candidate.includes(JETPACK));assert.ok(candidate.includes(CTA));
 assert.ok(candidate.indexOf(CTA)>candidate.indexOf('id="fv-hf-mind-title"'));
});
test('editorial feed and JSON-LD remain exact, no subscribe endpoint invented',()=>{
 assert.ok(candidate.includes(FEED)); assert.ok(candidate.includes(SCHEMA));
 assert.ok(!candidate.includes('fv-studios-title'));
});
test('candidate has actual seven chapters and cases',()=>assert.equal(attestCandidate().chapter_anchors,7));
test('reject missing required source SHA',()=>assert.throws(()=>run(legacy,fragment,{expectedFragmentSha:fragmentSha}),/source SHA/));
test('reject changed live page baseline',()=>assert.throws(()=>run(legacy+'\n',fragment),/page source changed/));
test('reject altered seven-chapter fragment',()=>assert.throws(()=>run(legacy,fragment+'\n'),/fragment SHA/));
test('reject missing independent fragment fingerprint',()=>assert.throws(()=>run(legacy,fragment,{expectedLegacySha:SHA(legacy)}),/fragment SHA/));
test('reject missing hero',()=>{const v=legacy.replace(HERO,'');assert.throws(()=>run(v,fragment,{...opts,expectedLegacySha:SHA(v)}),/no unique/);});
test('reject duplicate hero',()=>{const v=legacy+HERO;assert.throws(()=>run(v,fragment,{...opts,expectedLegacySha:SHA(v)}),/no unique/);});
test('reject renamed hero title',()=>{const v=legacy.replace('Find what others miss.','Explore the archive.');assert.throws(()=>run(v,fragment,{...opts,expectedLegacySha:SHA(v)}),/legacy hero structure/);});
test('reject protected Margins moved inside old hero',()=>{const v=legacy.replace(HERO,HERO.replace('</section>',marginTags+'</section>'));assert.throws(()=>run(v,fragment,{...opts,expectedLegacySha:SHA(v)}),/protected historical/);});
test('reject remote script in injected fragment despite digest',()=>{const f=fragment.replace('</div>','<script src="https://cdn.example/test.js"></script></div>');assert.throws(()=>run(legacy,f,{...opts,expectedFragmentSha:SHA(f)}),/executable/);});
test('reject nested main landmark despite digest',()=>{const f=fragment.replace('</div>','<main>wrong</main></div>');assert.throws(()=>run(legacy,f,{...opts,expectedFragmentSha:SHA(f)}),/main/);});
test('reject altered chapter anchor despite new digest',()=>{const f=fragment.replace('id="fv-hf-chronicle"','id="changed"');assert.throws(()=>run(legacy,f,{...opts,expectedFragmentSha:SHA(f)}),/chapter anchor/);});
test('reject hidden entire original preservation segment',()=>{
 const v=legacy.replace(MARGIN_BLOCK,`<div hidden aria-hidden="true">${MARGIN_BLOCK}</div>`);
 assert.throws(()=>attest(v,candidate.replace(MARGIN_BLOCK,`<div hidden aria-hidden="true">${MARGIN_BLOCK}</div>`),{expectedLegacySha:SHA(v)}),/concealed/);
});
test('reject hidden container around protected Margins',()=>assert.throws(()=>attestCandidate(candidate.replace(MARGIN_BLOCK,`<div hidden aria-hidden="true">${MARGIN_BLOCK}</div>`)),/concealed/));
test('reject display:none container around protected Margins',()=>assert.throws(()=>attestCandidate(candidate.replace(MARGIN_BLOCK,`<div style="display: none">${MARGIN_BLOCK}</div>`)),/concealed/));
test('reject inert template around all protected blocks',()=>assert.throws(()=>attestCandidate(candidate.replace(JETPACK,`<template>${JETPACK}</template>`)),/concealed/));
test('reject aria-hidden Focus links',()=>assert.throws(()=>attestCandidate(candidate.replace(CTA,`<div aria-hidden="true">${CTA}</div>`)),/concealed/));
test('reject visibility hidden Jetpack block',()=>assert.throws(()=>attestCandidate(candidate.replace(JETPACK,`<div style="visibility:hidden">${JETPACK}</div>`)),/concealed/));
test('reject opacity zero Focus blocks',()=>assert.throws(()=>attestCandidate(candidate.replace(CTA,`<section style="opacity:0">${CTA}</section>`)),/concealed/));
test('reject collapsed details with preserved subscription',()=>assert.throws(()=>attestCandidate(candidate.replace(JETPACK,`<details>${JETPACK}</details>`)),/concealed/));
test('reject content hidden within <script> despite raw regex occurrences',()=>assert.throws(()=>attestCandidate(candidate.replace(JETPACK,`<script type="text/plain">${JETPACK}</script>`)),/visible-source/));
test('reject old injected form in fragment even with reviewed digest',()=>{const f=fragment.replace('</div>','<form><input></form></div>');assert.throws(()=>run(legacy,f,{...opts,expectedFragmentSha:SHA(f)}),/form/);});
test('CLI writes private mode files then refuses overwrite',()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'fv-private-migration-'));
 const legacyFile=path.join(dir,'legacy.txt'),fragFile=path.join(dir,'fragment.txt'),out=path.join(dir,'candidate.html'),receipt=path.join(dir,'receipt.json');
 try {
  fs.writeFileSync(legacyFile,legacy);fs.writeFileSync(fragFile,fragment);
  const args=[path.join(__dirname,'assemble_homepage_migration.cjs'),'--legacy',legacyFile,'--fragment',fragFile,'--legacy-sha256',opts.expectedLegacySha,'--fragment-sha256',opts.expectedFragmentSha,'--out',out,'--receipt',receipt];
  const run=()=>cp.spawnSync(process.execPath,args,{encoding:'utf8'});
  const one=run();assert.equal(one.status,0,one.stderr);
  assert.equal(fs.readFileSync(out,'utf8'),candidate);
  assert.equal(JSON.parse(fs.readFileSync(receipt,'utf8')).status,'SELECTIVE_GUTENBERG_CANDIDATE_REVIEW_ONLY_NOT_DEPLOYED');
  assert.equal(fs.statSync(out).mode&0o777,0o600);
  assert.notEqual(run().status,0);
 } finally{fs.rmSync(dir,{recursive:true,force:true});}
});
