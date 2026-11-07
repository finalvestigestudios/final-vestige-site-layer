"""Fail-closed shape binding for an already cryptographically verified license.

The Ed25519 verifier is the authority. Its result must be the exact expected
Entitlement object for the selected premium product, not a truthy sentinel,
None, or a result carrying an entitlement for a different product.
This helper performs NO cryptography and authorizes no purchases or decisions.
"""


def has_verified_premium_proof(value: object, product: str, entitlement_type: type) -> bool:
    """Accept only an exact verifier result for the requested premium product."""
    return (type(product) is str and product in ("grants", "procurement")
            and type(entitlement_type) is type
            and type(value) is entitlement_type
            and value.product == product)
