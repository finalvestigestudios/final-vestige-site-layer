"""Fail closed on CPython-mediated network activity in all six desktop apps.

The suite is an offline financial tool: it has no justified network runtime
operation, including loopback sockets, DNS lookups, or browser requests. The
process-global CPython audit hook is intentionally not removable at runtime.
This is defense in depth, not an OS firewall against untrusted native code.
"""
from __future__ import annotations

import sys

_ENABLED = False
_BLOCKED_EVENTS = frozenset({
    "socket.__new__", "socket.bind", "socket.connect", "socket.sendto",
    "socket.sendmsg", "socket.getaddrinfo", "socket.getnameinfo",
    "socket.gethostbyname", "socket.gethostbyaddr", "socket.gethostname",
    "urllib.Request",
})


def _reject_network(event: str, args: tuple[object, ...]) -> None:
    # Never format args: event payloads can contain confidential client data,
    # local paths, credentials, and hostnames. Deny ALL socket transports,
    # including localhost and Unix sockets; no implicit network exceptions.
    if event in _BLOCKED_EVENTS:
        raise PermissionError("Network access is disabled for Final Vestige Labs")


def install_offline_guard() -> None:
    """Install once, before GUI, imports, or smoke processing begins.

    If audit-hook installation is unavailable or rejected, execution must fail
    before loading financial information or presenting a usable application.
    """
    global _ENABLED
    if _ENABLED:
        return
    sys.addaudithook(_reject_network)
    _ENABLED = True
