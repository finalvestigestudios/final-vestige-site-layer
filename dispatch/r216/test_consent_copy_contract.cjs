'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {test}=require('node:test');
const {patch,count}=require('./consent_copy_contract.cjs');
const specs=JSON.parse(fs.readFileSync(path.join(__dirname,'page_patch_specs.json'),'utf8')).patches;
for(const s of specs) {
 const fixture={id:s.id,slug:s.slug,modified:s.modified,content:'prefix<!-- wp:jetpack/subscriptions /-->'+s.before+' href="somewhere" data-fv-event="focus_pdf_click" suffix'};
 // For dispatch the signup block must appear after the disclosure, matching real WordPress.
 if(s.slug==='dispatch') fixture.content='prefix'+s.before+'<!-- wp:jetpack/subscriptions /--><a href="https://finalvestige.com">link</a> suffix';
 test(s.slug+' patch is exactly reversible and preserves block count',()=>{
  const output=patch(fixture,s);
  assert.equal(output.replace(s.after,s.before),fixture.content);
  assert.equal(count(output,'<!-- wp:jetpack/subscriptions'),count(fixture.content,'<!-- wp:jetpack/subscriptions'));
 });
 test(s.slug+' rejects wrong page ID',()=>assert.throws(()=>patch({...fixture,id:42},s),/MISMATCH/));
 test(s.slug+' rejects stale revision',()=>assert.throws(()=>patch({...fixture,modified:'stale'},s),/MISMATCH/));
 test(s.slug+' rejects absent anchor',()=>assert.throws(()=>patch({...fixture,content:fixture.content.replace(s.before,'')},s),/NOT_UNIQUE/));
 test(s.slug+' rejects duplicate anchor',()=>assert.throws(()=>patch({...fixture,content:fixture.content+s.before},s),/NOT_UNIQUE/));
 test(s.slug+' rejects already applied copy',()=>assert.throws(()=>patch({...fixture,content:fixture.content.replace(s.before,s.after)},s)));
 test(s.slug+' preserves links',()=>{
   const out=patch(fixture,s);assert.equal(count(out,'href='),count(fixture.content,'href='));
 });
}
test('two focused patches, no affiliate links or live writes',()=>{
 assert.equal(specs.length,2);
 for(const s of specs){assert.doesNotMatch(s.after,/awin1|clickbank|checkout|<script/i);assert.doesNotMatch(s.after,/https?:\/\//i);}
});
