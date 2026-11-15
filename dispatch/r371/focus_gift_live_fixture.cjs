// Read-only fixture: WordPress /focus/ page 1579, modified 2026-11-05T17:44:02.
// Extracted from <script id="fvf-gift-v2"> on 2026-11-15 05:39 UTC.
// This file is for an offline VM reproduction, NOT for deployment to the website.
"use strict";
module.exports = String.raw`(function(){var g=document.getElementById('fvf-gift');if(!g){return;}
var bad=['invalid_email','error','blocked_email','opted_out','blocked'];
function show(){g.hidden=false;}
var q=null;try{q=new URLSearchParams(window.location.search).get('subscribe');}catch(e){}
if(q){if(bad.indexOf(q)<0){show();}}
var c=document.querySelector('.wp-block-jetpack-subscriptions__container');
function check(){if(c){if(/\bis-subscriber\b/.test(c.className)){show();}}}
check();if(c){if(window.MutationObserver){new MutationObserver(check).observe(c,{attributes:true,attributeFilter:['class']});}}})();`;
