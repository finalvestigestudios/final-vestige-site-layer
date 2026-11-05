/** Offline Node CLI adversarial integration tests. No network, WordPress or user data. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp, readFile, writeFile, stat, access, rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {OLD_REDUCED_RULE, EXPECTED_CHAPTERS} from './margins_page6_native_patch.mjs';

const runner = new URL('./build_margins_page6_review.mjs', import.meta.url).pathname;
const makePublicPage = () => {
  const notes = Array.from({length:72},(_,i)=>'<span class="fv-margin-strip__item" style="--i:'+i+'">Synthetic historical fixture '+i+'</span>').join('');
  const hrefs = EXPECTED_CHAPTERS.map(id=>'<a href="#'+id+'">Chapter</a>').join('');
  const html = '<!-- wp:html -->\n<div class="fv-margin-strip fv-margin-strip--rotator"><div class="fv-margin-strip__inner"><div class="fv-margin-strip__label">Hidden in the Margins</div><div class="fv-margin-strip__window" tabindex="0" aria-label="Rotating source and accountability notes">'+notes+'</div></div></div><style>'+OLD_REDUCED_RULE+'</style>\n<!-- /wp:html --><!-- wp:html -->'+hrefs+'<a href="/focus/">Focus</a>'.repeat(4)+'<!-- wp:jetpack/subscriptions /--><!-- /wp:html -->';
  return {id:6,status:'publish',modified:'2026-11-04T14:39:24',content:html};
};
async function runWith(testFn){
  const dir = await mkdtemp(join(tmpdir(),'fv-margins-qa-'));
  const input = join(dir,'public.json');
  const output = join(dir,'review.review.blocks.html');
  const page = makePublicPage();
  const run = () => spawnSync(process.execPath,[runner,'--in',input,'--out',output,'--review-only'],{encoding:'utf8',timeout:10000});
  try { await writeFile(input, JSON.stringify(page)); await testFn({dir,input,output,page,run}); }
  finally { await rm(dir,{recursive:true,force:true}); }
}
async function absent(path){try{await access(path); return false;}catch{return true;}}
const sha256=x=>createHash('sha256').update(x).digest('hex');

test('positive offline review emits preserved 72 notes with SHA receipts and restrictive file modes',async()=>runWith(async({output,page,run})=>{
  const r=run();assert.equal(r.status,0,r.stderr);
  const result=await readFile(output,'utf8');const receipt=JSON.parse(await readFile(output+'.receipt.json','utf8'));
  assert.equal((result.match(/class="fv-margin-strip__item"/g)||[]).length,72);
  assert.equal(receipt.source_sha256,sha256(page.content));
  assert.equal(receipt.proposed_sha256,sha256(result));
  assert.equal(receipt.production_writes,0);assert.equal(receipt.release_gate,'HOLD');
  assert.equal((await stat(output)).mode&0o777,0o600);
  assert.equal((await stat(output+'.receipt.json')).mode&0o777,0o600);
}));

test('preexisting receipt fails closed, leaves no orphan output, preserves receipt bytes',async()=>runWith(async({output,run})=>{
  await writeFile(output+'.receipt.json','OWNER ORIGINAL');
  const r=run();assert.notEqual(r.status,0);assert.match(r.stderr,/REVIEW HOLD/);
  assert.equal(await absent(output),true);
  assert.equal(await readFile(output+'.receipt.json','utf8'),'OWNER ORIGINAL');
}));

test('preexisting output fails closed and never changes or deletes user content',async()=>runWith(async({output,run})=>{
  await writeFile(output,'OWNER ORIGINAL');const r=run();assert.notEqual(r.status,0);
  assert.equal(await readFile(output,'utf8'),'OWNER ORIGINAL');
  assert.equal(await absent(output+'.receipt.json'),true);
}));

test('stale source revision refuses to emit either review artifact',async()=>runWith(async({input,output,page,run})=>{
  page.modified='2026-11-05T00:00:00';await writeFile(input,JSON.stringify(page));
  const r=run();assert.notEqual(r.status,0);assert.match(r.stderr,/modified drift/);
  assert.equal(await absent(output),true);assert.equal(await absent(output+'.receipt.json'),true);
}));

test('private metadata is rejected before any review files are written',async()=>runWith(async({input,output,page,run})=>{
  page.meta={private_api_key:'synthetic-do-not-publish'};await writeFile(input,JSON.stringify(page));
  const r=run();assert.notEqual(r.status,0);assert.match(r.stderr,/private\/edit-context metadata/);
  assert.equal(await absent(output),true);assert.equal(await absent(output+'.receipt.json'),true);
}));

test('second run does not overwrite a completed first review or its receipt',async()=>runWith(async({output,run})=>{
  assert.equal(run().status,0);
  const before=[await readFile(output),await readFile(output+'.receipt.json')];
  const r=run();assert.notEqual(r.status,0);
  assert.deepEqual(await readFile(output),before[0]);
  assert.deepEqual(await readFile(output+'.receipt.json'),before[1]);
}));
