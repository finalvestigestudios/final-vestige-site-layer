import test from 'node:test';
import assert from 'node:assert/strict';
import {sanitizedSample,buildReceipt} from './lighthouse_receipt.mjs';
const good=(secret='private-nonce-SECRET',desktop=false)=>({
  configSettings:{formFactor:desktop?'desktop':'mobile',
    screenEmulation:{width:desktop?1440:390,height:desktop?900:844,mobile:!desktop},
    throttling:{cpuSlowdownMultiplier:desktop?1:4,
      rttMs:desktop?40:150,throughputKbps:desktop?10240:1638}},
  lighthouseVersion:'12.8.2',
  finalUrl:'http://127.0.0.1:9400/?nonce='+secret,
  categories:{performance:{score:0.86},accessibility:{score:1},
    'best-practices':{score:0.96}},
  audits:{
    'largest-contentful-paint':{numericValue:2092},
    'cumulative-layout-shift':{numericValue:0.00608},
    'first-contentful-paint':{numericValue:1023},
    'total-blocking-time':{numericValue:12},
    'speed-index':{numericValue:1590},
    'debug-audit':{details:{secret}}
  }
});
test('real numerical Lighthouse values and exact release HOLD',()=>{
  const m=sanitizedSample(good(),'mobile_390'),d=sanitizedSample(good('private-nonce-SECRET',true),'desktop_1440');
  const report=buildReceipt([m,d],'a'.repeat(40));
  assert.equal(report.audit_profiles[0].laboratory_metrics.lcp_ms,2092);
  assert.equal(report.audit_profiles[0].laboratory_metrics.cls,0.006);
  assert.equal(report.release.startsWith('HOLD'),true);
  assert.equal(report.public_wordpress_writes,false);
});
test('no leaked URL, nonce, page title, raw audits or cookie',()=>{
  const record=buildReceipt([sanitizedSample(good(),'mobile_390'),
    sanitizedSample(good('private-nonce-SECRET',true),'desktop_1440')],'a'.repeat(40));
  for(const forbidden of ['private-nonce-SECRET','127.0.0.1','finalUrl','debug-audit','cookie']){
    assert.equal(JSON.stringify(record).includes(forbidden),false,forbidden);
  }
});
test('Lighthouse runtime failure is a release hold',()=>{
  assert.throws(()=>sanitizedSample({...good(),runtimeError:{message:'secret'}},'mobile_390'));
});
test('missing or nonfinite metric fails closed',()=>{
  const x=good();delete x.audits['largest-contentful-paint'];
  assert.throws(()=>sanitizedSample(x,'mobile_390'));
  const y=good();y.audits['cumulative-layout-shift'].numericValue=NaN;
  assert.throws(()=>sanitizedSample(y,'mobile_390'));
});
test('missing category score or wrong profile fails closed',()=>{
  const x=good();x.categories.performance.score=null;
  assert.throws(()=>sanitizedSample(x,'mobile_390'));
  assert.throws(()=>sanitizedSample(good(),'rogue'));
});
test('desktop score requires actual desktop CPU and viewport preset',()=>{
  const m=good('secret',true);
  m.configSettings.throttling.cpuSlowdownMultiplier=4;
  assert.throws(()=>sanitizedSample(m,'desktop_1440'));
  const d=good('secret',true);
  d.configSettings.screenEmulation.width=412;
  assert.throws(()=>sanitizedSample(d,'desktop_1440'));
  const n=good('secret',true);
  n.configSettings.throttling.rttMs=150;
  assert.throws(()=>sanitizedSample(n,'desktop_1440'));
});
test('one profile or changed source SHA cannot be labeled complete',()=>{
  const s=sanitizedSample(good(),'mobile_390');
  assert.throws(()=>buildReceipt([s],'a'.repeat(40)));
  assert.throws(()=>buildReceipt([s,s],'a'.repeat(40)));
  assert.throws(()=>buildReceipt([s,{...s,profile:'desktop_1440'}],'short'));
});
