"""Offline reference model, synthetic tokens only. No network or send capability."""
import re

FIELDS = {'kind', 'key', 'before', 'after', 'proof', 'email_verified', 'consent', 'prior_confirmed', 'source', 'campaign', 'asset', 'join_verified'}
ROUTES = {('pending', 'confirmation_receipt'), ('absent', 'verified_account_subscription_receipt')}
DIAGNOSTIC = {'form_start', 'signup_submit', 'pdf_download', 'welcome_received', 'email_click'}
TOKEN = re.compile(r'[a-zA-Z0-9_-]{1,80}\Z')


def summarize(events, inventory=(), complete=False):
    """A confirmed signup is a first-time provider-verified email consent transition."""
    if type(complete) is not bool:
        raise ValueError('explicit completeness required')
    approved = set(inventory)
    observed = {}
    for e in events:
        if not isinstance(e, dict) or set(e) - FIELDS:
            raise ValueError('unexpected fields; no personal data')
        kind = e.get('kind')
        if kind in DIAGNOSTIC:
            continue
        if kind != 'provider_transition':
            raise ValueError('unknown event')
        if ((e.get('before'), e.get('proof')) not in ROUTES or e.get('after') != 'confirmed'
                or e.get('email_verified') is not True or e.get('consent') is not True
                or e.get('prior_confirmed') is not False):
            continue
        key = e.get('key')
        if not isinstance(key, str) or not re.fullmatch(r'synthetic-[a-zA-Z0-9_-]{1,64}', key):
            raise ValueError('synthetic-only alias required')
        tags = tuple(e.get(k) for k in ('source', 'campaign', 'asset'))
        attribution = (tags if e.get('join_verified') is True and
                       all(isinstance(t, str) and TOKEN.fullmatch(t) for t in tags) and
                       tags in approved else None)
        observed.setdefault(key, set()).add(attribution)
    # A repeated receipt can fill in a missing attribution, but contradictory verified joins cannot.
    joined = [tags - {None} for tags in observed.values()]
    count = len(observed)
    attributed = sum(len(tags) == 1 for tags in joined)
    conflicts = sum(len(tags) > 1 for tags in joined)
    return {'confirmed_signup': count if complete else None,
            'source_attributed': attributed if complete else None,
            'observed_confirmations': count,
            'attribution_conflicts': conflicts,
            'cohort_complete': complete}
