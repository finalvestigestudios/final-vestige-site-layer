"""Private Windows 11 six-app manual QA custody; NEVER authorizes distribution.

This deliberately cannot certify physical keyboard, NVDA, contrast, AV, signing,
licensing or human independence. A separately transmitted R9 SHA-256 is
mandatory for both template and verification; merely matching that hash cannot
establish an independent witness. Local witness bytes never leave the machine.
"""
from __future__ import annotations

import argparse
from private_review_cli_r146 import PrivateReviewParser
import hashlib
import hmac
import json
import math
import os
import platform
import re
import stat
import sys
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path

FREE = ("LedgerDiffLite.exe", "InvoiceTwinScout.exe", "SpendMapLite.exe", "PolicyDeltaDesk.exe")
PREMIUM = ("GrantAuditStudioPro.exe", "ProcureGuardStudioPro.exe")
ALL = FREE + PREMIUM
FREE_CHECKS = (
    "packaged_window", "physical_tab_shift_tab", "physical_shortcuts",
    "native_picker_cancel", "nvda_labels_and_order", "windows_high_contrast",
    "windows_scaling_200", "windows_scaling_400",
)
PREMIUM_CHECKS = (
    "no_entitlement_locked", "no_editor_or_file_access", "locked_keyboard_navigation",
    "nvda_locked_dialog", "locked_high_contrast", "locked_scaling_200",
    "locked_scaling_400",
)
SCHEMA = "fv-labs-win11-manual-r109-v1"
WITNESS_SCHEMA = "fv-labs-win11-check-witness-r110-v1"
WITNESS_SCHEMA_V2 = "fv-labs-win11-check-witness-r126-v2"
MIN_OBSERVATION_CHARS = 80
MAX_OBSERVATION_CHARS = 4096
PURPOSE = "PRIVATE_MANUAL_REVIEW_ONLY_NOT_RELEASE_AUTHORIZED"
HEX = re.compile(r"[0-9a-f]{64}\Z")
OPERATOR = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_-]{2,31}\Z")
MAX_REPORT_BYTES = 256 * 1024
MAX_WITNESS_BYTES = 32 * 1024
ERROR = "HOLD: Windows 11 manual source-to-witness acceptance unverified; release prohibited"


class ReviewHold(ValueError):
    """Caller must not print underlying path, witness, or user content."""


def _checks(app):
    if app in FREE:
        return FREE_CHECKS
    if app in PREMIUM:
        return PREMIUM_CHECKS
    raise ReviewHold("Unexpected product")


def _directory_chain(directory: Path) -> tuple[tuple[str, int, int], ...]:
    """Pin every ordinary directory ancestor of private evidence.

    A safe leaf path alone is insufficient: a linked parent or Windows
    junction can redirect the R9 source or human testimony outside custody.
    This is a cooperative on-disk identity check, not protection against a
    malicious administrator or an attacker who wins an in-place race.
    """
    try:
        current = directory.absolute()
        entries = []
        while True:
            meta = current.lstat()
            if (not stat.S_ISDIR(meta.st_mode) or current.is_symlink() or
                    (hasattr(current, "is_junction") and current.is_junction()) or
                    bool(getattr(meta, "st_file_attributes", 0) &
                         getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))):
                raise ReviewHold("Untrusted private evidence directory")
            entries.append((str(current), meta.st_dev, meta.st_ino))
            if current == current.parent:
                return tuple(entries)
            current = current.parent
    except OSError:
        raise ReviewHold("Untrusted private evidence directory") from None


