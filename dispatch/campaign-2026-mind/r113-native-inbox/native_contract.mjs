/**
 * R113: conservative, read-only native WordPress newsletter transport contract.
 * An editor preview is not an actual received email. Nothing here can send.
 * @see https://wordpress.com/support/newsletter/send-newsletter-emails/
 * @see https://wordpress.com/support/newsletter-settings/
 */
export const ORIGINAL_CAMPAIGN_HEAD = "d57ccdba3aee8f065e143e101c2945f4f3d01647";
export const COMMERCIAL_ISSUES = Object.freeze([3, 5]);
const own = (o, key) => Object.prototype.hasOwnProperty.call(o || {}, key);
const validText = v => typeof v === "string" && v.trim().length > 0;
const nullish = v => v === null || v === undefined;
const integer = v => Number.isInteger(v) && v > 0;
const isFirstParty = v => {
  try { const u = new URL(v); return u.protocol === "https:" && u.hostname === "finalvestige.com" && !u.username && !u.password; }
  catch { return false; }
};
function unique(a) { return [...new Set(a)]; }
export function auditNativeInbox({campaign, wordpress, editions = {}, previewEvidence = {}, mailboxEvidence = {}, attestation = {}} = {}) {
  const global = [];
  if (!campaign || campaign.source_head !== ORIGINAL_CAMPAIGN_HEAD) global.push("CAMPAIGN_SHA_NOT_LOCKED");
  const issues = campaign?.issues;
  if (!Array.isArray(issues) || issues.length !== 6 || !issues.every(i => integer(i.number)) ||
      new Set(issues.map(i => i.number)).size !== 6) global.push("SIX_ISSUE_MANIFEST_NOT_VERIFIED");
  else {
    const editorial = issues.filter(i => i.kind === "editorial");
    const commercial = issues.filter(i => i.kind === "commercial-review-pending");
    if (editorial.length !== 4 || commercial.length !== 2 ||
        commercial.map(i => i.number).sort().join(",") !== "3,5") global.push("FOUR_TWO_MIX_NOT_VERIFIED");
  }
  if (wordpress?.subscriptions !== true) global.push("NATIVE_LIST_NOT_CONFIRMED");
  if (wordpress?.email_new_posts_by_default !== false) global.push("AUTO_SEND_NOT_CONFIRMED_OFF");
  if (wordpress?.email_content_format !== "excerpt") global.push("OBSERVED_EXCERPT_MODE_DRIFT");
  if (!wordpress || !integer(wordpress.confirmed) || !integer(wordpress.total)) global.push("SUBSCRIBER_COUNTS_NOT_RECONCILED");
  // Even a confirmed count does not establish a currently reachable recipient.
  const deliverableRecipients = null;
  const results = (Array.isArray(issues) ? issues : []).map(i => {
    const holds = [];
    const creative = editions[i.number] || {};
    const preview = previewEvidence[i.number] || {};
    const receipt = mailboxEvidence[i.number] || {};
    const commercial = COMMERCIAL_ISSUES.includes(i.number);
    if (!validText(i.subject) || creative.post_title !== i.subject) holds.push("WP_POST_TITLE_MUST_MATCH_SUBJECT");
    if (!validText(i.preheader)) holds.push("PREFLIGHT_PREHEADER_MISSING");
    // WP docs confirm post title/subject and excerpt; not a separate preheader field.
    holds.push("NATIVE_PREHEADER_HEADER_NOT_VERIFIED");
    if (!validText(creative.custom_excerpt) || creative.custom_excerpt.trim().length > 420) holds.push("CUSTOM_EXCERPT_NOT_REVIEWED");
    // Candidate excerpt must link to a real first-party destination, not a placeholder or a merchant.
    if (!isFirstParty(creative.cta_url)) holds.push("FIRST_PARTY_CTA_NOT_VALIDATED");
    if (!validText(preview.desktop_capture_id) || !validText(preview.mobile_capture_id) ||
        !validText(preview.tablet_capture_id)) holds.push("ACTUAL_WP_EDITOR_PREVIEW_NOT_OBSERVED");
    if (!validText(receipt.source_message_proof_id) || receipt.plaintext_ok !== true ||
        receipt.html_ok !== true) holds.push("ACTUAL_RECEIVED_MIME_NOT_OBSERVED");
    if (receipt.publisher_postal_verified !== true) holds.push("PUBLISHER_POSTAL_NOT_VERIFIED_IN_RECEIVED_EMAIL");
    if (receipt.unsubscribe_function_test_verified !== true) holds.push("FUNCTIONAL_UNSUBSCRIBE_NOT_VERIFIED");
    if (commercial) {
      if (!validText(creative.custom_excerpt) || !/commission|affiliate/i.test(creative.custom_excerpt))
        holds.push("COMMERCIAL_DISCLOSURE_MISSING_FROM_INBOX_EXCERPT");
      if (attestation["merchant_email_rights_" + i.number] !== true) holds.push("MERCHANT_EMAIL_RIGHTS_NOT_VERIFIED");
      if (attestation["approved_guide_live_" + i.number] !== true) holds.push("WARMUP_GUIDE_NOT_APPROVED_LIVE");
      if (attestation["earning_link_format_" + i.number] !== true) holds.push("EARNING_LINK_FORMAT_NOT_VERIFIED");
      if (attestation["merchant_claims_fresh_" + i.number] !== true) holds.push("MERCHANT_PRICE_REFUND_CLAIMS_NOT_FRESH");
    }
    if (campaign?.source_head !== ORIGINAL_CAMPAIGN_HEAD) holds.push("ISSUE_VERSION_LOCK_FAILED");
    // This module is intentionally NEVER a sender or founder-approval substitute.
    return { number: i.number, kind: i.kind, subject: i.subject,
      email_transport: "WP_POST_TITLE_AND_EXCERPT", estimated_preheader: "NOT_VERIFIED",
      holds: unique(holds), release: "HOLD_UNSENT", verified_paid_orders: null };
  });
  return { source_head: campaign?.source_head || null,
    global_holds: unique(global),
    wordpress_mode: wordpress?.email_content_format || "UNKNOWN",
    newsletter_auto_send: wordpress?.email_new_posts_by_default ?? null,
    deliverable_recipients: deliverableRecipients,
    issues: results, campaign_release: "HOLD_UNSENT", sender_capability: false,
    metric_net_revenue_per_1000_qualified_sessions: null };
}
