# FVF-8 — Return Trail R1

## Repair scope

R1 closes the independent-QD P1 retention defect in the original Return Trail artifact. The UI promises that a saved place is kept only in this browser for up to 30 days, so expiry must be destructive rather than an in-memory filter.

On every storage read, R1 canonicalizes the stored list, rejects malformed, unsafe, future-dated and expired records, removes duplicate paths, enforces the three-record cap, and immediately writes the canonical surviving set back to `localStorage`. If nothing survives, the key is removed. An entry exactly 30 days old is expired.

## State-safety hardening

R1 also brings the feature under the current nondestructive DOM-state rule. It no longer writes marker datasets/classes to publisher nodes. Resume scrolling happens before any target mutation. When a previously non-focusable target needs temporary `tabindex="-1"`, that value is owned by Return Trail only for the focus transaction and is restored on blur or failure. Publisher-owned `tabindex`, IDs, classes, and a pre-existing `fv-return-trail-flash` token are preserved. When Return Trail temporarily adds the flash class to an element that originally had no `class` attribute, cleanup restores the attribute to absent.

The one-click `#fv-return-trail` fragment remains a governed transport marker and is removed from the address bar after it is consumed. Return Trail does not create publisher-node IDs.

## Trust and privacy

- Storage key remains `fvReturnTrailV1` so already-saved trails receive the destructive R1 cleanup rather than being orphaned.
- Stored identity is a query-free, fragment-free same-origin pathname only.
- At most three records survive canonicalization.
- No cookies, sessionStorage, IndexedDB, analytics, external API, fetch/XHR/WebSocket/sendBeacon, iframe, or third-party script is introduced.
- `Forget` remains explicit and immediate when browser storage is writable.
- Storage failure disables further persistence for the page and never blocks reading.

## Qualification

On single longform, R1 requires one and only one canonical `h2#sources.fv-source-heading` with no competing `#sources`/`.fv-source-heading` marker, at least 12 narrative paragraphs, 3,000 narrative characters, and at least 10 story markers before Sources. Landing resume remains bounded to Home, Blog, Archive and Investigations.

## Exact candidate identity

- Base branch: `production`
- Base production at branch creation: `3f7841a7c671f9e8e955b417480d853ad0a0a948`
- Payload: `payloads/return-trail-wp-block-r1.txt`
- Payload bytes: **11597**
- Payload SHA-256: **`9f93b6cf024495217d5ebffa9989f28cc8671aeec3fb903744b78c9e4151545d`**
- Verifier: `tests/verify_return_trail_r1.py`
- Workflow: `.github/workflows/return-trail-r1-ci.yml`

## Adversarial browser contract

The exact-payload browser suite seeds real browser `localStorage` and verifies:

1. mixed valid + expired + unsafe records are physically rewritten to only the valid rows;
2. an all-expired set physically removes the storage key;
3. an article read purges an expired sibling while preserving the current valid record;
4. resume from a target with absent `tabindex`/`class` restores both to absent after focus/highlight cleanup;
5. pre-owned `tabindex="-7"`, publisher class and pre-owned flash class survive;
6. repeat resume does not drift state;
7. ambiguous Sources boundaries fail closed.

Static verification locks exact payload bytes/hash, JavaScript syntax, privacy/no-network boundaries, TTL/count/path constraints, canonical Sources gating and state-ownership logic.

## Governance boundary

This is a source/build repair candidate only. CI success is evidence, not QD approval and not merge/deploy authority. Independent QD must review the exact frozen PR head and successful exact-head CI. Any payload/test/workflow/contract change invalidates the identity.

If QD PASS requires an executable Site Layer integration, rebuild from then-current `production`, freeze a new executable SHA/package, run fresh feature and repository CI, and return that new identity for fresh independent QD before the existing FAST APPROVAL → Chief of Staff → FVS Execution Dispatch path may act. Live destination readback remains mandatory before `IMPLEMENTED + VERIFIED`.
