#!/usr/bin/env python3
"""Adversarial tests: no revenue from traffic alone, no PII, no false sale proof."""
from copy import deepcopy
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from funnel_guard import assess,Hold,validate_cohort,validate_campaign,validate_offer

HERE=Path(__file__).resolve().parents[1]
base=json.loads((HERE/'proof-template.json').read_text())
checks=[]
def test(name,fn):
    try:fn();checks.append(name)
    except Exception as e:raise AssertionError(f'{name}: {e}') from e

def reject(name,modifier):
    def verify():
        d=deepcopy(base);modifier(d)
        try:assess(d)
        except Hold:return
        raise AssertionError('accepted invalid evidence')
    test(name,verify)

def accept(name,modifier,predicate):
    def verify():
        d=deepcopy(base);modifier(d);assert predicate(assess(d))
    test(name,verify)

def sample():
    return {'days':7,'start':'2026-11-01','end':'2026-11-07',
      'qualified_human_sessions':200,'landing_visits':160,'cta_clicks':45,'confirmed_leads':10,
      'settlement_reconciled':True,'source_attestation_ref':'reviewed-ledger-20261107',
      'orders':[{'settlement_line_ref':'merchant-line-A13','merchant_confirmed':True,
                 'paid_date':'2026-11-05','currency':'USD','gross_cents':2400,'fees_cents':150,'refunded_cents':100}]}

test('empty records do not invent sales or denominators',lambda: (
    (_ for _ in ()).throw(AssertionError('imputed number')) if assess(base)['net_revenue_per_1000_qualified_humans_verified'] is not None else None))
def assert_false(v):assert not v
test('no verified product',lambda:assert_false(validate_offer(base['offer'])))
test('no published creator',lambda:assert_false(validate_campaign(base['campaign'])))
reject('no commerce CTA activation',lambda d:d.update(commercial_cta_enabled=True))
reject('outside landing',lambda d:d.update(landing_url='https://attacker.example/'))
reject('visitor IP rejected',lambda d:d.update(ip_address='198.51.100.1'))
reject('nested personal info rejected',lambda d:d['campaign'].update(customer_email='x@example.com'))
reject('faked asset mismatch',lambda d:d['campaign'].update(utm_content='another_asset_1'))
reject('wrong medium',lambda d:d['campaign'].update(utm_medium='paid_clicks'))
reject('wrong campaign namespace',lambda d:d['campaign'].update(utm_campaign='apollo_blast'))
reject('claims views as purchased count',lambda d:d.update(cohorts=[dict(sample(),orders=5)]))
reject('formless invalid window',lambda d:d.update(cohorts=[dict(sample(),end='2026-11-08')]))
reject('unverified merchant sale',lambda d:d.update(cohorts=[dict(sample(),orders=[dict(sample()['orders'][0],merchant_confirmed=False)])]))
reject('duplicated settlement',lambda d:d.update(cohorts=[dict(sample(),orders=sample()['orders']*2)]))
reject('negative fees',lambda d:d.update(cohorts=[dict(sample(),orders=[dict(sample()['orders'][0],fees_cents=-1)])]))
reject('refund larger than gross',lambda d:d.update(cohorts=[dict(sample(),orders=[dict(sample()['orders'][0],refunded_cents=9000)])]))
reject('invalid dollar float',lambda d:d.update(cohorts=[dict(sample(),orders=[dict(sample()['orders'][0],gross_cents=24.0)])]))
reject('sale outside cohort',lambda d:d.update(cohorts=[dict(sample(),orders=[dict(sample()['orders'][0],paid_date='2026-10-30')])]))
reject('lead count exceeds clicks',lambda d:d.update(cohorts=[dict(sample(),confirmed_leads=60)]))
reject('missing independent attestation',lambda d:d.update(cohorts=[dict(sample(),source_attestation_ref='')]))
reject('duplicated cohort windows',lambda d:d.update(cohorts=[sample(),sample()]))
accept('synthetic reconciled arithmetic displayed as structural only',lambda d:d.update(cohorts=[sample()]),
       lambda r:r['cohorts'][0]['realized_net_cents_structural']==2150 and r['cohorts'][0]['net_usd_per_1000_qualified_sessions_structural']=='107.50' and r['paid_revenue_verified_by_this_tool'] is False and r['status']=='HARD_HOLD')
accept('no denominator yields null, not infinity',lambda d:d.update(cohorts=[dict(sample(),qualified_human_sessions=0,landing_visits=0,cta_clicks=0,confirmed_leads=0,orders=[])]),
       lambda r:r['cohorts'][0]['net_usd_per_1000_qualified_sessions_structural'] is None)
reject('lead conversion not purchase conversion',lambda d:d.update(cohorts=[dict(sample(),lead_attributed_confirmed_customers=99)]))
accept('unlinked purchases are not lead conversion',lambda d:d.update(cohorts=[sample()]),
       lambda r:r['cohorts'][0]['lead_to_customer_rate_structural'] is None)
accept('linked customers can be scored only when supplied',lambda d:d.update(cohorts=[dict(sample(),lead_attributed_confirmed_customers=1)]),
       lambda r:r['cohorts'][0]['lead_to_customer_rate_structural']==0.1)
accept('negative net after fees permitted',lambda d:d.update(cohorts=[dict(sample(),orders=[dict(sample()['orders'][0],fees_cents=2600)])]),
       lambda r:r['cohorts'][0]['realized_net_cents_structural']==-300)
print(json.dumps({'status':'PASS','checks':len(checks),'test_names':checks,'staging':'NOT_RUN',
    'real_sales':'NOT_VERIFIED'},indent=2,sort_keys=True))
