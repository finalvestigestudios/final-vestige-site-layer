'use strict';
/* Offline-only regression for actual Focus Page 1579 fvf-gift-v2.
   Does not contact WordPress, create leads, or assert actual Jetpack acceptance. */
const assert=require('node:assert/strict');
const vm=require('node:vm');
const crypto=require('node:crypto');
const LIVE=[
"(function(){var g=document.getElementById('fvf-gift');if(!g){return;}",
"var bad=['invalid_email','error','blocked_email','opted_out','blocked'];",
"function show(){g.hidden=false;}",
"var q=null;try{q=new URLSearchParams(window.location.search).get('subscribe');}catch(e){}",
"if(q){if(bad.indexOf(q)<0){show();}}",
"var c=document.querySelector('.wp-block-jetpack-subscriptions__container');",
"function check(){if(c){if(/\\bis-subscriber\\b/.test(c.className)){show();}}}",
"check();if(c){if(window.MutationObserver){new MutationObserver(check).observe(c,{attributes:true,attributeFilter:['class']});}}})();"
].join('\n');
const PROPOSED=[
"(function(){var g=document.getElementById('fvf-gift');if(!g){return;}",
"var c=document.querySelector('.wp-block-jetpack-subscriptions__container');",
"function check(){if(c && /(?:^|\\s)is-subscriber(?:\\s|$)/.test(c.className)){g.hidden=false;}}",
"check();if(c && window.MutationObserver){new MutationObserver(check).observe(c,{attributes:true,attributeFilter:['class']});}",
"})();"
].join('\n');
const PIN='f5b7a56cf46a17b350a6245684cc222d59ce4b7da62650515d208169f89426a7';
assert.equal(crypto.createHash('sha256').update(LIVE).digest('hex'),PIN,
 'Source drift: re-fetch authenticated WordPress Page 1579 before testing');
function run(script,query,subscriber,mutate){
 const gift={hidden:true}, container={className:subscriber?'is-subscriber':''};
 let observer=null;
 class Observer {constructor(cb){observer=cb;} observe(){}}
 const window={location:{search:query},MutationObserver:Observer};
 const document={
   getElementById:(id)=>id==='fvf-gift'?gift:null,
   querySelector:(selector)=>selector==='.wp-block-jetpack-subscriptions__container'?container:null
 };
 vm.runInNewContext(script,{window,document,URLSearchParams,MutationObserver:Observer},{timeout:200});
 if(mutate){container.className='is-subscriber';assert.ok(observer);observer();}
 return !gift.hidden;
}
let total=0;
const cases=[
 ['',false,false],['?subscribe=anything',false,false],['?subscribe=success',false,false],
 ['?subscribe=invalid_email',false,false],['?subscribe=error',false,false],
 ['?subscribe=success',true,false],['',true,false],['',false,true],
 ['?subscribe=anything',false,true]
];
for(const [query,subscriber,mutate] of cases){
 const oldExpected=subscriber||mutate||(Boolean(query)&&
    !query.includes('invalid_email')&&!query.includes('error'));
 const newExpected=subscriber||mutate;
 assert.equal(run(LIVE,query,subscriber,mutate),oldExpected,
   'Live script expected behavior: '+query+'/'+subscriber+'/'+mutate);total++;
 assert.equal(run(PROPOSED,query,subscriber,mutate),newExpected,
   'Review candidate expected behavior: '+query+'/'+subscriber+'/'+mutate);total++;
}
for(const bad of ['is-subscriber-pending','pre-is-subscriber','non-subscriber']){
 const gift={hidden:true},container={className:bad};
 const document={getElementById:()=>gift,querySelector:()=>container};
 vm.runInNewContext(PROPOSED,{window:{location:{search:''},MutationObserver:null},document},{timeout:200});
 assert.equal(gift.hidden,true,'Reject substring success marker '+bad);total++;
}
console.log(JSON.stringify({status:'PASS',assertions:total,source_sha256:PIN,
 finding:'Live gift appears on arbitrary subscribe=anything parameter',
 review_candidate:'Only class-token success signal reveals gift; Jetpack server/lead confirmation is still unverified',
 wp_writes:0,subscribers_created:0,orders:0},null,2));
