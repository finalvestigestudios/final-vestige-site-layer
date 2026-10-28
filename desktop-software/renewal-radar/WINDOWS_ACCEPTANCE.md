# Renewal Radar 0.2.0 — Windows acceptance checklist

Status: **NOT EXECUTED**. A passing unit test alone is not sufficient.

## Packaging and installation

- [ ] GitHub Windows job starts and passes all Python unit tests.
- [ ] Bundle `renewal_radar.py`, `renewal_safety.py`, `ical_utils.py` into the
      named `RenewalRadar.exe`. Verify PyInstaller includes sibling modules.
- [ ] Inno Setup builds `RenewalRadar-Setup-0.2.0-win64.exe`.
- [ ] Scan installer; capture signature, hash, size and reproducible CI provenance.
- [ ] Verify code signing and Windows SmartScreen experience.
- [ ] Run standard/silent installation and verify Start menu launch.
- [ ] Run uninstallation and reinstall; preserve user data intentionally.
- [ ] Test on clean Windows 11 x64 and Windows 10 x64 as supported.

## Functional UAT (use fictional data)

- [ ] Launch GUI without Python installed; display and save a renewal.
- [ ] Add a due-today, overdue one-time, leap-day yearly and day-31 monthly item.
- [ ] Verify displayed days-to-next and recurrence semantics.
- [ ] Import `examples/renewals.csv` and verify all entries appear.
- [ ] Re-import same CSV: zero new entries and clear duplicate warning.
- [ ] Import one valid and one malformed line: **zero** new entries.
- [ ] Import multiline quoted fields: error row reports physical line.
- [ ] Import repeated/ambiguous headers, extra fields, malformed quoting,
      oversized file, invalid date, negative reminder and invalid cadence:
      reject without database changes.
- [ ] Export a new .ics; verify calendar app imports titles, reminders, long
      Unicode text, repeated events and date boundaries.
- [ ] Export to an existing .ics: refusal, bytes remain identical.
- [ ] Try exporting to active SQLite .db: refusal, all records intact.
- [ ] Simulate DB write failure: zero partial rows.
- [ ] Restart and verify local SQLite data persisted and is still readable.
- [ ] Inspect app traffic: core workflow requires no network.
- [ ] Verify original CSV inputs are unchanged.

## Commercial release gate

- [ ] End-user documentation and actual screenshots validated.
- [ ] Versioned installer, SHA-256 checksum and release notes available.
- [ ] Installer checksums verified after downloading through finalvestige.com.
- [ ] Accessibility, DPI scaling, keyboard navigation and error states reviewed.
- [ ] Public page offers a download only after all critical checks pass.
