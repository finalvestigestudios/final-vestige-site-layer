# Final Vestige — Focus PDF provenance guard (offline)

This isolated QA tool checks whether WordPress media caption/description SHA-256 claims are consistent with a known archived PDF's fingerprint and the size reported for the hosted asset. It **never connects to the website or modifies anything**.

## New evidence, October 31, 2026

WordPress media **1737** reports **599,946 bytes**, but its caption and description both state SHA-256 **`8d1a0153f54ce10adf0b1a268a7f3d2d6d636dd87058511ba59e5a404064f8f4`**. That exact digest belongs to a separately verified archived **574,817-byte** 52-page reference PDF. The newer hosted PDF might be a valid different edition; actual hosted bytes were not fetched. This is a **CMS metadata provenance inconsistency**, not proof that a visitor's downloaded PDF is corrupted or that the media caption visibly appears on the landing page.

## Local use

```bash
python3 -m unittest discover -s qa/lead_magnet_provenance -p 'test_*.py' -v
python3 -m py_compile qa/lead_magnet_provenance/provenance_guard.py
python3 qa/lead_magnet_provenance/provenance_guard.py --media /private/sanitized_media_1737.json --reference /private/archived_reference.pdf
# Optionally, after independently obtaining real hosted bytes:
python3 qa/lead_magnet_provenance/provenance_guard.py --media /private/sanitized_media_1737.json --reference /private/archived_reference.pdf --hosted /private/downloaded_public_pdf.pdf
```

The sanitized JSON should include only `id`, `source_url`, `media_details.filesize`, `caption`, `description`. Never commit the PDFs, credentials, private metadata, visitor data, or downloaded HTML.

Exit **1 FAIL** means a definite metadata contradiction; **2 HOLD** means provenance/bytes could not be checked fully; **0 PASS_LOCAL_BYTES** means the locally supplied bytes, recorded size and digest claim agree, **not** that the public site, PDF pagination, email journey, publisher approval, or external HTTP has been verified. The guard caps input sizes, checks first-party HTTPS PDF metadata, and uses only Python standard-library functions.

## Release boundary

Keep existing Focus, Dispatch, homepage, navigation, subscriber list, and retired water-draft states unchanged. Do not modify WordPress media from QA; first independently download the actual hosted 599,946-byte PDF, verify bytes and 52-page content, identify the publisher-approved release, then coordinate any corrected caption/description with Claude and QD. Existing draft PR #133 covers bounded public HTTP/PDF GET and PR #282 covers WordPress-rendered inline JavaScript. This PR solely addresses **PDF metadata provenance** and cannot replace either gate.
