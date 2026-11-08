#!/usr/bin/env python3
"""Read-only, fail-closed WordPress custom-plugin backup/scan freshness gate.

Input is a LOCAL, manually sanitized JSON snapshot with keys activity, plugins,
backup, scan, restore, obtained from read-only WordPress connector responses.
Does not contact a site, handle credentials, restore backups, or modify WordPress.
"""
import argparse
import datetime as dt
import json
import sys
import unittest
from pathlib import Path

UTC = dt.timezone.utc


def when(value):
    if not value or not isinstance(value, str):
        raise ValueError("missing timestamp")
    value = value.replace("Z", "+00:00")
    parsed = dt.datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)  # WordPress connector uses UTC
    return parsed.astimezone(UTC)


def plugin_name(entry):
    return " ".join(str(entry.get(k, "")) for k in ("name", "slug", "plugin_file")).lower()


def is_custom_history(entry):
    label = plugin_name(entry)
    return "history" in label or "fv-history-lab" in label


def evaluate(snapshot):
    """Return scoped evidence, never a claim of restored plugin functionality."""
    activities = snapshot.get("activity", [])
    plugins = snapshot.get("plugins", [])
    backup = snapshot.get("backup", {})
    scan = snapshot.get("scan", {})
    restore = snapshot.get("restore", {})
    if not isinstance(activities, list) or not isinstance(plugins, list):
        raise ValueError("activity/plugins must be arrays")
    if not plugins:
        raise ValueError("missing current plugin inventory")
    current = [p for p in plugins if is_custom_history(p)]
    if not current:
        raise ValueError("no scoped custom History Lab plugins in inventory")
    known = {str(p.get("plugin_file", "")).split("/")[0].lower(): p for p in current}
    changed = []
    for a in activities:
        if a.get("group") != "plugin" or a.get("action") not in (
            "installed", "updated", "autoupdated", "activated", "deactivated"):
            continue
        for item in a.get("object", {}).get("plugin", []):
            if not is_custom_history(item):
                continue
            slug = str(item.get("slug", "")).split("/")[0].lower()
            matched = known.get(slug)
            # Inventory can omit an uninstalled retired add-on; do not infer live status.
            changed.append({
                "when": when(a.get("date")),
                "name": item.get("name"),
                "version_at_event": item.get("version"),
                "current_status": matched.get("status") if matched else "not_in_inventory",
                "current_version": matched.get("version") if matched else None,
            })
    changed.sort(key=lambda x: x["when"])
    if not changed:
        return {"state": "HOLD", "reason": "No reliable scoped plugin change event found",
                "backup_freshness": "UNKNOWN", "scan_freshness": "UNKNOWN",
                "restore_rehearsal": "UNVERIFIED", "changes": []}
    latest = changed[-1]["when"]
    info = backup.get("backups", backup)
    last_backup = None
    if (backup.get("state") == "active" and
            info.get("last_attempt_status") == "finished" and
            info.get("last_attempt_failed") is False):
        try:
            last_backup = when(info.get("last_backup_when"))
        except ValueError:
            pass
    back_pass = last_backup is not None and last_backup > latest
    last_scan = scan.get("last_scan") or {}
    scan_end = None
    if scan.get("state") == "idle" and last_scan.get("error") is False:
        try:
            scan_start = when(last_scan.get("started_at"))
            scan_end = scan_start + dt.timedelta(seconds=int(last_scan.get("duration_seconds", 0)))
        except (ValueError, TypeError):
            pass
    scan_pass = scan_end is not None and scan_end > latest
    restored = restore.get("last_restore", {}).get("has_restore_record") is True
    return {
        "state": "PASS_FRESHNESS_ONLY" if back_pass and scan_pass else "HOLD",
        "latest_plugin_change_utc": latest.isoformat(),
        "backup_freshness": "PASS" if back_pass else "HOLD",
        "scan_freshness": "PASS" if scan_pass else "HOLD",
        "last_backup_utc": last_backup.isoformat() if last_backup else None,
        "scan_finished_utc": scan_end.isoformat() if scan_end else None,
        "restore_rehearsal": "RECORD_EXISTS_UNVALIDATED" if restored else "UNVERIFIED",
        "package_provenance": "UNVERIFIED_BY_THIS_GATE",
        "changes": [{**x, "when": x["when"].isoformat()} for x in changed[-8:]],
        "limits": "Fresh backup/scan timestamps do not prove restore, vulnerability-free code, or public-browser behavior."
    }


