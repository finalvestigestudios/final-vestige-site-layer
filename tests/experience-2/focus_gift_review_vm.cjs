'use strict';
/* Browser-independent VM controls for the actual live script and offline review patch.
   NO requests, WordPress writes, subscriber records, or merchant events. */
const vm=require('node:vm');
const assert=require('node:assert/strict');
const crypto=require('node:crypto');
const fs=require('node:fs');
const live=[
"(function(){var g=document.getElementById('fvf-gift');if(!g){return;}",
"var bad=['invalid_email','error','blocked_email','opted_out','blocked'];",
"function show(){g.hidden=false;}",
"var q=null;try{q=new URLSearchParams(window.location.search).get('subscribe');}catch(e){}",
"if(q){if(bad.indexOf(q)<0){show();}}",
"var c=document.querySelector('.wp-block-jetpack-subscriptions__container');",
"function check(){if(c){if(/\\bis-subscriber\\b/.test(c.className)){show();}}}",
"check();if(c){if(window.MutationObserver){new MutationObserver(check).observe(c,{attributes:true,attributeFilter:['class']});}}})();"
].join('\n');
const pin='f5b7a56cf46a17b350a6245684cc222d59ce4b7da62650515d208169f89426a7';
assert.equal(crypto.createHash('sha256').update(live).digest('hex'),pin);
const candidate=fs.readFileSync(process.argv[2],'utf8');
let n=0;
function run(code,query,cls,change) {
 const gift={hidden:true}, container={className:cls};let observer=null;
 class Obs {constructor(callback){observer=callback} observe(){}}
 const document={getElementById:()=>gift,querySelector:()=>container};
 const window={location:{search:query},MutationObserver:Obs};
 vm.runInNewContext(code,{window,document,URLSearchParams,MutationObserver:Obs},{timeout:250});
 if(change!==null){container.className=change;if(observer)observer();}
 return !gift.hidden;
}
for(const q of ['','?subscribe=anything','?subscribe=success','?subscribe=error','?utm_content=approved_asset_001','?subscribe=unexpected&asset_id=001']){
 assert.equal(run(candidate,q,'',null),false,'query-only never triggers gift: '+q);n++;
}
for(const cls of ['is-subscriber','pending is-subscriber','is-subscriber-pending','is-subscriber-extra','prefix-is-subscriber','other','']) {
 assert.equal(run(candidate,'',cls,null),cls.split(/\s+/).includes('is-subscriber'),'exact-class: '+cls);n++;
}
for(const cls of ['is-subscriber','pending is-subscriber','is-subscriber-pending','']) {
 assert.equal(run(candidate,'','pending',cls),cls.split(/\s+/).includes('is-subscriber'),'mutation: '+cls);n++;
}
assert.equal(run(live,'?subscribe=anything','',null),true);n++;
assert.equal(run(live,'','is-subscriber-pending',null),true);n++;
assert.equal(run(candidate,'?subscribe=anything','',null),false);n++;
assert.equal(run(candidate,'','is-subscriber-pending',null),false);n++;
console.log(JSON.stringify({passed:n,failed:0,live_sha256:pin,scope:'OFFLINE VM / NOT JETPACK CONFIRMATION'},null,2));
