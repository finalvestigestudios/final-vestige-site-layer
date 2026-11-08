# Native delivery proof — R21 isolated addition

No senders, mailboxes, subscriber lists, mailing-address values, merchant URLs or live WordPress content are edited here. `check_received_mime.py` is a standard-library-only, **offline** observer for an `.eml` file **only if the founder independently authorizes obtaining that message**. All outputs remain release **HOLD**.

Run the **synthetic-only tests** from the campaign root:

```sh
python -m unittest discover -s native-delivery-proof-r21/tests -v
```

Run the pre-existing **campaign** tests from repository root:

```sh
python -m unittest discover -s dispatch/campaign-2026-mind/tests -v
node dispatch/campaign-2026-mind/tools/build_previews.cjs --check
```

See [RECEIVED_EMAIL_EVIDENCE_RUNBOOK.md](RECEIVED_EMAIL_EVIDENCE_RUNBOOK.md) for exact safe handling, privacy limitations, official seller/FTC/WordPress sources and all missing final approvals. The reporter intentionally never returns READY; a positive MIME check does **not** certify mail send permission, valid opt-out, or legal compliance. **Do not add `.eml` samples or private business address files to this repository.**