def _bytes(path: Path, maximum: int, *, minimum: int = 1) -> bytes:
    """Read a stable private file and reject redirected directory ancestors."""
    try:
        parent_chain = _directory_chain(path.parent)
        before = path.lstat()
        if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or
                path.is_symlink() or
                (hasattr(path, "is_junction") and path.is_junction()) or
                bool(getattr(before, "st_file_attributes", 0) &
                     getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)) or
                not minimum <= before.st_size <= maximum):
            raise ReviewHold("Untrusted evidence file")
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(path, flags)
        try:
            first = os.fstat(fd)
            if (not stat.S_ISREG(first.st_mode) or first.st_nlink != 1 or
                    (first.st_dev, first.st_ino, first.st_size) !=
                    (before.st_dev, before.st_ino, before.st_size)):
                raise ReviewHold("Evidence substituted")
            data = os.read(fd, maximum + 1)
            second = os.fstat(fd)
            after = path.lstat()
            # A stable file descriptor does not establish a stable parent:
            # a substituted directory can redirect later evidence reads.
            if (_directory_chain(path.parent) != parent_chain or
                    len(data) != first.st_size or
                    (second.st_dev, second.st_ino, second.st_size,
                     second.st_mtime_ns, second.st_ctime_ns) !=
                    (first.st_dev, first.st_ino, first.st_size,
                     first.st_mtime_ns, first.st_ctime_ns) or
                    (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns) !=
                    (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)):
                raise ReviewHold("Evidence changed during reading")
            return data
        finally:
            os.close(fd)
    except (OSError, UnicodeError) as exc:
        raise ReviewHold("Cannot safely read evidence") from None


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_r9(r9: dict, actual: dict) -> dict[str, str]:
    """Two independent R9/source-check claims must match exact six candidates."""
    if (not isinstance(r9, dict) or not isinstance(actual, dict) or
            type(r9.get("schema")) is not int or r9["schema"] != 1 or r9.get("status") != "windows_smoke_passed" or
            r9.get("windows_executables_verified") is not True or
            r9.get("smoke_simulated") is not False or
            r9.get("release_authorized") is not False or
            r9.get("premium_entitlement_verified") is not False or
            not isinstance(r9.get("artifacts"), list) or len(r9["artifacts"]) != 6 or
            set(actual) != set(ALL) or
            not isinstance(r9.get("checksums_sha256"), str) or
            HEX.fullmatch(r9["checksums_sha256"]) is None):
        raise ReviewHold("Candidate custody prerequisites not met")
    hashes = {}
    for item in r9["artifacts"]:
        if (not isinstance(item, dict) or item.get("name") not in ALL or
                item["name"] in hashes or item.get("pe_machine") != "AMD64" or
                item.get("smoke") != "passed" or
                not isinstance(item.get("sha256"), str) or
                HEX.fullmatch(item["sha256"]) is None or
                type(item.get("seconds")) not in (float, int) or
                item["seconds"] < 0 or
                (type(item["seconds"]) is float and not math.isfinite(item["seconds"])) or
                item["sha256"] != actual[item["name"]]):
            raise ReviewHold("Candidate artifact mismatch")
        hashes[item["name"]] = item["sha256"]
    if set(hashes) != set(ALL):
        raise ReviewHold("Missing expected products")
    return {name: hashes[name] for name in ALL}


def make_template(r9: dict, actual: dict, r9_raw: bytes) -> dict:
    hashes = verify_r9(r9, actual)
    return {
        "schema": SCHEMA, "purpose": PURPOSE,
        "r9_report_sha256": _sha(r9_raw),
        "checksums_sha256": r9["checksums_sha256"],
        "reviewer_id": "", "windows11_build": None, "observed_utc": None,
        "apps": {name: {"candidate_sha256": hashes[name],
                         "checks": {check: {"state": "NOT_RUN", "witness_sha256": None}
                                    for check in _checks(name)}} for name in ALL},
    }


