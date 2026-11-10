"use strict";
const {test}=require("node:test"), assert=require("node:assert/strict");
const {auditTemporalTruth:audit}=require("../temporal_truth.cjs");
const baseline=()=>({as_of_utc:"2026-11-09T23:00:00Z",
 sessions:[{session_id:"session_001",at_utc:"2026-11-08T20:00:00Z"}],
 confirmations:[{provider_transition_ref:"transition_001",at_utc:"2026-11-08T20:02:00Z",attributed_session_id:"session_001"}],
 actions:[{type:"affiliate_outbound",click_ref:"click_001",offer_id:"zen12_premium",at_utc:"2026-11-08T20:04:00Z",attributed_session_id:"session_001"}],
 orders:[{transaction_ref:"transaction_001",affiliate_click_ref:"click_001",offer_id:"zen12_premium",at_utc:"2026-11-08T20:06:00Z",attributed_session_id:"session_001"}]});
const result=x=>audit(x).blockers;
const contains=(mod,code)=>{let x=baseline();mod(x);assert(result(x).includes(code),`expected ${code}`)};
test("baseline no temporal conflict",()=>assert(!result(baseline()).some(x=>/_AFTER_REPORT_CUTOFF|_BEFORE_SOURCE_SESSION|_TIMESTAMP_INVALID_CIVIL_DATE|_DUPLICATE_ID/.test(x))));
test("future order",()=>contains(x=>x.orders[0].at_utc="2026-11-11T00:00:00Z","ORDER_AFTER_REPORT_CUTOFF"));
test("future confirmation",()=>contains(x=>x.confirmations[0].at_utc="2026-11-11T00:00:00Z","CONFIRMATION_AFTER_REPORT_CUTOFF"));
test("future click",()=>contains(x=>x.actions[0].at_utc="2026-11-11T00:00:00Z","CLICK_AFTER_REPORT_CUTOFF"));
test("future session",()=>contains(x=>x.sessions[0].at_utc="2026-11-11T00:00:00Z","SESSION_AFTER_REPORT_CUTOFF"));
test("invalid February 30",()=>contains(x=>x.orders[0].at_utc="2026-02-30T10:00:00Z","ORDER_TIMESTAMP_INVALID_CIVIL_DATE"));
test("invalid month 13",()=>contains(x=>x.orders[0].at_utc="2026-13-01T10:00:00Z","ORDER_TIMESTAMP_INVALID_CIVIL_DATE"));
test("invalid leap day 2025",()=>contains(x=>x.confirmations[0].at_utc="2025-02-29T10:00:00Z","CONFIRMATION_TIMESTAMP_INVALID_CIVIL_DATE"));
test("valid leap day 2024",()=>{let x=baseline();x.as_of_utc="2024-03-01T00:00:00Z";for(let row of [x.sessions[0],x.actions[0],x.orders[0],x.confirmations[0]])row.at_utc="2024-02-29T10:00:00Z";assert(!result(x).some(x=>x.includes("INVALID_CIVIL_DATE")))});
test("identical duplicate order",()=>contains(x=>x.orders.push({...x.orders[0]}),"ORDER_DUPLICATE_ID_EVEN_IF_IDENTICAL"));
test("identical duplicate confirmation",()=>contains(x=>x.confirmations.push({...x.confirmations[0]}),"CONFIRMATION_DUPLICATE_ID_EVEN_IF_IDENTICAL"));
test("identical duplicate click",()=>contains(x=>x.actions.push({...x.actions[0]}),"CLICK_DUPLICATE_ID_EVEN_IF_IDENTICAL"));
test("identical duplicate session",()=>contains(x=>x.sessions.push({...x.sessions[0]}),"SESSION_DUPLICATE_ID_EVEN_IF_IDENTICAL"));
test("order before session",()=>contains(x=>x.orders[0].at_utc="2026-11-08T19:00:00Z","ORDER_BEFORE_SOURCE_SESSION"));
test("click before session",()=>contains(x=>x.actions[0].at_utc="2026-11-08T19:00:00Z","CLICK_BEFORE_SOURCE_SESSION"));
test("confirmation before session",()=>contains(x=>x.confirmations[0].at_utc="2026-11-08T19:00:00Z","CONFIRMATION_BEFORE_SOURCE_SESSION"));
test("missing confirmation source session",()=>contains(x=>x.confirmations[0].attributed_session_id="missing_001","CONFIRMATION_SOURCE_SESSION_MISSING"));
test("missing affiliate click",()=>contains(x=>x.orders[0].affiliate_click_ref="missing_001","ORDER_CLICK_JOIN_AMBIGUOUS_OR_ABSENT"));
test("click after order",()=>contains(x=>x.actions[0].at_utc="2026-11-08T21:00:00Z","CLICK_AFTER_PAID_ORDER"));
test("no payout number ever output",()=>{let x=baseline();x.founder_final_campaign_approval=true;x.merchant_authorized=true;let r=audit(x);assert.equal(r.verified_paid_orders,null);assert.equal(r.net_revenue_per_1000_qualified_humans,null);assert.equal(r.status,"REVIEW_ONLY_HOLD_UNSENT")});
test("invalid report instant",()=>contains(x=>x.as_of_utc="2026-02-30T10:00:00Z","AS_OF_INVALID_UTC_INSTANT"));
test("invalid input refused",()=>assert.throws(()=>audit(null),/LEDGER_OBJECT_REQUIRED/));
test("missing arrays refused",()=>{let x=baseline();delete x.orders;assert.throws(()=>audit(x),/ARRAY_REQUIRED:orders/)});
test("permanent merchant hold",()=>{let r=audit(baseline());assert.deepEqual(r.affected_commercial_issues,[3,5]);assert(r.blockers.includes("NAMED_PARTNER_EMAIL_RIGHTS_UNVERIFIED"))});
