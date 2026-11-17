# R431 — Original manuscript-fork byte custody and reading-depth comparison

**Preparedness-only | Issues #136 and #820 / charter #818 | DRAFT / HARD HOLD.** Stacked on R430 PR #2842 (`5b3a92751526d8f8b8c780740e38121611bca8b8`). No merge or publication authority. No source text, article body, taxonomy, canonical route, product, CTA, CMS, navigation, social work queue or analytics script is changed.

## What the new read-only gate does

`preparedness/tools/r431_fork_content_delta_gate.py` builds on the exact original R397 Git-pinned 35-article source docket and R430's 14 unresolved cases. The R431 gate requires each of the nine disputed original manuscript/metadata/source-fragment paths' branch-specific Git objects, named by original SHA. It checks each object against the original Git blob SHA **and exact byte count**, blocks symlinks/hardlinks/non-regular files, rejects malformed JSON/citation tokens and generates pairwise reviewer-only text/citation deltas. It preserves branch identities even for identical content hashes, and NEVER selects a candidate.

**Original candidate inventory:** 9 disputed paths × 3 branch variants = **27 original candidate records**, with **25 unique Git blobs**, since fire-plan body and metadata on Shelter continuation/follow-up are identical. Of the nine paths, four are `.body.html`, four are `.meta.json`, and one is a source fragment JSON. The 5 source-applicability disputes remain separately unresolved. The rest of the 35-article original docket and 203 source IDs / 280 source occurrences / 17 shared exact-URL groups remain original, untouched inputs.

## New reproducible local tests

- `python -I -m unittest discover -s preparedness/tests -p 'test_r431_fork_content_delta_gate.py' -q` → **56/56 PASS**, synthetic-only, exact committed Python bytes (after terminal-newline Git correction).
- `python -I -m unittest discover -s preparedness/tests -p 'test_r43[01]*.py' -q` → **125/125 PASS**, including 69 inherited R430 tests in one local invocation. Neither result is a full repository suite or native build.
- `python -m py_compile preparedness/tools/r431_fork_content_delta_gate.py preparedness/tests/test_r431_fork_content_delta_gate.py` → PASS.

## Original branch/blob spot-and-full inventory checks

Direct GitHub blob reads returned **all 25 distinct originally enumerated candidate objects** with bytes equal to the original R397 docket's asserted lengths (27 branch/path records); this is remote blob/length identity evidence, **not** a local native R431 invocation, and not qualified source fact-checking.

A simple independent HTML-tag-stripped word estimate (not browser-visible text or a reading-depth PASS) identified material differences across the three original Shelter versions:

| Original body | First branch | Continuation | Follow-up | Citation tokens (same order) |
|---|---:|---:|---:|---|
| Family contact/reunification | ~3,027 | ~3,464 | ~3,564 | 62 / 67 / 69 |
| Home fire evacuation | ~3,747 | ~4,257 | ~4,257 | 70 / 73 / 73; continuation and follow-up are same Git blob |
| Heat/cold/generators | ~4,200 | ~4,467 | ~4,467 | 116 / 120 / 121 |
| Shelter vs evacuation | ~3,437 | ~4,089 | ~4,193 | 50 / 58 / 59 |

Original Shelter source fragments contain **31 / 41 / 45** source records respectively. These increases and differences are not proof that newer content is better or safer. Qualified reviewers must examine each variant and verify applicable source evidence, medical/emergency instructions, privacy and accessibility before selecting any candidate. Preserve the oldest version as evidence even when the newer one has more words.

## Reproduction on a genuine full checkout (read-only, no CMS)

```sh
mkdir -p /tmp/fv-r431-original-objects
# For each SHA in original_fork_disputes[*].variants[*].git_blob_sha:
# git cat-file blob "$sha" > "/tmp/fv-r431-original-objects/$sha.blob"
python -I preparedness/tools/r431_fork_content_delta_gate.py \
  preparedness/reviews/r397_original_source_fork_docket.json \
  /tmp/fv-r431-original-objects
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
```

The R431 CLI **always exits 2** and retains DRAFT_HARD_HOLD even with structurally authentic input. The native 35-article validate/build, authentic WordPress/private-preview export parity (70 pairs), exact rendered reading-depth comparison, independent QD #157 / synthetic fixture #169 / dependent #2205, five original source disputes, child privacy and qualified safety approvals are **not completed by R431**. A local full authenticated repository checkout was not available in this run; do not treat the isolated synthetic tests as native build evidence.

## Conversion-first acceptance (#820)

**One candidate audience/topic only:** a genuinely already-published Grok family-contact/reunification video may route to the **already live FREE official-resource** `/preparedness/` landing if Praxxis independently authenticates its exact asset ID, public permalink, literal hook, rights and permitted mobile UTM. Such an asset remains **UNMATCHED**; Article #15 and Tool #104 remain private/HOLD, Tool #102 is separate and retired water freebies stay excluded.

| Offer → step | Blocker | Next evidence/experiment | Owner |
|---|---|---|---|
| One genuine FV-owned Preparedness paid pack → paid purchase | No authenticated rights-cleared, genuinely payable and deliverable pack/SKU | Independently establish merchant owner, actual checkout/delivery, refund terms, applicable rights, and founder authorization BEFORE any paid CTA | Founder / Commerce — HOLD |
| Matching Grok family-contact asset → free agency-backed Archive | No verified real asset ID or matching post and mobile link | Independent already-published post/rights/UTM crosswalk; no new Grok task | Grok creator, Praxxis QA — UNMATCHED |
| Free Archive → optionally reviewed Tool #104 | Original Article #15 and Tool #104 emergency/child privacy/print requirements unapproved | Human qualified source, safety, accessibility and privacy QD | Preparedness / QD — HARD HOLD |
| Qualified-human sessions → verified paid order → realized net revenue per 1,000 | No verified SKU/orders/fees/refunds or 7/30-day cohort | Native existing privacy-safe campaign linkage, then merchant-confirmed settled orders less refunds/fees; never count CTA/affiliate clicks as sales | Claude analytics / Commerce — NOT COMPUTABLE |

**No public publishing, CMS/navigation changes, creator queue mutation, new offer/affiliate activation, emails, analytics scripts or spending.** Structural checks are only BUILT/TESTED on local synthetic fixtures, not LIVE or VERIFIED commercial evidence. Founder's commerce and release approval remains mandatory.
