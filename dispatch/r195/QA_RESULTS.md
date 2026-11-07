# R195 evidence QA

**25/25 passed** in V8 source-level execution directly against the generated text used to create the GitHub files. These checks are not native Node, browser screenshot, WordPress received-email or live merchant testing; all data fixtures are synthetic. Native Python original PR #175 suite separately executed this run on 2026-11-07: **6/6 passed**, against the previously reconstructed Git-blob-certified source (master PR head unchanged d57ccdba3aee8f065e143e101c2945f4f3d01647); not a full Git clone.

- initial_hold: PASS
- commercial_03_email_rights: PASS
- commercial_05_guide: PASS
- cannot_auto_send: PASS
- fake_url_rejected: PASS
- reader_rejected: PASS
- unconfirmed_rejected: PASS
- consent_out_rejected: PASS
- synthetic_confirmed: PASS
- duplicate_rejected: PASS
- private_id_not_emitted: PASS
- absent_orders_not_zero: PASS
- complete_zero_requires_attestation: PASS
- synthetic_net_kpi: PASS
- subject_parity: PASS
- preheader_parity: PASS
- single_editorial_cta: PASS
- three_primary_sources: PASS
- no_merchant_url: PASS
- no_tracking_url: PASS
- footer_hold_html: PASS
- html_accessibility_markup: PASS
- snapshot_nonadditive: PASS
- unknown_not_zero: PASS
- substantive_copy: PASS

Static HTML is UNSENT and contains no scripts or external graphics. Source/preheader/CTA/footer checks passed; mobile Chromium, real native Jetpack rendering and real opt-out remain **UNVERIFIED**. The new /focus/ client-side querystring proof failure is based on authenticated source inspection only; no real form or email submitted.
