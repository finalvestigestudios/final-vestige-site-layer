# Unsent email preview assets

These files illustrate the six standalone email editions for **internal design and copy review**. They are **not** renders produced by the WordPress.com Jetpack newsletter service and **must not** be sent as-is. The real WordPress editor, its notification system, excerpt/full setting, mail footer, unsubscribe controls and sender headers must all be separately verified.

Run from the repository:

```sh
node dispatch/campaign-2026-mind/tools/build_previews.cjs
node dispatch/campaign-2026-mind/tools/build_previews.cjs --check
python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -v
```

The generator uses only built-in Node APIs and creates six `.html`, six `.txt`, plus an offline index `previews/index.html`. No remote pixels, JavaScript, CSS fetches, fonts or client tracking. All product CTA destinations remain visibly blocked. Generic vendor source links were deliberately removed from commercial email bodies; exact merchant pages are documented for evidence review in `OFFER_ALIGNMENT_AUDIT_2026-10-30.md`.

**Release blockers:** real Jetpack end-to-end test email, rendered unsubscribe+valid sender postal address, reconciled confirmed audience, partner-approved email marketing/tracking terms, live reviewed FV warm-up pages, final founder send approval. **No email was sent or scheduled.**
