# Renewal Radar 0.2.0 — local renewal tracker

**Development preview, not a validated Windows release.** This application keeps
renewal records in local SQLite storage. It does **not** run in the background
or send notifications; export an .ics calendar and import it into a calendar
application if you want reminders. Calendar imports may not automatically
sync later changes; re-import with care to avoid duplicates.

## What it does

Track warranties, licenses, certification dates, insurance renewals, maintenance
obligations, or contract deadlines; repeat monthly or yearly; display next due
dates; export all items to an RFC 5545-compatible calendar. No account, cloud,
network access, or telemetry is required.

Run on Python 3.11+:

```sh
python renewal_radar.py                     # Desktop GUI
python renewal_radar.py --help
python renewal_radar.py --db renewals.sqlite3 add "License renewal" 2027-05-04 --cadence yearly --remind-days 30
python renewal_radar.py --db renewals.sqlite3 list
python renewal_radar.py --db renewals.sqlite3 import examples/renewals.csv
python renewal_radar.py --db renewals.sqlite3 export renewals-new.ics
```

The `--db` option precedes the command. By default, Windows data is saved
under `%APPDATA%\Final Vestige Studios\Renewal Radar\renewals.sqlite3`.
Back up that file while the application is closed. No automatic cloud backup.

## Safe bulk import

CSV must be UTF-8 or UTF-8 with BOM. Required columns: `title,due`.
Optional: `category,cadence,remind_days,notes` (no additional columns).
Dates use `YYYY-MM-DD`; cadence is `none`, `monthly`, or `yearly`;
reminder days range from 0 to 3650. Title limit: 200 characters; category:
120; notes: 2000. Max CSV size: 8 MiB; max 20,000 records per import.

**All-or-nothing:** No records are added if any row is invalid, repeated
within the CSV, or identical to an existing local record. The import checks
that its source has not changed during validation. Correct the reported
physical CSV row and retry; partial imports are not performed. On database
write failure, the import transaction is rolled back. This is intentional
to avoid surprising duplicate or partial reminders.

## Non-destructive calendar export

The application will **never overwrite** an existing file, including an
existing calendar or database selected accidentally. Choose a fresh
`.ics` filename each time. Exports contain renewal names, categories and
notes; these may be sensitive, so store/share the exported calendar carefully.
A calendar viewer, not Renewal Radar, is responsible for showing reminders.

Monthly events on the 31st skip months without 31 days; leap-day yearly events
skip non-leap years (RFC 5545 recurrence semantics). For obligations requiring
last-day-of-month adjustment, add distinct dates or use a suitable calendar.

## Development checks

Run from this directory:

```sh
python -m unittest discover -s . -p 'test_*.py' -v
```

The current release checklist is in `WINDOWS_ACCEPTANCE.md`. No unsigned
private CI artifact is a public release. A Windows installer must pass smoke
and real GUI acceptance tests, malware screening, version/checksum checks and
code signing before a public download is enabled.
