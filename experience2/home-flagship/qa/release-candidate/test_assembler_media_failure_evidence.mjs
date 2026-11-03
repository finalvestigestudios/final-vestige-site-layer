#!/usr/bin/env node
/** Offline adversarial custody tests — no network, WordPress writes or tokens.
 * A mock browser proves fail-closed behavior, NOT actual Chromium/axe success.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {imageBodies} from './playground_assembler_render_gate.mjs';

const APOLLO='https://finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp';
const FRANKLIN='https://finalvestige.com/wp-content/uploads/2026/08/Franklinexpeditionnote.jpg';
const bytes=Buffer.alloc(300,81);

function fakeImage(url,{decodeFails=false,width=1041,complete=true}={}){
  return {src:url,currentSrc:url,naturalWidth:width,naturalHeight:810,
    complete,loading:'lazy',
    async decode(){if(decodeFails)throw new Error('decode failed');}};
}
function fakePage(images,{status=200,mime='image/jpeg',body=bytes}={}){
  const requests=[];
  return {
    requests,
    page:{
      locator(selector){
        assert.equal(selector,'img');
        return {evaluateAll:async fn=>fn(images)};
      },
      request:{async get(url,options){
        requests.push({url,options});
        return {
          status:()=>status,
          headers:()=>({'content-type':mime}),
          body:async()=>body
        };
      }}
    }
  };
}

test('two distinct authentic source file names: HTTP byte hashes AND decoded pixels',async()=>{
  const p=fakePage([fakeImage(APOLLO),fakeImage(FRANKLIN)]);
  const rows=await imageBodies(p.page);
  assert.equal(rows.length,2);
  assert.ok(rows.every(x=>x.pass&&x.decoded&&x.status===200&&x.bytes===300));
  assert.ok(rows.every(x=>/^[a-f0-9]{64}$/.test(x.sha256)));
  assert.deepEqual(rows.map(x=>x.source_file),
    ['s67-19766.webp','Franklinexpeditionnote.jpg']);
  assert.equal(p.requests.length,2);
  assert.ok(p.requests.every(x=>x.options.failOnStatusCode===false));
});

test('duplicate visual and decorative image sources never re-download same URL',async()=>{
  const p=fakePage([fakeImage(APOLLO),fakeImage(APOLLO),fakeImage(FRANKLIN),fakeImage(FRANKLIN)]);
  const rows=await imageBodies(p.page);
  assert.equal(rows.length,4);
  assert.equal(p.requests.length,2);
});

test('HTTP 404 fails despite browser natural dimensions',async()=>{
  const p=fakePage([fakeImage(APOLLO),fakeImage(FRANKLIN)],{status:404});
  await assert.rejects(imageBodies(p.page),/byte or browser decode failure/);
});

test('non-image content type fails despite 200 and sufficient bytes',async()=>{
  const p=fakePage([fakeImage(APOLLO),fakeImage(FRANKLIN)],{mime:'text/html'});
  await assert.rejects(imageBodies(p.page),/byte or browser decode failure/);
});

test('zero-length or tiny media body fails closed',async()=>{
  const p=fakePage([fakeImage(APOLLO),fakeImage(FRANKLIN)],{body:Buffer.alloc(2)});
  await assert.rejects(imageBodies(p.page),/byte or browser decode failure/);
});

test('browser decode failure fails even when HTTP transfer succeeds',async()=>{
  const p=fakePage([fakeImage(APOLLO,{decodeFails:true}),fakeImage(FRANKLIN)]);
  await assert.rejects(imageBodies(p.page),/byte or browser decode failure/);
});

test('browser naturalWidth zero fails even when HTTP transfer succeeds',async()=>{
  const p=fakePage([fakeImage(APOLLO,{width:0}),fakeImage(FRANKLIN)]);
  await assert.rejects(imageBodies(p.page),/byte or browser decode failure/);
});

test('missing second distinct archival source fails closed',async()=>{
  const p=fakePage([fakeImage(APOLLO),fakeImage(APOLLO)]);
  await assert.rejects(imageBodies(p.page),/Missing distinct Apollo and Franklin/);
});

test('untrusted hosts and non-image URLs cannot count as source proof',async()=>{
  const p=fakePage([fakeImage(APOLLO),fakeImage('https://evil.example/Franklin.jpg')]);
  await assert.rejects(imageBodies(p.page),/Missing two archival browser image/);
  assert.equal(p.requests.length,0);
});

test('saved-style screenshots precede ALL layout assertions and axe',()=>{
  const code=readFileSync(new URL('./playground_assembler_render_gate.mjs',import.meta.url),'utf8');
  assert.ok(code.indexOf('await page.screenshot(')<code.indexOf('assert.equal(state.chapter_links'));
  assert.ok(code.indexOf('await page.screenshot(')<code.indexOf('await page.addScriptTag({path:axePath})'));
  assert.ok(code.includes("'assembler-1440-fullpage.png'"));
  assert.ok(code.includes("'assembler-390-nojs.png'"));
  assert.ok(code.includes("runBounded(document)"));
  assert.ok(code.includes("width===1440?await imageBodies(page):[]"));
  assert.ok(!code.includes("page.addStyleTag("),'No browser-only style overlay permitted');
});
