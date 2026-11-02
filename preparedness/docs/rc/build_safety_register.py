"""Generate the article-by-article safety register from the integrated candidate (machine-assembled; NOT a review).
Usage: python build_safety_register.py PREP_DIR(simulated copy) FIGURE_CHECKS.json SOURCE_ACCESS.json SX_REGISTER.md OUT_PREFIX
Every row stays NOT REVIEWED. The risk tier is a transparent keyword heuristic to order human review, not a safety judgment.
"""
import csv, html, json, re, sys
from collections import defaultdict
from pathlib import Path

PREP, FIG, ACC, SX, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]), sys.argv[5]
sys.path.insert(0, str(PREP / "tools"))
import build  # noqa: E402

lib = build.Library(root=PREP)
figs = json.loads(FIG.read_text(encoding="utf-8"))
acc = {a["url"]: a for a in json.loads(ACC.read_text(encoding="utf-8"))}
CATS = {
    "1 drinking water": r"bleach|chlorin|disinfect|boil|filter|iodine|purif|cistern|rain ?barrel|potable",
    "2 CO/combustion/heat": r"carbon monoxide|generator|kerosene|charcoal|propane|camp stove|space heater|fireplace|wood ?stove|combustion",
    "3 fire/evacuation/shelter": r"smoke alarm|escape plan|evacuat|shelter in place|shelter-in-place|high-rise|ventilat|seal(ing)? (the )?(room|door)",
    "4 food preservation": r"canning|curing|botulism|jerky|pickl|ferment|smok(ed|ing|ehouse)|salt(ed|ing)? (beef|pork|meat)|pemmican|dehydrat|root cellar",
    "5 medical/first aid": r"medicin|insulin|first aid|heat stroke|hypothermia|frostbite|dialysis|oxygen|prescription|medical device|infection|dehydration",
    "6 household chemicals": r"bleach|ammonia|disinfectant|pesticide|chemical|hazmat|sanitizer",
    "7 electrical/battery": r"battery|batteries|extension cord|power station|lithium|solar|charger|backfeed|transfer switch|inverter",
    "8 vulnerable people": r"infant|baby|child|older adult|elderly|pregnan|disabilit|wheelchair|pets?\b",
}
CONSEQ = {"1 drinking water", "2 CO/combustion/heat", "4 food preservation", "5 medical/first aid"}
sx = defaultdict(list)
for line in SX.read_text(encoding="utf-8").splitlines():
    m = re.match(r"\| (SX-\d+) \| (\w+) \|(.*)", line)
    if m:
        for slug in re.findall(r"`([a-z0-9\-]+)`", m.group(3).split("|")[0]):
            if slug in lib.articles:
                sx[slug].append(f"{m.group(1)} ({m.group(2)})")
fig_by = defaultdict(lambda: {"total": 0, "all": 0, "partial": 0, "none": 0, "untested": 0})
for x in figs:
    d = fig_by[x["slug"]]; d["total"] += 1
    d[{"ALL_FIGURES_FOUND": "all", "SOME_FIGURES_NOT_FOUND": "partial", "NO_FIGURES_FOUND": "none", "NO_TESTABLE_SOURCE": "untested"}[x["status"]]] += 1
rows = []
for slug, meta in sorted(lib.articles.items()):
    body = meta["_body"]; text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", body))).lower()
    ids = list(dict.fromkeys(re.findall(r"\{\{cite:([a-z0-9\-]+)\}\}", body)))
    srcs = [lib.source_for(meta, i) for i in ids]
    unreachable = [i for i, s in zip(ids, srcs) if s["url"] in acc and not acc[s["url"]]["ok"]]
    hits = {k: len(re.findall(v, text)) for k, v in CATS.items()}
    cats = [k for k, n in hits.items() if n >= 3]
    conseq = [c for c in cats if c in CONSEQ]
    modern = meta["track"] != "history"
    tier = "HIGH" if (modern and len(conseq) >= 2) or (modern and meta.get("gate")) and conseq else ("MEDIUM" if conseq or (modern and cats) else "LOW")
    if meta.get("kind") == "tool":
        tier = "HIGH" if conseq else "MEDIUM"
    sr = meta.get("safety_review", {})
    fb = fig_by.get(slug, {"total": 0, "all": 0, "partial": 0, "none": 0, "untested": 0})
    rows.append({
        "slug": slug, "kind": meta.get("kind", "article"), "track": meta["track"], "section": meta["section"], "gated": bool(meta.get("gate")),
        "safety_review_recorded": sr.get("state"), "reviewer_recorded": sr.get("reviewer") or "", "human_review_complete": "NO",
        "risk_tier_heuristic": tier, "consequential_categories": "; ".join(conseq) or "-", "other_categories": "; ".join(c for c in cats if c not in conseq) or "-",
        "distinct_sources": len(ids), "sources_human_link_checked": sum(1 for s in srcs if s.get("human_link_check") is True), "sources_unread_by_machine": len(unreachable), "unread_source_ids": "; ".join(unreachable) or "-",
        "figure_blocks": fb["total"], "figure_all_found": fb["all"], "figure_not_all_found": fb["partial"] + fb["none"], "figure_untested": fb["untested"],
        "open_safety_exceptions": "; ".join(sx.get(slug, [])) or "-",
        "verdict_if_historical": meta.get("verdict") or "-",
        "blockers": "human safety review; human link check; independent QD" + ("; resolve open exceptions" if sx.get(slug) else "") + ("; read unreachable sources" if unreachable else ""),
    })
cols = list(rows[0])
with open(OUT + ".csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n"); w.writeheader(); w.writerows(rows)
tiers = defaultdict(int)
for r in rows:
    tiers[r["risk_tier_heuristic"]] += 1
state = defaultdict(int)
for r in rows:
    state[(r["kind"], r["safety_review_recorded"])] += 1
print("rows", len(rows), dict(tiers), dict(state))
print("articles with open exceptions:", sum(1 for r in rows if r["open_safety_exceptions"] != "-"), "| with unread sources:", sum(1 for r in rows if r["sources_unread_by_machine"]))
md = ["# Article-by-article safety register (machine-assembled; every row NOT REVIEWED)", "",
      "Built by `docs/rc/build_safety_register.py` from the integrated candidate. **No row records a completed human, QD or founder review.** The risk tier is a keyword heuristic (consequential categories: drinking water, CO/combustion, food preservation, medical) to order the human review queue; it is not a safety judgment. Open exceptions come from `docs/r48/SAFETY-EXCEPTION-REGISTER-2026-11-01.md` (SX ids).", "",
      "| Slug | Kind | Track | Tier | Recorded state | Consequential categories | Sources (unread) | Figure blocks (all/not-all/untested) | Open exceptions |", "|---|---|---|---|---|---|---|---|---|"]
for r in sorted(rows, key=lambda r: ({"HIGH": 0, "MEDIUM": 1, "LOW": 2}[r["risk_tier_heuristic"]], r["slug"])):
    md.append(f"| {r['slug']} | {r['kind']} | {r['track']} | {r['risk_tier_heuristic']} | {r['safety_review_recorded']} | {r['consequential_categories']} | {r['distinct_sources']} ({r['sources_unread_by_machine']}) | {r['figure_blocks']} ({r['figure_all_found']}/{r['figure_not_all_found']}/{r['figure_untested']}) | {r['open_safety_exceptions']} |")
Path(OUT + ".md").write_text("\n".join(md) + "\n", encoding="utf-8", newline="\n")
