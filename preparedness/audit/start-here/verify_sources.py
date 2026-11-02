#!/usr/bin/env python3
"""Automated source re-check for the Start Here cluster.  Run from the repo root:

    python -I preparedness/audit/start-here/verify_sources.py [--only SOURCE_ID ...]

What it does: fetches every source cited by the four Start Here articles (HTML via the installed Edge browser
through Playwright, so sites that block plain HTTP clients still load; PDFs via Playwright's request API plus
`pdftotext`), then records for each source: HTTP status, final URL, title, page-stated dates, a SHA-256 of the
normalized text, text length, and whether every 'anchor' phrase of each claim in claims.json is present.

What it does NOT do: it does not show that an article's paraphrase is faithful, that a human opened the link,
or that the whole page was read. Automated results live in ledger.json / claim-matrix.json and never touch
`human_link_check` in the source register, which is reserved for a human reviewer.
"""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, re, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]            # preparedness/
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402

ARTICLES = ["household-emergency-plan", "three-day-kit", "go-bags", "preparedness-real-households"]
DATE_RE = re.compile(r"(Last [Uu]pdated|Updated|Published|Reviewed|Last modified|Posted|Last Reviewed)[:\s]+"
                     r"([A-Z][a-z]{2,8}\.? \d{1,2}, \d{4}|\d{1,2}/\d{1,2}/\d{4})")


def norm(s: str) -> str:
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("–", "-").replace("—", "-").replace(" ", " ").replace("​", "")
    s = re.sub(r"[*_`#>]", "", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def cited_ids(lib: build.Library) -> list[str]:
    ids: list[str] = []
    for slug in ARTICLES:
        _, order = build.resolve_tokens(lib, lib.articles[slug])
        for i in order:
            if i not in ids:
                ids.append(i)
    return ids


def fetch_all(urls: dict[str, str]) -> dict[str, dict]:
    from playwright.sync_api import sync_playwright
    out: dict[str, dict] = {}
    tmp = Path(tempfile.mkdtemp(prefix="start-verify-"))
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge")
        ctx = browser.new_context(user_agent="Mozilla/5.0 (FinalVestige source verifier)")
        for sid, url in urls.items():
            rec = {"requested_url": url, "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                   "http_status": None, "final_url": None, "content_type": None, "title": None, "text": "", "error": None}
            try:
                if url.lower().split("?")[0].endswith(".pdf"):
                    r = ctx.request.get(url, timeout=60000)
                    rec.update(http_status=r.status, final_url=r.url, content_type=r.headers.get("content-type"))
                    if r.ok:
                        f = tmp / f"{sid}.pdf"
                        f.write_bytes(r.body())
                        if not shutil.which("pdftotext"):
                            raise RuntimeError("pdftotext not installed")
                        t = subprocess.run(["pdftotext", str(f), "-"], capture_output=True, text=True, timeout=120)
                        rec["text"] = t.stdout
                        rec["title"] = f.name
                else:
                    page = ctx.new_page()
                    resp = page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    page.wait_for_timeout(1500)
                    rec.update(http_status=resp.status if resp else None, final_url=page.url,
                               content_type=(resp.headers.get("content-type") if resp else None), title=page.title())
                    rec["text"] = page.evaluate(r"""() => { const c = document.body.cloneNode(true);
                        c.querySelectorAll('script,style,noscript').forEach(e => e.remove());
                        const alts = [...c.querySelectorAll('img[alt]')].map(i => i.alt).join('\n');
                        return c.textContent + '\n' + alts; }""")
                    page.close()
            except Exception as e:  # noqa: BLE001
                rec["error"] = f"{type(e).__name__}: {str(e)[:200]}"
            out[sid] = rec
        browser.close()
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--dump", default=None, help="directory to write the extracted text of each source (for debugging; not committed)")
    args = ap.parse_args()
    lib = build.Library()
    ids = cited_ids(lib)
    if args.only:
        ids = [i for i in ids if i in args.only]
    urls = {i: lib.register[i]["url"] for i in ids}
    fetched = fetch_all(urls)

    claims = json.loads((HERE / "claims.json").read_text(encoding="utf-8"))["claims"]
    ledger = []
    for sid in ids:
        f = fetched[sid]
        reg = lib.register[sid]
        text = f.pop("text")
        if args.dump:
            Path(args.dump).mkdir(parents=True, exist_ok=True)
            (Path(args.dump) / f"{sid}.txt").write_text(text, encoding="utf-8", newline="\n")
        n = norm(text)
        f["text_chars"] = len(text)
        f["text_sha256_normalized"] = hashlib.sha256(n.encode("utf-8")).hexdigest()
        f["page_stated_dates"] = sorted({" ".join(m) for m in DATE_RE.findall(text)})[:8]
        f["resolves"] = bool(f["http_status"] and 200 <= f["http_status"] < 300 and f["text_chars"] > 200)
        f["redirected"] = (f["final_url"] or "").rstrip("/") != reg["url"].rstrip("/")
        mine = [c["id"] for c in claims if c.get("source") == sid]
        results = {}
        for c in claims:
            if c.get("source") != sid:
                continue
            missing = [a for a in c["anchors"] if norm(a) not in n]
            present_bad = [a for a in c.get("anchors_absent", []) if norm(a) in n]
            if not c["anchors"] and not c.get("anchors_absent"):
                results[c["id"]] = {"anchors_found": None, "anchors_missing": [], "forbidden_found": [], "note": "no automated check possible; see manual_evidence"}
            else:
                results[c["id"]] = {"anchors_found": not missing, "anchors_missing": missing, "forbidden_found": present_bad}
        ledger.append({
            "source_id": sid, "register_title": reg["title"], "publisher": reg["publisher"], "kind": reg["kind"],
            "register_verified_on": reg.get("verified_on"), "register_published": reg.get("published"),
            "register_updated": reg.get("updated"), "human_link_check": reg.get("human_link_check"),
            "automated": f, "claim_checks": results, "claims_using_source": mine,
            "coverage_note": "Automated: URL fetched and anchor phrases located. This is NOT a human link check and does not prove the whole document was read or that an article paraphrase is faithful.",
        })
    (HERE / "ledger.json").write_text(json.dumps({"generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                                                   "tool": "verify_sources.py (Playwright/Edge + pdftotext)",
                                                   "sources": ledger}, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n")
    by_src = {l["source_id"]: l for l in ledger}
    matrix = []
    for c in claims:
        row = dict(c)
        if c.get("source") and c["source"] in by_src:
            r = by_src[c["source"]]
            row["automated_result"] = r["claim_checks"].get(c["id"])
            row["source_resolves"] = r["automated"]["resolves"]
            row["date_reviewed_automated"] = r["automated"]["fetched_at"][:10]
        elif c.get("source"):
            row["automated_result"] = None
            row["source_resolves"] = None
        matrix.append(row)
    (HERE / "claim-matrix.json").write_text(json.dumps(matrix, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n")

    bad_src = [l["source_id"] for l in ledger if not l["automated"]["resolves"]]
    bad_claims = [m["id"] for m in matrix if m.get("automated_result") and (m["automated_result"]["anchors_found"] is False or m["automated_result"]["forbidden_found"])]
    print(f"sources checked: {len(ledger)}; not resolving: {bad_src}")
    print(f"claims with a source: {sum(1 for m in matrix if m.get('source'))}; anchor failures: {bad_claims}")
    for m in matrix:
        if m["id"] in bad_claims:
            print(" ", m["id"], m["source"], m["automated_result"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
