# 06 - Proposal: link the five 2026-11-02 posts (NOT APPLIED)

Status: **proposal only. Nothing in this file has been applied.** Hold until the content QA on posts 1917, 1920, 1922, 1924 and 1926 lands; then re-read every lock, rebuild, show the diffs to the user and apply only with approval.

**Locks go stale.** `expected_modified` / `expected_content_hash` / `index` below were read on 2026-11-02. Any edit to a target (including the QA corrections) invalidates them and the tool will refuse the write. Re-run `post-sections.list` / `page-sections.list` for each target immediately before applying; if the QA changes the number of top-level blocks on a new post, recompute its insertion index (the block just before the closing FAQPage JSON-LD `core/html`).

Scope: the new posts' *body text is not edited*; each change appends one new `core/group` block. Metadata and schema of the new posts are not touched. Counts: 5 outbound blocks (9 links: 2 per post except the Lycurgus Cup post, whose weaker The Working Order link was dropped), 9 inbound blocks on existing pages (10 links, 2 per new post). Total 19 links.

## Duplicate check

Each proposed link was compared with the links already present in the target's public `<main>` content (new posts fetched live from the public site; existing pages from `evidence/crawl-after-2026-11-02.json`). Duplicates found: **0**. For reference, the new posts already link out to these older posts, which are deliberately *not* proposed again: 1917 -> maps-places, the-lump-had-gears, they-painted-over-archimedes, all-well-was-written-first, the-mountain-buried-the-door; 1920 -> the-lump-had-gears, they-thought-the-books-were-charcoal, thirty-men-were-enough-vasa, objects-archaeology; 1922 -> they-taught-the-lake-to-breathe, a-wall-in-the-dark, the-light-said-closed, ed-pulaski, research-sources; 1924 -> how-petra-made-water-flow, add-no-more-load, all-well-was-written-first, change-blindness, puysegurs files; 1926 -> boston-molasses, halifax, courrieres, lycurgus-cup, piri-reis-map, objects-archaeology.

No link goes to a draft, to anything in the Preparedness Archive, or to the homepage.

## A. Outbound: from each new post to existing pages

### Post 1917: The Piri Reis Map: What the 1513 Chart Actually Shows
- `post-sections.insert` at index **26** (immediately before the closing FAQPage JSON-LD html block, after the sources list); lock: modified `2026-11-02T20:48:54`, content_hash `087bd41bbb4e66433ac377d82eeebbfe81fa5d7c`; duplicates: none
- **The Lost Landscape** (`/the-lost-landscape/`): The post is about reading an old chart's own notes and sources; The Lost Landscape is the site's guide to reconstructing places from old maps.
- **The Archive Trail** (`/the-archive-trail/`): The Antarctica claim is the classic claim-versus-record case; The Archive Trail is the site's field kit for verifying historical claims.
```html
<!-- wp:group {"className":"fv-related-reading","layout":{"type":"constrained"}} --><div class="wp-block-group fv-related-reading"><!-- wp:heading --><h2 class="wp-block-heading">Related reading</h2><!-- /wp:heading --><!-- wp:list --><ul class="wp-block-list"><li><a href="https://finalvestige.com/the-lost-landscape/">The Lost Landscape</a></li><li><a href="https://finalvestige.com/the-archive-trail/">The Archive Trail</a></li></ul><!-- /wp:list --></div><!-- /wp:group -->
```

### Post 1920: The Lycurgus Cup: The Roman Glass That Changes Color
- `post-sections.insert` at index **24** (immediately before the closing FAQPage JSON-LD html block, after the sources list); lock: modified `2026-11-02T20:50:12`, content_hash `c61b8530eb57d834814d8d09849e13cde83d7e38`; duplicates: none
- **They Painted Over Archimedes** (`/2026/08/18/they-painted-over-archimedes/`): Both are ancient objects whose real nature was recovered with modern analysis (this post: electron microscopy of the glass).
```html
<!-- wp:group {"className":"fv-related-reading","layout":{"type":"constrained"}} --><div class="wp-block-group fv-related-reading"><!-- wp:heading --><h2 class="wp-block-heading">Related reading</h2><!-- /wp:heading --><!-- wp:list --><ul class="wp-block-list"><li><a href="https://finalvestige.com/2026/08/18/they-painted-over-archimedes/">They Painted Over Archimedes</a></li></ul><!-- /wp:list --></div><!-- /wp:group -->
```

