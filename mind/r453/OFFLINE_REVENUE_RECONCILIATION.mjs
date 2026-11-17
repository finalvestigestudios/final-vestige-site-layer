/**
 * OFFLINE ONLY — FV Mind R453 reconciliation contract, NOT an analytics script.
 * No browser use, no cookies, no network, no uploads. Only immutable consent-safe fixtures.
 * A session/CTA is never a sale; a claim of net revenue requires independent merchant coverage.
 */
const MS_DAY=86400000;
const blockedKey=/(^|_)(email|phone|first_name|last_name|full_name|ip|ip_address|user_agent|cookie|fingerprint|password|medical|health|address)(_|$)/i;
export function assertNoPII(record) {
  if (!record || typeof record!=="object" || Array.isArray(record)) throw new Error("Record must be object");
  for (const [key,value] of Object.entries(record)) {
    if(blockedKey.test(key)) throw new Error("Forbidden PII field "+key);
    if(value && typeof value==="object" && !Array.isArray(value)) assertNoPII(value);
  }
}
function safeDate(v){const d=Date.parse(v);if(!Number.isFinite(d))throw new Error("Invalid ISO date");return d}
function nonnegativeCents(value){if(!Number.isSafeInteger(value)||value<0)throw new Error("Invalid cents");return value}
function uniqueBy(xs,key){const m=new Map();for(const x of xs){if(!m.has(x[key]))m.set(x[key],x)}return [...m.values()]}
export function summarizeOfflineLedger(payload,opts) {
  const {sessions=[],actions=[],merchantReceipts=[],coverage=null}=payload;
  const {asOf,days}=opts;
  if(![7,30].includes(days))throw new Error("Only 7/30 day cohorts");
  const upper=safeDate(asOf),lower=upper-days*MS_DAY;
  for(const rec of [...sessions,...actions,...merchantReceipts])assertNoPII(rec);
  function inWindow(x){const t=safeDate(x.timestamp);return t>=lower&&t<=upper}
  const qualified=uniqueBy(sessions.filter(s=>inWindow(s)&&s.qualifiedHuman===true&&s.botSuspected!==true&&typeof s.sessionToken==="string"&&s.sessionToken.length>=8&&typeof s.assetId==="string"&&s.assetId.length>0&&typeof s.utmCampaign==="string"&&s.utmCampaign.length>0),"sessionToken");
  const valid=new Set(qualified.map(s=>s.sessionToken));
  const joined=actions.filter(x=>inWindow(x)&&valid.has(x.sessionToken));
  const clicks=uniqueBy(joined.filter(x=>x.type==="cta_click"),"eventId").length;
  const affiliateClicks=uniqueBy(joined.filter(x=>x.type==="affiliate_click"),"eventId").length;
  const leads=uniqueBy(joined.filter(x=>x.type==="lead_confirmed"&&x.providerConfirmed===true),"eventId").length;
  // Without authenticated complete reporting, never turn unknown merchant revenue into "$0".
  const merchantCovered=coverage?.merchantSettlementsComplete===true&&coverage?.scope==="approved_product_and_period";
  const receipts=uniqueBy(merchantReceipts.filter(x=>inWindow(x)&&valid.has(x.sessionToken)&&x.merchantVerified===true&&x.settled===true&&typeof x.orderId==="string"&&x.orderId.length>0&&typeof x.settlementId==="string"&&x.settlementId.length>0),"orderId");
  let netCents=0;
  for(const r of receipts){let gross=nonnegativeCents(r.grossCents),fees=nonnegativeCents(r.feesCents),refund=nonnegativeCents(r.refundCents);if(refund>gross||fees>gross)throw new Error("Invalid refund/fees");netCents+=gross-fees-refund}
  return {cohortDays:days,qualifiedHumanSessions:qualified.length,ctaClicks:clicks,confirmedLeads:leads,affiliateClicks,verifiedPaidOrders:merchantCovered?receipts.length:null,netRevenueCents:merchantCovered?netCents:null,netRevenuePer1000SessionsCents:merchantCovered&&qualified.length?Math.round(netCents*1000/qualified.length):null,paidConversionRate:merchantCovered&&qualified.length?receipts.length/qualified.length:null,tinySample:qualified.length<100,missingMerchantCoverage:!merchantCovered,confidenceWarning:"Nonrandom traffic and tiny samples can make apparent uplift unreliable.",syntheticOnly:true};
}
