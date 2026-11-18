"use strict";
// Read-only decision layer; deliberately contains no sending capability.
function assess(x={}){const fields=["founder_copy","founder_audience","founder_schedule","provider_eligible","actual_native_preview","publisher_physical_postal","real_unsubscribe","historical_check"];const missing=fields.filter(k=>x[k]!==true);return {missing,preflight:missing.length===0,send_authorized:false,scheduled:false};}
function confirmedSignup(e){if(!e||e.provider!=="wordpress_jetpack"||e.event!=="subscription_transition"||e.current_status!=="Subscribed"||e.previous_status==="Subscribed"||e.email_subscriber!==true||e.consent_scope!=="dispatch"||typeof e.opaque_id!=="string"||e.opaque_id.length<8)return null;return {event:"confirmed_signup",opaque_id:e.opaque_id};}
function realizedRate(x={}){if(x.matured!==true||!Number.isInteger(x.sessions)||x.sessions<1||![x.settled,x.refunds,x.fees].every(n=>typeof n==="number"&&Number.isFinite(n)&&n>=0))return null;return {net:x.settled-x.refunds-x.fees,per_1000:1000*(x.settled-x.refunds-x.fees)/x.sessions};}
module.exports={assess,confirmedSignup,realizedRate};
