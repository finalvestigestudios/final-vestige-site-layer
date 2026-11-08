/**
 * Dispatch R110. Offline, pure source-of-truth contract. NO network, cookies,
 * email access, user exports, email delivery or WordPress mutations.
 * Synthetic data only. Not a production analytics emitter.
 */
const STATES = new Set(['none', 'not_confirmed', 'subscribed', 'not_subscribed', 'bounced', 'emails_paused', 'not_sending']);
const SOURCES = new Set(['youtube', 'tiktok', 'instagram', 'facebook', 'pinterest', 'x', 'bluesky']);
const CONTENT = /^[a-z0-9][a-z0-9_-]{2,70}$/;
const DIGEST = /^h:[a-f0-9]{64}$/;
const TYPE = 'confirmed_signup';
const DISCOVERY = 'organic_social';
const ROUTES = new Set(['/focus/', '/dispatch/']);
const ALLOWED_PROOF = new Set(['clicked_confirmation_link', 'account_preverified']);

const fail = (reason) => ({ event: null, reason, reachable: null });

/**
 * Evaluate a proposed ONE-TIME confirmed_signup against a native Jetpack record.
 * An already-verified WP account can subscribe without a confirmation-email click.
 * Reader-following is not equivalent to email subscription. A signed-up lead is
 * not necessarily currently reachable and never establishes a paid conversion.
 */
export function evaluateConfirmedSignup(input, alreadySeen = new Set()) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) return fail('invalid_input');
  const { previous, current, consent, proof, attribution } = input;
  if (!previous || !current || !consent || !proof) return fail('insufficient_evidence');
  if (!STATES.has(previous.email_subscription) || !STATES.has(current.email_subscription)) return fail('unknown_status');
  if (current.source !== 'native_jetpack_subscriber_filter' || proof.source !== 'native_jetpack_subscription_event') return fail('not_authoritative');
  if (!DIGEST.test(proof.subscriber_digest || '')) return fail('unsafe_or_absent_identity');
  if (typeof proof.event_ref !== 'string' || !CONTENT.test(proof.event_ref)) return fail('missing_event_ref');
  if (consent.kind !== 'explicit_site_newsletter_signup' || consent.site !== 'finalvestige.com' ||
      !Number.isFinite(Date.parse(consent.recorded_at)) || consent.active !== true) return fail('consent_not_proven');
  if (!ALLOWED_PROOF.has(proof.method)) return fail('confirmation_method_unverified');
  if (current.email_subscription !== 'subscribed' || current.suppressed === true || current.removed === true) return fail('email_ineligible');
  if (proof.method === 'clicked_confirmation_link' && previous.email_subscription !== 'not_confirmed') return fail('confirmation_transition_absent');
  if (proof.method === 'account_preverified' && (proof.identity_kind !== 'wordpress_account' || previous.email_subscription !== 'none')) return fail('preverified_transition_absent');
  // Existing list members, reactivations and upgrades have separate lifecycle semantics.
  if (previous.email_subscription === 'subscribed' || proof.is_imported === true || proof.is_admin_created === true) return fail('not_a_new_opt_in');
  const dedupeKey = `finalvestige.com:${proof.subscriber_digest}`;
  if (alreadySeen.has(dedupeKey)) return fail('duplicate_confirmation');
  const event = { type: TYPE, dedupe_key: dedupeKey, event_ref: proof.event_ref, proof_method: proof.method };
  if (attribution && attribution.origin === 'verified_first_party_landing' &&
      attribution.human_evidence === true && SOURCES.has(attribution.utm_source) &&
      attribution.utm_medium === DISCOVERY && CONTENT.test(attribution.utm_content || '') &&
      /^([a-z]+)_pilot_20\d{2}_\d{2}$/.test(attribution.utm_campaign || '') &&
      ROUTES.has(attribution.landing_path)) {
    event.attribution = {
      utm_source: attribution.utm_source, utm_medium: DISCOVERY,
      utm_campaign: attribution.utm_campaign, utm_content: attribution.utm_content,
      landing_path: attribution.landing_path
    };
  } else {
    event.attribution = null; // NO invented source or fallback to last referrer.
  }
  // Confirmed subscription is NOT verified inbox reachability or delivered mail.
  // Native aggregate subscriber counts, bounces and actual received-mail proof are separate.
  return { event, reason: 'confirmed_platform_opt_in', reachable: null };
}

/** Reports count UNIQUE confirmed signup events only; does not claim recipients,
 * opens, welcome receipt, sales, commissions, net revenue or attributed visitors.
 * Callers must not persist the opaque keys in public analytics. */
export function aggregateConfirmedSignups(records) {
  if (!Array.isArray(records)) throw new TypeError('records must be an array');
  const alreadySeen = new Set();
  const reasons = {};
  let confirmed = 0, linked = 0;
  for (const input of records) {
    const result = evaluateConfirmedSignup(input, alreadySeen);
    if (result.event) {
      alreadySeen.add(result.event.dedupe_key);
      confirmed++;
      if (result.event.attribution) linked++;
    } else reasons[result.reason] = (reasons[result.reason] || 0) + 1;
  }
  return { confirmed_signup_events: confirmed, attributable_opt_ins: linked,
    source_unknown_opt_ins: confirmed - linked, excluded_reasons: reasons,
    email_reachable_subscriber_count: null, paid_orders: null, net_revenue_per_1000: null };
}
