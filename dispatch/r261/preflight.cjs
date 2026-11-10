"use strict";
/** R261 draft-only QA. Pure, offline: no network, no sending authority. */
function inspect(manuscript, preview, manifest, issueNumber) {
  const faults = [];
  const requireThat = (ok, code) => { if (!ok) faults.push(code); };
  const has = (x) => manuscript.includes(x);
  const id = String(issueNumber).padStart(2, "0");
  const suffix = issueNumber === 3 ? "ZEN12" : "HYPNOSIS";
  const subject = manuscript.match(/^Subject: (.+)$/m)?.[1] || "";
  const preheader = manuscript.match(/^Preheader: (.+)$/m)?.[1] || "";
  const ctaLines = manuscript.split(/\r?\n/).filter(l => l.startsWith("**PRIMARY CTA (disabled pending approval):**"));
  const disclosureLines = manuscript.split(/\r?\n/).filter(l => l.startsWith("**Commercial disclosure (beside the proposed CTA):**"));
  const requiredCTA = "[[APPROVED_LIVE_" + suffix + "_GUIDE_URL_REQUIRED]]";
  requireThat(manifest.status === "DRAFT_UNSENT_NO_SCHEDULING", "CAMPAIGN_STATUS");
  requireThat(manifest.issues.length === 6, "SIX_ISSUES");
  requireThat(manifest.issues.filter(x => x.kind === "editorial").length === 4, "FOUR_EDITORIAL");
  requireThat(manifest.issues.filter(x => x.kind === "commercial-review-pending").length === 2, "TWO_COMMERCIAL");
  requireThat(manifest.issues.every(x => x.merchant_affiliate_url === null && x.publish_state === "hold"), "MERCHANT_ACTIVATION");
  requireThat(manifest.issues[issueNumber - 1].kind === "commercial-review-pending", "CORRECT_ISSUE_KIND");
  requireThat(manuscript.includes("UNSENT DRAFT") && has("HOLD_MERCHANT") && has("NOT ADOPTED"), "COPY_RELEASE_BANNER");
  requireThat(subject.length > 10 && subject.length <= 65 && !/free money|limited time|guaranteed/i.test(subject), "SUBJECT_QUALITY");
  requireThat(preheader.length > 35 && preheader.length <= 140, "PREHEADER_QUALITY");
  requireThat(ctaLines.length === 1 && ctaLines[0]?.includes(requiredCTA), "SINGLE_DISABLED_CTA");
  requireThat(ctaLines.length === 1 && !/https?:\/\//i.test(ctaLines[0] || ""), "CTA_MUST_BE_INACTIVE");
  requireThat(disclosureLines.length === 1, "DISCLOSURE_PRESENT");
  const lines = manuscript.split(/\r?\n/);
  const ci = lines.findIndex(x => x.startsWith("**PRIMARY CTA"));
  const di = lines.findIndex(x => x.startsWith("**Commercial disclosure"));
  requireThat(di === ci + 1, "DISCLOSURE_ADJACENT");
  requireThat(has("[[VALID_FINAL_VESTIGE_POSTAL_ADDRESS_REQUIRED]]") && has("[[JETPACK_REAL_UNSUBSCRIBE_VERIFICATION_REQUIRED]]") && has("[[ACTUAL_INBOX_RENDER_REQUIRED]]"), "COMPLIANCE_GATES");
  requireThat(has("No final founder approval") && has("Do not send, schedule"), "FOUNDER_APPROVAL_GATE");
  requireThat(has("not independently") || has("not independent") || has("NOT an independently") || has("not a product"), "PRODUCT_VS_SCIENCE");
  requireThat(!/clinically proven to reprogram|100% guaranteed to work|buy now before midnight|cures anxiety/i.test(manuscript), "MISLEADING_COPY");
  const urls = manuscript.match(/https:\/\/[^\s\])]+/g) || [];
  const good = ["pubmed.ncbi.nlm.nih.gov", "www.nccih.nih.gov", "zen12.com", "hypnosislive.com", "affiliates.inspire3.com", "finalvestige.com"];
  requireThat(urls.length >= 3 && urls.every(url => {
    try { const u = new URL(url); return good.includes(u.hostname) && !u.search && !u.username && !u.password; }
    catch { return false; }
  }), "SOURCE_URL_ALLOWLIST");
  requireThat(manuscript.includes("Research 1:") && manuscript.includes("Merchant 1:"), "PRIMARY_SOURCES");
  requireThat(preview.startsWith("<!DOCTYPE html>") && /<html lang="en">/.test(preview) && /name="viewport"/.test(preview), "PREVIEW_ACCESSIBILITY");
  requireThat(preview.includes("role=\"presentation\"") && preview.includes("<h1") && preview.includes(subject) && preview.includes(preheader), "PREVIEW_CONTENT");
  requireThat(preview.includes("CTA INACTIVE") && preview.includes("INTERNAL REVIEW ONLY") && !/<script\b/i.test(preview), "PREVIEW_SEND_HOLD");
  requireThat(!/href="\[\[APPROVED_LIVE_/i.test(preview) && !/mailto:/i.test(preview), "PREVIEW_LINK_GUARD");
  requireThat(!/(unsubscribe.*href="https?:\/\/example\.com|postage paid)/i.test(preview), "NO_FAKE_UNSUBSCRIBE");
  requireThat(id === (issueNumber === 3 ? "03" : "05"), "ISSUE_ONLY_03_05");
  return {pass: faults.length === 0, faults, subject, preheader, reference_count: urls.length, cta_count: ctaLines.length};
}
module.exports = {inspect};
