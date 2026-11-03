"""Build the SEO change set (meta + related-reading inserts) from the pre-edit snapshot.

Reads  docs/seo/evidence/seo-prestate-2026-11-02.json   (captured read-only from wp-admin, context=edit)
Writes docs/seo/evidence/changeset.json and docs/seo/04-CHANGESET-DIFFS.md
Run:   PYTHONUTF8=1 python docs/seo/tools/build_changeset.py
"""
import json, hashlib, html, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parents[1]
SNAP = {x["id"]: x for x in json.loads((ROOT / "evidence/seo-prestate-2026-11-02.json").read_text(encoding="utf-8"))}
B = " | Final Vestige"

# ---- meta: SEO title (jetpack_seo_html_title) -------------------------------------------------
TITLES = {
 # 18 pages whose SEO title was empty, so WordPress rendered "<name> - FINAL VESTIGE"
 1480: "Final Vestige Podcast | Evidence-First True Stories",
 1316: "Andrew Do and Orange County COVID Relief Funds" + B,
 1315: "Maximus: Public Money, Private Infrastructure" + B,
 1314: "Iraq WMD Intelligence vs. Public Claims" + B,
 1313: "Watergate: The Plumbers and Abuse of Power" + B,
 1312: "Gabriel Fernandez: Warnings Already in the System" + B,
 1310: "The Accountability Ledger" + B,
 1309: "Accountability Watch" + B,
 1308: "Votes & Decisions" + B,
 1307: "Abuse of Power: Document-Driven Investigations" + B,
 1306: "Public Money & Private Power" + B,
 1305: "Failures to Protect" + B,
 1304: "The Public Record: Evidence-First Investigations" + B,
 1311: "Evidence Room: Primary Sources Behind The Public Record" + B,
 747:  "The Exchange: History & Engineering Community" + B,
 16:   "Terms & Disclaimer" + B,
 15:   "Privacy Policy" + B,
 14:   "Affiliate Disclosure" + B,
 # 22 posts whose title put the entity after 60+ characters of hook (entity moved first, claim unchanged)
 299: "Why the Warship Vasa Sank on Its Maiden Voyage" + B,
 290: "Camp Century & Project Iceworm: The Base Beneath Greenland" + B,
 287: "The 1980 Sunshine Skyway Bridge Disaster" + B,
 285: "Three Mile Island: The Indicator That Wasn’t the Valve" + B,
 283: "Iroquois Theatre Fire: The Door Hardware It Changed" + B,
 280: "USS Pueblo and the Intelligence They Couldn’t Destroy" + B,
 279: "Cosmos 954 and Operation Morning Light" + B,
 278: "Lady Be Good: The Crew Lost in the Sahara" + B,
 274: "USS Tang: The Torpedo That Came Back and the Escape" + B,
 269: "Vincent Coleman and the Halifax Explosion" + B,
 258: "Silver Bridge Collapse: The Crack Inspectors Couldn’t See" + B,
 256: "Black Tom Explosion and the Statue of Liberty" + B,
 253: "The General Slocum Disaster and Its Life Preservers" + B,
 252: "Herculaneum Scrolls: Mistaken for Charcoal" + B,
 221: "SL-1 Nuclear Reactor Accident (1961): The Four-Inch Rod" + B,
 220: "USS Thresher and the Birth of SUBSAFE" + B,
 216: "1947 Texas City Disaster: The Fire Department" + B,
 214: "SS Eastland Disaster of 1915 and the Lifeboats" + B,
 211: "Port Chicago Disaster and the 1944 Mutiny Trial" + B,
 190: "1904 Baltimore Fire: How It Changed Firefighting Standards" + B,
 166: "St. Francis Dam Disaster, 1928: Checked That Morning" + B,
 156: "How Galveston Raised Itself After the 1900 Hurricane" + B,
}