### Post 1922: Change Blindness: Why You Miss Big Changes Right in Front of You
- `post-sections.insert` at index **29** (immediately before the closing FAQPage JSON-LD html block, after the sources list); lock: modified `2026-11-02T20:51:39`, content_hash `5ff50b4a0571a69beca449fee71acf8e19d17f09`; duplicates: none
- **The Failure Chain** (`/the-failure-chain/`): The post is about missed observations; The Failure Chain has a section on warning-to-action latency and evidence confidence for reading failures.
- **The Missing Caption** (`/the-missing-caption/`): Change blindness is the reason side-by-side photograph comparison fails; The Missing Caption is the site's guide to comparing and dating photographs.
```html
<!-- wp:group {"className":"fv-related-reading","layout":{"type":"constrained"}} --><div class="wp-block-group fv-related-reading"><!-- wp:heading --><h2 class="wp-block-heading">Related reading</h2><!-- /wp:heading --><!-- wp:list --><ul class="wp-block-list"><li><a href="https://finalvestige.com/the-failure-chain/">The Failure Chain</a></li><li><a href="https://finalvestige.com/the-missing-caption/">The Missing Caption</a></li></ul><!-- /wp:list --></div><!-- /wp:group -->
```

### Post 1924: Mesmerism: What Franklin’s 1784 Commission Actually Found
- `post-sections.insert` at index **32** (immediately before the closing FAQPage JSON-LD html block, after the sources list); lock: modified `2026-11-02T20:52:58`, content_hash `3d8f41cf528f27baf08ed4170079006f76834198`; duplicates: none
- **The Archive Trail** (`/the-archive-trail/`): The 1784 report is the model of a controlled test of a claim; The Archive Trail is the site's field kit for verifying historical claims.
- **Primary Historical Sources & Archives** (`/watch/primary-sources/`): The commission's report is a primary source (cited from Project Gutenberg); this is the site's primary-sources hub.
```html
<!-- wp:group {"className":"fv-related-reading","layout":{"type":"constrained"}} --><div class="wp-block-group fv-related-reading"><!-- wp:heading --><h2 class="wp-block-heading">Related reading</h2><!-- /wp:heading --><!-- wp:list --><ul class="wp-block-list"><li><a href="https://finalvestige.com/the-archive-trail/">The Archive Trail</a></li><li><a href="https://finalvestige.com/watch/primary-sources/">Primary Historical Sources &amp; Archives</a></li></ul><!-- /wp:list --></div><!-- /wp:group -->
```

### Post 1926: Crystal Skulls: What the Evidence Says About Their Age
- `post-sections.insert` at index **25** (immediately before the closing FAQPage JSON-LD html block, after the sources list); lock: modified `2026-11-02T20:54:10`, content_hash `b097f1ad3460780efabad87f24a7d2af57256eda`; duplicates: none
- **The Findspot** (`/the-findspot/`): The skulls' central problem is missing find context; The Findspot is the site's guide to documenting finds without losing context.
- **The Paper Witness** (`/the-paper-witness/`): The 2008 paper traces the skull's dealer and sale records; The Paper Witness is the site's guide to document provenance.
```html
<!-- wp:group {"className":"fv-related-reading","layout":{"type":"constrained"}} --><div class="wp-block-group fv-related-reading"><!-- wp:heading --><h2 class="wp-block-heading">Related reading</h2><!-- /wp:heading --><!-- wp:list --><ul class="wp-block-list"><li><a href="https://finalvestige.com/the-findspot/">The Findspot</a></li><li><a href="https://finalvestige.com/the-paper-witness/">The Paper Witness</a></li></ul><!-- /wp:list --></div><!-- /wp:group -->
```

## B. Inbound: from existing pages to the new posts

### Page/post 499: Historical Maps & Place Research (`/watch/maps-places/`)
- `page-sections.insert` at index **10** (appended as the last top-level block); lock: modified `2026-10-29T21:22:26`, content_hash `a12b1816450fb6f9138d44d3d0a2b9494a2b31a1`; duplicates: none
- **The Piri Reis Map: What the 1513 Chart Actually Shows**: The hub for historical maps and place research has no link to any map case study; this is the site's map-and-chart case study.
```html
<!-- wp:group {"className":"fv-related-reading","layout":{"type":"constrained"}} --><div class="wp-block-group fv-related-reading"><!-- wp:heading --><h2 class="wp-block-heading">Related case study</h2><!-- /wp:heading --><!-- wp:list --><ul class="wp-block-list"><li><a href="https://finalvestige.com/2026/11/02/piri-reis-map/">The Piri Reis Map: What the 1513 Chart Actually Shows</a></li></ul><!-- /wp:list --></div><!-- /wp:group -->
```

