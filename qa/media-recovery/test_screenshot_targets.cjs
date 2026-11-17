'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const {classifyImages}=require('./browser_probe_core.cjs');
const {selectScreenshotTarget}=require('./screenshot_target_core.cjs');
const u='https://archive.example.gov/shared.jpg';
const stored=[{key:'291:2',source_url:u,alt:'Dam face breach'},{key:'291:5',source_url:u,alt:'Post-collapse cleanup'}];
const dom=()=>stored.map((s,index)=>({index,src:u,currentSrc:u,dataSrc:'',alt:s.alt,complete:true,naturalWidth:0}));
const classified=()=>classifyImages(stored,dom(),[{url:u,status:404,encodedDataLength:237}],true);
test('same image URL with differing descriptions maps two exact DOM slots',()=>{
 const c=classified();assert.deepEqual(c.map(x=>x.rendered_index),[0,1]);
 assert.deepEqual(c.map(x=>x.rendered_alt),stored.map(x=>x.alt));
 assert.deepEqual(c.map(x=>selectScreenshotTarget(x,dom()).index),[0,1]);
});
test('duplicate URL cannot capture first item for second image slot',()=>{
 const d=dom();d[1].alt=d[0].alt;
 assert.equal(selectScreenshotTarget(classified()[1],d).reason,'active_image_identity_or_alt_changed');
});
test('DOM reorder invalidates the selected element',()=>{
 const d=dom();d[0].index=1;
 assert.equal(selectScreenshotTarget(classified()[0],d).reason,'dom_index_changed');
});
test('responsive currentSrc replacement invalidates the screenshot',()=>{
 const d=dom();d[0].currentSrc='https://other.example.net/unrelated.jpg';
 assert.equal(selectScreenshotTarget(classified()[0],d).reason,'active_image_identity_or_alt_changed');
});
test('source placeholder replacement invalidates the screenshot',()=>{
 const d=dom();d[0].src='https://other.example.net/placeholder.jpg';
 assert.equal(selectScreenshotTarget(classified()[0],d).reason,'active_image_identity_or_alt_changed');
});
test('successful image recovery after scrolling invalidates broken screenshot',()=>{
 const d=dom();d[0].naturalWidth=960;
 assert.equal(selectScreenshotTarget(classified()[0],d).reason,'image_no_longer_visibly_broken');
});
test('unverified image cannot generate screenshot',()=>{
 const c=classified()[0];c.verified_broken_in_browser=null;
 assert.equal(selectScreenshotTarget(c,dom()).reason,'not_a_confirmed_identity_bound_failure');
});
test('missing and out of bounds DOM index fail closed',()=>{
 const c=classified()[0];delete c.rendered_index;
 assert.equal(selectScreenshotTarget(c,dom()).reason,'missing_or_out_of_bounds_dom_index');
 c.rendered_index=9;assert.equal(selectScreenshotTarget(c,dom()).reason,'missing_or_out_of_bounds_dom_index');
});
test('ambiguous same ALT duplicates are not screenshot candidates',()=>{
 const d=dom();d[1].alt=d[0].alt;
 const s=stored.map(x=>({...x,alt:'duplicate'}));
 const c=classifyImages(s,d,[{url:u,status:404}],true);
 assert.ok(c.every(x=>selectScreenshotTarget(x,d).ok===false));
});
test('loaded image never counts as broken screenshot',()=>{
 const d=dom();d[0].naturalWidth=600;
 const c=classifyImages(stored,d,[{url:u,status:200,encodedDataLength:100}],true);
 assert.equal(selectScreenshotTarget(c[0],d).ok,false);
});
test('missing DOM snapshot is reported explicitly',()=>{
 assert.equal(selectScreenshotTarget(classified()[0],null).reason,'missing_dom_snapshot');
});
