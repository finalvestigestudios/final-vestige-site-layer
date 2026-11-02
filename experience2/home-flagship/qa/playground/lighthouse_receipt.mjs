/** Privacy-first Lighthouse receipt: only numerical audit data may leave the runner.
 * Do not serialize lhr, traces, URLs, cookies, page titles, audit debug messages, or screenshots.
 */
function finite(value, minimum=0) {
  return typeof value === 'number' && Number.isFinite(value) && value >= minimum;
}
function score(cat) {
  if (!finite(cat?.score) || cat.score > 1) throw Error('CATEGORY_SCORE_MISSING');
  return Math.round(cat.score * 100);
}
function audit(lhr, key, mandatory=true) {
  const value = lhr?.audits?.[key]?.numericValue;
  if (!finite(value)) {
    if (mandatory) throw Error('AUDIT_METRIC_MISSING');
    return null;
  }
  return Math.round(value * 1000) / 1000;
}
export function sanitizedSample(lhr, profile) {
  if (!['mobile_390', 'desktop_1440'].includes(profile)) throw Error('PROFILE_UNEXPECTED');
  if (lhr?.runtimeError) throw Error('LIGHTHOUSE_RUNTIME_FAILURE');
  if (typeof lhr?.lighthouseVersion !== 'string' ||
      !/^\d+\.\d+\.\d+/.test(lhr.lighthouseVersion)) throw Error('LIGHTHOUSE_VERSION_MISSING');
  // Validate the effective Lighthouse configuration, not merely our intended
  // CLI flags. Otherwise a mobile-slowdown run could be falsely called desktop.
  const s=lhr.configSettings, desktop=profile==='desktop_1440';
  const width=desktop?1440:390;
  const cpu=s?.throttling?.cpuSlowdownMultiplier;
  if (s?.formFactor!==(desktop?'desktop':'mobile') ||
      s?.screenEmulation?.width!==width ||
      s?.screenEmulation?.mobile!==!desktop ||
      !finite(cpu) || cpu===0 ||
      (desktop && cpu!==1)) throw Error('LIGHTHOUSE_EFFECTIVE_PROFILE_MISMATCH');
  return {
    profile,
    lighthouse_version: lhr.lighthouseVersion.slice(0, 24),
    effective_emulation: {form_factor:s.formFactor,viewport_width_px:width,
      cpu_slowdown_multiplier:cpu,throttling_method:'simulate'},
    scores_0_to_100: {
      performance: score(lhr.categories?.performance),
      accessibility: score(lhr.categories?.accessibility),
      best_practices: score(lhr.categories?.['best-practices']),
    },
    laboratory_metrics: {
      lcp_ms: audit(lhr, 'largest-contentful-paint'),
      cls: audit(lhr, 'cumulative-layout-shift'),
      fcp_ms: audit(lhr, 'first-contentful-paint'),
      tbt_ms: audit(lhr, 'total-blocking-time'),
      speed_index_ms: audit(lhr, 'speed-index', false),
    },
  };
}
export function buildReceipt(samples, sha) {
  if (!/^[0-9a-f]{40}$/.test(sha) || samples.length !== 2 ||
      samples[0]?.profile !== 'mobile_390' ||
      samples[1]?.profile !== 'desktop_1440') throw Error('EXACT_AUDIT_CONTRACT_FAILED');
  return {
    status: 'ISOLATED_AUTHENTICATED_WORDPRESS_LIGHTHOUSE_MEASURED_NOT_RELEASE',
    exact_source_commit: sha,
    audit_target: 'SEVEN_CHAPTER_ISOLATED_WORDPRESS_PRIVATE_RENDERER',
    audit_profiles: samples,
    laboratory_only: true,
    wpcom_host_parity: 'NOT_ESTABLISHED',
    field_cwv_p75: 'NOT_MEASURED',
    assistive_technology: 'MANUAL_REVIEW_REQUIRED',
    nypl_image_rights: 'HOLD_PENDING_CAPTURE_SPECIFIC_CLEARANCE',
    public_wordpress_writes: false,
    release: 'HOLD_PENDING_QD_RIGHTS_FOUNDER_AND_HOSTED_ACCEPTANCE'
  };
}
