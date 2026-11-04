'use strict';
/* Apollo R122 — pure Node, no external dependencies. Run from this directory:
 * node --test test_r122_print_recovery.cjs
 * This tests the actual landing's extracted print controller, NOT browser acceptance. */
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const html=fs.readFileSync(path.join(__dirname,'landing-preview.html'),'utf8');
const start=html.indexOf('/* R122: recover an interrupted native print');
const stop=html.indexOf('</script>',start);
assert(start>=0&&stop>start,'R122 actual print-controller marker missing');
const controller=html.slice(start,stop);
function harness(options={}){
  const events={window:{},document:{},button:{},media:{}};
  const classes=new Set();const timers=[];let prints=0;
  const button={hidden:true,addEventListener(n,fn){events.button[n]=fn;}};
  const media={matches:false,addEventListener(n,fn){events.media[n]=fn;}};
  const win={
    print:options.unsupported?null:()=>{prints++;if(options.throwPrint)throw Error('Print blocked');},
    matchMedia:()=>media,
    addEventListener(n,fn){events.window[n]=fn;},
    setTimeout(fn){timers.push(fn);}
  };
  const doc={
    querySelector(q){
      if(q==='[data-fv-print-student]')return options.missingButton?null:button;
      if(q==='[data-fv-student-print]')return options.missingSheet?null:{};
      return null;
    },
    body:{classList:{add:k=>classes.add(k),remove:k=>classes.delete(k),contains:k=>classes.has(k)}},
    addEventListener(n,fn){events.document[n]=fn;}
  };
  vm.runInNewContext(controller,{window:win,document:doc,String},{timeout:1000});
  return {button,media,events,timers,classes,click(){events.button.click();},prints(){return prints;},
    pending(){return classes.has('fv-worksheet-only');}};
}
test('actual source preserves six separate NASA photo records, without embedded photo files',()=>{
  for(let i=1;i<=6;i++)assert.match(html,new RegExp('data-fv-student-photo="'+String(i).padStart(2,'0')+'"'));
  assert.doesNotMatch(html,/<(?:img|picture|iframe)\b/i);
});
test('print option is described by a unique adjacent guidance element',()=>{
  assert.match(html,/data-fv-print-student aria-describedby="student-print-guidance" hidden/);
  assert.equal((html.match(/id="student-print-guidance"/g)||[]).length,1);
});
test('real controller remains hidden when browser printing unsupported',()=>{
  assert.equal(harness({unsupported:true}).button.hidden,true);
});
test('real controller remains hidden if print sheet is unavailable',()=>{
  assert.equal(harness({missingSheet:true}).button.hidden,true);
});
test('real controller remains hidden if trigger is unavailable',()=>{
  assert.equal(harness({missingButton:true}).events.window.afterprint,undefined);
});
test('explicit print enters student-only mode, and afterprint restores ordinary print',()=>{
  const h=harness();assert.equal(h.button.hidden,false);
  h.click();assert.equal(h.prints(),1);assert(h.pending());
  h.events.window.afterprint();assert(!h.pending());
});
test('canceled print without afterprint does not block a second click',()=>{
  const h=harness();h.click();h.click();assert.equal(h.prints(),2);assert(h.pending());
});
test('Ctrl+P restores complete packet without intercepting the browser shortcut',()=>{
  const h=harness();h.click();
  h.events.document.keydown({key:'p',ctrlKey:true,metaKey:false});
  assert(!h.pending());
});
test('Cmd+P restores the complete packet',()=>{
  const h=harness();h.click();
  h.events.document.keydown({key:'P',ctrlKey:false,metaKey:true});
  assert(!h.pending());
});
test('unrelated shortcuts never clear pending print',()=>{
  const h=harness();h.click();
  h.events.document.keydown({key:'x',ctrlKey:true,metaKey:false});
  assert(h.pending());
});
test('native print exception resets full evidence packet',()=>{
  const h=harness({throwPrint:true});h.click();assert.equal(h.prints(),1);assert(!h.pending());
});
test('print media exit clears worksheet-only state',()=>{
  const h=harness();h.click();
  h.events.media.change({matches:false});assert(!h.pending());
});
test('print media entry does not prematurely reset worksheet-only state',()=>{
  const h=harness();h.click();
  h.events.media.change({matches:true});assert(h.pending());
});
test('focus fallback restores abandoned print once print media is closed',()=>{
  const h=harness();h.click();h.events.window.focus();
  assert.equal(h.timers.length,1);h.timers[0]();assert(!h.pending());
});
test('focus fallback never clears an active print media session',()=>{
  const h=harness();h.click();h.media.matches=true;h.events.window.focus();
  h.timers[0]();assert(h.pending());
});
test('pagehide removes stale worksheet-only mode',()=>{
  const h=harness();h.click();h.events.window.pagehide();assert(!h.pending());
});
test('controller never prevents default native print or creates tracking',()=>{
  assert.doesNotMatch(controller,/preventDefault|fetch\(|sendBeacon|localStorage|sessionStorage|cookie/);
  assert.doesNotMatch(controller,/if\s*\(pending\)\s*return\s*;/);
});
