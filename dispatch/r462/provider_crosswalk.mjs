// R462 pure provider observation classifier; READ ONLY. No network, list mutation, or identity exports.
// Inputs MUST be pre-aggregated, privacy-filtered per the companion observation JSON.
function reconcileProviderViews(v) {
  if (!v || typeof v!=="object") throw new TypeError("missing provider views");
  const allowed=["status","email_subscriber"];
  for(const f of ["all","email","reader","unconfirmed"])for(const row of (v.filters?.[f]?.rows||[]))for(const k of Object.keys(row))if(!allowed.includes(k))throw new Error("PII or unsupported field rejected: "+k);
  const ints=[v.newsletter?.total,v.newsletter?.confirmed,v.newsletter?.unconfirmed,v.filters?.all?.total,v.filters?.email?.total,v.filters?.reader?.total,v.filters?.unconfirmed?.total,v.followers?.email,v.followers?.wpcom];
  if(ints.some(x=>!Number.isInteger(x)||x<0))throw new Error("all nine counts must be nonnegative integers");
  const n=v.newsletter,f=v.filters,g=v.followers;const warnings=[];
  if(n.confirmed>n.total)warnings.push("NEWSLETTER_CONFIRMED_EXCEEDS_TOTAL");
  if(n.confirmed+n.unconfirmed>n.total)warnings.push("UNCONFIRMED_IS_SEPARATE_COORT_NOT_ADDITIVE");
  if(f.all.total!==f.all.rows.length||f.email.total!==f.email.rows.length||f.reader.total!==f.reader.rows.length||f.unconfirmed.total!==f.unconfirmed.rows.length)warnings.push("FILTER_ROWS_TOTAL_MISMATCH");
  if(f.all.rows.some(z=>z.status!=="Subscribed")||f.email.rows.some(z=>z.email_subscriber!==true||z.status!=="Subscribed"))warnings.push("SUBSCRIBER_STATUS_NOT_CONFIRMED");
  if(f.unconfirmed.rows.some(z=>z.status==="Subscribed"))warnings.push("UNCONFIRMED_FILTER_CONTAINS_CONFIRMED");
  if(f.email.total>f.all.total||f.reader.total>f.all.total)warnings.push("FILTER_EXCEEDS_ALL");
  if(!g.partial && (g.email!==f.email.total||g.wpcom!==f.reader.total))warnings.push("FOLLOWERS_AND_SUBSCRIBERS_DISAGREE");
  if(g.partial)warnings.push("FOLLOWERS_PARTIAL_NO_COMPARISON");
  return {
    release:"HOLD_UNSENT",
    sourceCounts:{newsletter_total:n.total,newsletter_confirmed:n.confirmed,newsletter_unconfirmed_additional:n.unconfirmed,stats_all:f.all.total,stats_email:f.email.total,stats_reader:f.reader.total,stats_unconfirmed:f.unconfirmed.total,stats_followers_email:g.email,stats_followers_reader:g.wpcom},
    warnings,
    reconciled:warnings.length===0,
    unique_confirmed_human_signups:null,
    attributable_confirmed_signup_events:null,
    email_delivery_witnessed:false,
    note:"Provider buckets do not establish unique external opt-ins or consent transitions. Unconfirmed records are not added to total; no recipient identifiers retained."
  };
}
export { reconcileProviderViews };
