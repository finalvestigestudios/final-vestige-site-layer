/** R453 synthetic-only cohort tests. Not proof of any actual orders, audiences or revenue. */
import test from 'node:test';
import assert from 'node:assert/strict';
import { measureClosedCohort } from './cohort_math.mjs';
const p={verified:true},s={id:'opaque-session-1',seen_at:'2026-09-01T15:00:00Z',kind:'qualified_human',bot:false,proof:p,
 utm:{source:'youtube',medium:'organic_social',asset_id:'YT001'}};
const o={id:'opaque-order-1',session_id:s.id,sale_type:'affiliate',currency:'USD',gross_cents:2700,fees_cents:300,refunds_cents:400,
 settled_at:'2026-09-03T12:00:00Z',state:'settled',settlement_proof:p,attribution_proof:p};
const v={horizon_days:7,cohort_start:'2026-09-01T00:00:00Z',cohort_end:'2026-09-02T00:00:00Z',
 as_of:'2026-11-18T18:30:00Z',complete_sessions:true,complete_orders:true,sessions_proof:p,orders_proof:p,sessions:[s],orders:[o]};
test('fully synthetic mature cohort computes',()=>assert.equal(measureClosedCohort(v).status,'COMPUTABLE'));
test('synthetic net cents subtracts refunds and fees',()=>assert.equal(measureClosedCohort(v).net_cents,2000));
test('synthetic normalized net scales to 1000 sessions',()=>assert.equal(measureClosedCohort(v).net_revenue_per_1000_cents,2000000));
test('immature cohort must be held',()=>assert.equal(measureClosedCohort({...v,as_of:'2026-09-05T00:00:00Z'}).status,'UNCOMPUTABLE'));
test('no sessions must be held',()=>assert.equal(measureClosedCohort({...v,sessions:[]}).status,'UNCOMPUTABLE'));
test('incomplete provider orders must be held',()=>assert.equal(measureClosedCohort({...v,complete_orders:false}).status,'UNCOMPUTABLE'));
test('duplicate session deduped',()=>assert.equal(measureClosedCohort({...v,sessions:[s,s]}).verified_qualified_sessions,1));
test('duplicate order deduped',()=>assert.equal(measureClosedCohort({...v,orders:[o,o]}).independently_attributed_paid_orders,1));
test('conflicting duplicate order fails closed',()=>assert.equal(measureClosedCohort({...v,orders:[o,{...o,gross_cents:2800}]}).status,'UNCOMPUTABLE'));
test('unattributed order cannot inherit social credit',()=>assert.equal(measureClosedCohort({...v,orders:[{...o,attribution_proof:null}]}).independently_attributed_paid_orders,0));
test('pending order is not settled',()=>assert.equal(measureClosedCohort({...v,orders:[{...o,state:'pending'}]}).status,'UNCOMPUTABLE'));
test('refund beyond gross fails closed',()=>assert.equal(measureClosedCohort({...v,orders:[{...o,refunds_cents:2800}]}).status,'UNCOMPUTABLE'));
test('order after 7-day horizon is not attributed',()=>assert.equal(measureClosedCohort({...v,orders:[{...o,settled_at:'2026-10-03T12:00:00Z'}]}).independently_attributed_paid_orders,0));
test('bot sessions excluded',()=>assert.equal(measureClosedCohort({...v,sessions:[{...s,bot:true}]}).status,'UNCOMPUTABLE'));
test('unproven human visit blocked',()=>assert.equal(measureClosedCohort({...v,sessions:[{...s,proof:null}]}).status,'UNCOMPUTABLE'));
test('30 day mature cohort supported',()=>assert.equal(measureClosedCohort({...v,horizon_days:30}).status,'COMPUTABLE'));
test('unsupported 8-day lookback blocked',()=>assert.equal(measureClosedCohort({...v,horizon_days:8}).status,'UNCOMPUTABLE'));
test('unverified ledger snapshots blocked',()=>assert.equal(measureClosedCohort({...v,orders_proof:null}).status,'UNCOMPUTABLE'));
