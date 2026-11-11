# Dispatch R280 — Apollo fact precision and delivered-email evidence

**DRAFT / UNSENT / NO PRODUCTION WRITE.** Parent PR #2040 at db933efa2362dc5a1815fad3dbeb5982708fd1c6; original campaign PR #175 unmodified; safeguard PR #201 unmodified; frozen homepage PR #49 unmodified.

- `issue04-precision-REVIEW-ONLY.md`: optional source-led surgical Issue 04 manuscript; maintains historical evidence identity and the *one editorial CTA*; **not adopted**.
- `issue04-precision-REVIEW-ONLY.html` and `.txt`: accessible offline review specimens; not actual WordPress newsletter output. They retain deliberate postal/unsubscribe hard-hold tokens.
- `received_email_inspector.py` and `test_received_email_inspector.py`: privacy-minimized read-only Python stdlib MIME structural checks with synthetic fixtures. They cannot authenticate an actual sender, received message, effective opt-out, postal ownership, consent or compliance; release always HOLD.
- `RECEIVED-EMAIL-EVIDENCE-RUNBOOK.md`: real provider preview vs delivered MIME separation and no-send instructions.
- `CONVERSION-AND-CLAIM-GATES.md`: one-offer authorization, exact merchant claim evidence, subscriber and paid-revenue owner plan.
- `QA-R280.md`: test/provenance and limitations.

Reproduction once cloned: `python -m unittest -v dispatch/r280/test_received_email_inspector.py` may require running `cd dispatch/r280 && python -m unittest -v test_received_email_inspector.py` for local relative imports. No real EML should be committed, transferred to GitHub, or printed. The original exact PR #175 immutable test suite independently passed 6/6 natively from byte-identical source in this sprint; R280 synthetic and screenshot QA in the separately linked local package does **not** certify GitHub native CI.

All six **HOLD_UNSENT**. #03/#05 **HOLD_MERCHANT**. Actual eligible audience UNKNOWN. Paid conversions and net-revenue / 1,000 qualified humans NOT COMPUTABLE.