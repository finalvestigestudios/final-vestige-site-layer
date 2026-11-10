"use strict";
// Dispatch R249: WordPress REST-rendered Subscribe blocks are not a live form test.
// No network requests, submissions, subscriber data, or production writes.
function auditSignupSnapshot({blockHtml="", expectedPageId=0}={}) {
  const s=String(blockHtml);
  const hasBlock=/wp-block-jetpack-subscriptions\b/.test(s);
  const hasForm=/<form\b/i.test(s);
  const hasEmailControl=/<input\b[^>]*\btype\s*=\s*["']?email\b/i.test(s);
  const anchors=[...s.matchAll(/<a\b[^>]*\bhref\s*=\s*["']([^"']+)["'][^>]*>([\s\S]*?)<\/a>/gi)];
  const selfLink=anchors.some(a=>{
    const url=a[1].replace(/&(?:amp|#038);/gi,"&");
    return expectedPageId>0 && /[?&]p=/.test(url) && new RegExp("[?&]p="+expectedPageId+"(?:&|$)").test(url)
     ;
  });
  const fallbackShape=hasBlock&&selfLink&&!hasForm&&!hasEmailControl;
  return Object.freeze({
    source:"WORDPRESS_REST_RENDERED_CONTENT_NOT_BROWSER",
    jetpack_block_present:hasBlock,
    form_in_returned_markup:hasForm,
    email_control_in_returned_markup:hasEmailControl,
    self_linking_subscribe_fallback:selfLink,
    requires_real_browser_render_and_keyboard_QA:fallbackShape,
    classification:fallbackShape?"POSSIBLE_RENDERED_FALLBACK__LIVE_FUNCTION_UNVERIFIED":"NO_FALLBACK_SHAPE_PROVEN",
    live_signup_working:null, confirmed_signup:null, subscribers_contacted:false
  });
}
module.exports={auditSignupSnapshot};
