// Dispatch R382: PURE OFFLINE proof reference. NOT a live tracker, authorizer, event emitter, or email sender.
function hasProof(p,authority){return !!p&&p.verified===true&&p.authority===authority&&typeof p.ref==="string"&&/^[A-Za-z0-9:_/-]{12,160}$/.test(p.ref)&&typeof p.checkedAt==="string"&&/^\d{4}-\d\d-\d\dT/.test(p.checkedAt)}

function opaque(x){return typeof x==="string"&&/^[A-Za-z0-9_-]{12,100}$/.test(x)}

function asset(x){return typeof x==="string"&&/^[a-z0-9][a-z0-9_-]{4,63}$/.test(x)}

function confirmedSignup(r){
 if(!r||r.origin!=="jetpack_email_subscription"||r.status!=="confirmed"||r.emailEligible!==true||!opaque(r.providerId)||!hasProof(r.providerProof,"jetpack"))return {confirmed:false,attribution:"UNVERIFIED"};
 const a=r.sourceJoin;
 const canAttribute=!!a&&a.medium==="organic_social"&&asset(a.assetId)&&a.utm_content===a.assetId&&typeof a.campaign==="string"&&/^[a-z0-9_-]{8,80}$/.test(a.campaign)&&hasProof(a.landingProof,"first_party")&&hasProof(a.consentSafeJoinProof,"consented_join");
 return {confirmed:true,providerId:r.providerId,attribution:canAttribute?"VERIFIED_JOIN":"UNATTRIBUTABLE",assetId:canAttribute?a.assetId:null};
}

function cohortLeads(records){
 if(!Array.isArray(records))return null;
 const seen=new Set(),byAsset={};let confirmed=0,unknownSource=0;
 for(const r of records){const v=confirmedSignup(r);if(!v.confirmed||seen.has(v.providerId))continue;seen.add(v.providerId);confirmed++;if(v.attribution==="VERIFIED_JOIN")byAsset[v.assetId]=(byAsset[v.assetId]||0)+1;else unknownSource++;}
 return {providerConfirmedUnique:confirmed,verifiedAssetLeads:byAsset,confirmedWithoutSourceJoin:unknownSource};
}

function commission(o){
 if(!o||o.status!=="paid_settled"||o.basis!=="publisher_paid_commission"||o.currency!=="USD"||!opaque(o.orderId)||o.refundWindowFinalized!==true||!hasProof(o.merchantProof,"merchant"))return null;
 if(!["paidCommission","clawbacks","fees"].every(k=>typeof o[k]==="number"&&Number.isFinite(o[k])&&o[k]>=0))return null;
 return o.paidCommission-o.clawbacks-o.fees;
}

function revenuePer1000(denominator,orders){
 if(!denominator||!Number.isInteger(denominator.qualifiedHumanSessions)||denominator.qualifiedHumanSessions<=0||!hasProof(denominator.proof,"first_party")||!Array.isArray(orders)||orders.length===0)return {value:null,reason:"UNVERIFIED_DENOMINATOR_OR_SETTLEMENT"};
 let total=0,mapped=0;const used=new Set(),byAsset={};
 for(const order of orders){
  const earned=commission(order);
  if(earned===null||used.has(order.orderId))return {value:null,reason:"UNVERIFIED_OR_DUPLICATE_COMMISSION"};
  total+=earned;used.add(order.orderId);
  const a=order.sourceMap;
  if(a&&asset(a.assetId)&&a.merchantSubIdApproved===true&&hasProof(a.merchantMapProof,"merchant")&&hasProof(a.publisherMapProof,"first_party")){mapped+=earned;byAsset[a.assetId]=(byAsset[a.assetId]||0)+earned}
 }
 return {value:Math.round(total*100000/denominator.qualifiedHumanSessions)/100,publisherNet:Math.round(total*100)/100,assetAttributedNet:Math.round(mapped*100)/100,unattributedNet:Math.round((total-mapped)*100)/100,verifiedAssetRevenue:byAsset,reason:"SYNTHETIC_SCHEMA_CALCULATION_NOT_LIVE_REPORT"};
}
export {hasProof,opaque,asset,confirmedSignup,cohortLeads,commission,revenuePer1000};
