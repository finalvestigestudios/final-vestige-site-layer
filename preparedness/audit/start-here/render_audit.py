#!/usr/bin/env python3
"""Render ledger.json + claim-matrix.json into human-readable SOURCE-AUDIT.md.  Run from the repo root:
    python -I preparedness/audit/start-here/render_audit.py
"""
import json
from pathlib import Path

H = Path(__file__).resolve().parent
led = json.loads((H / "ledger.json").read_text(encoding="utf-8"))
mat = json.loads((H / "claim-matrix.json").read_text(encoding="utf-8"))
out = []
out.append("# Start Here: source audit and claim matrix (generated)\n")
out.append(f"Generated {led['generated']} by `verify_sources.py` ({led['tool']}). Regenerate with the two commands in `README.md`.\n")
out.append("**What this is.** An automated re-fetch of every source the four Start Here articles cite, plus a check that short anchor phrases for each consequential claim are present in the fetched text. **What it is not.** It is not a human link check (`human_link_check` stays `false` for every source), it does not prove an article's paraphrase is faithful, and a phrase being present does not mean the whole page or PDF was read. Items marked `needs human` could not be confirmed by the tool.\n")
n_ok = sum(1 for s in led["sources"] if s["automated"]["resolves"])
out.append(f"**Sources:** {len(led['sources'])} fetched, {n_ok} resolved with usable text.\n")
sc = [m for m in mat if m.get("source")]
found = sum(1 for m in sc if (m.get("automated_result") or {}).get("anchors_found") is True)
failed = [m["id"] for m in sc if (m.get("automated_result") or {}).get("anchors_found") is False]
manual = [m["id"] for m in sc if (m.get("automated_result") or {}).get("anchors_found") is None]
out.append(f"**Claims with a source:** {len(sc)}; anchors found: {found}; anchor failures: {failed or 'none'}; not checkable by tool: {manual or 'none'}. Editorial (no source): {[m['id'] for m in mat if not m.get('source')]}.\n")
out.append("## Source ledger\n")
out.append("| Source | Publisher / kind | HTTP | Redirected | Page-stated dates | Text chars | Normalized-text SHA-256 (first 12) | Claims |")
out.append("|---|---|---|---|---|---|---|---|")
for s in led["sources"]:
    a = s["automated"]
    out.append(f"| `{s['source_id']}` | {s['publisher']} / {s['kind']} | {a['http_status']} | {'yes: ' + a['final_url'] if a['redirected'] else 'no'} | {'; '.join(a['page_stated_dates']) or 'none found'} | {a['text_chars']} | `{a['text_sha256_normalized'][:12]}` | {', '.join(s['claims_using_source']) or '(background only)'} |")
out.append("\n## Claim-to-source matrix\n")
out.append("Columns: claim, article, source, location in source, basis (direct = agency text reproduced; synthesis; interpretation; editorial), automated anchor result, confidence and limitations, who must review.\n")
out.append("| ID | Article | Claim | Source | Location | Basis | Automated | Confidence / limits | Review |")
out.append("|---|---|---|---|---|---|---|---|---|")
for m in mat:
    r = m.get("automated_result")
    if not m.get("source"):
        res = "n/a (editorial)"
    elif r is None:
        res = "source not fetched"
    elif r["anchors_found"] is True:
        res = "anchors found" + (" (absence confirmed)" if m.get("anchors_absent") else "")
    elif r["anchors_found"] is None:
        res = "needs human"
    else:
        res = "FAILED: " + "; ".join(r["anchors_missing"])
    lim = (m.get("confidence", "") + ". " + m.get("limits", "")).replace("|", "/")
    if m.get("manual_evidence"):
        lim += " Manual evidence: " + m["manual_evidence"].replace("|", "/")
    out.append(f"| {m['id']} | {m['article']} | {m['claim'].replace('|','/')} | `{m.get('source') or '-'}` | {m.get('location','').replace('|','/')} | {m['basis']} | {res} | {lim} | {m['review']} |")
(H / "SOURCE-AUDIT.md").write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
print("wrote SOURCE-AUDIT.md", len(out), "lines")
