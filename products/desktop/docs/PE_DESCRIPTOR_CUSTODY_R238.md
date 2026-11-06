# R238 — PE candidate descriptor and error custody (issue #73)

Status: **DRAFT / independent QD + founder approval required. NOT RELEASED.**

## Actual change

The offline release-candidate verifier `products/desktop/release_gate.py` invokes
`pe_image_guard.verify_amd64_pe` for **each of the six distinct Windows x64
images**. Its previous `os.open -> os.fstat -> os.fdopen` chain could leak an
open candidate file descriptor whenever `fstat` or `fdopen` failed before
ownership transferred to the Python stream. On injected OS errors it could also
propagate private candidate paths from `OSError.__str__`.

The R238 patch closes the raw descriptor for **all** failure and interruption
paths before ownership transfer, and wraps ordinary inspection errors in a
fixed `PEFormatError("Cannot inspect candidate file")` without displaying
raw OS messages. Existing explicit `PEFormatError` contract failures are
preserved, including non-regular candidate rejection. KeyboardInterrupt and
SystemExit are re-raised after cleanup. A successfully acquired stream retains
the original parser and context manager; no PE structural acceptance criteria
were relaxed, no executables were run, and no money or premium entitlement
logic was touched.

This change does **not** prove against privileged in-process inspection of
exception context, hostile file replacement during later reads, malware,
Authenticode or actual Win11 functioning. The existing descriptor-first PE
structure check and release gates remain necessary but insufficient for release.

## Reproducible local evidence

On **Linux x86_64, CPython 3.13**, source from the exact prior R237 Git blob
`7d7c8ff484bc360798fbe2d28ad557697b0d3f59` was reconstructed
byte-identically. An initial ten-method probe against the unmodified source
produced **five errors/failures** (three raw path-bearing `OSError`
propagations, two unclosed-descriptor interrupts), with five passes. This
reproduced the failure without any customer files or real Windows executables.

The committed patch `pe_image_guard.py` and the committed new
`test_pe_descriptor_custody_r238.py` were exercised locally after amendment.
They cover fstat permission/I/O errors, fstat and fdopen interrupts,
SystemExit, fdopen OSError and ValueError, expected nonregular input,
failure of initial open, closed FD on malformed input, valid **synthetic**
PE32+ shape, and unchanged source bytes. Fixture data is synthetic.

Run from the repository root (no dependencies beyond Python stdlib):

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_pe_descriptor_custody_r238.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_pe_descriptor_custody_r238.py'
python -m compileall -q products/desktop/pe_image_guard.py products/desktop/tests/test_pe_descriptor_custody_r238.py
```

Observed on the isolated exact-module reproduction: **14/14 PASS normal**,
**14/14 PASS optimized** = **28 method executions**, zero skips;
compileall PASS. Source Git blob SHA `43ecafe1e33cc6ac3ef629dfe2421bb47cba79f0`;
new test Git blob SHA `620d8c97ba3e27d0d3bba0ad4f1a522f90978aca`.
These blobs are byte-identical to the locally executed files. This is
**not a full checkout**, end-to-end six-app regression, Windows package smoke,
CI pass or Defender result. Hosted Ubuntu and Windows now require both modes
before any packaging step.

## Release hard holds / next acceptance

GitHub Actions has repeatedly failed before test steps or runner allocation,
including R237 run #42258084916. CI infrastructure cause is still unconfirmed.
Repository owner must inspect the run banner, Actions billing/spending, account
workflow policy, and hosted runner scheduling, restore execution, then rerun
the **unchanged PR head**. Do not infer a passing build from workflow presence.

Next high-impact step: execute the inherited full six-app regressions and
R237 publisher integration in a real checkout, build all six genuine Windows
x64 executables privately, checksum, Defender/EDR-scan, smoke on Win11,
assess keyboard/NVDA and 100/200/400% DPI, validate protected Pro distribution
and obtain independent QD review plus founder approval. No WordPress/site
publication, merge, public EXEs, real customer data or unrestricted premium
downloads are authorized by this sprint.
