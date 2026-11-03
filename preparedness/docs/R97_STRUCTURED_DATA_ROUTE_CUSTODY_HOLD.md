# R97 — generated route and JSON-LD integrity (PRIVATE DRAFT / HOLD)

Issue: #136. Parent: immutable R96 ba4c3937b6cf3c1fed6fc7cd93df9f50bfa6bf70.

This is an additive, read-only source/citation safety and consistency gate. It is NOT approval to publish, qualified emergency review, human source verification, browser QA or independent QD approval.

## Gap closed

R93–R96 protect citation attribution, authored body and DOM, and the visible source/review shell. R96 checked that a JSON-LD shell script existed with the correct MIME type, but did not independently parse and verify its claims. Someone could inject a false published date, government publisher, clinical review, or unrelated canonical destination while retaining every visible original citation and warning. An altered generated breadcrumb, table of contents, or related link could misroute readers without changing original article content.

R97 reconstructs from exact authoring metadata the expected canonical destination, root section/track, four-level breadcrumb list, two-graph JSON-LD schema, and generated breadcrumb/TOC/related markup. A strict DOM event parser compares this independently with the rendered HTML. The audit rejects unexpected, missing or reordered root/shell nodes; retargeted or duplicate generated links; missing/duplicate/executable JSON-LD; duplicate JSON object keys; published dates on draft pages; false claim review, medical, safety, source or publisher assertions; unknown article destinations; and duplicated canonical routes. Failures remain HOLD.

This is a transport/content consistency proof, not proof that cited sources support instructions, that advice is medically safe, that CSS really shows every warning, or that live WordPress will preserve source HTML. The independent R93–R96 gates must also pass.

## Offline review commands

1. python -I -m unittest discover -s preparedness/tests -p test_r97_structured_data_route_custody.py -v
2. python -I preparedness/tools/r97_structured_data_route_custody.py --private-json-stdout
3. python -I preparedness/tools/validate.py
4. python -I preparedness/tools/build.py
5. python -I -m unittest discover -s preparedness/tests -v

The build writes only to private, ignored draft artifacts. No WordPress or CMS write is authorized. Run against the exact branch SHA. Check all seven contributor heads and the separate release candidate. Independently recheck PR #157 and PR #169 at exact heads; do not merge either. The mandatory 13-stage pipeline and unresolved contributor provenance still block publication.

## Inventory and unresolved approvals

35 original authored articles plus one currently importable tool = 36 private draft pages. Five other planned tools lack complete importable drafts; 41 historic reviewer packets are not 41 WordPress pages. Preserve all research, reading depth, source IDs, literal URLs, collision groups and safety states. Duplicate source URLs never constitute independent source verification.

All human citation/claim, medical/emergency safety, link, editorial and independent QD approvals remain NOT_REVIEWED. No articles, source records, metadata, taxonomy, homepage, navigation, CMS or public website material are changed by this PR.
