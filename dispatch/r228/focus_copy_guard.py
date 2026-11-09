"""Offline, non-sending Focus/Dispatch signup-copy regression guard.

Accepts exported page TEXT, never browser URLs, subscribers or credentials.
This does not authenticate provider subscriptions or assert delivered email.
"""
import re
from dataclasses import dataclass

BAD_REPEAT = re.compile(r"(?<!do not )(?<!don't )(?<!not )\b(sign\s*up|subscribe|enter\s+your\s+email)\s+again\b", re.I)
MISLEADING_PROOF = re.compile(r"(?:download(?:ing)?(?: the file)?|browser success|opened pdf).{0,80}(?:makes you|means you (?:are|became)|proves you are|is proof you are) (?:a )?(?:confirmed subscriber|verified signup)", re.I | re.S)

@dataclass(frozen=True)
class Result:
    repeat_signup_instructions: tuple[str, ...]
    unproved_confirmation_claims: tuple[str, ...]
    passes: bool

def audit(content: str) -> Result:
    if not isinstance(content, str):
        raise TypeError("page content must be a string")
    repeat = tuple(m.group(0) for m in BAD_REPEAT.finditer(content))
    mislead = tuple(m.group(0) for m in MISLEADING_PROOF.finditer(content))
    return Result(repeat, mislead, not (repeat or mislead))

def safe_help_copy() -> str:
    return (
        "If an in-app browser cannot open the PDF, open the download link "
        "from your welcome email in Safari or Chrome. If you have already subscribed, "
        "do not enter your email again. A visible download button is not proof "
        "that your newsletter subscription was confirmed."
    )

if __name__ == '__main__':
    import sys
    text = sys.stdin.read()
    report = audit(text)
    print('PASS' if report.passes else 'REVIEW_REQUIRED')
    print('repeat_signup_instructions:', len(report.repeat_signup_instructions))
    print('unproved_confirmation_claims:', len(report.unproved_confirmation_claims))
    sys.exit(0 if report.passes else 2)