# ---- meta: description (advanced_seo_description), only where current length >200 or <80 --------
DESCS = {
 1484: "The 1937 New London inquiry found a probable ignition path beneath the school but not where the gas came from. Federal evidence, sources and transcript.",
 1148: "Browse 205 curated historical manuals, technical reports, government investigations and primary sources, with subject filters and direct Internet Archive links.",
 1127: "A research guide to reconstructing historical households and city blocks with census schedules, enumeration district maps, city directories and Sanborn maps.",
 1125: "A research guide to reading old-building evidence: construction seams, blocked openings, paint and plaster ghosts, phase mapping and non-destructive methods.",
 1123: "A research guide to historical paper evidence: laid and wove structure, watermarks, folds, provenance, later repairs and responsible authentication language.",
 1122: "A research guide to identifying and dating historical photographs using captions, neighboring frames, call numbers, directories, maps and confidence grades.",
 1120: "A field manual for reconstructing historical machines and industrial processes with HAER records, patents, photographs, production evidence and change history.",
 1060: "A free field manual for reading historical store ledgers, daybooks and cash books: debits, credits, payment in kind, running balances and merchant inventories.",
 1054: "A free field manual for researching historical property boundaries: PLSS descriptions, GLO survey plats, land patents, tract books, monuments and resurveys.",
 1044: "A free field manual for documenting accidental historical finds without losing their context: photos, location, disturbance, reporting and legal boundaries.",
 1033: "A free field manual for building an emergency communication plan: backup paths, an out-of-area contact, check-in windows, power planning and no-comms fallbacks.",
 1029: "A free guide to reconstructing historical engineering failures: event clocks, cause stacks, official reports, evidence grading and recommendation tracking.",
 1027: "A free field guide to identifying historical screw threads and fasteners (Whitworth, Sellers, Unified, metric, Acme) and separating originals from repairs.",
 16:   "Final Vestige terms of use: what it publishes, the limits of historical records, and why content is not professional legal, medical or engineering advice.",
 15:   "How Final Vestige receives and uses information you provide, such as an email address for The Dispatch, plus technical data collected by service providers.",
 14:   "Some Final Vestige links are affiliate links. How commissions work, why the seller sets the price, and why affiliates never control editorial conclusions.",
 370:  "When LST-353 exploded at Pearl Harbor in 1944, fire left some mooring lines unreachable, helping turn one explosion into a harbor-wide disaster.",
 285:  "At Three Mile Island in 1979, the control room indicated a relief valve had closed. It had not, and that gap helped turn a shutdown into a partial meltdown.",
 269:  "Vincent Coleman died after warning the railway about the Halifax Explosion. Whether he saved a train is disputed. What his last message did may matter more.",
 221:  "At Idaho’s SL-1 reactor in 1961, a procedure allowed the control rod only four inches of travel. Investigators found it about twenty inches withdrawn.",
 216:  "When the Grandcamp caught fire in Texas City in 1947, the city sent all four of its fire trucks to the docks. Minutes later the ship exploded.",
}
SCHEMA_TEST = {1029: "article"}   # jetpack_seo_schema_type test on one page; revert to "" if no Article JSON-LD appears

# ---- related-reading inserts --------------------------------------------------------------------
def link(i):
    return SNAP[i]["link"]


def visible_title(i):
    return re.sub(r"\s+", " ", html.unescape(SNAP[i]["title_raw"])).strip()


GUIDE_FC = 1029
GUIDE_AT = 189
FC_POSTS = {  # engineering-failure case-study ring; each post gets the guide plus three neighbours
 291: [166, 146, 276], 166: [291, 146, 258], 146: [291, 166, 258], 258: [276, 287, 291],
 276: [258, 287, 166], 287: [258, 276, 285], 285: [221, 287, 258], 221: [285, 291, 258],
}
AT_POSTS = {  # disputed-or-incomplete-record case studies -> The Archive Trail
 434: [269, 433], 269: [434, 433], 433: [434, 269],
}
ACCT = {  # accountability case pages -> parent hub, sibling case, Evidence Room, The Public Record
 1313: dict(parent=1307, sib=[1314]), 1314: dict(parent=1307, sib=[1313]),
 1316: dict(parent=1306, sib=[1315]), 1315: dict(parent=1306, sib=[1316]),
 1312: dict(parent=1305, sib=[]),
}


def li(i):
    return f'<li><a href="{link(i)}">{html.escape(visible_title(i), quote=False)}</a></li>'


def group(heading, intro, items):
    ul = "".join(items)
    return ('<!-- wp:group {"className":"fv-related-reading","layout":{"type":"constrained"}} -->'
            '<div class="wp-block-group fv-related-reading">'
            f'<!-- wp:heading --><h2 class="wp-block-heading">{heading}</h2><!-- /wp:heading -->'
            + (f'<!-- wp:paragraph --><p>{intro}</p><!-- /wp:paragraph -->' if intro else "")
            + f'<!-- wp:list --><ul class="wp-block-list">{ul}</ul><!-- /wp:list --></div><!-- /wp:group -->')


INSERTS = []


def add_insert(i, kind, markup, note):
    s = SNAP[i]
    INSERTS.append(dict(id=i, kind=kind, op=("post-sections.insert" if s["type"] == "post" else "page-sections.insert"),
        index=s["blocks"], expected_modified=s["modified"], expected_content_hash=s["content_sha1"],
        expected_block_type="core/group", block_markup=markup,
        block_markup_sha1=hashlib.sha1(markup.encode()).hexdigest(), note=note))


for pid, nb in FC_POSTS.items():
    m = group("Related reading",
        f'Method: <a href="{link(GUIDE_FC)}">The Failure Chain</a>, a free guide to reconstructing historical engineering failures from the record.',
        [li(n) for n in nb])
    add_insert(pid, "failure-chain", m, "post -> The Failure Chain + 3 case studies")
