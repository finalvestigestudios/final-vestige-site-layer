"use strict";
/**
 * PROPOSAL ONLY — deterministic, fail-closed WordPress /focus/ body patch.
 * Does not access WordPress, email, a subscriber, analytics or the network.
 * Feed current authenticated page content to this pure function AFTER
 * separate founder/Claude approval and a fresh source signature review.
 *
 * Public PDF remains public. Joining The Dispatch is a separate opt-in
 * controlled by WordPress, NOT by URL query parameters or CSS classes.
 */
const PDF = "https://finalvestige.com/wp-content/uploads/2026/10/Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf";
const GIFT_OPEN = '<div id="fvf-gift" class="fvf-gift" hidden role="status">';
const GIFT_REPLACE = '<div id="fvf-gift" class="fvf-gift" role="region" aria-label="Free Seven Day Focus Fieldbook download">';
const GIFT_INFO = 'Please confirm your email to join The Dispatch. The welcome email will include this same download link. Check Spam or Promotions if needed.';
const GIFT_INFO_NEW = 'The Fieldbook is a free public download. Downloading it does not subscribe you to The Dispatch. To join the newsletter, use the separate signup form and confirm your address if WordPress asks. The welcome message is configured to include this same PDF link.';
const FAQ_OPEN = 'Tap the download button after you confirm your email. Depending on your browser, the PDF will either open on screen or download. On an iPhone, the Share button in Safari offers Save to Files. Chrome on Android usually saves it to Downloads.';
const FAQ_NEW = 'The free PDF download button is available on this page without signing up. On an iPhone, Safari may show a Share button to save the PDF to Files; on Android, your browser may save it to Downloads. Downloading does not confirm a newsletter subscription.';
const FAQ_MOBILE = 'Some social apps use their own built-in browser, and it may not open PDFs. If that happens, use the menu to open this page in Safari or Chrome and sign up again. The welcome email also carries the link.';
const FAQ_MOBILE_NEW = 'Some social apps use an in-app browser that cannot open PDFs. Open the same PDF link in Safari or Chrome instead. You do not need to enter your email address again. If you separately joined The Dispatch, its configured welcome message also includes the PDF.';
const SCRIPT = /<script id="fvf-gift-v2">[\s\S]*?<\/script>/g;
const SIGNUP = /(<a class="fvf-btn" href="#subscribe-blog" data-fv-event="focus_signup_click" data-fv-location="(?:after_why|after_routine|after_inside|after_limits|close)">)(?:Get the free fieldbook|Send me the fieldbook)(<\/a>)/g;
const count = (html,fragment) => html.split(fragment).length - 1;
function inspect(html) {
  if(typeof html !== "string" || html.length < 16000) throw new TypeError("Need full authenticated Focus page body; no fragments");
  const matches = [...html.matchAll(SCRIPT)];
  const signup = [...html.matchAll(SIGNUP)];
  return {
    script_count: matches.length, gift_count: count(html,GIFT_OPEN),
    gift_copy_count: count(html,GIFT_INFO), faq_count: count(html,FAQ_OPEN),
    mobile_count: count(html,FAQ_MOBILE), signup_ctas:signup.length,
    pdf_link_count:count(html,PDF), pdf_click_count:count(html,'data-fv-event="focus_pdf_click"'),
    old_location_count:count(html,'data-fv-location="after_signup"'),
    subscription_blocks:count(html,'class="wp-block-jetpack-subscriptions'),
    script_matches_expected: matches.length===1 && 
      matches[0][0].includes("new URLSearchParams(window.location.search).get('subscribe')") &&
      matches[0][0].includes('if(q){if(bad.indexOf(q)<0){show();}}') &&
      matches[0][0].includes('is-subscriber')
  };
}
function proposePatch(html) {
  const before=inspect(html);
  if(before.script_count!==1 || !before.script_matches_expected ||
     before.gift_count!==1 || before.gift_copy_count!==1 ||
     before.faq_count!==1 || before.mobile_count!==1 ||
     before.signup_ctas!==5 || before.pdf_link_count!==1 ||
     before.pdf_click_count!==1 || before.old_location_count!==1 ||
     before.subscription_blocks<1) {
     throw new Error("HOLD_SOURCE_DRIFT: actual WordPress source differs; do not produce patch");
  }
  // The PDF is already in public markup. Make it accessible without false
  // consent inference; remove all read-from-query/class gift reveal logic.
  let out=html.replace(GIFT_OPEN,GIFT_REPLACE)
    .replace(GIFT_INFO,GIFT_INFO_NEW)
    .replace(FAQ_OPEN,FAQ_NEW)
    .replace(FAQ_MOBILE,FAQ_MOBILE_NEW)
    .replace('data-fv-location="after_signup"','data-fv-location="public_pdf"')
    .replace(SCRIPT,'<!-- Gift is publicly downloadable. WordPress newsletter confirmation is independent. -->')
    .replace(SIGNUP,'$1Join The Dispatch (free)$2');
  if(out===html)throw new Error("HOLD_NO_CHANGE");
  // Fail closed on partial modifications, compromised embedded signup, tracking or links.
  if(count(out,PDF)!==1 || count(out,'data-fv-event="focus_pdf_click"')!==1 ||
      count(out,'data-fv-location="public_pdf"')!==1 ||
      count(out,'Join The Dispatch (free)')!==5 ||
      count(out,'class="wp-block-jetpack-subscriptions')!==before.subscription_blocks ||
      count(out,'fvf-gift-v2')!==0 || count(out,'focus_signup_click')!==5 ||
      count(out,GIFT_REPLACE)!==1 ||
      out.includes('sign up again.') || out.includes('after you confirm your email.') ||
      /<script[^>]*id="fvf-gift-v3"/.test(out)) {
     throw new Error("HOLD_PATCH_VERIFICATION_FAILURE");
  }
  return {status:"DRAFT_ONLY_NOT_PUBLISHED",html:out,proof:{
    source_page:"https://finalvestige.com/focus/",
    original_script_removed:true,public_pdf_unchanged:true,
    wordpress_subscribe_block_preserved:true,
    signup_clicks_not_confirmed_signups:true,
    no_live_changes:true,
    requires_fresh_authoritative_consent:true,
    separate_final_founder_approval_required:true
  },before};
}
module.exports={PDF,GIFT_OPEN,GIFT_REPLACE,GIFT_INFO,GIFT_INFO_NEW,FAQ_OPEN,FAQ_NEW,FAQ_MOBILE,FAQ_MOBILE_NEW,inspect,proposePatch};
