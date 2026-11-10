"""Compile vetted desktop integration test source directly, never from .pyc.

Only the R316/R317 fail-closed AES integration gate uses this loader. The gate
continues to own source custody witnesses, required method IDs and zero-skip
assertions. This file has no filesystem writes, uploads or release side effects.
"""
from __future__ import annotations

import hashlib
import hmac
import importlib.machinery
from pathlib import Path
import sys
import types
import unittest


def load_source_suite(source: Path, *, expected_sha256: bytes | None = None) -> tuple[unittest.TestSuite, types.ModuleType, list[str]]:
    """Return tests compiled from the exact current .py bytes, not bytecode cache.

    The caller must first verify path and byte identity. The optional SHA-256
    digest binds the compiled bytes to the gate's earlier custody witness; a
    changed source between witness and loader read must never be executed.
    An existing sys.modules entry is intentionally replaced; on any
    import/discovery fault it is evicted. Exception redaction is the enclosing
    integration gate's responsibility.
    """
    if type(source) is not type(Path()) or source.suffix != ".py":
        raise ValueError("expected a source module Path")
    if expected_sha256 is not None and (type(expected_sha256) is not bytes or len(expected_sha256) != 32):
        raise ValueError("expected a SHA-256 digest")
    name = source.stem
    # Source is read as bytes: compile() honors the Python encoding cookie,
    # while importlib SourceFileLoader might silently execute a cached .pyc.
    source_bytes = source.read_bytes()
    if expected_sha256 is not None and not hmac.compare_digest(hashlib.sha256(source_bytes).digest(), expected_sha256):
        raise ValueError("source digest did not match custody witness")
    code = compile(source_bytes, str(source), "exec", dont_inherit=True)
    module = types.ModuleType(name)
    module.__file__ = str(source)
    module.__package__ = ""
    module.__spec__ = importlib.machinery.ModuleSpec(name, loader=None, origin=str(source))
    sys.modules.pop(name, None)
    sys.modules[name] = module
    try:
        exec(code, module.__dict__)
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(module)
        return suite, module, loader.errors
    except BaseException:
        sys.modules.pop(name, None)
        raise
