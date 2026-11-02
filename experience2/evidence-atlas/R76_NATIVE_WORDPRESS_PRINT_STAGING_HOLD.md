# Apollo R76 — Native WordPress research-print pagination (STAGING_HOLD)

## Reproduced R74/R75 defect
R74 exact-head WordPress/Assembler PDF had 21 pages. Page 20 contains the
research/source footers plus a generic Assembler example-contact footer; page
21 contains only a pale gray continuation stripe (no words, photos, annotations,
or dark markings). R75 normalized an **offline review copy** to 20 pages but
correctly retained the defective original browser PDF.

## Scoped change
The Apollo integration stylesheet now hides the *WordPress Gutenberg template
footer* **only during printing, only on pages containing the Apollo suite**.
This removes the unrelated example-address footer without changing screen
layout, the original R38 Research Desk, Atlas records, NASA citations, or the
source-bearing internal research footers. No theme files, CMS blocks, WP
settings, homepage branches, or live website are modified.

## New exact-head acceptance
The genuine private WordPress Playground/Assembler test now directly audits
the **unmodified** Chromium PDF *before* R75's normalization. It checks all
six known NASA identifiers and exact URLs using R74 custody checks, rejects
decorative terminal or interior pages, requires the Gutenberg footer's
print-only exclusion and both internal source footers, and renders the final
native print page to a PNG. Five adversarial synthetic-PDF tests cover a gray
orphan, genuine text, non-text diagrams, interior gaps and absent NASA custody.

The pre-existing R75 offline review copy remains generated only for forensic
comparison. Never conflate a normalized copy with a fixed browser print.

## Review and release restrictions
A test passing in private genuine WordPress is not proof of WordPress.com
hosted parity; independent physical-device and NVDA/VoiceOver review, QD,
manual rights verification for all six NASA source images, field CWV, and
founder release approval remain outstanding. Catalog S67-19766 is provisional.
No NASA photographs, unreviewed geographic pins, commercial image permissions,
paid services, or production writes were introduced. **Do not merge/deploy.**