for pid, nb in AT_POSTS.items():
    m = group("Related reading",
        f'Method: <a href="{link(GUIDE_AT)}">The Archive Trail</a>, a field kit for verifying historical claims and tracing contradictions in the record.',
        [li(n) for n in nb])
    add_insert(pid, "archive-trail", m, "post -> The Archive Trail + 2 posts with disputed or incomplete records")
add_insert(GUIDE_FC, "failure-chain-hub", group("Worked examples on Final Vestige",
    "Case studies on this site that apply these methods to specific failures.",
    [li(n) for n in [291, 166, 146, 258, 276, 287, 285, 221, 621]]), "guide page -> 9 case studies")
add_insert(GUIDE_AT, "archive-trail-hub", group("Case studies where the record is disputed or incomplete",
    "Posts on this site that show these verification habits in use.",
    [li(n) for n in [434, 269, 433]]), "guide page -> 3 case studies")
for pid, c in ACCT.items():
    items = [li(c["parent"]), *[li(n) for n in c["sib"]], li(1311), li(1304)]
    add_insert(pid, "accountability", group("More from The Public Record", "", items),
               "case page -> parent hub, sibling case, Evidence Room, The Public Record")

# ---- meta change records ------------------------------------------------------------------------
META = []
for i in sorted(set(TITLES) | set(DESCS) | set(SCHEMA_TEST)):
    s = SNAP[i]
    ch = {}
    if i in TITLES:
        ch["jetpack_seo_html_title"] = [s["seo_title"], TITLES[i]]
    if i in DESCS:
        ch["advanced_seo_description"] = [s["seo_desc"], DESCS[i]]
    if i in SCHEMA_TEST:
        ch["jetpack_seo_schema_type"] = [s["schema_type"], SCHEMA_TEST[i]]
    META.append(dict(id=i, type=s["type"], op=("posts.update" if s["type"] == "post" else "pages.update"),
                     url=s["link"], modified_before=s["modified"], changes=ch))

# ---- sanity checks ------------------------------------------------------------------------------
bad = [(i, len(d)) for i, d in DESCS.items() if len(d) > 160]
bad_t = [(i, len(t)) for i, t in TITLES.items() if len(t) > 75]
assert not bad, f"descriptions over 160: {bad}"
assert not bad_t, f"titles over 75: {bad_t}"
for i in list(TITLES) + list(DESCS) + [x["id"] for x in INSERTS]:
    assert i in SNAP, i
for i in TITLES:
    if i in range(1304, 1317) or i in (1480, 747, 16, 15, 14):
        assert not SNAP[i]["seo_title"], f"{i} already has a title"

out = dict(generated_from="evidence/seo-prestate-2026-11-02.json", meta=META, inserts=INSERTS)
(ROOT / "evidence/changeset.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

# ---- human-readable diff ----------------------------------------------------------------------------
NAMES = {"jetpack_seo_html_title": "SEO title", "advanced_seo_description": "meta description", "jetpack_seo_schema_type": "schema type"}
L = ["# 04 - Change set: exact diffs (proposed, not applied until approved)", "",
     "Generated by `tools/build_changeset.py` from the read-only pre-edit snapshot. `before` is the raw stored value (empty = WordPress falls back to its default).", "",
     f"- Meta edits: {len(META)} items ({sum(1 for m in META if m['type']=='page')} pages, {sum(1 for m in META if m['type']=='post')} posts). No body content changes.",
     f"- Related-reading inserts: {len(INSERTS)} (one new top-level block appended at the end of each; nothing existing is altered). Page 6 (homepage) is in neither list.", "",
     "## A. Meta changes (title / description / schema type)", "", "| ID | Path | Field | Before | After | Len |", "|---|---|---|---|---|---|"]
for m in META:
    for f, (b, a) in m["changes"].items():
        before = (b or "(empty)").replace("|", "\\|")
        after = a.replace("|", "\\|")
        L.append(f"| {m['id']} | {m['url'].replace('https://finalvestige.com', '')} | {NAMES[f]} | {before} | {after} | {len(a)} |")
L += ["", "## B. Related-reading inserts (exact block markup)", ""]
for x in INSERTS:
    L += [f"### {x['id']} - {SNAP[x['id']]['link'].replace('https://finalvestige.com', '')}",
          f"- {x['note']}; `{x['op']}` at index {x['index']} (current block count); lock tokens modified `{x['expected_modified']}`, content_hash `{x['expected_content_hash']}`.",
          "```html", x["block_markup"], "```", ""]
(ROOT / "04-CHANGESET-DIFFS.md").write_text("\n".join(L), encoding="utf-8")
print(len(META), "meta items;", len(INSERTS), "inserts")
