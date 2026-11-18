"""Read-only Dispatch cadence and provider-count classifier; never sends or approves email."""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Evidence:
    total: int
    confirmed: int
    unconfirmed_excluded: int
    email_subscribed: int
    automatic_post_emails: bool
    public_copy_promises_email_when_published: bool
    welcome_pdf_configured: bool
    welcome_received_proven: bool
    new_provider_confirmations_proven: Optional[int]
    merchant_email_permission_proven: bool
    validated_postal_address: bool
    rendered_unsubscribe_proven: bool
    native_preview_proven: bool
    founder_final_send_approval: bool


def classify(e: Evidence) -> dict:
    numbers = (e.total, e.confirmed, e.unconfirmed_excluded, e.email_subscribed)
    if any(type(v) is not int or v < 0 for v in numbers):
        raise ValueError('Invalid provider count; integers >=0 required')
    if e.confirmed > e.total or e.email_subscribed > e.confirmed:
        raise ValueError('Subscriber totals contradict the provider snapshot')
    if e.new_provider_confirmations_proven is not None:
        if (type(e.new_provider_confirmations_proven) is not int
                or e.new_provider_confirmations_proven < 0
                or e.new_provider_confirmations_proven > e.email_subscribed):
            raise ValueError('Invalid proven newly confirmed subset')
    for name in ("automatic_post_emails", "public_copy_promises_email_when_published",
                 "welcome_pdf_configured", "welcome_received_proven",
                 "merchant_email_permission_proven", "validated_postal_address",
                 "rendered_unsubscribe_proven", "native_preview_proven",
                 "founder_final_send_approval"):
        if type(getattr(e, name)) is not bool:
            raise ValueError(f'{name} must be a real boolean')
    if e.welcome_received_proven and not e.welcome_pdf_configured:
        raise ValueError('A received configured PDF welcome needs a configured message')
    flags = []
    if e.public_copy_promises_email_when_published and not e.automatic_post_emails:
        flags.append('PUBLIC_CADENCE_EXPECTATION_MISMATCH')
    if e.unconfirmed_excluded:
        flags.append('UNCONFIRMED_EXCLUDED_FROM_CONFIRMED')
    if not e.welcome_received_proven:
        flags.append('WELCOME_DELIVERY_NOT_WITNESSED')
    if e.new_provider_confirmations_proven is None:
        flags.append('NO_VERIFIED_NEW_CONFIRMED_SIGNUP_EVENT')
    for ok, code in (
        (e.merchant_email_permission_proven, 'MERCHANT_EMAIL_PERMISSION_UNVERIFIED'),
        (e.validated_postal_address, 'POSTAL_NOT_WITNESSED'),
        (e.rendered_unsubscribe_proven, 'UNSUBSCRIBE_NOT_WITNESSED'),
        (e.native_preview_proven, 'NATIVE_PREVIEW_NOT_WITNESSED'),
        (e.founder_final_send_approval, 'FOUNDER_SEND_APPROVAL_MISSING'),
    ):
        if not ok:
            flags.append(code)
    # This deliberately never emits a send-ready state or a recipient address.
    return {
        'release': 'HOLD_UNSENT',
        'confirmed_inventory': e.confirmed,
        'email_eligible_inventory': e.email_subscribed,
        'unconfirmed_excluded': e.unconfirmed_excluded,
        'new_confirmed_leads': e.new_provider_confirmations_proven,
        'welcome_configured': e.welcome_pdf_configured,
        'welcome_delivered': e.welcome_received_proven,
        'flags': flags,
    }
