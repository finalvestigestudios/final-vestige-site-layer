#!/usr/bin/env python3
"""Apollo R402: deterministic read-only request admission for R401 staged QA.

Does not navigate, install, activate, deploy, or approve a product. Requests for
unreviewed scripts, REST endpoints, tracking pixels or arbitrary same-host files
are refused and *also* cause a staging HOLD, rather than quietly disappearing.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ASSET_PREFIX = re.compile(r"^/wp-content/plugins/[A-Za-z0-9_-]+/experience2/")
REVIEWED_SUFFIXES = frozenset((
    "/apollo-r384/assets/gallery.css",
    "/apollo-r395/assets/mobile-fit.css",
))
EXPECTED_CONTEXTS = ("320", "390-touch", "768", "1440", "1920", "320-nojs", "390-reduced")


def read_only_permits(url: str, method: str, landing: str, base) -> bool:
    """Allow only the exact staging document and exact SHA-checked reviewed CSS.

    R400 performs actual SHA-256 HTTP checks and CSP checks *after* this
    admission. This function is an independent path/method/scope filter.
    """
    if method not in ("GET", "HEAD") or not isinstance(url, str):
        return False
    if not (getattr(base, "safe_url", None) or base.canonical)(landing, landing=True) or not (getattr(base, "permits", None) or base.approved_request)(url, method, landing):
        return False
    if url == landing:
        return True
    stylesheet = (getattr(base, "reviewed_css", None) or base.css_class)(url)
    if stylesheet not in REVIEWED_SUFFIXES:
        return False
    try:
        target = urlsplit(url)
        origin = urlsplit(landing)
    except ValueError:
        return False
    if target.hostname != origin.hostname or not ASSET_PREFIX.match(target.path):
        return False
    # Prevent arbitrary same-site paths ending with approved CSS filename.
    plugin_relative = target.path.split("/experience2/", 1)[-1]
    if plugin_relative != stylesheet.lstrip("/") or target.path.count("/experience2/") != 1:
        return False
    return True


def inspect_trace(report: dict, staging: bool) -> list[str]:
    """No sensitive visitor query parameters or headers are written to receipts."""
    if not staging:
        return []
    errors = []
    events = report.get("network")
    if not isinstance(events, list) or not events:
        return ["staging_network_trace_missing"]
    denied = [e for e in events if not isinstance(e, dict) or not e.get("allowed")]
    if denied:
        errors.append("unreviewed_network_requests_denied:%d" % len(denied))
    unexpected_method = [e for e in events if isinstance(e, dict) and e.get("method") not in ("GET", "HEAD")]
    if unexpected_method:
        errors.append("mutating_or_unknown_http_methods:%d" % len(unexpected_method))
    screens = report.get("screens", [])
    observed = [r.get("context") for r in screens if isinstance(r, dict)]
    if observed != list(EXPECTED_CONTEXTS):
        errors.append("incomplete_browser_context_inventory")
    # The original R400 checks source, CSP and HTTP stylesheet bytes internally.
    if report.get("http_css_sha256") != "MATCHED":
        errors.append("delivered_css_not_verified")
    if report.get("csp") != "PRESENT":
        errors.append("document_csp_not_verified")
    if report.get("axe") != "PASS_GENUINE_ASSET":
        errors.append("genuine_axe_not_verified")
    return errors


def audit_run(args, overlay, base):
    """Patch only in this process. Always restore the parent QA function."""
    staging = bool(args.url)
    method_name = "permits" if hasattr(base, "permits") else "approved_request"
    original = getattr(base, method_name)
    # Avoid wrapping an already patched function or its own recursion.
    def narrow(url, method, landing):
        class Admission:
            safe_url = staticmethod(getattr(base, "safe_url", None) or base.canonical)
            permits = staticmethod(original)
            reviewed_css = staticmethod(getattr(base, "reviewed_css", None) or base.css_class)
        return read_only_permits(url, method, landing, Admission)
    setattr(base, method_name, narrow)
    try:
        report = overlay.run(args)
    finally:
        setattr(base, method_name, original)
    defects = inspect_trace(report, staging)
    report["r402_network_policy"] = "document_plus_two_sha256_reviewed_stylesheets_only"
    report["r402_unreviewed_requests_are_blockers"] = True
    report["r402_trace_defects"] = defects
    report["release_allowed"] = False
    if defects:
        report.setdefault("blockers", []).extend(defects)
        report["status"] = "HARD_HOLD_UNREVIEWED_NETWORK_OR_STAGING_PROOF"
    Path(args.out).mkdir(parents=True, exist_ok=True)
    (Path(args.out) / "r402-report.json").write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--fixture")
    group.add_argument("--url")
    parser.add_argument("--host")
    parser.add_argument("--axe")
    parser.add_argument("--axe-sha256")
    parser.add_argument("--chromium", default="/usr/bin/chromium")
    parser.add_argument("--out", default="experience2/apollo-r402/QA")
    args = parser.parse_args()
    exp = Path(__file__).resolve().parents[2]
    overlay_path = exp / "apollo-r401" / "qa" / "custody_overlay.py"
    if not overlay_path.is_file():
        raise SystemExit("HARD HOLD: exact parent R401 inspector missing")
    spec = importlib.util.spec_from_file_location("custody_overlay", overlay_path)
    overlay = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(overlay)
    base, visual = overlay.modules()
    report = audit_run(args, overlay, base)
    print(json.dumps({"status": report["status"], "network_defects": report["r402_trace_defects"],
                      "upstream_exact": report.get("exact_remote_upstream")}, sort_keys=True))
    return 2 if report.get("blockers") or (args.url and not report.get("exact_remote_upstream")) else 0


if __name__ == "__main__":
    raise SystemExit(main())
