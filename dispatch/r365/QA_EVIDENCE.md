# Dispatch R365 — exact-source QA evidence and release ledger

**Reviewed:** 2026-11-14 PT. **Founder approval:** draft campaign only. **All six originals:** `HOLD_UNSENT`. **Offer editions 03 and 05:** additionally `HOLD_MERCHANT`. **New alternative 02:** `NOT_ADOPTED`, not an approved copy substitution.

## GitHub provenance and regression

- Master [draft PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) remains at exact head `d57ccdba3aee8f065e143e101c2945f4f3d01647`. Independently fetched all eight relevant original source files from this ref. **8/8 Git blob SHA values matched** the unmodified archived fixture used for native local tests.
- Executed archived original suite in isolated local runtime with command `python -I -m unittest discover -s master/dispatch/campaign-2026-mind/tests -v`: **6/6 PASS** (one real native invocation; executable archive source was checked against the exact master Git blob identities). No subscriber API or merchant API called by suite.
- New branch created from exact [draft PR #2532](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2532) head `2420d2e16dd1ddd3d5624e40767c3a5433bb175f`. **Six** new additive draft files initially committed; the source dossier link formatting was then corrected in a follow-up commit.
- All six newly committed files were re-read from GitHub. An independent 21-check review of their **exact remote content** passed **21/21**: source URLs, one primary CTA, metadata, HTML table semantics, lang/H1, both hard-stop footer tokens in all formats, source claim qualifiers, deliverability and commercial holds, editorial split, no merchant checkout activation, pricing-drift notice and privacy/measurement cautions.
- Separately, the initial publication helper applied **eight V8 integrity checks** (one baseline plus seven adversarial mutations of approval, purchase-link, 4:2 and recipient/preview states); **8/8 passed**. This was in-memory testing; no new native Node suite or browser/Inbox QA is claimed.
- Browser screenshot, screen-reader, true Jetpack preview or received-email tests: **NOT TESTED**. Static HTML is a reviewer rendering, not Jetpack output, and the preheader and legal footer cannot be accepted as native proof.

## Evidence-first editorial change

The OPTIONAL Issue 02, `A sleeping patient. An unresolved claim.`, provides a seven-paragraph historical explanation of Puységur's May 1784 account; differentiates the original reported episode from a modern verifiable experiment; refuses to mistake Franklin's *related* 1784 commission for an exact replication of that encounter; includes a practical three-line evidence exercise. One primary CTA to the existing Puységur archive; four documentary source links, not affiliate offers. HTML, plaintext, Markdown and manifest match on subject, preheader, destination, and hold tokens. No medical, efficacy or supernatural claim is adopted.

## Fresh source and platform checks

- [Harvard 2026 historical analysis](https://cswr.hds.harvard.edu/news/2026/07/13/artificial-somnambulism-and-hypnotism), [Crabtree 2019 scholarly DOI](https://doi.org/10.1002/jhbs.21974), and [1784 digitization inventory](https://www.circee.org/puysegur-memoires-pour-servir-a-l-histoire-du-magnetisme-animal-1784/).
- Official seller [Zen12](https://zen12.com/) claims 12 levels/four listening styles and hour-equivalence (not independent proof). Official [Total Focus](https://hypnosislive.com/mental-skills/total-focus) currently visibly lists 33 min/47 MB, with price displays drifting between fresh retrieved page and search index; **no price inserted in campaign**. Current linked checkout and refund terms for the specific affiliate identity remain unverified.
- Official [Inspire3 affiliate portal](https://affiliates.inspire3.com/) provides general information and login, **not named Final Vestige acceptance, email permission, issued URLs or sales receipts**.
- Live authenticated WordPress newsletter read-only at **2026-11-14 23:37 UTC**: subscriptions enabled; new-post auto-send false; full content; sender name Final Vestige Studios; welcome message points to complete 52-page Focus Fieldbook. Counts: total=3, confirmed=3, unconfirmed=2, not arithmetically additive; sampled five posts never sent due to opted-out flag. Actual inbox-eligible audience cannot be inferred.
- [WordPress Newsletter support](https://wordpress.com/support/newsletter-settings/) explains why WordPress.com follower and direct-email follower labels must not be combined as unique recipients. [Jetpack preview guidance](https://jetpack.com/support/newsletter/) distinguishes a non-sending editor preview from Send test email.
- Actual welcome receipt and PDF guest download, verified Final Vestige publisher address, functional rendered unsubscribe, and authorized genuine native Jetpack preview are **not evidenced**. [FTC guidance](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) governs commercial email requirements.

## Business measurement and owners

**Paid outcome:** no independently reported settled affiliate/FV orders, fees or refunds correlated to independently verified qualified-human sessions; net revenue per 1,000 qualified human sessions = **NOT COMPUTABLE**. No synthetic sales or A/B data. See [conversion handoff](CONVERSION_AND_CONSENT_HANDOFF.md) for OFFER → FUNNEL STEP → BLOCKER → OFFLINE CHANGE → EVIDENCE → OWNER, including a non-deployed deduplicated `confirmed_signup` contract and segregated social/email UTMs.

**Owner handoff:** Mind/Commerce obtains SKU-specific affiliate EMAIL permission, issued earning URLs, approved live buyer guides and checkout/refund verification. Claude/Focus verifies opaque provider-confirmed consent and actual Fieldbook welcome/guest download. Founder/Dispatch verifies native email preview, actual qualifying FV postal footer, functional opt-out, recipient eligibility and final sending approval. Grok creates/posts social; Praxxis QA; no changes to Grok queue, Claude engineering, homepage or frozen #49.

**Non-actions verified for this sprint:** no WordPress writes, subscriber queries/export, subscriber contact, messages or test messages, merchant activation, social posts, scheduled sends, PR merge, deployment, tracking script or expense. This is **source-only, no release authority**.
