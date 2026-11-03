"""Build the (unapplied) linking proposal for the five 2026-11-02 content-package posts.

Locks (expected_modified / expected_content_hash / index) were read with post-sections.list /
page-sections.list on 2026-11-02 and are RECORDED BELOW. They go stale as soon as any target is edited
(e.g. by the content QA), so re-read them immediately before applying.

Run:  PYTHONUTF8=1 python docs/seo/tools/build_newposts_proposal.py
Out:  docs/seo/06-NEW-POSTS-LINKING-PROPOSAL.md, docs/seo/evidence/newposts-proposal.json
"""
import json, re, html, hashlib, pathlib, urllib.request, time

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = "https://finalvestige.com"
AFTER = {x["id"]: x for x in json.loads((ROOT / "evidence/crawl-after-2026-11-02.json").read_text(encoding="utf-8"))}


def fetch(u):
    for _ in range(4):
        try:
            return urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=40).read().decode("utf-8", "replace")
        except Exception:
            time.sleep(3)
    return ""


def norm(l):
    l = l.split("#")[0].split("?")[0]
    if l.startswith("/"):
        l = BASE + l
    return l if l.endswith("/") else l + "/"


def live_links(url):
    h = fetch(url)
    m = re.search(r"<main.*?</main>", h, re.S | re.I)
    return {norm(l) for l in re.findall(r'<a\s[^>]*href=["\'](.*?)["\']', (m.group(0) if m else h), re.I)}


# ---- the five new posts: id, url, title, lock tokens as read, insertion index (immediately before the closing FAQPage JSON-LD html block)
NEW = {
 1917: dict(url=f"{BASE}/2026/11/02/piri-reis-map/", title="The Piri Reis Map: What the 1513 Chart Actually Shows",
            modified="2026-11-02T20:48:54", hash="087bd41bbb4e66433ac377d82eeebbfe81fa5d7c", sections=27, index=26),
 1920: dict(url=f"{BASE}/2026/11/02/lycurgus-cup/", title="The Lycurgus Cup: The Roman Glass That Changes Color",
            modified="2026-11-02T20:50:12", hash="c61b8530eb57d834814d8d09849e13cde83d7e38", sections=25, index=24),
 1922: dict(url=f"{BASE}/2026/11/02/change-blindness/", title="Change Blindness: Why You Miss Big Changes Right in Front of You",
            modified="2026-11-02T20:51:39", hash="5ff50b4a0571a69beca449fee71acf8e19d17f09", sections=30, index=29),
 1924: dict(url=f"{BASE}/2026/11/02/mesmerism/", title="Mesmerism: What Franklin’s 1784 Commission Actually Found",
            modified="2026-11-02T20:52:58", hash="3d8f41cf528f27baf08ed4170079006f76834198", sections=33, index=32),
 1926: dict(url=f"{BASE}/2026/11/02/crystal-skulls/", title="Crystal Skulls: What the Evidence Says About Their Age",
            modified="2026-11-02T20:54:10", hash="b097f1ad3460780efabad87f24a7d2af57256eda", sections=26, index=25),
}

