# First-party five-PNG hero staging gate — 2026-11-05

**Lane:** FV Media Recovery, independent of interim homepage design and Site QA #154. **Disposition:** source/metadata verification + offline-only staging code; draft review, **not production deployment**.

## Fresh, concrete WordPress finding

Read live `posts.get(context=edit)` for posts 34–38 and `media.get(context=edit)` for their five exact attachment IDs 39–43. Each published post has a Gutenberg image block with `sizeSlug:"large"` and stored HTML `width="1024" height="576"`, **but its stored `src` targets the original 1672×941 PNG** and has **no stored `srcset`**. Every corresponding WordPress Media Library entry reports an **empty `sizes` collection**: no registered intermediate rendition for these particular images. This is a concrete *potential* user-byte optimization opportunity, **not a measured visitor download**, because themes/Jetpack may rewrite runtime HTML or requests.

| Article | WP media | Exact original bytes | Actual source |
|---|---:|---:|---|
| 34 — San Francisco lost its water | 39 | 2,892,087 | https://finalvestige.com/wp-content/uploads/2026/08/bceca0bd-a16f-44f7-be08-16376fbf08ca.png |
| 35 — James Caird lifeboat | 40 | 2,552,136 | https://finalvestige.com/wp-content/uploads/2026/08/377e08da-e121-4f57-9174-1548343402b3.png |
| 36 — Vicksburg shelter caves | 41 | 2,498,247 | https://finalvestige.com/wp-content/uploads/2026/08/a44f673d-a8a8-4c83-9f29-7e24dd55156b.png |
| 37 — Petra water engineering | 42 | 2,488,823 | https://finalvestige.com/wp-content/uploads/2026/08/c1237ffd-4a47-4988-8254-e3b021069e72.png |
| 38 — SF emergency cistern | 43 | 2,836,245 | https://finalvestige.com/wp-content/uploads/2026/08/01340c2e-1165-4ca0-aa96-87398a83d13a.png |
| **Total stored originals** | **5** | **13,267,538** | **Not visitor transfer** |

Every image is explicitly labeled *AI-assisted historical reconstruction* in the published caption and is a first-party upload, **not** a primary-source photograph. First-party hosting does not independently establish image-generation and modification rights. The manifest therefore sets every derivative clearance to **HOLD**. Original bytes/geometry are WordPress metadata, not locally decoded/downloaded master verification.

## Concrete deliverable — offline, actual-PNG derivative stager

`qa/media-recovery/firstparty_hero5_20261105.json` is the machine-readable five-row frozen source ledger, including actual live original URLs, WordPress media/post IDs, exact original stored byte counts, HTML display geometry, null browser status/bytes, 960×540 conditional derivative target, rights holds, and no upload permission.

`qa/media-recovery/stage_firstparty_hero_png_v1.py` implements:

- Default **read-only plan**. No HTTP requests, downloads, WordPress operations, writes, or external scraping.
- Execution requires a **local original file**, correct first-party original filename, exact length and PNG signature, independently pinned original SHA-256, and explicit per-item approval with accountable evidence in a copied/edited manifest. Every current live row fails closed under HOLD.
- Verifies decoded original 1672×941, orientation, constrained 960×540 aspect ratio/no upscale; stages **WebP quality 88** to an existing separate local directory only, using exclusive create (no overwrite), validating the resulting 960×540 WebP and hashing output. Discards candidate if its file bytes are not smaller than the corresponding local master.
- Preserves ICC profile where available, refuses altered source data, writes no HTML, keeps `editorial_visual_qa=HOLD`, `wordpress_upload_authorized=false`, and **never claims a visitor-wire reduction**.
- Performs no change to live featured images, permalink, ALT, caption, Gutenberg blocks, or homepage design.

**Native execution here:** Python 3 / Pillow 12.3.0, `python -m unittest -v qa/media-recovery/test_stage_firstparty_hero_png_v1.py` (from the directory or with PYTHONPATH adjusted) — **10/10 PASS**, including synthetic 1672×941 PNG conversion to 960×540 WebP, output existence, duplicate refusal, SHA tamper rejection, no-rights gate, source URL/geometry drift, and no false browser status. This test generated **only disposable synthetic pixels**, not a Final Vestige or third-party image binary. The default `--manifest` dry plan also executed. GitHub CI/actual browser checks are separate.

## Separate high-value media queue

Read-only WordPress post 621 additionally confirms two inline **full-size original JPEG URLs** despite `sizeSlug:"large"` and no stored `srcset`: 1257 tunnel photograph (4,798,395 bytes, 4000×3000), 1258 NYPL 1903 system map (5,553,669 bytes, 5667×3831). Both have WordPress-registered 1024px and 768px alternatives; re-use existing variants should be studied before generating more copies. **Map legibility is an explicit exception-review:** do not silently downsample cartographic lettering to an illegible 960px without approved zoom/large accessible alternative. Original metadata baseline still has 13 files >1.5MiB totaling 43,522,829 *stored* bytes, not network bytes. Vasa files already offer Jetpack derivatives.

## Reproduction and release gate

```sh
# safe: print plan only; does not require source binaries
python qa/media-recovery/stage_firstparty_hero_png_v1.py --manifest qa/media-recovery/firstparty_hero5_20261105.json

# tests on synthetic fixtures; pip install Pillow in a separate development environment if needed
cd qa/media-recovery && python -m unittest -v test_stage_firstparty_hero_png_v1.py
```

To stage **after separate item-specific rights approval**, acquire the **authorized first-party original** under source-custodian terms, hash and decode it, record `approved_source_sha256` and signed derivative rights evidence in a separate reviewed manifest, then use `--execute --media-id <39..43> --source <local-file.png> --output-directory <existing-local-staging-dir>`. The original pinned HOLD manifest must remain unchanged in review. Obtain human visual comparison against master (reconstruction details, text/edge artifacts), desktop/mobile screenshot parity, and Site QA's **existing** logged-out CDP cold transfer and decode proof. A separately approved WordPress media workflow can then add a responsive derivative with exact image ID/rollback mapping; **do not rewrite raw Gutenberg blocks or publish within this PR**.

The reported **42 broken images are still not independently browser verified**, and the suggested **76% transfer reduction is not measured**. The updated complete site census is 66 posts/361 stored image URLs (#1138), not the frozen 61/355. The Site QA #154 six-slot priority queue remains 285:5, 285:2, 287:5, 418:1, 418:2, 407:1, and our new work does **not** duplicate its browser scripts. No production media repaired or staging of real images this sprint.

**No costs, outside licensed media copied, WordPress writes, or production design changes.**
