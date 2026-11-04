/* Reproducible read-only Mind R115 gate checks.
 * Run from any directory with: node mind/r115/release-gates.test.cjs
 * No network, no tracking, no merchant writes, no paid dependencies.
 */
function runChecks(gates, A, B, vtt, article, contract) {
  const checks = [];
  function check(label, ok) { checks.push({label,pass:Boolean(ok)}); }
  const ids = new Set(gates.source_register.map(s => s.id));
  check('seller sources are exact official links', gates.source_register.some(s => s.url === 'https://zen12.com/hnp') &&
    gates.source_register.some(s => s.url === 'https://subliminalguru.com/'));
  check('seller privacy link present', gates.source_register.some(s => s.url === 'https://inspire3.com/privacy/'));
  check('independent paper and FTC sources', gates.source_register.filter(s => s.type.startsWith('independent')).length >= 5 &&
    gates.source_register.filter(s => s.type === 'regulatory_guidance').length === 2);
  check('every referenced evidence ID exists', gates.claim_matrix.every(c => c.sources.every(s => ids.has(s))));
  check('claims uniquely identified', new Set(gates.claim_matrix.map(c => c.id)).size === gates.claim_matrix.length);
  check('hour equivalence blocked', gates.claim_matrix.some(c => c.id === 'ZEN_EQUIVALENCE' && c.status === 'blocked'));
  check('audio extrapolation blocked', gates.claim_matrix.some(c => c.id === 'SUB_PRIMING' && c.status === 'blocked'));
  check('money promises blocked', gates.claim_matrix.some(c => c.id === 'SUB_FINANCIAL' && c.status === 'blocked'));
  check('affiliate named authorization absent', gates.revenue_offer.merchant_acceptance_document === null);
  check('earning URL absent', gates.revenue_offer.authorized_affiliate_url === null &&
    gates.revenue_offer.commercial_cta_enabled === false);
  check('buyer reporting privacy unresolved', gates.revenue_offer.aggregate_only_buyer_reporting_agreement === null);
  check('owned paid SKU not invented', gates.owned_product_fallback.sku === null && gates.owned_product_fallback.no_activation);
  check('missing merchant proof gives NULL KPI', gates.revenue_offer.net_revenue_per_1000_qualified_sessions === null &&
    gates.revenue_offer.verified_paid_order_count === null && gates.revenue_offer.verified_qualified_sessions === null);
  check('no outbound treated as sale', gates.traffic_event_contract.outbound_is_sale === false &&
    gates.traffic_event_contract.confirmed_signup_is_sale === false);
  check('allowlist has only four UTM fields', gates.traffic_event_contract.allowlist_utm.join(',') ===
    'utm_source,utm_medium,utm_campaign,utm_content');
  check('seven and thirty day cohorts', gates.traffic_event_contract.cohorts_days.join(',') === '7,30');
  check('multiple hard release gates remain', gates.unmet_release_gates.length >= 10);
  for (const [name, html] of [['A', A], ['B', B]]) {
    check(name + ' remains noindex and readable without scripts', html.includes('noindex,nofollow') &&
      !/<script\b/i.test(html) && html.includes('<main>'));
    check(name + ' merchant source exact but unclickable', html.includes('https://zen12.com/hnp') &&
      !/href=["'][^"']*(zen12\.com|subliminalguru\.com)/i.test(html));
    check(name + ' disabled commerce with near commission disclosure', /<button[^>]*disabled[^>]*>/i.test(html) &&
      Math.abs(html.indexOf('commission') - html.indexOf('disabled aria-disabled')) < 450);
    check(name + ' no live auto tracking or signup', !/<(form|iframe|video)[\s>]/i.test(html) &&
      !/autoplay\s*=/i.test(html));
  }
  check('video is explicitly storyboard not playback', B.includes('data-film-status="storyboard-only"') &&
    B.includes('video has NOT been produced'));
  check('B minus one film section equals A', B.replace(/<section aria-labelledby="film-title" id="optional-film"[\s\S]*?<\/section>\n/, '') === A);
  const cues = [...vtt.matchAll(/(\d\d):(\d\d):(\d\d)\.(\d{3}) --> (\d\d):(\d\d):(\d\d)\.(\d{3})/g)]
    .map(x => [Number(x[1])*3600000 + Number(x[2])*60000 + Number(x[3])*1000 + Number(x[4]),
      Number(x[5])*3600000 + Number(x[6])*60000 + Number(x[7])*1000 + Number(x[8])]);
  check('40 seconds contiguous captions', cues.length === 6 && cues[0][0] === 0 &&
    cues[cues.length-1][1] === 40000 && cues.every((c,i) => c[1] > c[0] && (i===0 || c[0]===cues[i-1][1])));
  check('article clearly uncommercial', article.includes('no earning links') || article.includes('no earning links'.toUpperCase()) ||
    article.includes('no earning links'.replace('no','NO')));
  check('release contract names confirmed merchant order', contract.includes('merchant_confirmed_paid_order') &&
    contract.includes('NOT') && contract.includes('NULL'));
  check('new article cites blinded evidence not current product efficacy', article.includes('[S1]') &&
    article.includes('[S3]') && article.includes('did not buy'));
  return { passed: checks.filter(c => c.pass).length, total: checks.length, failures: checks.filter(c => !c.pass) };
}
if (typeof module !== 'undefined') module.exports = {runChecks};
if (typeof require === 'function' && require.main === module) {
  const fs = require('node:fs'), path = require('node:path'), root = path.resolve(__dirname, '../..');
  const get = p => fs.readFileSync(path.join(root, p), 'utf8');
  const result = runChecks(JSON.parse(get('mind/r115/commercial-claim-gates.json')),
    get('mind/r114/zen12-text-A.html'), get('mind/r114/zen12-film-B.html'),
    get('mind/r114/film-40s.vtt'), get('mind/r115/subliminal-audio-investigation.md'),
    get('mind/r115/conversion-release-contract.md'));
  process.stdout.write(JSON.stringify(result, null, 2) + '\n');
  if (result.failures.length) process.exitCode = 1;
}
