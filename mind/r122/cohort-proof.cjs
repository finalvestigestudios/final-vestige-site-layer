'use strict';
// FV Mind R122. OFFLINE calculation contract for independently reconciled settlement evidence.
// NOT a live tracker. Inputs must be aggregate, not customer rows. Passing a synthetic fixture
// does NOT establish any real sale. Final authoritative merchant proof lives outside this repo.

const PII_KEYS = /(email|e[_-]?mail|phone|ip[_-]?address|postal|street|full[_-]?name|first[_-]?name|last[_-]?name|customer[_-]?id|buyer[_-]?id|order[_-]?id|transaction[_-]?id|visitor[_-]?id|fingerprint|cookie|user[_-]?agent)/i;
const REQUIRED = [
  'campaign_id','cohort_start','cohort_days','qualified_human_sessions',
  'qualified_session_method','merchant','merchant_report_reference',
  'merchant_report_confirmed','attribution_join_verified','fully_settled',
  'confirmed_paid_orders','confirmed_customers','gross_settled_revenue',
  'refunds','merchant_fees','chargebacks'
];

function rejectIdentifiers(value, path = 'input') {
  if (value && typeof value === 'object') {
    for (const [key, next] of Object.entries(value)) {
      if (PII_KEYS.test(key)) throw new Error('Identifying data forbidden: ' + path + '.' + key);
      rejectIdentifiers(next, path + '.' + key);
    }
  }
}
function isSafeId(s) { return typeof s === 'string' && /^[a-z0-9_-]{3,100}$/.test(s); }
function validMoney(n) { return typeof n === 'number' && Number.isFinite(n) && n >= 0; }
function validCount(n) { return Number.isSafeInteger(n) && n >= 0; }
function evaluateCohort(row) {
  if (!row || typeof row !== 'object' || Array.isArray(row)) return { status:'NOT_COMPUTABLE', missing:['aggregate_input'] };
  rejectIdentifiers(row);
  const missing = REQUIRED.filter(k => row[k] === undefined || row[k] === null || row[k] === '');
  if (missing.length) return {status:'NOT_COMPUTABLE',missing};
  if (!isSafeId(row.campaign_id) || !/^\d{4}-\d{2}-\d{2}$/.test(row.cohort_start)) return {status:'INVALID',reason:'campaign/date'};
  if (![7,30].includes(row.cohort_days)) return {status:'INVALID',reason:'cohort_days'};
  if (!['payhip','inspire3_partner','other_authorized_merchant'].includes(row.merchant)) return {status:'INVALID',reason:'merchant'};
  if (!row.merchant_report_confirmed || !row.attribution_join_verified || !row.fully_settled
      || !isSafeId(row.merchant_report_reference) || !isSafeId(row.qualified_session_method))
    return {status:'NOT_COMPUTABLE',missing:['merchant_confirmation_or_attribution_or_settlement']};
  if (!validCount(row.qualified_human_sessions) || !validCount(row.confirmed_paid_orders)
      || !validCount(row.confirmed_customers) || !validMoney(row.gross_settled_revenue)
      || !validMoney(row.refunds) || !validMoney(row.merchant_fees) || !validMoney(row.chargebacks))
    return {status:'INVALID',reason:'counts_or_money'};
  if (row.confirmed_customers > row.confirmed_paid_orders) return {status:'INVALID',reason:'customer_count_exceeds_orders'};
  if (row.qualified_human_sessions === 0) return {status:'NOT_COMPUTABLE',missing:['positive_qualified_session_denominator']};
  const net = row.gross_settled_revenue - row.refunds - row.merchant_fees - row.chargebacks;
  if (row.refunds + row.chargebacks > row.gross_settled_revenue + 1e-9)
    return {status:'INVALID',reason:'refunds_and_chargebacks_exceed_gross'};
  return {
    status:'COMPUTABLE_FROM_SUPPLIED_ATTESTED_AGGREGATES_NOT_INDEPENDENTLY_VERIFIED',
    campaign_id:row.campaign_id,cohort_days:row.cohort_days,
    qualified_human_sessions:row.qualified_human_sessions,
    confirmed_paid_orders:row.confirmed_paid_orders,confirmed_customers:row.confirmed_customers,
    net_revenue:Number(net.toFixed(2)),
    net_revenue_per_1000_qualified_sessions:Number((net / row.qualified_human_sessions * 1000).toFixed(2)),
    paid_order_rate:Number((row.confirmed_paid_orders / row.qualified_human_sessions).toFixed(6)),
    tiny_sample_warning:row.qualified_human_sessions < 1000 || row.confirmed_paid_orders < 30,
    explicit_limit:'Only authoritative external merchant/account records can verify real sales and eligibility.'
  };
}
module.exports = {evaluateCohort,rejectIdentifiers};
