# R329 — exact committed-source native execution evidence

**Verification date:** November 13, 2026, same isolated non-sending sprint. All source is additive in `dispatch/r329/` and does not affect original #175 / prior R328 #2337 assets.

## Independent source identities
The GitHub connector read R329's committed `receipt_guard.cjs` blob SHA `5b329163753adf30cc682a3b85d2b4cdd0b1e1b8` and `receipt_guard.test.cjs` blob SHA `ac530965435d499b902e9c77dba9d5af30bd7a4c`. Both files were reconstructed in the independent native filesystem; running `git hash-object` returned **exactly the same two SHA values**, byte-for-byte, before testing. No modified content was used in the native run.

## Executed tests
| Runtime | Exact input source | Result |
| --- | --- | --- |
| Python 3.13.5 `python -m unittest discover ...` | Original master #175 manifest, six issues, test (archived provenance with four independently rechecked SHA values from live original PR head) | **6/6 PASS**, 0.001 sec |
| Isolated V8/CommonJS test shim | Exact committed R329 source and tests freshly fetched from GitHub, following correction of one mistaken test expectation | **23/23 PASS**, 0 fail |
| Node v22.16.0 `node --test dispatch/r329/receipt_guard.test.cjs` | Two bytes-identical GitHub files independently reconstructed and SHA matched | **23/23 PASS**, 0 fail, 0 skip; 106.925741 ms reported |

Cases include absence of independent postal verification, missing final rendered footer, false unsubscribe header/body, invalid sender/subject, unverified welcome, nonexistent consent proof, disabled placeholders, mailto-only vs one-click, no leaked PII, false sales signals, and hard HOLD even for an otherwise all-attested synthetic message.

## Boundaries
- Synthetic MIME is `example.invalid`, not a real person or actual received Final Vestige email.
- Passing the parser does **not** establish genuine provider rendering, valid business mailing address, functionality of the unsubscribe endpoint, actual delivery, welcome attachment opening, subscriber eligibility, affiliate authorization or legal compliance.
- The `inspectReceived` function intentionally **never emits a release-ready/sent state**; every output stays `HOLD_UNSENT`.
- No live WordPress update, email, test send, list export, merchant link or paid tracking occurred.
- Real net commission and unique qualified human session denominator remain absent; **net revenue / 1,000 qualified humans is NOT COMPUTABLE**.

Proof artifacts: native run log `r329_native_node.log`, original Python log `original_master_py.log`, GitHub committed source SHAs above. Logs are benign synthetic QA only and may be shared separately, not with real MIME.