class GateTests(unittest.TestCase):
    def fixture(self):
        return {
            "plugins": [
                {"name": "Final Vestige History Lab", "version": "0.4.0-rc24",
                 "plugin_file": "final-vestige-history-lab/final-vestige-history-lab", "status": "active"},
                {"name": "Final Vestige History Lab LIVEPASS Full34 Successor Controller",
                 "version": "0.3.1-predeploy-full34-rc24",
                 "plugin_file": "final-vestige-history-livepass-full34-successor/final-vestige-history-livepass-full34", "status": "inactive"}
            ],
            "activity": [
                {"group": "plugin", "action": "installed", "date": "2026-11-08T07:08:48Z",
                 "object": {"plugin": [{"name": "Final Vestige History Lab", "version": "0.4.0-rc24",
                                           "slug": "final-vestige-history-lab/final-vestige-history-lab.php"}]}},
                {"group": "plugin", "action": "installed", "date": "2026-11-08T07:09:14Z",
                 "object": {"plugin": [{"name": "Final Vestige History Lab LIVEPASS Full34 Successor Controller",
                                           "version": "0.3.1-predeploy-full34-rc24",
                                           "slug": "final-vestige-history-livepass-full34-successor/final-vestige-history-livepass-full34.php"}]}}
            ],
            "backup": {"state": "active", "backups": {
                "last_backup_when": "2026-11-08 04:30:02",
                "last_attempt_status": "finished", "last_attempt_failed": False}},
            "scan": {"state": "idle", "last_scan": {"started_at": "2026-11-08T04:30:10+00:00",
                                                      "duration_seconds": 55, "error": False}},
            "restore": {"last_restore": {"has_restore_record": False}},
        }

    def test_actual_current_evidence_is_hold(self):
        result = evaluate(self.fixture())
        self.assertEqual((result["backup_freshness"], result["scan_freshness"]), ("HOLD", "HOLD"))
        self.assertEqual(result["restore_rehearsal"], "UNVERIFIED")

    def test_fresh_backup_and_scan_pass_timestamps_only(self):
        f = self.fixture()
        f["backup"]["backups"]["last_backup_when"] = "2026-11-08T08:20:00Z"
        f["scan"]["last_scan"]["started_at"] = "2026-11-08T08:21:00Z"
        self.assertEqual(evaluate(f)["state"], "PASS_FRESHNESS_ONLY")
        self.assertEqual(evaluate(f)["package_provenance"], "UNVERIFIED_BY_THIS_GATE")

    def test_backup_failure_blocks_even_after_new_timestamp(self):
        f = self.fixture()
        f["backup"]["backups"]["last_backup_when"] = "2026-11-08T08:20:00Z"
        f["backup"]["backups"]["last_attempt_failed"] = True
        self.assertEqual(evaluate(f)["backup_freshness"], "HOLD")

    def test_scan_error_blocks_even_if_newer(self):
        f = self.fixture()
        f["scan"]["last_scan"]["started_at"] = "2026-11-08T08:21:00Z"
        f["scan"]["last_scan"]["error"] = True
        self.assertEqual(evaluate(f)["scan_freshness"], "HOLD")

    def test_unrelated_plugin_does_not_change_gate(self):
        f = self.fixture()
        f["activity"].append({"group": "plugin", "action": "updated", "date": "2026-11-08T12:00:00Z",
                              "object": {"plugin": [{"name": "Akismet", "slug": "akismet/akismet.php"}]}})
        self.assertEqual(evaluate(f)["latest_plugin_change_utc"], "2026-11-08T07:09:14+00:00")

    def test_malformed_inventory_fails_closed(self):
        f = self.fixture()
        f["plugins"] = []
        with self.assertRaisesRegex(ValueError, "missing current"):
            evaluate(f)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        sys.argv.pop(1)
        unittest.main()
    else:
        ap = argparse.ArgumentParser(description=__doc__)
        ap.add_argument("snapshot", type=Path, help="Locally sanitized read-only snapshot.json")
        args = ap.parse_args()
        try:
            result = evaluate(json.loads(args.snapshot.read_text(encoding="utf-8")))
        except (ValueError, TypeError, KeyError, json.JSONDecodeError) as e:
            print(json.dumps({"state": "HOLD", "error": str(e)}))
            sys.exit(2)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["state"] == "PASS_FRESHNESS_ONLY" else 2)
