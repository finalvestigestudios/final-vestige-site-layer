"""Fail-closed Dispatch release decision, *never* sends or contacts recipients.
For R149 Issue #174: platform/UI evidence is not native consent or revenue.
"""
from __future__ import annotations
from dataclasses import dataclass

ISSUES = {1:'editorial',2:'editorial',3:'commercial',4:'editorial',5:'commercial',6:'editorial'}
REQUIRED_ALL = ('final_founder_send_approval','eligible_recipient_evidence',
                'received_native_email_preview_review','valid_publisher_postal_address',
                'working_unsubscribe_verified','current_wp_delivery_configuration_reviewed')
REQUIRED_MERCHANT = ('named_inspire3_acceptance','email_promotion_rights',
                     'exact_product_earning_url','live_approved_warmup_guide',
                     'exact_checkout_and_refund_checked','near_cta_disclosure_reviewed')

@dataclass(frozen=True)
class Decision:
    issue: int
    kind: str
    state: str
    blocked: tuple[str, ...]
    sends: int = 0
    subscribers_changed: int = 0


def gate(issue: int, evidence: dict) -> Decision:
    if type(issue) is not int or issue not in ISSUES:
        raise ValueError('unknown issue')
    if not isinstance(evidence, dict):
        raise TypeError('evidence must be a dict')
    required=REQUIRED_ALL + (REQUIRED_MERCHANT if ISSUES[issue]=='commercial' else ())
    blocked=tuple(name for name in required if evidence.get(name) is not True)
    # Even all-true manually constructed evidence cannot authorize a send:
    # evidence needs human audit of actual sources and founder's final action.
    state='HOLD_MERCHANT_AND_UNSENT' if ISSUES[issue]=='commercial' else 'HOLD_UNSENT'
    return Decision(issue,ISSUES[issue],state,blocked)


def evaluate_campaign(evidence: dict) -> list[Decision]:
    return [gate(n,evidence) for n in range(1,7)]


def confirmed_signup(provider: dict, ui: dict | None = None) -> bool:
    """Only explicit verified provider confirmation, never a UI success flag.
    A real provider evidence reference must be independently authenticated.
    This function is a validator, not proof of native verification.
    """
    if not isinstance(provider,dict):return False
    return (provider.get('provider')=='jetpack_native' and
            provider.get('subscription_state')=='confirmed' and
            provider.get('consent_scope')=='dispatch_newsletter' and
            provider.get('independently_verified') is True and
            isinstance(provider.get('record_reference'),str) and
            provider['record_reference'].startswith('opaque-provider-ref:') and
            len(provider['record_reference'])>22)


def human_net_revenue_metric(sessions: dict | None, settlement: dict | None):
    """Never infer paid orders or a denominator from clicks/followers/views."""
    if not isinstance(sessions,dict) or not isinstance(settlement,dict):return None
    n=sessions.get('qualified_human_sessions')
    if type(n) is not int or n<=0 or sessions.get('independently_verified') is not True:return None
    if settlement.get('independently_verified') is not True:return None
    if type(settlement.get('settled_orders')) is not int:return None
    if settlement['settled_orders']<0:return None
    for k in ('gross_revenue_cents','refunds_cents','fees_cents'):
        if type(settlement.get(k)) is not int or settlement[k]<0:return None
    return round(1000*(settlement['gross_revenue_cents']-settlement['refunds_cents']-settlement['fees_cents'])/(100*n),4)
