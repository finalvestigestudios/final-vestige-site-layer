"use strict";
const vm = require("node:vm");
// Source excerpt from live WordPress Focus page ID1579 on 2026-11-07; READ ONLY.
// Visible gift is never a provider-confirmed subscription.
const LIVE_SCRIPT = "(function(){var g=document.getElementById('fvf-gift');if(!g){return;} var bad=['invalid_email','error','blocked_email','opted_out','blocked']; function show(){g.hidden=false;} var q=null;try{q=new URLSearchParams(window.location.search).get('subscribe');}catch(e){} if(q){if(bad.indexOf(q)<0){show();}} var c=document.querySelector('.wp-block-jetpack-subscriptions__container'); function check(){if(c){if(/\\bis-subscriber\\b/.test(c.className)){show();}}} check();if(c){if(window.MutationObserver){new MutationObserver(check).observe(c,{attributes:true,attributeFilter:['class']});}}})();";
function probe(search, className="") {
  const gift = {hidden:true};
  const document={
    getElementById(id){return id==="fvf-gift"?gift:null;},
    querySelector(sel){return sel===".wp-block-jetpack-subscriptions__container"?{className}:null;}
  };
  vm.runInNewContext(LIVE_SCRIPT,{document,window:{location:{search},MutationObserver:null},URLSearchParams},{timeout:1000});
  return Object.freeze({gift_visible:!gift.hidden,confirmed_signup:null,consent_verified:false,welcome_received:false});
}
module.exports={probe,LIVE_SCRIPT};
