'use strict';
// Privacy-safe *offline* revenue math. No network, cookies, IPs, emails, user or order identifiers.
// Financial report MUST be independently obtained from merchant/partner; synthetic tests are not sales.
function finiteNonneg(n){return typeof n==='number' && Number.isFinite(n) && n>=0;}
function cohortScorecard({qualified_human_sessions,qualified_sessions_verified=false,merchant_report_verified=false,paid_orders=[],affiliate_clicks=0,confirmed_leads=null,window_days=7}={}){
 if(![7,30].includes(window_days))throw Error('Window must be 7 or 30 days');
 if(!Number.isInteger(affiliate_clicks)||affiliate_clicks<0)throw Error('Invalid outbound click count');
 const context={window_days,affiliate_clicks,confirmed_leads:Number.isInteger(confirmed_leads)&&confirmed_leads>=0?confirmed_leads:null,qualified_human_sessions:qualified_sessions_verified&&Number.isInteger(qualified_human_sessions)&&qualified_human_sessions>=0?qualified_human_sessions:null};
 if(!qualified_sessions_verified||!merchant_report_verified||!Number.isInteger(qualified_human_sessions)||qualified_human_sessions<=0)
  return {...context,status:'NOT_COMPUTABLE',reason:'Unverified or zero qualified-human denominator or merchant-paid report',confirmed_paid_orders:null,net_revenue:null,net_revenue_per_1000:null,paid_conversion_rate:null};
 let gross=0,refunds=0,fees=0,count=0;
 for(const order of paid_orders){
  if(!order||typeof order!=='object')throw Error('Malformed paid order');
  if(order.attribution_verified!==true)continue; // never attribute unknown merchant purchases to a campaign
  if(order.settled!==true)continue; // never count clicks, intent, authorizations or pending payouts
  if(!['owned_product','affiliate_commission'].includes(order.kind))throw Error('Unsupported revenue kind');
  if(!finiteNonneg(order.gross)||!finiteNonneg(order.refunds)||!finiteNonneg(order.fees))
   return {...context,status:'NOT_COMPUTABLE',reason:'Settled order missing independently verified gross/refund/fees',confirmed_paid_orders:null,net_revenue:null,net_revenue_per_1000:null,paid_conversion_rate:null};
  if(order.refunds>order.gross)throw Error('Refund greater than gross - reconcile with chargeback source');
  gross+=order.gross; refunds+=order.refunds; fees+=order.fees;count++;
 }
 const net=Math.round((gross-refunds-fees)*100)/100;
 const metric=Math.round((1000*net/qualified_human_sessions)*100)/100;
 return {...context,status:'COMPUTABLE_ONLY_IF_INPUTS_PROVIDER_VERIFIED',confirmed_paid_orders:count,gross_revenue:Math.round(gross*100)/100,refunds:Math.round(refunds*100)/100,fees:Math.round(fees*100)/100,net_revenue:net,net_revenue_per_1000:metric,paid_conversion_rate:count/qualified_human_sessions,tiny_sample_warning:qualified_human_sessions<100||count<10};
}
module.exports={cohortScorecard};