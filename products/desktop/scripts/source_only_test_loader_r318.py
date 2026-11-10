"""Compile vetted desktop integration test source directly, never from .pyc.

Only the R316/R317 fail-closed AES integration gate uses this loader. The gate
continues to own source custody witnesses, required method IDs and zero-skip
assertions. This file has no filesystem writes, uploads or release side effects.
"""
from __future__ import annotations

import importlib.machinery
from pathlib import Path
import sys
import types
import unittest


def load_source_suite(source: Path) -> tuple[unittest.TestSuite, types.ModuleType, list[str]]:
    """Return tests compiled from the exact current .py bytes, not bytecode cache.

    The caller must first verify path and byte identity. An existing sys.modules
    entry is intentionally replaced; on any import/discovery fault it is evicted.
    Exception redaction is the responsibility of the enclosing integration gate.
    """
    if type(source) is not type(Path()) or source.suffix != ".py":
        raise ValueError("expected a source module Path")
    name = source.stem
    # Source is read as bytes: compile() honors the Python encoding cookie,
    # while importlib SourceFileLoader might silently execute a cached .pyc.
    source_bytes = source.read_bytes()
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
