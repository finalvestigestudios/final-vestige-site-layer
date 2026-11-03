# R80 — Jetpack excerpt sensitivity and editorial conversion audit

Status: **REVIEW ONLY / HOLD_UNSENT**. No WordPress posts or subscriber sends. Master campaign PR #175, hard-stop gate PR #201, current stack PR #710 and Issue #174 are authoritative. These optional reviews do not replace original copy.

## The real transport question

Authenticated Jetpack config at 2026-11-03 02:29 UTC: `email_content_format=excerpt`, `email_new_posts_by_default=false`, `recent_sends=[]`. WordPress's current support describes approximately **55 words** in an unspecified excerpt fallback; Jetpack's separate help describes **350 characters** when a custom excerpt is not defined. These may represent different implementations or revisions. **Do not choose one as fact for this site without a native preview, and do not claim that a Markdown PROPOSED CUSTOM EXCERPT has been configured on WordPress.** Links: https://wordpress.com/support/newsletter-settings/ and https://jetpack.com/support/newsletter/customize-the-newsletter-experience/ . A custom post excerpt is described as replacing the fallback, but the rendering (including any automatic read-more CTA, footer and preheader) has not been observed.

### Side-by-side *simulations* (NOT delivery results)

#### 01-the-conversation-continued.md — The person changed. The conversation went on.

**Author-suggested custom excerpt** (48 words):

> In a 1998 sidewalk experiment, a conversation continued even after the person asking for directions was replaced. That is not proof that your memory is unreliable in every situation. It is a reason to ask what any witness could actually notice. Follow the evidence before accepting the story.

**Simulated 55-word excerpt if WordPress falls back to opening body:**

> A stranger stops you to ask for directions. While you answer, two workers carry a door between you. When the door has passed, the person who asked the question isn't the same person. Would you notice? In an experiment reported by Daniel Simons and Daniel Levin in 1998, a conversation on a college campus was

**Simulated 350-character excerpt if WordPress falls back to opening body:**

> A stranger stops you to ask for directions. While you answer, two workers carry a door between you. When the door has passed, the person who asked the question isn't the same person.

Would you notice?

In an experiment reported by Daniel Simons and Daniel Levin in 1998, a conversation on a college campus was interrupted by a door being carried thr

**Editorial check:** neither fallback is a substitute for entering the proposed custom excerpt in the native post editor. Even if a rendering resembles the simulation, the subject/preheader, footer, unsubscribe and display in actual clients remain unverified. No promotional claims or earning links appear in this editorial issue.

#### 02-the-letter-and-the-witness.md — A sleeping witness, a letter, and a 1784 puzzle

**Author-suggested custom excerpt** (46 words):

> On May 4, 1784, the Marquis de Puységur said he observed an unusual state in a young man he was treating. In a letter dated May 8, he tried to describe it. His account survives. That makes it a valuable historical source, not a verified explanation.

**Simulated 55-word excerpt if WordPress falls back to opening body:**

> On May 4, 1784, in Buzancy, an aristocrat experimenting with animal magnetism described something he had not expected. A young man later identified by historians as Victor Race appeared to enter a quiet, responsive state rather than the crisis-like reactions associated with some of Franz Mesmer's practices. We know this first as **Puységur's account**. The

**Simulated 350-character excerpt if WordPress falls back to opening body:**

> On May 4, 1784, in Buzancy, an aristocrat experimenting with animal magnetism described something he had not expected. A young man later identified by historians as Victor Race appeared to enter a quiet, responsive state rather than the crisis-like reactions associated with some of Franz Mesmer's practices.

We know this first as **Puységur's accou

**Editorial check:** neither fallback is a substitute for entering the proposed custom excerpt in the native post editor. Even if a rendering resembles the simulation, the subject/preheader, footer, unsubscribe and display in actual clients remain unverified. No promotional claims or earning links appear in this editorial issue.

#### 06-the-boring-days.md — Your focus log should include the boring days

**Author-suggested custom excerpt** (48 words):

