# Packet Preflight — User guide (development preview)

**Status:** offline Python prototype. No public signed installer or approved download yet.

Packet Preflight checks **file names, folder locations, sizes and attachment counts**
against a checklist *you* define. It can discover an absent application, unexpectedly
nested file, oversized packet, overlapping requirements and a scan that could not
inspect every file. It **does not** open PDF/Word contents, certify validity,
provide legal advice, evaluate eligibility or guarantee acceptance.

## Quick start

From the repository checkout, install Python 3.11 or newer and open
desktop-software/packet-preflight/packet_preflight.py for the desktop GUI:

    python desktop-software/packet-preflight/packet_preflight.py

1. Create your own JSON checklist using the **Create sample checklist** button
   (or copy samples/fictional-grant-packet.json).
2. Modify rules to match the *actual* requirements of your intended recipient.
   No checklist in this repository is official.
3. Choose a folder containing only the planned submission packet.
4. Run preflight. Investigate every CHECK result and warning.
5. Save a new HTML report **outside** the packet folder. If files or checklist
   have changed, rerun analysis first. Existing reports are never overwritten.

The program does not connect to accounts or upload data.

## Rules reference

    {
      "title": "My submission requirements — review against official instructions",
      "forbid_unmatched": true,
      "max_total_size_mb": 25,
      "rules": [
        {
          "name": "Signed application",
          "pattern": "application*.pdf",
          "minimum": 1,
          "maximum": 1,
          "max_size_mb": 10,
          "extensions": [".pdf"],
          "allow_empty": false
        },
        {
          "name": "Budget",
          "pattern": "budget*.xlsx",
          "minimum": 1,
          "maximum": 1
        },
        {
          "name": "Supporting documents",
          "pattern": "supporting/**",
          "minimum": 0
        }
      ]
    }

All file sizes use MiB (1 MiB = 1,048,576 bytes); limits are inclusive.
Minimum defaults to 1; maximum and max_size_mb are optional.
Allow_empty defaults to false. Forbid_unmatched defaults to false, so
an extra file is listed but not itself an issue unless you opt in.
Max_total_size_mb applies to the entire scanned folder, including files
that did not match a rule.

**Glob semantics matter:** *.pdf matches PDFs at the selected folder root,
NOT PDFs in subfolders. supporting/* matches direct children only;
supporting/** matches files at all depths inside that folder.
**/*.pdf matches PDFs anywhere, including the root. Matching is
case-insensitive to approximate ordinary Windows filenames.

Each file should ordinarily match a single rule. If a file satisfies two
rules, the tool reports **OVERLAPPING_RULES**, so a generic rule cannot
silently double-count required evidence.

## Example command-line usage

Run from the repository root (paths are illustrative):

    python desktop-software/packet-preflight/packet_preflight.py "C:\Packets\Submission" --rules "C:\Checklists\submission.json"

Save a new HTML report outside the scanned packet:

    python desktop-software/packet-preflight/packet_preflight.py "C:\Packets\Submission" --rules "C:\Checklists\submission.json" --report "C:\Reports\submission-review.html"

Create a sample checklist without overwriting an existing file:

    python desktop-software/packet-preflight/packet_preflight.py --sample "C:\Checklists\new-checklist.json"

Exit code **0** means no configured metadata issues, **1** means issues
were found, and **2** means the scan, inputs, or output operation failed.
Neither code 0 nor a CHECK-free report proves that documents are valid.

## Understanding the report

- TOO_FEW / TOO_MANY: attachment count is outside the rule bounds.
- EMPTY / OVERSIZE / WRONG_EXTENSION: a matched file violates metadata limits.
- TOTAL_OVERSIZE: the sum of sizes exceeds the optional packet cap.
- UNMATCHED_FILE: a nonmatching file exists and forbid_unmatched is enabled.
- OVERLAPPING_RULES: a file matches multiple rules and needs manual review.
- SCAN_ERROR: a file/folder was unreadable, was a symbolic link, or a
  Windows filename collision could make copying unreliable.

Skipped symbolic links and directory enumeration errors prevent PASS.
The report includes a SHA-256 digest of the checklist and a SHA-256
**metadata snapshot** based on paths, sizes and modification times.
The latter is **not a cryptographic hash of document contents**. It helps
detect ordinary changes between analysis and export but cannot detect
intentional timestamp forgery or validate document content.

## Privacy and file safety

The scanner does not open underlying document contents. It reads only
checklist JSON and filesystem metadata. It does not follow symlinks.
All reports and example checklists use exclusive creation: you must choose
a new destination, and reports cannot be placed inside the scanned folder.
The UI checks for changed inputs immediately before report export.
The CLI rescans before export for the same reason.

## Pre-release QA still required

Full regression suite, packaged Windows executable behavior, GUI accessibility,
clean-machine installation/uninstallation, antimalware scans, independent smoke
testing, checksum verification and code signing are pending.
Do not distribute a development artifact as a public download.
