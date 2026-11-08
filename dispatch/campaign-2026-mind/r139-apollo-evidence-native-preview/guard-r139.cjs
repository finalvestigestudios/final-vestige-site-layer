/* Dispatch R139 — source-only, no network, no DOM writes, no email capability.
 * Works as Node -r ./guard-r139.cjs ./test-r139.cjs, or V8 eval for inspection.
 * A passing source test is NOT a native Jetpack email preview or compliance approval.
 */
(function () {
  "use strict";
  const CTA = "https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/";
  const NASA1 = "https://sma.nasa.gov/sma-disciplines/accllp/apollo-1";
  const NASA2 = "https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/";
  const POSTAL = "[[FV_VALID_PHYSICAL_POSTAL_ADDRESS_REQUIRED]]";
  const UNSUB = "[[REAL_JETPACK_UNSUBSCRIBE_RENDERING_AND_FUNCTION_REQUIRED]]";
  const MERCHANT_RE = /affiliates\.inspire3\.com|zen12\.com|hypnosislive\.com|(?:https?:\/\/[^\s"'<>]*?(?:clk|hop|ref|affiliate)[^\s"'<>]*)/i;
  const INTERNAL = /^https:\/\/finalvestige\.com\//;
  function isString(x) { return typeof x === "string"; }
  function has(x, s) { return isString(x) && x.includes(s); }
  function result(checks) { return {pass: checks.every(x => x.ok), checks: checks.map(x => ({id:x.id, pass:x.ok}))}; }
  function auditManuscript(s) {
    const body = isString(s) ? s : "";
    const checks = [
      {id:"hold_banner",ok:/HOLD_UNSENT|DRAFT.*HOLD_UNSENT/i.test(body)},
      {id:"subject",ok:/\*\*Subject:\*\* A hatch, a cabin, and an unanswered question/.test(body)},
      {id:"preheader",ok:/\*\*Preheader:\*\* NASA identified the hazards without proving the first spark/.test(body)},
      {id:"nuanced_ignition",ok:/not conclusively established/i.test(body) && /most probable initiator/i.test(body)},
      {id:"all_three_crew",ok:/Grissom/i.test(body)&&/White/i.test(body)&&/Chaffee/i.test(body)},
      {id:"six_conditions",ok:/oxygen/i.test(body)&&/combustible/i.test(body)&&/wiring/i.test(body)&&/plumbing/i.test(body)&&/escape/i.test(body)&&/rescue/i.test(body)},
      {id:"one_editorial_cta",ok:(body.match(/\*\*Read the evidence →/g)||[]).length===1 && has(body,CTA)},
      {id:"nasa_sources",ok:has(body,NASA1)&&has(body,NASA2)},
      {id:"guard_placeholders",ok:has(body,POSTAL)&&has(body,UNSUB)},
      {id:"no_merchant",ok:!MERCHANT_RE.test(body)},
      {id:"no_false_duration",ok:!/fourteen seconds|14 seconds|exact (first|ignition) (spark|point) (was|is) known/i.test(body)},
      {id:"no_deceptive_claims",ok:!/guaranteed|miracle|100% prov(?:en|ed)|scientifically proven/i.test(body)}
    ];
    return result(checks);
  }
  function auditPreview(h) {
    const s = isString(h) ? h : "";
    const links = [...s.matchAll(/<a\s+[^>]*href="([^"]+)"[^>]*>/gi)].map(m=>m[1]);
    const firstParty = links.filter(x=>INTERNAL.test(x));
    const checks = [
      {id:"doctype_language",ok:/<!doctype html>/i.test(s)&&/<html lang="en">/i.test(s)},
      {id:"mobile_width",ok:/name="viewport"/i.test(s)&&/max-width:600px/i.test(s)&&/width:100%/i.test(s)},
      {id:"clear_hold",ok:has(s,"DO NOT SEND OR PUBLISH")&&has(s,"NOT A COMPLIANT SEND FOOTER")},
      {id:"preheader",ok:has(s,"NASA identified the hazards without proving the first spark.")},
      {id:"one_first_party_cta",ok:firstParty.length===1&&firstParty[0]===CTA},
      {id:"two_documentation_sources",ok:links.includes(NASA1)&&links.includes(NASA2)&&links.length===3},
      {id:"source_link_text",ok:/Apollo 1 \/ AS-204/.test(s)&&/Report of the Apollo 204 Review Board/.test(s)},
      {id:"actual_witnesses",ok:/Grissom/.test(s)&&/White/.test(s)&&/Chaffee/.test(s)},
      {id:"nuance",ok:/not conclusively established/.test(s)},
      {id:"no_external_assets",ok:!/<(?:img|script|iframe|object|embed|form)\b/i.test(s)&&!/<link\s+rel="stylesheet"/i.test(s)},
      {id:"no_live_postal",ok:has(s,POSTAL)&&has(s,UNSUB)},
      {id:"no_merchant",ok:!MERCHANT_RE.test(s)}
    ];
    return result(checks);
  }
  function auditSourceMatrix(matrix) {
    if (!matrix || typeof matrix!=="object") return result([{id:"source_matrix",ok:false}]);
    const c = matrix.campaign || {}, w=matrix.native_wordpress||{}, slots=matrix.cta_destination_contract||[], claims=matrix.claims||[], a=matrix.release_attestations||{};
    const checkedFalse = Object.keys(a).length>=14 && Object.values(a).every(v=>v===false);
    const check=[
      {id:"six_two_four",ok:c.issue_count===6&&JSON.stringify(c.editorial_slots)==="[1,2,4,6]"&&JSON.stringify(c.commercial_hold_slots)==="[3,5]"},
      {id:"default_no_send",ok:w.email_new_posts_by_default===false&&w.email_content_format==="excerpt"&&w.newsletter_enabled===true},
      {id:"nonadditive_counts",ok:w.subscriber_totals?.nonadditive===true&&w.subscriber_totals?.total===3&&w.subscriber_totals?.imported_last_24h===1},
      {id:"receipt_unknown",ok:w.welcome_received_verified===false&&w.pdf_delivery_verified===false&&w.confirmed_email_recipients_verified===false},
      {id:"4_to_live_published",ok:slots.length===6 && slots[3]?.destination===CTA&&slots[3]?.status.includes("published")&&slots[5]?.destination==="https://finalvestige.com/focus/"},
      {id:"2_commercial_disabled",ok:[2,4].every(i=>slots[i]?.destination===null && slots[i]?.status?.startsWith("HOLD_MERCHANT"))},
      {id:"all_attestations_false",ok:checkedFalse},
      {id:"no_revenue_fabrication",ok:matrix.revenue_kpi?.net_revenue_per_1000_qualified_sessions===null},
      {id:"all_claims_cited",ok:claims.length>=8&&claims.every(x=>x.source?.startsWith("https://")&&x.assertion&&x.certainty)},
      {id:"no_approval",ok:c.approved_for_sending===false&&c.publication_authorized===false&&c.send_cadence_approved===false}
    ];
    return result(check);
  }
  function nativeDecision(settings, requested) {
    const w=settings||{}, r=requested||{};
    const notAuthorized= r.founder_final_approval!==true || r.post_publication_authorized!==true;
    // Deliberately NEVER return SEND_READY. This is a planning artifact only.
    const evidence=[
      {id:"enabled",ok:w.subscriptions===true},
      {id:"site_send_capable",ok:w.site_can_send===true},
      {id:"default_off",ok:w.email_new_posts_by_default===false},
      {id:"excerpt",ok:w.email_content_format==="excerpt"},
      {id:"correct_post_kind",ok:r.post_type==="post"},
      {id:"preview_without_sending",ok:r.preview_mode==="native_non_sending_editor"}
    ];
    return {status:"HOLD_UNSENT",preview_plausible:evidence.every(e=>e.ok),awaiting_founder_approval:notAuthorized,
      checks:evidence.map(x=>({id:x.id,pass:x.ok})),
      limitations:["native preview is not a received email","excerpt may replace the primary CTA with Jetpack Read More","post creation/publication is forbidden here"]};
  }
  globalThis.FVDispatchR139 = Object.freeze({auditManuscript,auditPreview,auditSourceMatrix,nativeDecision});
})();