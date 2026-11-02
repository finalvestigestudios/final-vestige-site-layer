"""Privacy-safe, strict argument parsing for private Windows 11 QA custody CLIs.

Untrusted flags, paths, alleged pins, and human witness labels must never be
echoed by argparse diagnostics into terminal logs or support tickets. A CLI
argument failure is not evidence of a failed physical Windows 11 test; it is
a HOLD before the review operation begins. Help alone remains static.
"""
from __future__ import annotations

import argparse
import sys
from typing import Sequence


class PrivateReviewParser(argparse.ArgumentParser):
    """Fail closed on invalid or ambiguous review invocation arguments."""

    def __init__(self, *args, **kwargs):
        # Prefix abbreviations can make a pasted confidential flag appear
        # valid or route it to the wrong custody option.
        kwargs["allow_abbrev"] = False
        super().__init__(*args, **kwargs)

    def error(self, message: str) -> None:
        # argparse's default error() prints the rejected value/flag to stderr.
        # The caller catches ValueError and emits its one constant HOLD line.
        raise ValueError("Private review command arguments rejected") from None

    def parse_args(self, args: Sequence[str] | None = None, namespace=None):
        tokens = list(sys.argv[1:] if args is None else args)
        seen: set[str] = set()
        for token in tokens:
            if type(token) is not str:
                raise ValueError("Private review command arguments rejected")
            if token == "--":
                break
            option = token.partition("=")[0]
            if option in ("-h", "--help") and len(tokens) != 1:
                raise ValueError("Private review command arguments rejected")
            if option in self._option_string_actions and option not in ("-h", "--help"):
                # Reject --pin=A --pin B, --dist=A --dist=B, etc. argparse
                # otherwise silently selects the last value, undermining an
                # operator's certainty about which evidence was reviewed.
                if option in seen:
                    raise ValueError("Private review command arguments rejected")
                seen.add(option)
        return super().parse_args(tokens, namespace)
