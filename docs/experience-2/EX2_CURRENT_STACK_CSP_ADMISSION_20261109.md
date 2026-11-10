# EX2 Current Seven-Chapter Stack — CSP and Interaction Admission (2026-11-09)

**Release decision: HOLD.** Independent staging acceptance is **not** established.

## Exact source and purpose
- Parent draft #1816 exact HEAD: `9cd6c75835e78d26db2911650712d75633c31870`.
- Frozen homepage v1 PR #49 exact HEAD: `10495883299d53596992c26a8987f629b2904670`. **No changes to this PR.**
- Parent PR #1816 preserves fragment-specific Franklin and Malbone evidence selection; this companion addresses a different gap: strict Chromium/CSP validation on the **current** integrated seven-chapter source.
- Existing PR #252 supplied the original strict CSP test on a separate, older stack. Its source was copied from its verified GitHub blob `f5a7f6e511b8f4dda884ff9a750d0a9c59fc5763`; the original PR remains unchanged.
- PR #1810 moved the art-direction selector into a **collapsed native details** control. The earlier test clicked a hidden direction button without opening details; current-source Chromium reproduced `TimeoutError` at 390 CSS px. This companion explicitly opens the summary before testing art-direction choice.

## Independently executed exact-blob offline browser evidence
Eleven actual source blobs were retrieved/checked against GitHub at `9cd6c758...`. A separately implemented source-pinned Chromium 144 test executed **10/10 PASS** (seven widths at **320, 360, 390, 768, 1024, 1440 and 1920 CSS px** plus three negative controls). At each width, the four genuine interactions were:
1. Native details expansion and Museum After Hours art-direction selection;
2. Franklin evidence case selection (Apollo hidden);
3. Chronicle 1848-addition switch;
4. Observer illustrated Frame B selection (Frame A hidden).

Negative controls: JavaScript-disabled all-three-case/observer meaning, injected un-nonced inline script rejection, and wrong-flagship-nonce static fail-open. Meta CSP had no reported violation in legitimate seven-width scenarios. Source was loaded through an in-memory **offline** Chromium assembly, external network requests were blocked. A separate stale-test reproduction confirmed direct hidden-button click timeout, while details-first selection succeeded. Images could not be transferred.

This PR commits a port of #252's exact-checkout test with the necessary current-source details activation. **The newly committed test itself has not been executed on a complete clean checkout of this new PR HEAD.** Do not mislabel the independent 10/10 replication as a current PR exact-checkout CI/QD pass. Run:

```bash
python tests/experience-2/verify_stacked_csp_chromium.py \
  --root experience2/home-flagship \
  --expected-head "$(git rev-parse HEAD)" \
  --output /tmp/fv-ex2-csp-current
```

Check a clean checkout and verify the saved JSON and responsive screenshots. The test intentionally aborts external image requests. It cannot certify WordPress HTTP CSP headers, nonce propagation through WordPress, cookies, iframe auth, Playground renderer, or live asset bytes.

## Staging and release gates
Authenticated `wpcom_user_sites(environment='all')` exposed only **production** site `256784396`. The Personal plan does not offer a native staging clone; the included `.wpcomstaging.com` domain is **not** a second site. The approved path is a free isolated Playground/Assembler developer environment with **public content only** and no subscriber/database import, secret files, production install or publish. Local runtime remained unavailable because external package registries cannot resolve from this environment.

Before release: exact-clean-Git script run, isolated WordPress-native assembly with real media/network requests and anonymous-content-denial checks, axe + manual WCAG 2.2 AA/keyboard/touch/no-JS/200%-zoom/Safari checks, genuine lab Lighthouse (field CWV measured separately), archival image usage/rights review (#1730), Focus Jetpack confirmation-state validation (#1681), CI green + independent QD + founder visual/release approval.

## Conversion, ownership and safety
**Offer:** Current free 52-page Focus Fieldbook. **Funnel step:** authentic archive evidence → relevant Focus CTA → verified Jetpack lead → independently confirmed purchase. **Blocker:** stale CSP QA could not exercise the actual current art-direction interaction. **Change:** source-controlled 7-width/4-interaction/3-negative-control test adapted to current DOM. **Pass/fail evidence:** 10/10 on independently pinned offline source; newly committed exact-checkout script is **unrun** and remains HOLD. **Owner:** interim homepage engineering for test; Claude for attribution, Praxxis/Grok for campaign IDs; founder for production release. No verified new leads, purchases, affiliate conversions, fees or net revenue.

No new artwork, source claims, subscriptions, trackers, affiliate links or visual chapters; no GitHub merge, WordPress production edit, plugin install, publishing or spending. Apollo #158 and Mind #171 remain separate lanes.
