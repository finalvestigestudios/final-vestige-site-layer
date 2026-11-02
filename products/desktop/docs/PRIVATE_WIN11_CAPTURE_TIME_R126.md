# Labs R126 — Windows 11 private per-check capture-time provenance

**DRAFT / RELEASE HOLD** · Issue #73 · stacked on R125 draft PR #541; no production or release changes.

## Defect and implemented contract

The R122 recorder previously copied the review matrix's one-time
`observed_utc` into every human PASS/FAIL note. Checks recorded hours or days
apart would carry exactly the same timestamp and could mislead an auditor into
believing they happened simultaneously. R126 fixes this provenance defect.

Each **new** locally recorded check uses witness schema
`fv-labs-win11-check-witness-r126-v2`, retains the review's original
`observed_utc` as an immutable session anchor and adds `recorded_utc`
from the recording workstation's UTC clock. The validator rejects missing,
unexpected, non-string or malformed UTC timestamps; impossible calendar
dates; capture before the declared session anchor; and a recorded clock more
than one minute ahead of the verification clock. Both writer and read-only
reviewer verifier use the same validator. The SHA-256 of each complete witness
envelope remains bound to its exact application/check in the local matrix.

**Important distinction:** `recorded_utc` means *this program recorded
the human's testimony at this workstation time*. It does NOT prove when
NVDA, keyboard, contrast, scaling or antivirus testing physically occurred,
that the machine's clock was authenticated or that the reviewer is independent.
The original review-session timestamp retains its 30-day freshness window.

Old `fv-labs-win11-check-witness-r110-v1` records stay verifiable as
legacy testimony without an invented per-check timestamp. Do **not** hand-edit
or migrate original v1 evidence to v2; preserve it for investigation. New
recordings use v2 only. Treat historical v1 notes' shared timestamp as a
review-session claim, never as individual capture provenance.

## Controlled private acceptance workflow

1. Arrange approved custody of all **six actual Windows x64 candidate EXEs**
   (four free, two premium) and obtain the R9 evidence SHA-256 from a truly
   independent authenticated channel. A locally matching digest alone cannot
   establish independent provenance.
2. On a physical Windows 11 x64 workstation use the private R109 matrix,
   R122 one-check witness tool and R123 read-only progress utility. Complete
   each physical action, then write a specific observation before invoking the
   one-check recorder. Never invent, backdate or automate a human conclusion.
3. Preserve candidate checksums, review matrix and witness files under
   reviewer-only filesystem permissions. On any timestamp or evidence failure,
   **HOLD**, preserve files and investigate with independent QD.
4. Separately complete all 46 human accessibility checks, actual Defender/EDR
   and remediation-history examination, code signing, authenticated premium
   distribution, independent QD review and founder authorization.

Sixteen synthetic adversarial and compatibility methods in normal and Python
`-OO` modes are mandatory on Linux and Windows CI. These tests do not create
physical Windows 11 testimony, verify the PC clock independently or publish
an EXE. Failure keeps the release on **HOLD**. Local customer financial data,
premium candidate executables and reviewer observations must never enter
CI artifacts, logs or unrestricted downloads.