# ---- existing targets (read 2026-11-02): url, title, op, modified, hash, sections (= append index)
EXIST = {
 499:  dict(url=f"{BASE}/watch/maps-places/", title="Historical Maps & Place Research", op="page", modified="2026-10-29T21:22:26", hash="a12b1816450fb6f9138d44d3d0a2b9494a2b31a1", index=10),
 193:  dict(url=f"{BASE}/the-lost-landscape/", title="The Lost Landscape", op="page", modified="2026-08-26T11:16:25", hash="bcc5bbea15f18003d74919b89c0225e62d09a6e6", index=2),
 501:  dict(url=f"{BASE}/watch/objects-archaeology/", title="Archaeology, Objects & Museum Collections", op="page", modified="2026-08-31T22:32:56", hash="bfe9a11f9c5cd27c704e15b7bcce6d72c825dbb4", index=10),
 254:  dict(url=f"{BASE}/2026/08/18/the-lump-had-gears/", title="The Lump Had Gears", op="post", modified="2026-10-29T15:50:32", hash="e7be9cf3b7159f9e4f6bfed0bedd5ea31a37ce74", index=40),
 1122: dict(url=f"{BASE}/the-missing-caption/", title="The Missing Caption", op="page", modified="2026-11-02T21:41:04", hash="325dbd1f21c0c9bbdae3b708ad7e47b379cefac2", index=3),
 1338: dict(url=f"{BASE}/free-resources/research-sources/", title="Research Sources", op="page", modified="2026-10-29T12:50:46", hash="4c4f8f303c55ac56d3472b9f5db81038be33c064", index=3),
 1377: dict(url=f"{BASE}/free-resources/puysegurs-animal-magnetism-files/", title="Puységur’s Animal Magnetism Files", op="page", modified="2026-10-23T02:10:19", hash="108c81d667f53b52a9d3c0cdbdbb9414195f1e34", index=1),
 498:  dict(url=f"{BASE}/watch/primary-sources/", title="Primary Historical Sources & Archives", op="page", modified="2026-10-29T21:21:30", hash="20e9fd2b28d39779763e0d1d2d259f5b97a64df1", index=12),
 1044: dict(url=f"{BASE}/the-findspot/", title="The Findspot", op="page", modified="2026-11-02T21:40:56", hash="fd368ad49a80029260dbc344369a23c2eaddf13a", index=6),
}
# outbound targets that are not locked (we only link to them)
LINKABLE = {
 189:  ("The Archive Trail", f"{BASE}/the-archive-trail/"),
 193:  ("The Lost Landscape", f"{BASE}/the-lost-landscape/"),
 1029: ("The Failure Chain", f"{BASE}/the-failure-chain/"),
 1122: ("The Missing Caption", f"{BASE}/the-missing-caption/"),
 1120: ("The Working Order", f"{BASE}/the-working-order/"),
 1123: ("The Paper Witness", f"{BASE}/the-paper-witness/"),
 1044: ("The Findspot", f"{BASE}/the-findspot/"),
 498:  ("Primary Historical Sources & Archives", f"{BASE}/watch/primary-sources/"),
 268:  ("They Painted Over Archimedes", f"{BASE}/2026/08/18/they-painted-over-archimedes/"),
}

# ---- OUTBOUND from each new post: (target id, relevance reason)
OUT = {
 1917: [(193, "The post is about reading an old chart's own notes and sources; The Lost Landscape is the site's guide to reconstructing places from old maps."),
        (189, "The Antarctica claim is the classic claim-versus-record case; The Archive Trail is the site's field kit for verifying historical claims.")],
 1920: [(268, "Both are ancient objects whose real nature was recovered with modern analysis (this post: electron microscopy of the glass)."),
        ],  # The Working Order link dropped on the founder's instruction (no compelling editorial connection); 19 links remain
 1922: [(1029, "The post is about missed observations; The Failure Chain has a section on warning-to-action latency and evidence confidence for reading failures."),
        (1122, "Change blindness is the reason side-by-side photograph comparison fails; The Missing Caption is the site's guide to comparing and dating photographs.")],
 1924: [(189, "The 1784 report is the model of a controlled test of a claim; The Archive Trail is the site's field kit for verifying historical claims."),
        (498, "The commission's report is a primary source (cited from Project Gutenberg); this is the site's primary-sources hub.")],
 1926: [(1044, "The skulls' central problem is missing find context; The Findspot is the site's guide to documenting finds without losing context."),
        (1123, "The 2008 paper traces the skull's dealer and sale records; The Paper Witness is the site's guide to document provenance.")],
}

# ---- INBOUND to each new post: (existing target id, new post id, relevance reason)
IN = [
 (499, 1917, "The hub for historical maps and place research has no link to any map case study; this is the site's map-and-chart case study."),
 (193, 1917, "The old-maps method guide: a worked example of a single historical chart and what it does and does not show."),
 (501, 1920, "Objects hub: the Lycurgus Cup is an object case study."),
 (501, 1926, "Objects hub: crystal skulls are an object-authenticity case study (same block as the Lycurgus Cup)."),
 (254, 1920, "Both are ancient objects that modern analysis explained; the Antikythera post already points readers at what instruments reveal."),
 (1122, 1922, "Photograph-comparison guide; change blindness explains why people miss differences between two images."),
 (1338, 1922, "Research Sources is where the change-blindness post already sends readers from its side; this makes the link reciprocal."),
 (1377, 1924, "The Puységur files page is the continuation of the Mesmer story (Mesmer's follower); the post already links to it, this makes it reciprocal."),
 (498, 1924, "Primary-sources hub: the 1784 commission report is a primary source."),
 (1044, 1926, "Find-context guide: crystal skulls are the standard example of objects with no recorded find context."),
]


