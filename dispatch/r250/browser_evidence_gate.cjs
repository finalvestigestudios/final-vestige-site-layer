"use strict";
// R250 evidence *adjudication*, not a signup checker or mailer. No network/PII operations.
// The only affirmative claim allowed is that a form was OBSERVED in a visitor rendering.
const EXPECTED=new Set(["https://finalvestige.com/focus/","https://finalvestige.com/dispatch/"]);
const WIDTHS=[390,1440];
function canonicalUrl(raw) {
  try { const u=new URL(String(raw));if(u.protocol!=="https:"||u.hostname!=="finalvestige.com"||u.search||u.hash)return null;
    return "https://finalvestige.com"+(u.pathname.endsWith("/")?u.pathname:u.pathname+"/");}catch{return null;}
}
function isNonnegativeInteger(n){return Number.isInteger(n)&&n>=0;}
function evaluateProbe(o) {
 const failures=[];
 if(!o||typeof o!=="object")return {classification:"INVALID_PROOF",failures:["missing observation"],subscription_verified:false,release_authorized:false};
 const url=canonicalUrl(o.url);
 if(!EXPECTED.has(url))failures.push("unexpected destination");
 if(!WIDTHS.includes(o.viewport_width))failures.push("unexpected viewport");
 if(o.unauthenticated_context!==true)failures.push("anonymous browser context not attested");
 if(o.blocked_non_get_requests!==true)failures.push("non-GET guard not attested");
 if(o.user_data_typed!==false||o.form_submitted!==false)failures.push("no-input/no-submit boundary not attested");
 if(o.received_email_sent!==false)failures.push("received-email boundary not attested");
 if(!/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d/.test(o.observed_at_utc||"")||!Number.isFinite(Date.parse(o.observed_at_utc)))failures.push("missing UTC observation");
 for(const f of ["visible_email_inputs","accessible_visible_email_inputs","visible_submit_controls","safe_openers_clicked","self_navigation_count","browser_errors"])if(!isNonnegativeInteger(o[f]))failures.push("invalid counter "+f);
 if(o.record_source!=="UNAUTHENTICATED_PLAYWRIGHT_BROWSER")failures.push("not genuine browser observation");
 if(failures.length)return {classification:"INVALID_PROOF",failures,subscription_verified:false,release_authorized:false};
 const visuallyReady=o.visible_email_inputs>0&&o.accessible_visible_email_inputs>0&&o.visible_submit_controls>0;
 const classification=visuallyReady?"VISUAL_ENTRY_PRESENT_UNSUBMITTED":
   o.visible_email_inputs>0?"VISIBLE_FIELD_INCOMPLETE_ACCESSIBILITY":
   o.safe_openers_clicked>0&&o.self_navigation_count>0?"SELF_NAVIGATION_WITHOUT_VISIBLE_FIELD":
   o.safe_openers_clicked>0?"POPUP_OR_HYDRATION_NOT_VERIFIED":
   "NO_VISIBLE_INPUT_FOUND";
 return {classification,failures:[],
   url,viewport_width:o.viewport_width,keyboard_reached_subscribe:o.keyboard_reached_subscribe===true,
   visual_entry_pass:visuallyReady&&o.keyboard_reached_subscribe===true,
   js_errors_reported:o.browser_errors>0,subscription_verified:false,confirmation_verified:false,
   welcome_delivered_verified:false,release_authorized:false};
}
function evaluateMatrix(observations) {
 if(!Array.isArray(observations))return {status:"INVALID",missing:["records"],release_authorized:false};
 const slots=new Set(),items=[],duplicates=[];
 for(const o of observations){const grade=evaluateProbe(o);items.push(grade);
   if(grade.url){let k=grade.url+"|"+grade.viewport_width;if(slots.has(k))duplicates.push(k);slots.add(k);}
 }
 const missing=[];
 for(const u of EXPECTED)for(const w of WIDTHS)if(!slots.has(u+"|"+w))missing.push(u+"@"+w);
 const status=!missing.length&&!duplicates.length&&items.length===4&&items.every(i=>i.visual_entry_pass&&!i.js_errors_reported)?"VISUAL_ONLY_COMPLETE":"NEEDS_REVIEW";
 return {status,missing,duplicates,items,release_authorized:false,confirmed_signup:null,confirmed_receivers:null,actual_paid_orders:null,net_revenue_per_1000:null};
}
module.exports={canonicalUrl,evaluateProbe,evaluateMatrix};