### Page/post 193: The Lost Landscape (`/the-lost-landscape/`)
- `page-sections.insert` at index **2** (appended as the last top-level block); lock: modified `2026-08-26T11:16:25`, content_hash `bcc5bbea15f18003d74919b89c0225e62d09a6e6`; duplicates: none
- **The Piri Reis Map: What the 1513 Chart Actually Shows**: The old-maps method guide: a worked example of a single historical chart and what it does and does not show.
```html
<!-- wp:group {"className":"fv-related-reading","layout":{"type":"constrained"}} --><div class="wp-block-group fv-related-reading"><!-- wp:heading --><h2 class="wp-block-heading">Related case study</h2><!-- /wp:heading --><!-- wp:list --><ul class="wp-block-list"><li><a href="https://finalvestige.com/2026/11/02/piri-reis-map/">The Piri Reis Map: What the 1513 Chart Actually Shows</a></li></ul><!-- /wp:list --></div><!-- /wp:group -->
```

### Page/post 501: Archaeology, Objects & Museum Collections (`/watch/objects-archaeology/`)
- `page-sections.insert` at index **10** (appended as the last top-level block); lock: modified `2026-08-31T22:32:56`, content_hash `bfe9a11f9c5cd27c704e15b7bcce6d72c825dbb4`; duplicates: none
- **The Lycurgus Cup: The Roman Glass That Changes Color**: Objects hub: the Lycurgus Cup is an object case study.
- **Crystal Skulls: What the Evidence Says About Their Age**: Objects hub: crystal skulls are an object-authenticity case study (same block as the Lycurgus Cup).
```html
<!-- wp:group {"className":"fv-related-reading","layout":{"type":"constrained"}} --><div class="wp-block-group fv-related-reading"><!-- wp:heading --><h2 class="wp-block-heading">Related case studies</h2><!-- /wp:heading --><!-- wp:list --><ul class="wp-block-list"><li><a href="https://finalvestige.com/2026/11/02/lycurgus-cup/">The Lycurgus Cup: The Roman Glass That Changes Color</a></li><li><a href="https://finalvestige.com/2026/11/02/crystal-skulls/">Crystal Skulls: What the Evidence Says About Their Age</a></li></ul><!-- /wp:list --></div><!-- /wp:group -->
```

### Page/post 254: The Lump Had Gears (`/2026/08/18/the-lump-had-gears/`)
- `post-sections.insert` at index **40** (appended as the last top-level block); lock: modified `2026-10-29T15:50:32`, content_hash `e7be9cf3b7159f9e4f6bfed0bedd5ea31a37ce74`; duplicates: none
- **The Lycurgus Cup: The Roman Glass That Changes Color**: Both are ancient objects that modern analysis explained; the Antikythera post already points readers at what instruments reveal.
```html
<!-- wp:group {"className":"fv-related-reading","layout":{"type":"constrained"}} --><div class="wp-block-group fv-related-reading"><!-- wp:heading --><h2 class="wp-block-heading">Related case study</h2><!-- /wp:heading --><!-- wp:list --><ul class="wp-block-list"><li><a href="https://finalvestige.com/2026/11/02/lycurgus-cup/">The Lycurgus Cup: The Roman Glass That Changes Color</a></li></ul><!-- /wp:list --></div><!-- /wp:group -->
```

### Page/post 1122: The Missing Caption (`/the-missing-caption/`)
- `page-sections.insert` at index **3** (appended as the last top-level block); lock: modified `2026-11-02T21:41:04`, content_hash `325dbd1f21c0c9bbdae3b708ad7e47b379cefac2`; duplicates: none
- **Change Blindness: Why You Miss Big Changes Right in Front of You**: Photograph-comparison guide; change blindness explains why people miss differences between two images.
```html
<!-- wp:group {"className":"fv-related-reading","layout":{"type":"constrained"}} --><div class="wp-block-group fv-related-reading"><!-- wp:heading --><h2 class="wp-block-heading">Related case study</h2><!-- /wp:heading --><!-- wp:list --><ul class="wp-block-list"><li><a href="https://finalvestige.com/2026/11/02/change-blindness/">Change Blindness: Why You Miss Big Changes Right in Front of You</a></li></ul><!-- /wp:list --></div><!-- /wp:group -->
```

