"""Fail-closed provenance classification for six-app Windows executable smoke.

A test-injected subprocess runner or platform override must never create
apparently native Windows executable evidence. This module does not authorize
release or substitute for clean-machine Windows 11 QA.
"""
from __future__ import annotations


class SmokeProvenanceError(ValueError):
    """The requested smoke result cannot be trusted as native Windows evidence."""


def classify_smoke(*, enabled: bool, native_os: str, native_arch: str,
                   runner_injected: bool, platform_override: str | None) -> str:
    """Classify a smoke attempt without trusting caller-supplied platform claims.

    ``native_os`` and ``native_arch`` must be obtained by the production caller
    from its actual runtime, not from command-line options. Explicit overrides
    are permitted only for dependency-injected tests and remain synthetic.
    """
    if type(enabled) is not bool or type(runner_injected) is not bool:
        raise SmokeProvenanceError("Invalid smoke verification request")
    if not enabled:
        return "integrity_only"
    if type(native_os) is not str or type(native_arch) is not str:
        raise SmokeProvenanceError("Native smoke platform could not be established")
    if platform_override is not None and type(platform_override) is not str:
        raise SmokeProvenanceError("Invalid smoke platform override")
    observed = platform_override if platform_override is not None else native_os
    if observed != "nt":
        raise SmokeProvenanceError("Packaged EXE smoke testing requires actual Windows x64")
    if not runner_injected and native_os != "nt":
        # platform_override='nt' alone must not let a Linux host launch a .exe.
        raise SmokeProvenanceError("Packaged EXE smoke testing requires actual Windows x64")
    if runner_injected or platform_override is not None:
        return "synthetic_smoke_only"
    if native_arch.upper() not in ("AMD64", "X86_64"):
        raise SmokeProvenanceError("Packaged EXE smoke testing requires native Windows x64")
    return "windows_smoke_passed"