def li(href, text):
    return f'<li><a href="{href}">{html.escape(text, quote=False)}</a></li>'


def group(heading, items):
    return ('<!-- wp:group {"className":"fv-related-reading","layout":{"type":"constrained"}} --><div class="wp-block-group fv-related-reading">'
            f'<!-- wp:heading --><h2 class="wp-block-heading">{heading}</h2><!-- /wp:heading -->'
            f'<!-- wp:list --><ul class="wp-block-list">{"".join(items)}</ul><!-- /wp:list --></div><!-- /wp:group -->')


items = []
# outbound blocks: one per new post
for pid, rows in OUT.items():
    n = NEW[pid]
    existing = live_links(n["url"])
    dups = [LINKABLE[t][1] for t, _ in rows if norm(LINKABLE[t][1]) in existing]
    markup = group("Related reading", [li(LINKABLE[t][1], LINKABLE[t][0]) for t, _ in rows])
    items.append(dict(direction="outbound", target_id=pid, target_url=n["url"], op="post-sections.insert", index=n["index"],
                      expected_modified=n["modified"], expected_content_hash=n["hash"], expected_block_type="core/group", block_markup=markup,
                      links=[dict(to=LINKABLE[t][1], title=LINKABLE[t][0], reason=r) for t, r in rows], duplicates_found=dups,
                      insertion_note="immediately before the closing FAQPage JSON-LD html block, after the sources list"))
# inbound blocks: one per existing target (501 carries two links)
by_target = {}
for t, p, r in IN:
    by_target.setdefault(t, []).append((p, r))
for t, rows in by_target.items():
    e = EXIST[t]
    existing = AFTER[t]["internal_targets"] if t in AFTER else []
    existing = {norm(x) for x in existing}
    dups = [NEW[p]["url"] for p, _ in rows if norm(NEW[p]["url"]) in existing]
    heading = "Related case study" if len(rows) == 1 else "Related case studies"
    markup = group(heading, [li(NEW[p]["url"], NEW[p]["title"]) for p, _ in rows])
    items.append(dict(direction="inbound", target_id=t, target_url=e["url"], target_title=e["title"], op=f"{e['op']}-sections.insert", index=e["index"],
                      expected_modified=e["modified"], expected_content_hash=e["hash"], expected_block_type="core/group", block_markup=markup,
                      links=[dict(to=NEW[p]["url"], title=NEW[p]["title"], reason=r) for p, r in rows], duplicates_found=dups,
                      insertion_note="appended as the last top-level block"))

for it in items:
    it["block_markup_sha1"] = hashlib.sha1(it["block_markup"].encode()).hexdigest()
(ROOT / "evidence/newposts-proposal.json").write_text(json.dumps(dict(status="PROPOSED, NOT APPLIED", locks_read="2026-11-02 (stale after any edit)", items=items), ensure_ascii=False, indent=1), encoding="utf-8")

