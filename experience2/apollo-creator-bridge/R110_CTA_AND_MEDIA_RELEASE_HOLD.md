# Apollo R110 — free-exercise CTA acceptance, rights and revenue truth

**Classification:** SOURCE-CONTROLLED STAGING CHANGE; historical facts remain based on the R37 custody ledger; browser behavior **NOT YET EXECUTED** against this exact head. Nothing published or merchant-verified. **RELEASE HOLD.**

## Why this patch precedes further visual work

Apollo R108's primary action `Review the free classroom evidence exercise` is a native in-page jump, not a product purchase, confirmed lead, or paid sale. The previous R108 browser runner merely inspected its `href`. This leaves the most important site bridge untested: a viewer on mobile, with scripting disabled, or using a keyboard must actually reach the classroom evidence, not just see a link with the correct string.

**R110 changes** `qa_r108.py` to exercise the existing CTA at 320, 360, 390, 768, 1024, 1440 and 1920px, each with JavaScript enabled and disabled (14 configurations). At <=390px + JavaScript, it uses a genuine touch activation; other modes use keyboard Enter. It verifies the real `#classroom-preview` fragment, visible target, meaningful classroom heading, two native evidence/answer disclosures, source-table keyboard scrolling, and native keyboard opening of the NASA rights/source drawer. It checks the absence of merchant destinations, checkout UI, and forms in every mode. The structured result labels the action `free_exercise_fragment_navigated_not_sale`.

The previous screenshot matrix (six local HTTP captures), optional locally supplied axe-core scans (390/1440), six laboratory LCP/CLS observations (390/1440, three each), reduced-motion emulation, no-JS, no external requests and unchanged thresholds remain in place. **No new analytics or tracking script was added.** The runner is still an isolated HTTP preview, not genuine WordPress/Assembler or live Core Web Vitals. Its run must be repeated after GitHub Actions executors recover; code presence is not test evidence.

## Public NASA media policy — preliminary rights triage, NOT a license

Read-only policy sources verified November 3, 2026:

- NASA Brand Center: https://www.nasa.gov/nasa-brand-center/ — NASA generally does not assert ownership over much public agency-created media, but this does not automatically resolve third-party copyright, institutional identifiers, identifiable-person publicity rights, or commercial endorsement.
- NASA Advertising Guidelines: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ — no false sponsorship/endorsement; astronaut likeness and deceased-person estate issues may matter in advertising and merchandising.
- NASA image-use summary: https://gpm.nasa.gov/image-use-policy — third-party content and recognisable people can carry restrictions even when hosted by NASA.
- NASA Apollo resources: https://www.nasa.gov/apollo-1-resources/ — original historical investigation sources are different from NASA image reproduction rights.

R37 source crosswalk remains authoritative for this staging branch. **Six separate photo-specific reuse reviews are still pending**, and no photograph is newly embedded, copied, licensed, merchandised, or used as a purchase advertisement. Direct textual links to public NASA pages are source attribution, not authorization to sell images.

| R37 record | NASA canonical source | Current disposition |
|---|---|---|
| 01 — crew image, `S67-19766` label provisional | https://www.nasa.gov/image-detail/apollo-1-crew-honored/ | HOLD: verify identity from authoritative item record; identifiable crew / estate and endorsement boundaries require review |
| 02 — `S67-15717` | https://www.nasa.gov/image-detail/amf-s67-15717/ | HOLD: verify item metadata, authorship/third-party notices, proposed use |
| 03 — `S66-58038` | https://www.nasa.gov/image-detail/amf-s66-58038/ | HOLD: verify earlier-event date and source-specific reuse |
| 04 — `KSC-20170124-PH_KLS01_0164` | https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/ | HOLD: label retrospective 2017 exhibit; source-specific image assessment |
| 05 — `S67-21294` | https://www.nasa.gov/image-detail/amf-s67-21294/ | HOLD: post-fire scene, no single ignition-source inference; source-specific image assessment |
| 06 — `KSC-20170124-PH_KLS01_0090` | https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/ | HOLD: retrospective 2017 redesigned-hatch exhibit; source-specific image assessment |

**Editorial boundary:** event chronology must not be merged with photograph exposure or publication dates; no invented Atlas pins, map edges or implied temporal causality. Preserve the Review Board's unresolved specific ignition source, historical differentiation and complete open-source access.

## Highest-priority commercial funnel decision

**Buyer hypothesis:** grades 6–9 educators looking for a ready-to-teach primary-source incident investigation, reached through a *future*, Grok-owned Apollo documentary/Shorts asset. An Apollo 1 education casefile remains only a proposed SKU; current pricing, seller-origin delivery, rights, refund terms, independently confirmed transactions, and audience demand **not verified**.

**User pathway:** Grok approved asset ID + campaign parameters → **live original Apollo investigation** (not this unpublished preview) → optional free evidence exercise once release-qualified → relevant seller/rights-approved paid casefile *only when an actual SKU is verified and separately approved* → independent Payhip confirmed order → refunds/fees → net realized revenue. An unrelated Focus or Mind affiliate product must never be inserted merely to create a buy button.

| Priority | OFFER → STEP | BLOCKER | CHANGE / EXPERIMENT | PASS / FAIL EVIDENCE | OWNER |
|---|---|---|---|---|---|
| P0 | Apollo teacher casefile → actual buyer | No independently confirmed matching Payhip SKU / rights / delivery / refunds | Seller-origin review using R109 preflight plus independent license and checkout verification | **BLOCKED**; offline manifest alone cannot prove a merchant sale | Claude/Growth; founder commercial approval |
| P1 | Future Grok Apollo asset → investigation → free exercise | No approved Apollo creator asset/campaign; R108 link interaction never browser-accepted | R110 actual keyboard/touch/no-JS CTA assertions | **BUILT; real browser not yet executed** | Apollo site QA; Grok owns asset, Praxxis independent review |
| P2 | Free exercise → paid checkout | No licensed, priced Apollo-specific seller destination | No paid CTA until merchant and rights evidence; do not add placeholder Payhip links | **NOT OBSERVABLE** | Claude/Site QA; founder release |
| P3 | Purchase → net realized revenue per 1,000 qualified human sessions | No verified order/customer/fee/refund and campaign denominators | Coordinate existing privacy-respecting Issue #820 metric contract, without duplicate tags | **NOT COMPUTABLE**; clicks and signups are not orders | Claude/Growth; independent Site QA |

**Pass criteria for R110's own QA:** 14/14 browser modes including native CTA activation, two selected-state axe-core scans with zero recorded WCAG 2.2 AA violations when a local approved bundle is supplied, six finite LCP<=2500ms/CLS<=0.1 observations, six checksummed screenshots, source/rights disclosure, and no external requests. Verify in disposable WordPress/Assembler separately; report any flake/failure with actual numerical evidence. Manual screen reader, physical device and hosted performance require independent review.

**Release HOLD:** NASA item-level rights 0/6 reviewed, provisional crew photo identity, genuine WordPress/Assembler and exact-head CI, manual accessibility/independent historical review, verified applicable merchant offer and founder decision. Frozen homepage PR #49 and original Research Desk PR #158 untouched. No WordPress, seller, social, Drive queue, email, paid-service or production writes.

References: Apollo [#150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150); conversion [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820); charter [#818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818); Grok/Praxxis TASK-008 remains owned externally.