> The most useful line in an attention log may be “nothing changed.” A spectacular success story is hard to check. Seven ordinary observations, including missed days and interruptions, give you something better: a record you can inspect. Here is a simple way to make one without buying anything.

**Simulated 55-word excerpt if WordPress falls back to opening body:**

> Here is a small temptation that catches good investigators: keep the result that makes a tidy story, and quietly forget the day when the experiment failed. In a historical investigation, we would call that selection a problem. In a notebook about our own attention, it can look like encouragement. One day felt extraordinary, so we

**Simulated 350-character excerpt if WordPress falls back to opening body:**

> Here is a small temptation that catches good investigators: keep the result that makes a tidy story, and quietly forget the day when the experiment failed.

In a historical investigation, we would call that selection a problem. In a notebook about our own attention, it can look like encouragement. One day felt extraordinary, so we remember it. Four

**Editorial check:** neither fallback is a substitute for entering the proposed custom excerpt in the native post editor. Even if a rendering resembles the simulation, the subject/preheader, footer, unsubscribe and display in actual clients remain unverified. No promotional claims or earning links appear in this editorial issue.

## Copy-conversion hard review

1. **Issue 01** is now a demonstrable scene rather than an unsourced assertion that perception is unreliable. The "only about half" result is restricted to the specific first Simons/Levin field experiment. Its single CTA follows a question about archival witnesses, deliberately moving from modern observation to Final Vestige historical evidence.
2. **Issue 02** dates the reported encounter **May 4** and letter **May 8**, and distinguishes them from the BnF 1784–1785 publication history. We do not claim that the 1784 account proves magnetic influence, successful treatment or literal mind-reading; original page-image quotation check still required before any direct quote.
3. **Issue 06** offers an independently useful seven-day log whether or not the reader clicks. It avoids fake testimonials or a promised outcome; its single CTA is the already-published Focus Fieldbook, not another email list or a purchase.
4. **The proposed preheader** is not currently a verified Jetpack metadata field. Do not insert dummy zero-width preheader hacks or claim that inbox clients will show our planning text.
5. **The first 55 words of commercial Issues 03/05** should continue to include disclosures from R79 if those versions are separately approved; these three editorial candidates do not grant merchant or sending permission.

## Genuine release evidence — what is still needed

- Final Vestige must establish a qualifying current mailing address. An Automattic address in a generic WordPress confirmation is not the publisher's.
- In private WordPress admin, reconcile diagnostic `total=2 confirmed=2 unconfirmed=2` with follower snapshot `email=0 wpcom=2` and eligible recipient filters. These are differently classified endpoints, **not a count of four**. Do not export or log recipient addresses.
- Obtain **founder's separate authorization** for a native WordPress draft-post visual preview (if appropriate) and then a genuine received test email to an authorized controlled inbox. Preview a genuine excerpt; check subject, rendered HTML/plaintext, the required physical-address footer, actual unsubscribe URL and its mechanism. Avoid clicking real subscribers' links.
- Source references for each candidate and all offers must be rechecked before final publication. Official Zen12 https://zen12.com/hnp promotes a 12-minute equivalence and brainwave claims, while Total Focus https://hypnosislive.com/mental-skills/total-focus promotes a 33-minute recording and brain-reprogramming effects. These are **vendor assertions**. No independent proof of product-specific outcome is shown; no Final Vestige-specific affiliate email permissions or current approved URLs supplied. Mind & Affiliate Issue #171 owns guide decisions.
- Never confuse a Jest/Chromium/offline reviewer or GitHub-hosted Python suite with an actual Jetpack email or a completed legal review.
- Regulatory guidance: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business (honest subject, sender, physical address, workable opt-out and ongoing suppression obligations). This is not legal advice.

**Decision:** All original six newsletters HOLD_UNSENT, 03+05 additionally HOLD_MERCHANT; all R80 changes are optional. Founder final creative/audience/schedule and send approvals still absent. No merge, WordPress write, email, merchant contact, tracking, subscriber import, or live link activation.
