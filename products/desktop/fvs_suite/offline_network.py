"""Fail closed on CPython-mediated network and child-process activity in all apps.

The suite is an offline financial tool: it has no justified network runtime
operation, including loopback sockets, DNS lookups, or browser requests. The
process-global CPython audit hook is intentionally not removable at runtime.
Block audited child-process creation too: a shell can otherwise bypass the
Python socket fence. This is defense in depth, not an OS sandbox.
"""
from __future__ import annotations

import sys

_ENABLED = False


class _OfflineGuardProbe(Exception):
    """Private sentinel proving this exact hook was registered."""


_BLOCKED_EVENTS = frozenset({
    "socket.__new__", "socket.bind", "socket.connect", "socket.sendto",
    "socket.sendmsg", "socket.getaddrinfo", "socket.getnameinfo",
    "socket.gethostbyname", "socket.gethostbyaddr", "socket.gethostname",
    "urllib.Request",
})


# External child processes can make their own network requests without the
# parent's CPython audit hook. Never delegate local customer data to shells,
# file-association handlers, or child interpreters. These are CPython's public
# audit event names on the supported Windows/POSIX source-test platforms.
_BLOCKED_PROCESS_EVENTS = frozenset({
    "subprocess.Popen", "os.system", "os.spawn", "os.posix_spawn",
    "os.exec", "os.fork", "os.forkpty", "os.startfile", "os.startfile/2",
})


def _reject_network(event: str, args: tuple[object, ...]) -> None:
    # Never format args: event payloads can contain confidential client data,
    # local paths, credentials, and hostnames. Deny ALL socket transports,
    # including localhost and Unix sockets; no implicit network exceptions.
    if event == "fvs.offline.guard_probe":
        raise _OfflineGuardProbe()
    if event in _BLOCKED_EVENTS:
        raise PermissionError("Network access is disabled for Final Vestige Labs")
    if event in _BLOCKED_PROCESS_EVENTS:
        raise PermissionError("External process launch is disabled for Final Vestige Labs")


def install_offline_guard() -> None:
    """Install once, before GUI, imports, or smoke processing begins.

    If audit-hook installation is unavailable or rejected, execution must fail
    before loading financial information or presenting a usable application.
    """
    global _ENABLED
    if _ENABLED:
        return
    sys.addaudithook(_reject_network)
    # CPython may silently drop a hook when an earlier hook raises RuntimeError
    # during registration. Confirm our exact hook actually received an event.
    try:
        sys.audit("fvs.offline.guard_probe")
    except _OfflineGuardProbe:
        _ENABLED = True
        return
    except Exception:
        raise RuntimeError("Offline network guard could not be installed") from None
    raise RuntimeError("Offline network guard could not be installed")
