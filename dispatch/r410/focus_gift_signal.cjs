'use strict';
// Read-only reproduction of the published /focus/ inline fvf-gift-v2 script.
// This script never contacts WordPress, collects personal data or counts subscribers.
const vm = require('node:vm');

const PUBLISHED_SCRIPT = String.raw`(function(){var g=document.getElementById('fvf-gift');if(!g){return;}
var bad=['invalid_email','error','blocked_email','opted_out','blocked'];
function show(){g.hidden=false;}
var q=null;try{q=new URLSearchParams(window.location.search).get('subscribe');}catch(e){}
if(q){if(bad.indexOf(q)<0){show();}}
var c=document.querySelector('.wp-block-jetpack-subscriptions__container');
function check(){if(c){if(/\bis-subscriber\b/.test(c.className)){show();}}}
check();if(c){if(window.MutationObserver){new MutationObserver(check).observe(c,{attributes:true,attributeFilter:['class']});}}})();`;

function reproduce({ search = '', subscriberClass = '', giftExists = true, hasContainer = true } = {}) {
  const gift = {hidden: true};
  const container = hasContainer ? {className: subscriberClass} : null;
  let mutationCallback = null;
  class FakeMutationObserver {
    constructor(callback) { mutationCallback = callback; }
    observe() {}
  }
  const context = {
    URLSearchParams,
    MutationObserver: FakeMutationObserver,
    document: {
      getElementById: () => giftExists ? gift : null,
      querySelector: () => container
    },
    window: {location: {search}, MutationObserver: FakeMutationObserver}
  };
  vm.runInNewContext(PUBLISHED_SCRIPT, context, {timeout: 500});
  return {
    giftVisible: !gift.hidden,
    mutationCallbackInstalled: Boolean(mutationCallback),
    changeContainerClass(value) {
      if (!container) return !gift.hidden;
      container.className = value;
      mutationCallback?.();
      return !gift.hidden;
    }
  };
}

// This is intentionally a classification of evidence, not an analytics event emitter.
function evidenceClass({urlFlag = false, giftVisible = false, pdfClick = false, providerRecord = false} = {}) {
  if (providerRecord) return 'PROVIDER_RECORD_REQUIRES_PRIVATE_AUTHENTICATION';
  if (urlFlag || giftVisible || pdfClick) return 'CLIENT_ONLY_NOT_CONFIRMED_SIGNUP';
  return 'NO_SUBSCRIPTION_EVIDENCE';
}

module.exports = {PUBLISHED_SCRIPT, reproduce, evidenceClass};
