// R396: SOURCE-ONLY offer/SKU/email identity guard over R395. No send or network.
import {assessAttributableCohort} from '../r395/cohort_guard.mjs';
export const SEND_ENABLED=false;
const families=Object.freeze({3:'zen12',5:'hypnosis_live'});
const id=x=>typeof x==='string' && /^[a-z][a-z0-9_:-]{2,79}$/.test(x);
const date=x=>typeof x==='string' && /^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$/.test(x) && !Number.isNaN(Date.parse(x)) && new Date(x).toISOString()===x;
const bad=x=>({status:'NOT_COMPUTABLE',reason:x,send_enabled:false});
const forbidden=new Set(['email','subscriber_email','ip','ip_address','phone','full_name','customer_name','postal_address']);
function privateField(x,d=0){if(d>8)return true;if(!x||typeof x!=='object')return false;return Object.entries(x).some(([k,v])=>forbidden.has(k.toLowerCase())||privateField(v,d+1));}
export function assessScopedOffer(x){
  if(!x||typeof x!=='object'||privateField(x))return bad('invalid input or PII');
  const family=families[x.issue],p=x.permission,g=x.guide,a=x.asset,c=x.cohort;
  if(!family)return bad('only original commercial slots 03 and 05');
  if(!p||p.issue!==x.issue||p.partner!=='inspire3'||p.family!==family||!id(p.sku)||!id(p.publisher_account_ref)||
    !id(p.named_acceptance_ref)||!id(p.email_channel_grant_ref)||!id(p.sku_grant_ref)||!id(p.issued_earning_link_ref)||
    p.named_partner_accepted!==true||p.email_marketing_permitted!==true||p.exact_sku_permitted!==true||
    p.email_creative_authorized!==true||p.checkout_and_refund_checked!==true||!date(p.checked_at))
    return bad('partner or exact EMAIL/SKU earning-link authority unverified');
  if(!g||g.issue!==x.issue||g.family!==family||g.sku!==p.sku||
    typeof g.url!=='string'||!/^https:\/\/finalvestige\.com\/mind\/[a-z0-9/-]+\/$/.test(g.url)||
    g.live_http_200!==true||g.wp_published_verified!==true||g.claims_checked!==true||
    g.disclosure_adjacent_to_cta!==true||g.outbound_matches_issued_link!==true||!id(g.source_review_ref))
    return bad('approved live guide and near-CTA disclosure absent');
  if(!a||!id(a.asset_id)||!id(a.campaign_id)||!id(a.published_post_ref)||
    a.independently_verified!==true||!id(a.asset_inventory_review_ref))
    return bad('published Grok asset not verified');
  if(!c||c.campaign_id!==a.campaign_id||!Array.isArray(c.sessions)||!c.ledger||!Array.isArray(c.ledger.records))
    return bad('no matching auditable cohort');
  for(const s of c.sessions){
    if(!s||s.asset_id!==a.asset_id||s.campaign_id!==a.campaign_id||s.utm_content!==a.asset_id||
      s.utm_campaign!==a.campaign_id||s.utm_medium!=='organic_social'||!id(s.source_audit_ref)||
      s.window_start_utc!==c.window_start_utc||s.window_end_utc!==c.window_end_utc)
      return bad('social session source or window mismatch');
  }
  const l=c.ledger;
  if(l.partner!=='inspire3'||l.family!==family||l.sku!==p.sku||
     l.publisher_account_ref!==p.publisher_account_ref||l.issued_earning_link_ref!==p.issued_earning_link_ref||
     !id(l.merchant_export_ref)||!id(l.independent_reconciliation_ref))
    return bad('merchant ledger unrelated to authorized publisher/offer');
  for(const row of l.records){
    if(!row||row.partner!=='inspire3'||row.family!==family||row.sku!==p.sku||
      row.issued_earning_link_ref!==p.issued_earning_link_ref||row.asset_id!==a.asset_id||
      row.issue!==x.issue||row.attribution_method!=='merchant_asset_postback'||!id(row.attribution_proof_ref)||
      !date(row.session_at_utc)||!date(row.settled_at_utc)||
      Date.parse(row.settled_at_utc)<Date.parse(row.session_at_utc))
      return bad('settled row different product/link/asset or implausible chronology');
  }
  const r=assessAttributableCohort({...c,issue:x.issue});
  if(r.status!=='COMPUTABLE')return bad('base cohort rejected: '+r.reason);
  return Object.freeze({...r,status:'SYNTHETIC_CALCULABLE_NOT_RELEASED',offer_family:family,
    disclaimer:'Input attestation identifiers are NOT authenticated merchant evidence or final send approval',
    send_enabled:false});
}