def _strict_json(raw: bytes) -> dict:
    """Strict RFC 8259 JSON: no duplicate keys or nonfinite numeric tokens.

    json.loads normally accepts NaN/Infinity literals and overflows e.g.
    1e9999 to float infinity. Financial audit/QA evidence cannot silently
    represent such values, even when a local SHA-256 is recomputed.
    """
    def reject_constant(_value):
        raise ReviewHold("Nonfinite JSON constant")

    def finite_float(value):
        parsed = float(value)
        if not math.isfinite(parsed):
            raise ReviewHold("Nonfinite JSON number")
        return parsed

    def unique(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise ReviewHold("Duplicate JSON key")
            obj[key] = value
        return obj
    result = json.loads(raw, object_pairs_hook=unique,
                        parse_constant=reject_constant, parse_float=finite_float)
    if not isinstance(result, dict):
        raise ReviewHold("Expected JSON object")
    return result


def _ambiguous_observation_char(char: str) -> bool:
    """Prevent hidden text and display-spoofing glyphs in human QA evidence.

    Rejection applies to v1 legacy and v2 current private witness validation.
    Ordinary multilingual letters and accent combining marks remain allowed.
    """
    cp = ord(char)
    category = unicodedata.category(char)
    return (
        (category in ("Cc", "Cf", "Cs", "Zl", "Zp") and char not in ("\t", "\n"))
        or (char.isspace() and char not in (" ", "\t", "\n"))
        or cp in (0x034F, 0x115F, 0x1160, 0x2800, 0x3164, 0xFFA0)
        or 0x180B <= cp <= 0x180F
        or 0xFE00 <= cp <= 0xFE0F
        or 0xE0100 <= cp <= 0xE01EF
    )


def _bound_witness(raw: bytes, review: dict, app: str, check: str, state: str,
                   *, now: datetime | None = None) -> None:
    """Require each private note to identify its own check, reviewer and exact EXE.

    A SHA-256 of anonymous free-form text cannot prevent accidental reuse of a
    note from another app, test, candidate build or reviewer. This versioned JSON
    envelope is still reviewer-declared and is NOT proof of independent QA.
    """
    try:
        note = _strict_json(raw)
    except (UnicodeError, json.JSONDecodeError):
        raise ReviewHold("Witness JSON cannot be decoded") from None
    # Legacy r110 notes remain readable. All new writes are timestamped v2.
    schema = note.get("schema")
    if type(schema) is not str or schema not in (WITNESS_SCHEMA, WITNESS_SCHEMA_V2):
        raise ReviewHold("Unknown witness version")
    keys = {"schema", "app", "check", "state", "candidate_sha256",
            "r9_report_sha256", "reviewer_id", "windows11_build",
            "observed_utc", "observation"}
    if schema == WITNESS_SCHEMA_V2:
        keys.add("recorded_utc")
    if set(note) != keys:
        raise ReviewHold("Witness fields are incomplete or unexpected")
    expected = {
        "schema": schema,
        "app": app,
        "check": check,
        "state": state,
        "candidate_sha256": review["apps"][app]["candidate_sha256"],
        "r9_report_sha256": review["r9_report_sha256"],
        "reviewer_id": review["reviewer_id"],
        "windows11_build": review["windows11_build"],
        "observed_utc": review["observed_utc"],
    }
    if (type(note["windows11_build"]) is not int or
            any(note[field] != value or type(note[field]) is not type(value)
                for field, value in expected.items())):
        raise ReviewHold("Witness belongs to a different review or check")
    if schema == WITNESS_SCHEMA_V2:
        clock = now if now is not None else datetime.now(timezone.utc)
        captured = _observed_time(note["recorded_utc"], clock)
        session_start = _observed_time(review["observed_utc"], clock)
        # Local wall-clock sanity only; not trusted physical observation time.
        if captured < session_start or captured > clock + timedelta(minutes=1):
            raise ReviewHold("Inconsistent check capture time")
    observation = note["observation"]
    if (type(observation) is not str or
            not MIN_OBSERVATION_CHARS <= len(observation.strip()) <= MAX_OBSERVATION_CHARS or
            any(_ambiguous_observation_char(ch) for ch in observation)):
        raise ReviewHold("Witness observation invalid or insufficient")


def _observed_time(value: str, now: datetime):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", value):
        raise ReviewHold("Invalid observation time")
    try:
        observed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        raise ReviewHold("Invalid observation time") from None
    if not now - timedelta(days=30) <= observed <= now + timedelta(hours=1):
        raise ReviewHold("Observation is stale or future dated")
    return observed


def validate_review(review: dict, template: dict, witnesses: Path,
                    *, now: datetime | None = None) -> dict:
    """Counts only genuine local witness digests; no distribution decision."""
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None or not isinstance(review, dict):
        raise ReviewHold("Invalid reviewer or review")
    expected = {"schema", "purpose", "r9_report_sha256", "checksums_sha256",
                "reviewer_id", "windows11_build", "observed_utc", "apps"}
    if (set(review) != expected or review.get("schema") != SCHEMA or
            review.get("purpose") != PURPOSE or
            not isinstance(review.get("reviewer_id"), str) or
            OPERATOR.fullmatch(review["reviewer_id"]) is None or
            type(review.get("windows11_build")) is not int or
            not 22000 <= review["windows11_build"] <= 99999 or
            any(review.get(k) != template.get(k) for k in (
                "r9_report_sha256", "checksums_sha256")) or
            not isinstance(review.get("apps"), dict) or
            set(review["apps"]) != set(ALL)):
        raise ReviewHold("Unbound or incomplete manual review")
    _observed_time(review.get("observed_utc"), now)
    if witnesses.is_symlink() or not witnesses.is_dir():
        raise ReviewHold("Witness directory must be ordinary")
    witness_chain = _directory_chain(witnesses)
    counts = {"PASS": 0, "FAIL": 0, "NOT_RUN": 0}
    for name in ALL:
        obj = review["apps"][name]
        original = template["apps"][name]
        if (not isinstance(obj, dict) or set(obj) != {"candidate_sha256", "checks"} or
                obj["candidate_sha256"] != original["candidate_sha256"] or
                not isinstance(obj["checks"], dict) or set(obj["checks"]) != set(_checks(name))):
            raise ReviewHold("Product manual matrix mismatch")
        for check in _checks(name):
            one = obj["checks"][check]
            if not isinstance(one, dict) or set(one) != {"state", "witness_sha256"}:
                raise ReviewHold("Unrecognized manual check")
            state, digest = one["state"], one["witness_sha256"]
            if type(state) is not str or state not in counts:
                raise ReviewHold("Invalid reviewer conclusion")
            if state == "NOT_RUN":
                if digest is not None:
                    raise ReviewHold("Unperformed checks cannot cite evidence")
            else:
                if not isinstance(digest, str) or HEX.fullmatch(digest) is None:
                    raise ReviewHold("Missing local witness seal")
                witness = witnesses / (name.removesuffix(".exe") + "--" + check + ".json")
                data = _bytes(witness, MAX_WITNESS_BYTES, minimum=64)
                if _sha(data) != digest:
                    raise ReviewHold("Witness content changed")
                _bound_witness(data, review, name, check, state, now=now)
            counts[state] += 1
    if _directory_chain(witnesses) != witness_chain:
        raise ReviewHold("Witness directory changed during validation")
    complete = counts["NOT_RUN"] == 0 and counts["FAIL"] == 0
    return {"schema": SCHEMA, "status": "MANUAL_MATRIX_COMPLETE_UNCERTIFIED" if complete
            else "REVIEW_HOLD_INCOMPLETE_OR_FAILED", "counts": counts,
            "release_authorized": False, "premium_editor_licensed": False,
            "claims": "Reviewer-reported, checksum-bound private notes; NOT independently witnessed"}


def external_r9_pin(value: str) -> str:
    """Require a caller-supplied out-of-band SHA-256, never infer it locally.

    This tests digest equality, NOT whether the operator truly sourced the
    claimed pin from an independent, authenticated QD-approved channel.
    """
    if type(value) is not str or HEX.fullmatch(value) is None:
        raise ReviewHold("A separate lowercase 64-hex R9 evidence pin is required")
    return value


def load_custody(dist: Path, r9_path: Path,
                 expected_r9_sha256: str) -> tuple[dict, dict, bytes]:
    # R9 proof is not an independent anchor when a tool re-hashes its own
    # local report. The separately supplied digest is mandatory at intake.
    expected = external_r9_pin(expected_r9_sha256)
    try:
        report_raw = _bytes(r9_path, MAX_REPORT_BYTES)
        if not hmac.compare_digest(_sha(report_raw), expected):
            raise ReviewHold("R9 report differs from the separate custody pin")
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from release_gate import verify
        report = _strict_json(report_raw)
        independent = verify(dist, smoke=False)
        if independent["checksums_sha256"] != report.get("checksums_sha256"):
            raise ReviewHold("Checksum manifest changed")
        actual = {item["name"]: item["sha256"] for item in independent["artifacts"]}
        verify_r9(report, actual)
        return report, actual, report_raw
    except (ValueError, UnicodeError, OSError) as exc:
        raise ReviewHold("Candidate verification unavailable") from None



def native_win11_build() -> int:
    """An unattended Linux/Windows Server invocation is never a Win11 review."""
    if os.name != "nt" or platform.machine().lower() not in ("amd64", "x86_64"):
        raise ReviewHold("A native Windows 11 x64 reviewer workstation is required")
    getter = getattr(sys, "getwindowsversion", None)
    if getter is None:
        raise ReviewHold("Cannot verify Windows workstation version")
    version = getter()
    if (type(version.major) is not int or version.major != 10 or
            type(version.build) is not int or version.build < 22000 or
            getattr(version, "product_type", None) != 1):
        raise ReviewHold("Windows 11 workstation is not independently established")
    return version.build


def main(argv: list[str] | None = None) -> int:
    parser = PrivateReviewParser(description=__doc__)
    parser.add_argument("action", choices=("template", "verify"))
    parser.add_argument("--dist", type=Path, required=True)
    parser.add_argument("--r9-report", type=Path, required=True)
    # Deliberately not argparse-required: missing pins fail with the same
    # redacted HOLD message as other privacy-sensitive custody failures.
    parser.add_argument("--expected-r9-sha256")
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--witnesses", type=Path)
    try:
        # CLI parsing is part of the private HOLD boundary, not an
        # argparse stderr/usage path that can disclose a rejected value.
        args = parser.parse_args(argv)
        report, actual, report_raw = load_custody(
            args.dist, args.r9_report, external_r9_pin(args.expected_r9_sha256))
        template = make_template(report, actual, report_raw)
        if args.action == "template":
            # Do not write candidate directory; never overwrite an existing QA record.
            if args.review.resolve().parent == args.dist.resolve():
                raise ReviewHold("Review record may not live with EXEs")
            with args.review.open("x", encoding="utf-8", newline="\n") as fp:
                json.dump(template, fp, indent=2)
                fp.write("\n")
            print("TEMPLATE CREATED: 46 source-bound private manual checks; NO tests attested")
        else:
            if args.witnesses is None:
                raise ReviewHold("Private witnesses required")
            record = _strict_json(_bytes(args.review, MAX_REPORT_BYTES))
            if record.get("windows11_build") != native_win11_build():
                raise ReviewHold("Reviewer build does not match actual workstation")
            result = validate_review(record, template, args.witnesses)
            print("MANUAL MATRIX: " + json.dumps(result, sort_keys=True))
            if result["status"] != "MANUAL_MATRIX_COMPLETE_UNCERTIFIED":
                return 2
        return 0
    except (ReviewHold, OSError, UnicodeError, ValueError, TypeError, KeyError):
        print(ERROR, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
