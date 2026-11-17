'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {gitBlobSha,checkPinnedParts,checkFrozenBaseline,FROZEN_PART_BLOBS}=require('./frozen_census_claim_gate_20261102.cjs');
function fixture(){
 const parts=Array.from({length:8},()=>({posts:[],images:[]}));
 const pages=[];
 for(let j=0;j<61;j++){
  const id=j+1000,n=j<50?6:5,url='https://finalvestige.com/test-'+id+'/';
  const part=parts[Math.floor(j*8/61)];
  part.posts.push({id,url,images:n});
  const stored_images=[];
  for(let i=0;i<n;i++){
   const key=id+':'+i,source_url='https://finalvestige.com/wp-content/uploads/frozen-'+key+'.png';
   part.images.push({key,post_id:id,slot:i,source_url});
   stored_images.push({image_key:key,stored_url:source_url});
  }
  pages.push({post_id:id,url,stored_image_count:n,stored_images});
 }
 return {snapshot:{parts},baseline:{pages}};
}
const reject=(label,mutate,expected)=>test(label,()=>{
 const {snapshot,baseline}=fixture();mutate(snapshot,baseline);
 const got=checkFrozenBaseline(snapshot,baseline);
 assert.ok(got.some(x=>x.includes(expected)),JSON.stringify(got));
});
test('exactly 61 frozen articles and 355 immutable source references accepted',()=>{
 const {snapshot,baseline}=fixture();assert.deepEqual(checkFrozenBaseline(snapshot,baseline),[]);
});
reject('same 61/355 totals but different article is rejected',(_s,b)=>{b.pages[0].post_id=9000;b.pages[0].url='https://finalvestige.com/test-9000/'},'baseline_post_url_not_in_frozen');
reject('same totals but mismatched baseline image URL is rejected',(_s,b)=>{b.pages[0].stored_images[0].stored_url='https://finalvestige.com/wp-content/uploads/swap.png'},'baseline_image_not_frozen');
reject('same totals but swapped slot image IDs are rejected',(_s,b)=>{const a=b.pages[0].stored_images;a[0].image_key=a[1].image_key},'baseline_image_not_frozen');
reject('same totals but changed article permalink is rejected',(_s,b)=>{b.pages[0].url+='changed/'},'baseline_post_url_not_in_frozen');
reject('duplicate article ID rejected',(_s,b)=>{b.pages[0].post_id=b.pages[1].post_id},'baseline_duplicate_or_invalid_post_id');
reject('missing article slot rejected',(_s,b)=>{b.pages[0].stored_images.pop()},'baseline_image_count_not_frozen');
reject('wrong source inventory total rejected', (s)=>{s.parts[0].images.pop()},'frozen_61_355_count_mismatch');
reject('frozen records cannot claim duplicate photo keys',(s)=>{s.parts[0].images[0].key=s.parts[0].images[1].key},'duplicate_or_invalid_frozen_image');
reject('wrong post source count rejected',(s)=>{s.parts[0].posts[0].images=3},'baseline_image_count_not_frozen');
test('git blob hashing uses Git object format including byte length',()=>{
 assert.equal(gitBlobSha(Buffer.from('hello\n')),'ce013625030ba8dba906f756967f9e9ca394464a');
});
test('all eight archive parts are hash-pinned and bad edits are rejected',()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'fv-image-pin-'));
 try{
  fs.mkdirSync(path.join(dir,'parts'));
  const shas=[];
  for(let i=1;i<=8;i++){
   const b=Buffer.from(JSON.stringify({batch:i}));shas.push(gitBlobSha(b));
   fs.writeFileSync(path.join(dir,'parts',String(i).padStart(2,'0')+'.json'),b);
  }
  assert.equal(checkPinnedParts(dir,shas),true);
  fs.appendFileSync(path.join(dir,'parts','02.json'),' ');
  assert.throws(()=>checkPinnedParts(dir,shas),/frozen_source_part_mismatch:parts\/02.json/);
 }finally{fs.rmSync(dir,{recursive:true,force:true})}
});
test('release manifest pins all eight 40-character Git SHA-1 object IDs',()=>{
 assert.equal(FROZEN_PART_BLOBS.length,8);
 for(const sha of FROZEN_PART_BLOBS)assert.match(sha,/^[a-f0-9]{40}$/);
});
