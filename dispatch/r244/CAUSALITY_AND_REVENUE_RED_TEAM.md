# R244 | Native red-team of R243 revenue code | Action-required findings

**Target:** existing R243 draft PR #1812 at exact head `f66796e2c6678806504b13adc299deb9ab238af6`, `dispatch/r243/safe_attribution.cjs` Git blob `00caa9bb9f03ecc5f446e656aeb020c568506ea8`, `tests/test_safe_attribution.cjs` blob `973596a72be30a1c3955c1d890d09f53eedb9c56`, fixture blob `95c301063f4b1c2f037181bb702de0c15161c919`.

**Execution:** locally reconstructed the three exact GitHub-authenticated bytes (Git blob SHA-1 matches 3/3) and ran `node --test` on the *exact* 25-case committed R243 suite with Node.js 22.16.0: **25 passed, 0 failed**. Also reran original PR #175 six Python tests with Python 3.13.5 against its 8 exact GitHub blob identities: **6 passed**. Prior tests prove the implementation's stated checks, NOT revenue audit correctness.

## Five documented native adversarial experiments
Each mutation used the R243 synthetic-only fixture; no FV production revenue or customer data. Original `scoreLedger` still returned 1 putative settled attributed order / 800 minor units for all variants below:
1. **Order precedes visitor**: order 2026-11-08 19:00Z, session 20:00Z. *Old R243 computes order anyway.*
2. **Signup precedes visitor**: provider confirmation 19:00Z, session 20:00Z. *Old R243 still computes a confirmed lead.*
3. **No outbound click event at all**: `actions=[]`. *Old R243 still attributes a paid commission to the session.* A merchant attribution string field does not independently prove that an FV click actually occurred.
4. **Unverified transaction currency**: set an order `currency=JPY`. *Old R243 still sums into same minor-unit total* without currency validation.
5. **Self-declared production reconciliations**: change `mode=PRODUCTION_READONLY_EXPORT`, keep booleans set true. *Old R243 prints numeric source-ledger amounts despite no independently authenticated merchant, session or provider receipt.* It does clearly label `SOURCE_LEDGER_NOT_EXTERNALLY_AUDITED`, but that warning is easy to drop in downstream dashboards.

These are **claim-admission gaps**, not evidence of actual fraudulent transactions. Do not call the old calculator a real revenue verifier; keep it a synthetic exploratory calculator.

## Corrective design now source-controlled
`review_causality.cjs` is an **additional, read-only fail-closed reviewer**, not a replacement for R243 and not a production commerce service. It enforces causal timing (session before provider confirmation/click/order), unique transaction/session identifiers, matching offer and actual click ID, no duplicate click claim, currency scope (USD for this pilot), basic settlement field sanity, and email eligibility state. It always holds email and reports **null** real verified orders and net metrics because it cannot independently authenticate merchant acceptance, consent, live checkouts, publisher rights or booked commissions. No new production analytics. Current R243 fixture intentionally triggers missing-click/currency blockers. An enriched synthetic fixture exercises the data-level guard but never becomes a real sale.

**Cohort naming issue:** R243 calculates **rolling 7/30-day activity windows** with an order and session both inside the same window; it is not a settled 7/30-day *acquisition cohort* with conversion lag. Do not label those numbers "7/30-day cohorts" until cohort anchoring and late order/refund rules are defined.

**No partner account approval or email permission authenticated.** Mind #171 newest R254 handoff explicitly continues hard hold; six original issues remain 4 editorial + 2 provisional commercial, original master #175 unchanged.

## Source/assurance status
| Layer | Status |
| --- | --- |
| Original #175 Python | NATIVE PASS 6/6, eight source blobs match |
| R243 native Node | NATIVE PASS 25/25, three source blobs match |
| R243 adversarial evidence | NATIVE GAP CONFIRMED, synthetic only |
| R244 guard and 25 tests | EXACT COMMITTED SOURCE V8 PASSED 25/25 WITH MOCKED NODE APIS; **not native Node** |
| Partner consent/earning URL | UNVERIFIED |
| Native WordPress preview/received MIME | NOT PERFORMED |
| Paid settled revenue and qualified-human denominator | UNVERIFIED, KPI NOT COMPUTABLE |

**Metric contract**: Report `net_revenue_per_1000_qualified_human_sessions = 1000*(independently settled paid commission - refund/reversal - attributable fees)/verified qualified-human sessions` only with true comparable currency, valid causal attribution, documented 7/30 acquisition cohort, and source-of-truth rights/transaction evidence. In all other states **NOT COMPUTABLE**, never zero or illustrative 800 minor units.

## Offer → step → blocker → experiment → evidence → owner
| Offer / funnel | Blocker | Corrective experiment | Gate | Owner |
| --- | --- | --- | --- | --- |
| Zen12 → paid affiliate conversion | No named acceptance, email rights or earning URL | Private documentary verification, live vetted guide and checkout terms | HOLD_MERCHANT | Mind #171 |
| Grok → Focus → verified lead | Consent status and source asset IDs unjoined | Aggregate provider status and immutable asset/session join, without PII | HOLD | Grok/Praxxis/Claude #129/#820 |
| Email → paid order | R243 admits impossible event ordering / absent click | Causal reviewer and synthetic adversarial tests | REVIEW_ONLY | Dispatch / Commerce |
| Dispatch → native preview | Earlier runbook assumed per-post toggle must ON; current official support says ON or OFF | Founder-authorized unpublished draft, toggle OFF, visual-only preview | NOT YET AUTHORIZED | Dispatch / Site QA |
| Dispatch → legally compliant inbox | Publisher postal address/unsubscribe/welcome receipt unknown | Separately authorized received email then MIME and opt-out audit | HOLD | Founder / Site QA |
| Buyer → attributable net | No independent merchant settlements/fees/refunds | Reconcile full currency-matched partner statement and click IDs | NOT COMPUTABLE | Commerce / Praxxis |

No live actions, subscribers, emails, posts, transactions, affiliate links, metrics scripts, or spending changed.