L = ["# 06 - Proposal: link the five 2026-11-02 posts (NOT APPLIED)", "",
     "Status: **proposal only. Nothing in this file has been applied.** Hold until the content QA on posts 1917, 1920, 1922, 1924 and 1926 lands; then re-read every lock, rebuild, show the diffs to the user and apply only with approval.", "",
     "**Locks go stale.** `expected_modified` / `expected_content_hash` / `index` below were read on 2026-11-02. Any edit to a target (including the QA corrections) invalidates them and the tool will refuse the write. Re-run `post-sections.list` / `page-sections.list` for each target immediately before applying; if the QA changes the number of top-level blocks on a new post, recompute its insertion index (the block just before the closing FAQPage JSON-LD `core/html`).", "",
     "Scope: the new posts' *body text is not edited*; each change appends one new `core/group` block. Metadata and schema of the new posts are not touched. Counts: "
     f"{sum(1 for i in items if i['direction']=='outbound')} outbound blocks (9 links: 2 per post except the Lycurgus Cup post, whose weaker The Working Order link was dropped), {sum(1 for i in items if i['direction']=='inbound')} inbound blocks on existing pages (10 links, 2 per new post). Total 19 links.", "",
     "## Duplicate check", "",
     "Each proposed link was compared with the links already present in the target's public `<main>` content (new posts fetched live from the public site; existing pages from `evidence/crawl-after-2026-11-02.json`). "
     f"Duplicates found: **{sum(len(i['duplicates_found']) for i in items)}**. For reference, the new posts already link out to these older posts, which are deliberately *not* proposed again: "
     "1917 -> maps-places, the-lump-had-gears, they-painted-over-archimedes, all-well-was-written-first, the-mountain-buried-the-door; "
     "1920 -> the-lump-had-gears, they-thought-the-books-were-charcoal, thirty-men-were-enough-vasa, objects-archaeology; "
     "1922 -> they-taught-the-lake-to-breathe, a-wall-in-the-dark, the-light-said-closed, ed-pulaski, research-sources; "
     "1924 -> how-petra-made-water-flow, add-no-more-load, all-well-was-written-first, change-blindness, puysegurs files; "
     "1926 -> boston-molasses, halifax, courrieres, lycurgus-cup, piri-reis-map, objects-archaeology.", "",
     "No link goes to a draft, to anything in the Preparedness Archive, or to the homepage.", "",
     "## A. Outbound: from each new post to existing pages", ""]
for it in [i for i in items if i["direction"] == "outbound"]:
    n = NEW[it["target_id"]]
    L += [f"### Post {it['target_id']}: {n['title']}", f"- `{it['op']}` at index **{it['index']}** ({it['insertion_note']}); lock: modified `{it['expected_modified']}`, content_hash `{it['expected_content_hash']}`; duplicates: {it['duplicates_found'] or 'none'}"]
    for l in it["links"]:
        L.append(f"- **{l['title']}** (`{l['to'].replace(BASE,'')}`): {l['reason']}")
    L += ["```html", it["block_markup"], "```", ""]
L += ["## B. Inbound: from existing pages to the new posts", ""]
for it in [i for i in items if i["direction"] == "inbound"]:
    L += [f"### Page/post {it['target_id']}: {it['target_title']} (`{it['target_url'].replace(BASE,'')}`)",
          f"- `{it['op']}` at index **{it['index']}** ({it['insertion_note']}); lock: modified `{it['expected_modified']}`, content_hash `{it['expected_content_hash']}`; duplicates: {it['duplicates_found'] or 'none'}"]
    for l in it["links"]:
        L.append(f"- **{l['title']}**: {l['reason']}")
    L += ["```html", it["block_markup"], "```", ""]
L += ["## Risks and checks for when this is applied", "",
      "- Pages 499, 501 and 498 are styled \"learning\" pages built from several custom groups and CSS `html` blocks; an appended plain group should inherit the theme but **must be checked visually** after applying (remove the block if it looks wrong; rollback = `page-sections.remove` of the `fv-related-reading` block).",
      "- Pages 1122 and 1044 were last modified by my 2026-11-02 meta edit (21:41:04 and 21:40:56), which is why their tokens differ from the earlier snapshot.",
      "- The Lycurgus Cup -> The Working Order link was dropped (no compelling editorial connection). That post's block carries one link (They Painted Over Archimedes); it already has four other internal links.",
      "- Do not change the sources list, FAQ headings or JSON-LD of the new posts; the proposal inserts before the JSON-LD block and leaves it last.",
      "- After applying: re-crawl, confirm one Article + one FAQPage + one BreadcrumbList still render on each new post, and record before/after content hashes in the ledger.", ""]
(ROOT / "06-NEW-POSTS-LINKING-PROPOSAL.md").write_text("\n".join(L), encoding="utf-8")
print(len(items), "blocks;", sum(len(i["duplicates_found"]) for i in items), "duplicates")
