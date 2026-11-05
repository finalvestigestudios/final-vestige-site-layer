/**
 * EX2 homepage: combine independent exact-HEAD isolated WordPress and
 * current anonymous guest evidence. Evaluation is ALWAYS release HOLD:
 * WP.com hosted parity, archival image rights, independent QD, manual WCAG
 * and founder approval cannot be conferred by local test results.
 *
 * Pure data contract: no network requests, cookies, tokens, PII or side effects.
 * Runner and tests are separate. Do not deploy or call this a WCAG certificate.
 */
export const STAGE_WIDTHS = Object.freeze([360, 390, 768, 1440, 1920]);
export const GUEST_WIDTHS = Object.freeze([320, 390, 768, 1440]);
const isSha = x => typeof x === 'string' && /^[0-9a-f]{40}$/.test(x);
const allTrue = obj => obj && typeof obj === 'object' && !Array.isArray(obj)
  && Object.keys(obj).length > 0 && Object.values(obj).every(v => v === true);
// Use the *actual keys* emitted by verify_exact_staging.py and focus_guest_gate.py.
// Arbitrary {checks:{ok:true}} is not evidence that required tests executed.
const mustHaveChecks = (checks, required) => allTrue(checks)
  && required.every(name => Object.hasOwn(checks,name) && checks[name] === true);
export const REQUIRED_STAGE_CHECKS = Object.freeze([
  'server_exposes_exact_index_hash','header_no_cache','header_no_index',
  'response_csp_nonces','exactly_one_heading','all_seven_chapters',
  'no_horizontal_root_overflow','source_galleries_survive',
  'focus_link_present','two_cleared_archival_images',
  'real_images_loaded','actual_image_http_payloads',
  'locked_visual_identity','nypl_capture_not_embedded',
  'franklin_folio_editorial_disclosure','axe_no_aa_violations'
]);
export const REQUIRED_NOJS_CHECKS = Object.freeze([
  'private_shortcode_renders','all_chapters','three_cases',
  'no_root_overflow','true_390px_viewport','no_js_case_panels_visible',
  'nojs_archival_photographs_fetched','nojs_only_approved_photo_sources',
  'nojs_malbone_map_not_reproduced'
]);
export const REQUIRED_GUEST_CHECKS = Object.freeze([
  'focus_root','jetpack_block','guest_email_form','labelled_email',
  'email_touch_height_44px','submit_touch_height_44px',
  'no_self_link_only_fallback','no_horizontal_overflow','no_existing_email_data'
]);
const isHash = x => typeof x === 'string' && /^[0-9a-f]{64}$/.test(x);
// media_transfer_admission.py measures *decoded response-body bytes*, not
// Content-Length or actual on-wire bytes. A status flag alone is insufficient.
const validDeliveredImages = item => {
  if (item?.status !== 'PASS' || !Array.isArray(item.images)
      || item.images.length !== 2 || !hasNoFailures(item.failure_codes)) return false;
  const ids=item.images.map(x=>x?.archive).sort();
  if (ids[0] !== 'apollo' || ids[1] !== 'franklin') return false;
  const bytes=item.images.map(x=>x?.decoded_payload_bytes);
  if (bytes.some(x=>!Number.isSafeInteger(x)||x<32||x>8*1024*1024)) return false;
  const hashes=item.images.map(x=>x?.payload_sha256);
  if (hashes.some(x=>!isHash(x)) || hashes[0]===hashes[1]) return false;
  if (item.images.some(x=>x.http_status!==200||!x.response_seen
    || !['jpeg','png','webp','avif'].includes(x.detected_raster_format)
    || !['image/jpeg','image/png','image/webp','image/avif'].includes(x.content_type))) return false;
  return Number.isSafeInteger(item.decoded_payload_total_bytes)
    && item.decoded_payload_total_bytes===bytes.reduce((a,b)=>a+b,0);
};
const widthsAre = (items, expected) => Array.isArray(items)
  && items.length === expected.length
  && expected.every((w,i) => items[i]?.width === w);
