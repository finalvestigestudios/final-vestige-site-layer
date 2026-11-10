# EX2 original-media gate — redirect egress containment (2026-11-10)

**DRAFT / HOLD. Parent:** PR #1927, exact commit `96162f0b0f40c196eb2611dd9bcb0f36fd056dd6`. **Frozen PR #49:** unchanged (`10495883299d53596992c26a8987f629b2904670`). No publication, merge, production WordPress writes, plugin installation, emails, affiliate activation, tracking changes or paid service.

## Reproduced review blocker

The previous `verify_ex2_media_bytes.py` used `urllib.request.urlopen`, which **automatically follows HTTP 301/302/303/307/308 redirects**. It validated `response.geturl()` *after* opening the response. A first-party URL redirecting to an unauthorized destination could therefore cause the verifier to **send an HTTP request to that destination before reporting FAIL**. A failed report alone is not proof of no redirect egress.

A genuine, local-only `127.0.0.1` HTTP server reproduced the previous behavior: `GET /origin` with `Location: /unapproved-second-request` caused **two GET requests** before the caller could validate the final URL. This test made no requests to Final Vestige, WordPress or outside services.

## Fix and repeatable evidence

The default network path now builds a `urllib.request` opener with `NeverFollowRedirect`. Its `redirect_request` raises `GateFailure` **before opening the Location destination**, including same-origin redirected paths. The original response-location, MIME, exact byte-count, signature and SHA-256 validation remains in place; `inspect(row, opener=...)` still supports injected test doubles.

`tests/test_ex2_media_redirect_egress.py` tests a real loopback HTTP server, first reproduces the vulnerable default redirect behavior as a **negative control**, then confirms **one and only one GET** for each of **301, 302, 303, 307 and 308** with the corrected opener. A second test proves the default `inspect()` path selects the guarded opener rather than `urlopen`. Existing `tests/test_ex2_media_bytes.py` remains unchanged.

Reproduce, from the full exact GitHub checkout on this branch:

```bash
python -m unittest discover -s tests -p 'test_ex2_media*.py' -v
python tools/experience-2/verify_ex2_media_bytes.py
```

**Local source-pinned result:** 14/14 tests passed (12 existing + 2 new); both new source blobs were retrieved again from GitHub and match the local tested Git blob identities: verifier `8c817b12ec8799e19645da4ab6e2b2faebe658e2`, redirect tests `b40e04160c27501daede81acc1298ce218b5f8db`. Loopback tests exercise real HTTP and do not establish external image transfer. The committed tests still require independent exact-HEAD CI/QD.

## Hard safety/release boundaries

- The three **fixed original first-party URLs** remain the only accepted image resources: WordPress media 473 / 474 / 1258. The WordPress-reported original sizes were rechecked as 78,346 / 466,043 / 5,553,669 bytes. The media metadata is not a successful transfer.
- `--network` is opt-in. It will now **fail closed on any redirect**, including a legitimate WordPress or CDN redirect, rather than silently following it. Any necessary CDN derivative transfer verification must be separately scoped and approved to an exact host, URL and rights review—**never** by silently relaxing this rule.
- Local container DNS cannot currently resolve wordpress.org or finalvestige.com. There is **no successful original-asset byte transfer**, browser responsive-image verification or measured Lighthouse/CWV performance from this run.
- Apollo 1 NASA attribution/no-endorsement, Franklin's 1869 printed reproduction, and NYPL's U.S.-specific 1903 map rights qualifications from PR #1927 remain unresolved for derivative identity and independent final rights approval.
- The actual seven-chapter flagship must still pass **isolated genuine WordPress/Assembler** rendering, keyboard/touch/no-JS/reduced-motion/200%-zoom/axe WCAG 2.2 AA, responsive image loading, Jetpack confirmation and independent exact-SHA CI/QD before founder release decision.
- WordPress.com **Personal** plan cannot create a native staging clone; use a free WordPress Playground or isolated developer runtime containing public content only, with no subscriber data/secrets/live DB sync.
- Business hierarchy: **verified paid orders and net revenue** > confirmed leads > qualified human acquisition > views. This change strengthens historical-asset trust and release safety; it does not imply additional sales.

**Decision:** HOLD; security fix ready for independent code review, not WordPress publication.
