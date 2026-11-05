'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const os=require('node:os');
const {assetPolicy,repairSearch,renderDocument,build,STATE}=require('./r133_build_research_desk_preview.cjs');
const css='.fv-ex2-ledger{display:block}';
const js="document.querySelectorAll('[data-fvx-ledger]').forEach(root=>{root.dataset.test='ok'});";
const html='<section class="fv-ex2-ledger" data-fvx-ledger><h1>Source custody</h1></section>';
test('R133 creates an offline, static-first HTML staging document with source content',()=>{
 const out=renderDocument(html,css,js);
 assert.match(out,/<!doctype html>/i);
 assert.match(out,/Apollo 1 Research Desk · NOT LIVE/);
 assert.match(out,/data-fvx-ledger/);
 assert.match(out,/EDITORIAL STAGING ONLY/);
 assert.match(out,/noindex,nofollow,noarchive/);
 assert.match(out,/default-src 'none'/);
 assert.match(out,/connect-src 'none'/);
 assert.match(out,/form-action 'none'/);
 assert.match(out,/source links, not technical instruments/i);
 assert.ok(out.indexOf(html)<out.lastIndexOf('<script>'));
});
test('CSP hashes are deterministic, scoped, and change when bundled assets change',()=>{
 const a=renderDocument(html,css,js),b=renderDocument(html,css,js);
 assert.equal(a,b);
 assert.notEqual(a,renderDocument(html,css+'\n.fv-ex2-ledger{color:white}',js));
 assert.match(a,/style-src 'sha256-[a-zA-Z0-9+/=]+'/);
 assert.match(a,/script-src 'sha256-[a-zA-Z0-9+/=]+'/);
});
test('Network stylesheet import is rejected',()=>assert.ok(assetPolicy(css+'@import url("https://example.org/x.css")',js).includes('EXTERNAL_STYLE_DEPENDENCY')));
test('External font loading is rejected',()=>assert.ok(assetPolicy(css+'@font-face{font-family:x}',js).includes('EXTERNAL_STYLE_DEPENDENCY')));
test('Fetch API addition is rejected',()=>assert.ok(assetPolicy(css,js+'fetch("https://example.org")').includes('NETWORK_OR_STORAGE_DEPENDENCY')));
test('Browser visitor storage is rejected',()=>assert.ok(assetPolicy(css,js+'localStorage.setItem("k","v")').includes('NETWORK_OR_STORAGE_DEPENDENCY')));
test('Arbitrary runtime JS evaluation is rejected',()=>assert.ok(assetPolicy(css,js+'eval("alert(1)")').includes('DYNAMIC_EVALUATION')));
test('HTML injection through close-style and close-script tags is rejected',()=>{
 assert.ok(assetPolicy(css+'</style>',js).includes('UNSAFE_EMBED_TERMINATOR'));
 assert.ok(assetPolicy(css,js+'</script>').includes('UNSAFE_EMBED_TERMINATOR'));
});
test('Missing original component scopes are rejected',()=>assert.ok(assetPolicy('body{}','alert(1)').includes('COMPONENT_ASSET_MISMATCH')));
test('No paid offer, individual image rights, or browser acceptance can be claimed',()=>{
 assert.equal(STATE.release,'STAGING_HOLD');
 assert.equal(STATE.rights,'0_OF_6_CLEARED');
 assert.equal(STATE.paid_offer,'NOT_VERIFIED');
 assert.equal(STATE.browser_acceptance,'NOT_ESTABLISHED');
});
test('Full repository fixture: fail closed if R132 upstream source gate has not approved it',()=>{
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'fv-apollo-r133-negative-'));
 const outDir=path.join(root,'out');
 try{
  const src=path.join(root,'experience2/apollo-creator-bridge');
  const assets=path.join(root,'experience2/research-desk/assets');
  fs.mkdirSync(src,{recursive:true});fs.mkdirSync(assets,{recursive:true});
  fs.writeFileSync(path.join(src,'r132_research_desk_source_role_review.html'),html);
  fs.writeFileSync(path.join(assets,'source-ledger.css'),css);
  fs.writeFileSync(path.join(assets,'source-ledger.js'),js);
  assert.throws(()=>build({root,outDir}),/REFUSED_R132_SOURCE_GATE/);
  assert.equal(fs.existsSync(path.join(outDir,'apollo-r133-research-desk-editorial-preview.html')),false);
 }finally{fs.rmSync(root,{recursive:true,force:true});}
});
test('R132 omission of optional search-clear control is repaired once for isolated review only',()=>{
 const source='<span class="fv-ex2-ledger__status" role="status" aria-live="polite" data-fvx-status></span>';
 const repaired=repairSearch(source);
 assert.match(repaired,/data-fvx-clear hidden/);
 assert.equal(repairSearch(repaired),repaired);
 assert.throws(()=>repairSearch('<p>none</p>'),/REFUSED_SEARCH_REPAIR_AMBIGUOUS/);
});
test('Repository checkout: positive actual-source build is executed when required inputs are present',t=>{
 const root=path.resolve(__dirname,'../..');
 const source=path.join(root,'experience2/apollo-creator-bridge/r132_research_desk_source_role_review.html');
 if(!fs.existsSync(source)){t.skip("Exact R132 input files are not included in the standalone test package; repository CI must run the positive build.");return;}
 const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'fv-apollo-r133-actual-'));
 try{
  const first=build({root,outDir:tmp});const one=fs.readFileSync(first.output);
  const second=build({root,outDir:tmp});const two=fs.readFileSync(second.output);
  assert.deepEqual(one,two);
  assert.equal(first.manifest.artifact_sha256,second.manifest.artifact_sha256);
  assert.equal(first.manifest.count_verified_nasa_link_targets,6);
  assert.equal(first.manifest.release,'STAGING_HOLD');
 }finally{fs.rmSync(tmp,{recursive:true,force:true});}
});