### Page/post 1338: Research Sources (`/free-resources/research-sources/`)
- `page-sections.insert` at index **3** (appended as the last top-level block); lock: modified `2026-10-29T12:50:46`, content_hash `4c4f8f303c55ac56d3472b9f5db81038be33c064`; duplicates: none
- **Change Blindness: Why You Miss Big Changes Right in Front of You**: Research Sources is where the change-blindness post already sends readers from its side; this makes the link reciprocal.
```html
<!-- wp:group {"className":"fv-related-reading","layout":{"type":"constrained"}} --><div class="wp-block-group fv-related-reading"><!-- wp:heading --><h2 class="wp-block-heading">Related case study</h2><!-- /wp:heading --><!-- wp:list --><ul class="wp-block-list"><li><a href="https://finalvestige.com/2026/11/02/change-blindness/">Change Blindness: Why You Miss Big Changes Right in Front of You</a></li></ul><!-- /wp:list --></div><!-- /wp:group -->
```

### Page/post 1377: Puységur’s Animal Magnetism Files (`/free-resources/puysegurs-animal-magnetism-files/`)
- `page-sections.insert` at index **1** (appended as the last top-level block); lock: modified `2026-10-23T02:10:19`, content_hash `108c81d667f53b52a9d3c0cdbdbb9414195f1e34`; duplicates: none
- **Mesmerism: What Franklin’s 1784 Commission Actually Found**: The Puységur files page is the continuation of the Mesmer story (Mesmer's follower); the post already links to it, this makes it reciprocal.
```html
<!-- wp:group {"className":"fv-related-reading","layout":{"type":"constrained"}} --><div class="wp-block-group fv-related-reading"><!-- wp:heading --><h2 class="wp-block-heading">Related case study</h2><!-- /wp:heading --><!-- wp:list --><ul class="wp-block-list"><li><a href="https://finalvestige.com/2026/11/02/mesmerism/">Mesmerism: What Franklin’s 1784 Commission Actually Found</a></li></ul><!-- /wp:list --></div><!-- /wp:group -->
```

### Page/post 498: Primary Historical Sources & Archives (`/watch/primary-sources/`)
- `page-sections.insert` at index **12** (appended as the last top-level block); lock: modified `2026-10-29T21:21:30`, content_hash `20e9fd2b28d39779763e0d1d2d259f5b97a64df1`; duplicates: none
- **Mesmerism: What Franklin’s 1784 Commission Actually Found**: Primary-sources hub: the 1784 commission report is a primary source.
```html
<!-- wp:group {"className":"fv-related-reading","layout":{"type":"constrained"}} --><div class="wp-block-group fv-related-reading"><!-- wp:heading --><h2 class="wp-block-heading">Related case study</h2><!-- /wp:heading --><!-- wp:list --><ul class="wp-block-list"><li><a href="https://finalvestige.com/2026/11/02/mesmerism/">Mesmerism: What Franklin’s 1784 Commission Actually Found</a></li></ul><!-- /wp:list --></div><!-- /wp:group -->
```

### Page/post 1044: The Findspot (`/the-findspot/`)
- `page-sections.insert` at index **6** (appended as the last top-level block); lock: modified `2026-11-02T21:40:56`, content_hash `fd368ad49a80029260dbc344369a23c2eaddf13a`; duplicates: none
- **Crystal Skulls: What the Evidence Says About Their Age**: Find-context guide: crystal skulls are the standard example of objects with no recorded find context.
```html
<!-- wp:group {"className":"fv-related-reading","layout":{"type":"constrained"}} --><div class="wp-block-group fv-related-reading"><!-- wp:heading --><h2 class="wp-block-heading">Related case study</h2><!-- /wp:heading --><!-- wp:list --><ul class="wp-block-list"><li><a href="https://finalvestige.com/2026/11/02/crystal-skulls/">Crystal Skulls: What the Evidence Says About Their Age</a></li></ul><!-- /wp:list --></div><!-- /wp:group -->
```

## Risks and checks for when this is applied

- Pages 499, 501 and 498 are styled "learning" pages built from several custom groups and CSS `html` blocks; an appended plain group should inherit the theme but **must be checked visually** after applying (remove the block if it looks wrong; rollback = `page-sections.remove` of the `fv-related-reading` block).
- Pages 1122 and 1044 were last modified by my 2026-11-02 meta edit (21:41:04 and 21:40:56), which is why their tokens differ from the earlier snapshot.
- The Lycurgus Cup -> The Working Order link was dropped (no compelling editorial connection). That post's block carries one link (They Painted Over Archimedes); it already has four other internal links.
- Do not change the sources list, FAQ headings or JSON-LD of the new posts; the proposal inserts before the JSON-LD block and leaves it last.
- After applying: re-crawl, confirm one Article + one FAQPage + one BreadcrumbList still render on each new post, and record before/after content hashes in the ledger.
