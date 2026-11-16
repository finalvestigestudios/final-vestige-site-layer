// R391: read-only editorial truth firewall. It NEVER authorizes a send.
export function inspectIssue05({manifest, evidence, html, plaintext}) {
  const issues = manifest?.issues ?? [];
  const permits = evidence?.permissions ?? {};
  const findings = evidence?.findings ?? [];
  const checks = {};
  checks.masterSixDrafts = manifest?.status === 'DRAFT_UNSENT_NO_SCHEDULING'
    && issues.length === 6 && issues.filter(x => x.kind === 'editorial').length === 4
    && issues.filter(x => x.kind === 'commercial-review-pending').length === 2;
  checks.originalUnmodified = issues.every(x => x.publish_state === 'hold' && x.merchant_affiliate_url === null);
  checks.issuerIs05 = issues.find(x => x.number === 5)?.kind === 'commercial-review-pending';
  checks.permissionsAllUnverified = Object.keys(permits).length >= 10
    && Object.values(permits).every(v => v === false)
    && Array.isArray(evidence?.allowed_merchant_links) && evidence.allowed_merchant_links.length === 0;
  checks.actualSubscriberEligibilityNotAssumed = evidence?.last_authenticated_jetpack_snapshot?.eligible_receiving_inboxes === null
    && evidence?.last_authenticated_jetpack_snapshot?.actual_welcome_receipt_verified === false;
  checks.oneDisabledPrimaryCta = (html.match(/data-primary-cta=/g) || []).length === 1
    && /data-primary-cta="disabled"[^>]*aria-disabled="true"/.test(html)
    && !/<a[^>]*data-primary-cta/i.test(html)
    && html.includes('[[APPROVED_MIND_TOTAL_FOCUS_GUIDE_URL_REQUIRED');
  checks.noExposedAffiliateUrl = !/href="[^"]*(?:clickbank|hoplink|affiliate_id|aff_id|ref=|utm_|zen12\.com\/secret)/i.test(html)
    && !/https?:\/\/[^\s]*\?(?:aff|affiliate|ref|utm_)/i.test(plaintext);
  const ctaAt = html.indexOf('data-primary-cta="disabled"');
  const disclosureAt = html.indexOf('Commercial disclosure', ctaAt);
  checks.proximateDisclosure = ctaAt >= 0 && disclosureAt > ctaAt
    && disclosureAt - ctaAt < 750 && /commission/i.test(html.slice(disclosureAt, disclosureAt + 250));
  checks.claimBoundaries = /seller claims/i.test(html) && /not independently demonstrated outcomes/i.test(html)
    && /product-specific/i.test(evidence.findings.map(f => f.editorial_policy).join(' '));
  checks.directSources = [
    'https://www.gutenberg.org/files/78413/78413-h/78413-h.htm',
    'https://hypnosislive.com/mental-skills/total-focus',
    'https://hypnosislive.com/faq',
    'https://www.nccih.nih.gov/health/hypnosis'
  ].every(u => html.includes(u) && plaintext.includes(u));
  checks.deliveryUnverifiedVisible = html.includes('NOT JETPACK RENDERED') && plaintext.includes('NOT VERIFIED IN JETPACK');
  checks.postalStillBlocked = html.includes('[[VALID_POSTAL_ADDRESS_REQUIRED]]')
    && plaintext.includes('[[VALID_POSTAL_ADDRESS_REQUIRED]]');
  checks.unsubscribeStillBlocked = html.includes('[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]')
    && plaintext.includes('[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]');
  checks.noActiveTrackingOrForm = !/<(?:script|form|input|iframe|img)\b/i.test(html)
    && !/\bon(?:click|load|error)\s*=/i.test(html);
  checks.sellerVsGeneralStudy = findings.some(f => f.id === 'F02' && f.category === 'seller-claim-not-validated')
    && findings.some(f => f.id === 'F08' && f.category === 'independent-general-evidence');
  checks.noOfferPriceInEmail = !/\$\d+/.test(html) && !/\$\d+/.test(plaintext);
  return {release:'HOLD_UNSENT_NO_AUTOMATIC_OVERRIDE',checks,
    passed:Object.values(checks).filter(Boolean).length,
    total:Object.keys(checks).length,
    failures:Object.entries(checks).filter(([,ok])=>!ok).map(([k])=>k)};
}
