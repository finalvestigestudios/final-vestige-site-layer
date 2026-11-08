// R12 read-only source-of-truth guard. Offline. No WordPress/Gmail/network API.
// This tool cannot verify merchant approval, postal address, unsubscribe or actual email.
// It NEVER returns SEND_READY; a PASS means only that the hold ledger is internally consistent.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export function auditEvidence(e) {
  const violations = [];
  const fail = (code, condition) => { if (condition) violations.push(code); };
  const issueNumbers = Array.isArray(e?.issues) ? e.issues.map(x => x.number) : [];
  const claims = Array.isArray(e?.offer_claims) ? e.offer_claims : [];
  const site = e?.site || {};
  const partner = e?.account_partner || {};
  const pages = e?.pages || {};
  const legal = e?.legal_posture || {};
  const a = site.subscriber_aggregates || {};
  fail("CAMPAIGN_RELEASE_DRIFT", e?.release !== "HOLD_UNSENT");
  fail("MANIFEST_NOT_SIX_UNIQUE", issueNumbers.length !== 6 ||
       new Set(issueNumbers).size !== 6 ||
       [...issueNumbers].sort((x, y) => x - y).join(",") !== "1,2,3,4,5,6");
  fail("MIX_DRIFT", !Array.isArray(e?.issues) ||
       e.issues.filter(x => x.kind === "editorial").length !== 4 ||
       e.issues.filter(x => x.kind === "commercial-review-pending").length !== 2 ||
       e.issues.filter(x => x.affiliate_placement).map(x => x.number).sort().join(",") !== "3,5");
  fail("ISSUE_NOT_HELD", !Array.isArray(e?.issues) || e.issues.some(x => x.release !== "HOLD_UNSENT"));
  fail("PROMO_DESTINATION_ACTIVATED", !Array.isArray(e?.issues) ||
       e.issues.filter(x => x.affiliate_placement).some(x => x.planned_destination !== null));
  fail("AFFILIATE_APPROVAL_ASSUMED",
       partner.approval_for_final_vestige !== "UNVERIFIED" ||
       partner.written_email_channel_permission !== "UNVERIFIED" ||
       partner.tracking_format !== "UNVERIFIED" ||
       partner.approved_creatives !== "UNVERIFIED" ||
       partner.commission_terms !== "UNVERIFIED" ||
       partner.approved_zen12_product_link !== null ||
       partner.approved_total_focus_product_link !== null);
  fail("WARMUP_PRETENDED_LIVE", !pages.zen12_guide || !pages.total_focus_guide ||
       [pages.zen12_guide, pages.total_focus_guide].some(x => x.published !== false || x.url !== null));
  fail("JETPACK_DELIVERY_DRIFT", site.email_new_posts_by_default !== false ||
       site.email_content_format !== "excerpt" || site.recent_sends !== 0 ||
       site.native_editor_preview_observed !== false ||
       site.received_native_campaign_mime !== false);
  fail("WELCOME_DELIVERY_INFERRED", site.welcome_delivery_proven !== false);
  fail("RECIPIENTS_INFERRED", site.unique_permissioned_deliverable !== null ||
       site.subscriber_count_conflict !== "UNRESOLVED" ||
       site.subscriber_pii_in_ledger !== false);
  fail("AGGREGATES_CHANGED", a.total !== 2 || a.confirmed !== 2 ||
       a.unconfirmed !== 2 || a.suppressed !== 0);
  fail("LEGAL_EVIDENCE_INFERRED", site.address_of_FV_verified !== false ||
       site.actual_commercial_unsubscribe_verified !== false ||
       legal.physical_address_required_for_commercial !== true ||
       legal.unsubscribe_verification_required !== true);
  fail("OFFERS_INSUFFICIENTLY_DISTINGUISHED", claims.length < 12 ||
       new Set(claims.map(x => x.id)).size !== claims.length ||
       !claims.some(x => x.sku === "Zen12" && x.evidence_tier === "UNSUBSTANTIATED_SELLER_EFFECTIVENESS") ||
       !claims.some(x => x.sku.includes("Total Focus") && x.evidence_tier === "NO_SKU_SPECIFIC_INDEPENDENT_EVIDENCE"));
  fail("UNSUPPORTED_OUTCOME_APPROVED", claims.some(x =>
       (x.evidence_tier.startsWith("UNSUBSTANTIATED_") ||
        x.evidence_tier === "NO_SKU_SPECIFIC_INDEPENDENT_EVIDENCE" ||
        x.evidence_tier === "NO_FIRST_HAND_EVIDENCE" ||
        x.evidence_tier === "DYNAMIC_SELLER_PRICE") &&
       (x.public_email_safe !== null || x.approved_as_fv_result !== false)));
  fail("UNTRUSTED_PUBLIC_LINK", claims.some(x => x.source != null &&
       !/^https:\/\/(?:zen12\.com|hypnosislive\.com|www\.nccih\.nih\.gov)\//.test(x.source)));
  fail("SENSITIVE_LEDGER_FIELDS", /(?:subscriber_email|unsubscribe_token|api_key|affiliate_tracking_token)\s*":/i.test(JSON.stringify(e)));
  const blockers = ["actual sender postal-address verification","native WordPress rendered preview",
    "real received opt-out and MIME proof","private subscriber consent/count reconciliation",
    "account-specific Inspire3 rights and email promotion permission",
    "two published first-party guides","founder final copy/audience/date/send approval"];
  return {source_only:violations.length ? "INVALID" : "SOURCE_ONLY_PASS",
    release:"HOLD_UNSENT", can_send:false, known_editorial:4,
    optional_merchant_editions:[3,5], blocker_count:blockers.length,
    blockers, violations, no_actual_email_verified:true, no_partner_approval_verified:true};
}

const isCli = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isCli) {
  const file = path.join(path.dirname(fileURLToPath(import.meta.url)), "R12_EVIDENCE_LEDGER.json");
  const report = auditEvidence(JSON.parse(fs.readFileSync(file,"utf8")));
  console.log(JSON.stringify(report,null,2));
  if (report.violations.length) process.exitCode = 1;
}