const hasNoFailures = x => Array.isArray(x) && x.length === 0;
const metric = x => typeof x === 'number' && Number.isFinite(x) && x >= 0;
export function classifyReleaseEvidence({sha, stage, local, lighthouse, usability, guest, guestAgeHours} = {}) {
  const codes = [];
  const must = (condition,code) => {if (!condition) codes.push(code);};
  must(isSha(sha), 'EXPECTED_SHA_INVALID');
  must(stage?.source_git_head === sha, 'STAGE_EXACT_SHA_MISMATCH');
  must(stage?.status === 'HOLD_INDEPENDENT_RELEASE_APPROVAL_REQUIRED'
    && stage?.pass_for_measured_browser_gates === true
    && hasNoFailures(stage?.failure_codes)
    && stage?.production_mutations === 0, 'STAGE_BROWSER_ADMISSION_HOLD');
  must(widthsAre(stage?.viewports, STAGE_WIDTHS), 'STAGE_WIDTH_SET_MISSING');
  if (widthsAre(stage?.viewports, STAGE_WIDTHS)) {
    for (const v of stage.viewports) {
      must(mustHaveChecks(v.checks,REQUIRED_STAGE_CHECKS), 'STAGE_CHECKS_FAIL_' + v.width);
      must(v.axe?.status === 'RUN' && hasNoFailures(v.axe.violations),
        'STAGE_AXE_NOT_ZERO_' + v.width);
      must(validDeliveredImages(v.image_http_delivery),
        'STAGE_REAL_IMAGE_TRANSFER_HOLD_' + v.width);
    }
  }
  must(mustHaveChecks(stage?.no_javascript?.checks, REQUIRED_NOJS_CHECKS), 'STAGE_NOJS_MEANING_HOLD');
  must(local?.status === 'ISOLATED_BROWSER_AND_LAB_ADMISSION_PASSED_NOT_RELEASE'
    && local?.public_wordpress_writes === false
    && local?.wordpress_com_host_parity === 'NOT_ESTABLISHED',
    'LOCAL_WORDPRESS_RUN_HOLD');
  must(lighthouse?.status === 'ISOLATED_AUTHENTICATED_WORDPRESS_LIGHTHOUSE_MEASURED_NOT_RELEASE'
    && lighthouse?.exact_source_commit === sha
    && lighthouse?.public_wordpress_writes === false
    && lighthouse?.laboratory_only === true
    && lighthouse?.field_cwv_p75 === 'NOT_MEASURED',
    'LIGHTHOUSE_SHA_LAB_RECEIPT_HOLD');
  const profiles = lighthouse?.audit_profiles;
  must(Array.isArray(profiles) && profiles.length === 2
    && profiles[0]?.profile === 'mobile_390'
    && profiles[1]?.profile === 'desktop_1440'
    && profiles.every(p => ['performance','accessibility','best_practices']
      .every(k=>metric(p?.scores_0_to_100?.[k]) && p.scores_0_to_100[k] <= 100)
      && ['lcp_ms','cls','fcp_ms','tbt_ms'].every(k=>metric(p?.laboratory_metrics?.[k]))),
    'LIGHTHOUSE_MEASURED_PROFILES_MISSING');
  must(usability?.exact_source_commit === sha
    && usability?.status === 'ISOLATED_WORDPRESS_KEYBOARD_TOUCH_REFLOW_PASS_NOT_WCAG_CERTIFIED'
    && usability?.production_writes === false
    && hasNoFailures(usability?.failure_codes),
    'REAL_WORDPRESS_USABILITY_HOLD');
  must(guest?.url === 'https://finalvestige.com/focus/'
    && widthsAre(guest?.results, GUEST_WIDTHS)
    && guest.results.every(r => r.pass === true && mustHaveChecks(r.checks, REQUIRED_GUEST_CHECKS)
      && r.markers?.guest_email_form === true
      && r.markers?.email_is_empty === true),
    'ANONYMOUS_FOCUS_GUEST_RENDER_HOLD');
  // The guest script can run against synthetic HTML; its receipt MUST prove
  // exact public URL (not 'offline synthetic fixture') and current file age.
  must(metric(guestAgeHours) && guestAgeHours <= 24,
    'ANONYMOUS_GUEST_EVIDENCE_STALE_OR_UNDATED');
  return {
    schema: 'FV_EX2_RELEASE_EVIDENCE_JOIN_V1',
    exact_source_commit: isSha(sha) ? sha : null,
    classification: codes.length
      ? 'CURRENT_SOURCE_LOCAL_AND_GUEST_ACCEPTANCE_HOLD'
      : 'LOCAL_WORDPRESS_AND_GUEST_LAB_EVIDENCE_COMPLETE_NOT_RELEASE',
    lab_evidence_satisfied: codes.length === 0,
    failure_codes: codes,
    independent_release_gates_still_required: [
      'WP_COM_HOSTED_ACCEPTANCE','NYPL_AND_MEDIA_RIGHTS_CLEARANCE',
      'INDEPENDENT_EXACT_HEAD_QD_AND_CI','FOUNDER_VISUAL_AND_RELEASE_APPROVAL',
      'MANUAL_WCAG_2_2_AA_AT_AND_200_PERCENT_ZOOM',
      'ACTUAL_CONFIRMED_LEAD_AND_MERCHANT_REVENUE_REPORTING'
    ],
    // Never confuse test admission with publication or business outcomes.
    production_wordpress_mutations: 0,
    confirmed_subscriptions: 'NOT_TESTED',
    verified_paid_orders: 'NOT_MEASURED',
    net_revenue_per_1000_qualified_sessions: 'NOT_COMPUTABLE',
    release: 'HOLD'
  };
}
