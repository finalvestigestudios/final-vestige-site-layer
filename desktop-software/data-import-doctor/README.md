# Data Import Doctor — offline CSV preflight

**Free Windows utility · development build 0.2.0 · not yet a released download**

Check CSV exports **before** importing into accounting, scheduling, inventory,
grant or CRM systems. The app runs locally using Python's standard library.
It does not transmit CSVs, upload data, modify source files, or require an
account. The GUI is a Tkinter desktop program; a command-line mode supports
repeatable checks and CI scripts.

## What it actually checks

- Missing required columns or required cells, ambiguous/blank headers.
- Mismatched column counts, malformed CSV quoting, empty/header-only inputs.
- Repeated keys (case-insensitive Unicode-aware matches), including correct
  physical-line references when CSV cells contain multiple lines.
- Configured types: **integer, finite decimal, ISO date, boolean, text**.
- Allowed values for specified columns.
- Source and rule-file **SHA-256 fingerprints**; refuses to export a report
  after source or rules change.
- Limits: source 80 MiB, rules 1 MiB, 250,000 records, field size 1,000,000
  characters, and 250 displayed issue examples. Counts include all issues.
- Results **PASS**, **ISSUES**, or **INCOMPLETE**. Malformed, ambiguous,
  truncated and empty input cannot report PASS.

## Important limitations

**PASS means only that the checks you configured did not find an issue.**
It does not guarantee another system will accept the import. Without a JSON
schema, the utility primarily checks CSV structural integrity; it cannot
know which columns or values a destination system requires. It does not
parse Excel .xlsx files, connect to external systems, or repair documents.

The CSV reader supports UTF-8 (including BOM); detects comma, semicolon,
tab and pipe separators heuristically. Confirm the detected delimiter in
the report, especially for unusually small files. Date is exactly
`YYYY-MM-DD`; decimal values use a period as decimal separator, with
optional properly grouped commas (e.g., `1,234.50`). Blank optional values
are permitted; list a column in `required_columns` to forbid blanks.

## Quick start (source checkout)

Requirements: **Python 3.11 or newer**.

From the repository root:

```sh
python desktop-software/data-import-doctor/data_import_doctor.py
```

This opens the Windows/desktop graphical interface, where you choose the CSV
and optionally a JSON rules file. Analysis is nonblocking, and reports can
be saved as JSON only after the source and rules are rechecked.

For terminal usage:

```sh
python desktop-software/data-import-doctor/data_import_doctor.py examples/sample-import.csv --schema examples/sample-schema.json --report diagnostic.json
```

For the command above, first change into
`desktop-software/data-import-doctor` so the `examples/` paths resolve.

**CLI exit codes:** 0 = structural/rule PASS; 1 = issues found;
2 = incomplete review or operational error. When `--report` is used, the
destination must not already exist, and may not be the input or schema path.
Exports are intentionally *non-destructive*. Reports are plain JSON.

## Build a schema

Make a UTF-8 JSON document containing only the options below:

```json
{
  "required_columns": ["invoice_id", "amount", "date", "status"],
  "keys": ["invoice_id"],
  "types": {"amount": "decimal", "date": "date"},
  "allowed_values": {"status": ["open", "closed", "paid", "void"]}
}
```

The names must exactly match trimmed CSV header names. Unknown schema
options, duplicate JSON properties, unsupported types, and contradictory
rules cause explicit errors rather than silent fallback. The example files
in `examples/` intentionally contain four issues: a duplicate invoice
identifier, a nonfinite amount, an invalid calendar date and an unknown
status. The expected issue counts are:

```json
{"duplicate_key": 1, "invalid_allowed_value": 1, "invalid_type": 2}
```

## Developer acceptance tests

Run existing and new tests together:

```sh
python -m unittest discover -s desktop-software/data-import-doctor -p "test_*.py" -v
```

Build workflow:
`.github/workflows/free-utilities-windows.yml`, using PyInstaller and
Inno Setup. A build recipe is **not** a validated/signed Windows installer.
Do not publish binaries before Windows CI, first-run GUI verification,
uninstall/reinstall, security checks, checksums and signing pass.

## Privacy and report handling

Analysis takes place on the selected machine. JSON reports contain the
source filename, hashes, header names, line references and a *limited*
number of diagnostic messages. Inspect reports before sharing: column
names and invalid values can still be sensitive in your context.
Store your own copies of the originals; this tool is not a backup utility.
