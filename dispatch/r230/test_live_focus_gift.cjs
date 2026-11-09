'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const script = fs.readFileSync(__dirname+'/live_focus_gift_20261109.js','utf8');
function render(url, subscriberClass='',hasGift=true){
 const gift={hidden:true}, container={className:subscriberClass};
 const document={getElementById(id){return hasGift&&id==='fvf-gift'?gift:null;},querySelector(selector){return selector==='.wp-block-jetpack-subscriptions__container'?container:null;}};
 const window={location:{search:(new URL(url)).search}};
 vm.runInNewContext(script,{document,window,URLSearchParams,MutationObserver:undefined},{timeout:1000});
 return gift.hidden===false;
}
const samples=[
 ['ordinary page', 'https://finalvestige.com/focus/', '', false],
 ['arbitrary query', 'https://finalvestige.com/focus/?subscribe=arbitrary', '', true],
 ['unconfirmed query', 'https://finalvestige.com/focus/?subscribe=unconfirmed', '', true],
 ['subscriber-looking query', 'https://finalvestige.com/focus/?subscribe=confirmed', '', true],
 ['blocked query', 'https://finalvestige.com/focus/?subscribe=blocked', '', false],
 ['invalid email query', 'https://finalvestige.com/focus/?subscribe=invalid_email', '', false],
 ['arbitrary percent encoded', 'https://finalvestige.com/focus/?subscribe=%66oo', '', true],
 ['is-subscriber CSS', 'https://finalvestige.com/focus/', 'wp-block is-subscriber', true],
 ['Reader-only unknown CSS', 'https://finalvestige.com/focus/', 'wp-block reader-only', false],
];
let pass=0;for(const [name,url,cls,expected] of samples){assert.equal(render(url,cls),expected,name);pass++;}
assert.equal(render('https://finalvestige.com/focus/?subscribe=anything','',false),false);
pass++;
console.log('LIVE SCRIPT REPRODUCTION: '+pass+'/'+pass+' passed; untrusted subscribe query values reveal the gift UI; NOT proof of subscriber confirmation.');
