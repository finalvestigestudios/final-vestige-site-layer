# Dispatch R457 — exact-source QA and release receipt

**Run:** Wednesday 2026-11-18 around 14:38–15:00 Pacific. Owner Issue [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), coordinated [Mind #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), [Focus #129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129), [Revenue #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). Stacked on prior Dispatch [PR #3048](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/3048) at `6f2c1d7fd15c808e3014a4932581369ae02ad96c`. Original master [#175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) current head `d57ccdba3aee8f065e143e101c2945f4f3d01647`; original copy and separate frozen homepage #49 unchanged. Previous native original master suite was documented in R448; **not rerun natively this run**.

## What this incremental sprint actually adds
- A SOURCE-ONLY, native-tested evidence checker: audience inconsistency (without counting unconfirmed as new leads), each issue release gate, email/merchant permissions requiring both an attestation flag and nonempty HTTPS source reference, missing consent/welcome/postal/opt-out/native preview, exact WordPress title/subject check, fail-closed money calculation requiring audited human denominator and an independently claimed complete settlement ledger. It returns only HOLD or HUMAN_REVIEW_ONLY; **never sends or makes any edition release-ready by itself**.
- An aggregate timestamped WordPress snapshot (no subscriber PII), current external merchant and mail permission audit, exact owner pass/fail matrix with proof requests.
- Three substantial *OPTIONAL* email follow-up drafts and six paired HTML/plaintext OFFLINE reviewer specimens. A and B are evidence-first and point to public FV free resources; C is Zen12-only, visibly disclosed, **disabled** pending merchant proof. This is **not** a change to the founder's six-week 4 editorial / 2 commercial pilot, not a new drip-sending system and not substitution of Issue 03/05.
- All six offline specimens carry prominent UNSENT/NOT JETPACK label, use semantic H1, inline email CSS and presentation tables, no remote scripts/imagery, no active merchant earning URL or unapproved buyer guide URL. Source links may be used for offline review only; subscriber-ready appearance is NOT claimed.

## Exact tested source hashes
Local Linux Node 22 native execution `node --test release_gate.test.mjs`: **9/9 passed, 0 failed**, exit 0. Local `git hash-object` exactly matches independently fetched GitHub blob SHA after committing:
- `release_gate.mjs`: `14bcb681e0635104018295b593c6ce367bedf273`
- `release_gate.test.mjs`: `08914af0311ac12d89c30e3f61e7fc46f17dd424`

Cases included invalid aggregates, five-person conflation prevention, edition allocation, insufficient naked booleans, human review non-authorization, unknown revenue, duplicate orders, refund larger than gross and a **SYNTHETIC** calculated settlement. The synthetic test is NOT a transaction, observed revenue or claim of a real payer. A source-reference string is necessary but NOT proof validation; humans must inspect the actual provider evidence.

## Postcommit source-only reviewer specimen QA
All six HTML/plaintext files independently fetched from the isolated GitHub branch; **34/34 static assertions PASS** against committed content. Safety labels, semantic layout, no script/image/merchant-link leakage or unresolved `[[` markers, disabled Zen12 placement, live first-party Focus/Puységur resource URLs. Git blobs:
- A HTML `d0cf0706b17ce407f953bf48671916ff8211a1b0` / text `7329ef04858cee0a27bfafa6d9db52f3d3b96186`
- B HTML `7d803f802ac059b9012d73a9fe6ce527c824491b` / text `516a83691688ce4a03420d31dc786185e99b88b7`
- C HTML `659d260ab382cc58021b4800e7b5c823254cb46f` / text `996927322426d3f09fba89a19e2a172b2131f91a`

Static output checks are **not** real browser, screen-reader, client delivery, inbox, actual link-attribution or Jetpack tests. No actual WordPress draft saved or Preview witnessed. No contact/address exported. No real send or test email. No source-backed real paid sale, refund or human session denominator; 7/30-day revenue is **NOT COMPUTABLE**, not zero.

## Release / compliance gates, all remain HOLD
1. Founder-provided and legally reviewed FV publisher physical postal address in actual rendered emails, plus working opt-out; no Automattic address substitution. See [FTC CAN-SPAM](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business).
2. Non-sending genuine Jetpack email Preview for selected exact WP title/post body and preheader appearance; site current `full` content / `no-reply` mode, default auto-send off, so manual verification needed. [WordPress support](https://wordpress.com/support/newsletter/email-appearance/).
3. Authoritative new, consent-confirmed subscriber and actually delivered welcome/download evidence; provider Stats Subscribers email3/Reader0 versus Stats Followers email0/Reader3, newsletter confirmed3+unconfirmed2 (different universes; never sum). All counts private-safe.
4. Specific verified affiliate partner account approval, EMAIL channel permission, issued earning URL, LIVE Mind-approved guide, claim substantiation, exact current checkout/refunds, adjacent disclosure and actual paid commission reports for 03/05. [Zen12 official page](https://zen12.com/about), [Zen12 promo](https://zen12.com/secret/), [Hypnosis Live FAQ](https://hypnosislive.com/faq).
5. Explicit founder final creative/audience/timing approval for any publication or sending. No campaign-wide scheduling or WordPress settings changes.

**Status:** 13 additive files under `dispatch/r457/`; no original issue rewritten; no WordPress writes, new subscribers, message sends, social posts, live affiliate links, merges, expenses, or homepage changes.
