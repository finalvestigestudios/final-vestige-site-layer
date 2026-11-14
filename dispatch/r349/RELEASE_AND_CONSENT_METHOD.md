# R349 — non-sending source-of-truth verification procedure

**Current live state (authenticated WordPress, 2026-11-14 07:35 UTC):** Newsletter ON, automatic post-notification send OFF, email format FULL, from-name Final Vestige Studios, reply-to NO-REPLY, 52-page Fieldbook link inside welcome-message settings. Recent five published posts: `never_sent_opted_out`. Provider diagnostic `total=3 / confirmed=3 / unconfirmed=2` is **non-additive**; Jetpack stats reports WordPress.com followers=3 and direct email followers=0. There is no evidenced count of three eligible inboxes.

**What the evidence DOES NOT prove:** setting a welcome message ≠ delivery; a 2026-10-25 Gmail *Confirm your subscription* request ≠ a completed confirmation or welcome receipt; free PDF download ≠ signup; follower ≠ eligible subscriber; test HTML ≠ a received email. WordPress documentation separates **Preview email** (in-editor display) from **Send test email** (real recipient). We executed neither in this run.

**Current site routes:** `/dispatch/` explicitly promises investigations/archive email and Fieldbook on confirmation; `/focus/` has an existing Jetpack Subscribe form plus a direct PDF link. They share one existing list. Nothing in the task authorizes publishing new content, importing people, or changing those pages.

### Stepwise release boundary — founder still controls each gate
1. **Partner proof:** Mind / Commerce obtains a named publisher acceptance for FV, explicit **email marketing permission** for each specific product and link format, permitted audiences/claims/creatives, earning URL, documented terms, independently approved live FV warm-up guide. Public affiliate portal/merchant contact address is not sufficient.
2. **Consent truth:** Claude / Focus inspects provider-authoritative subscriber identities and confirmations privately, recording only aggregate deduped consent outcomes in Issue #129. Do not export personal addresses in GitHub/Drive.
3. **Welcome truth:** an independently consented owner-controlled account (only if founder separately authorizes a real test) confirms the actual welcome and Fieldbook PDF; do not count a Gmail confirmation request as this.
4. **Email legal identity:** verify a physical address legally usable by Final Vestige Studios (FTC permits certain qualifying PO boxes or private mailboxes; consult actual guidance); the seller's London address or Automattic's address is not FV's. Inspect Jetpack native markup, functional unsubscribe and commercial disclosure near each intended link in actual received HTML + text.
5. **Native inbox:** Preview email via WordPress editor does not inherently send, but must not create/publish a post. A **Send test email is a real email** requiring explicit founder authorization even if addressed to self. Test mobile, dark mode, screen reader and preheader rendering on evidence, not assumption.
6. **Independent final founder approval** specifying exact manuscript and version, six-edition selection, eligible audience, date/schedule and delivery method must precede any actual email or publishing. Today's tool can only report HOLD even if booleans were later populated.

### Tests / reproducing
Run from repository root:
`node dispatch/r349/test_evidence_release_gate.cjs`
The tests use synthetic data only, do not open network connections, create records, contact subscribers, or send mail. Inputs under `evidence_snapshot.json` are **read-only point-in-time observations, not an immutable regulator-grade audit log**. The module never returns `SEND`. The Python original master suite was independently executed against 8 Git-blob-verified master files, not a newer draft.

All six original newsletter copies remain `HOLD_UNSENT`. Issues 03/05 additionally `HOLD_MERCHANT`. Proposed alternative drafts R340–R348 are NOT_ADOPTED. Four editorial / two reserved commercial issues remain intact.
