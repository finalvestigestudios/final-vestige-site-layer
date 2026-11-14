"""Fail-closed shape binding for an already cryptographically verified license.

The Ed25519 verifier is the authority. Its result must be the exact expected
Entitlement object for the selected premium product, not a truthy sentinel,
None, or a result carrying an entitlement for a different product.
This helper performs NO cryptography and authorizes no purchases or decisions.
"""


def has_verified_premium_proof(value: object, product: str, entitlement_type: type) -> bool:
    """Accept only an exact verifier result with a native, matching product.

    Check types before looking up the result product, so a str subclass with
    hostile equality cannot masquerade as another premium app. Any malformed
    verifier result denies access rather than escaping a UI authorization gate.
    """
    if (type(product) is not str or product not in ("grants", "procurement")
            or type(entitlement_type) is not type
            or type(value) is not entitlement_type):
        return False
    try:
        proof_product = value.product
    except Exception:
        return False
    return type(proof_product) is str and proof_product == product
