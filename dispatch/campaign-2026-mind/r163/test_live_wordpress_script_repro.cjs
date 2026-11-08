'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');
// Script body transcribed from authenticated WordPress page #1579 on 2026-11-06, no POST or email.
const liveScript="(function(){var g=document.getElementById('fvf-gift');if(!g){return;}\nvar bad=['invalid_email','error','blocked_email','opted_out','blocked'];\nfunction show(){g.hidden=false;}\nvar q=null;try{q=new URLSearchParams(window.location.search).get('subscribe');}catch(e){}\nif(q){if(bad.indexOf(q)<0){show();}}\nvar c=document.querySelector('.wp-block-jetpack-subscriptions__container');\nfunction check(){if(c){if(/\\bis-subscriber\\b/.test(c.className)){show();}}}\ncheck();if(c){if(window.MutationObserver){new MutationObserver(check).observe(c,{attributes:true,attributeFilter:['class']});}}})();";
function simulate(query='',cls=''){
 const gift={hidden:true};
 const container={className:cls};
 const ctx={document:{getElementById:id=>id==='fvf-gift'?gift:null,querySelector:()=>container},window:{location:{search:query},MutationObserver:null},URLSearchParams};
 vm.runInNewContext(liveScript,ctx,{timeout:800});
 return gift.hidden;
}
test('REPRO current script: arbitrary query reveals gift without confirmation',()=>assert.equal(simulate('?subscribe=anything'),false));
test('REPRO current script: positive-sounding query reveals gift without confirmation',()=>assert.equal(simulate('?subscribe=confirmed'),false));
test('REPRO current script: denylist errors are hidden',()=>assert.equal(simulate('?subscribe=invalid_email'),true));
test('REPRO current script: CSS class alone reveals gift',()=>assert.equal(simulate('', 'wp-block-jetpack-subscriptions__container is-subscriber'),false));
test('REPRO current script: plain visitor stays hidden',()=>assert.equal(simulate('', 'wp-block-jetpack-subscriptions__container'),true));
