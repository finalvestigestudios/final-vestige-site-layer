#!/usr/bin/env python3
"""R70 PRIVATE HOLD: source URL trust boundaries tied to each candidate citation.

Read-only: all 244 candidate source readings remain distinct by (origin, id),
even if IDs or URLs repeat. 2,173 candidate citation occurrences are traced
through R68 and R69 seals. URL syntax is NOT source access, claim support,
medical safety, human review, accessibility or publication authorization.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import hashlib
import importlib.util
import io
import ipaddress
import json
from pathlib import Path
import re
import sys
from urllib.parse import parse_qsl, unquote, urlsplit

SCHEMA = "r70-private-rc-source-url-and-citation-link-custody-v1"
R67_SCHEMA = "r67-original-to-release-candidate-source-custody-v1"
R68_SCHEMA = "r68-private-rc-document-citation-source-scope-v1"
R69_SCHEMA = "r69-private-rc-dom-citation-context-review-v1"
EXPECTED = (35, 6, 244, 2173)
HOLD = ("may_publish", "independent_QD_approval",
        "qualified_safety_clearance", "human_source_links_verified")
HEX = re.compile(r"[a-f0-9]{64}\Z")
BAD_URL_CHARS = re.compile(r"[\x00-\x20\x7f<>\"'\\]")
HOST_LABEL = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\Z", re.I)
REDIRECT_KEYS = frozenset(("redirect", "redirect_url", "redirect_uri", "return",
                           "return_url", "next", "target", "destination",
                           "continue", "url", "dest"))
SECRET_KEYS = frozenset(("token", "api_key", "apikey", "key", "secret",
                         "access_token", "authorization", "auth"))


class ReviewHold(ValueError):
    """Custody mismatch, undocumented alias, or fabricated safety approval."""


def need(test, reason):
    if not test:
        raise ReviewHold(reason)


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def is_sha(s):
    return type(s) is str and HEX.fullmatch(s) is not None


def sealed(report, schema):
    need(type(report) is dict and report.get("schema") == schema and
         report.get("release_state") == "HOLD" and
         report.get("machine_only") is True and
         all(report.get(k) is False for k in HOLD) and
         is_sha(report.get("fingerprint_sha256")) and
         digest({k: v for k, v in report.items()
                 if k != "fingerprint_sha256"}) == report["fingerprint_sha256"],
         schema + ": lost sealed evidence or false release/safety claim")


def classify_url(exact):
    """Lexical URL flags only. Never fetch, resolve DNS, normalize or alias."""
    blockers, review = [], []
    if type(exact) is not str or not exact:
        return ["MISSING_SOURCE_URL"], []
    if BAD_URL_CHARS.search(exact) or len(exact) > 8192:
        blockers.append("UNSAFE_RAW_URL_CHARACTERS_OR_LENGTH")
    try:
        parsed = urlsplit(exact)
        hostname = parsed.hostname
        port = parsed.port
    except ValueError:
        return sorted(set(blockers + ["MALFORMED_URL_AUTHORITY"])), []
    if parsed.scheme != "https" or not parsed.netloc or not hostname:
        blockers.append("NON_HTTPS_OR_MISSING_HOST")
    if parsed.username is not None or parsed.password is not None or "@" in parsed.netloc:
        blockers.append("URL_CONTAINS_USERINFO")
    if parsed.fragment:
        review.append("FRAGMENT_DEEP_LINK_NEEDS_PASSAGE_REVIEW")
    if "%" in exact:
        try:
            decoded = unquote(exact, errors="strict")
        except UnicodeError:
            blockers.append("INVALID_PERCENT_ENCODING_UTF8")
        else:
            if BAD_URL_CHARS.search(decoded):
                blockers.append("PERCENT_DECODED_CONTROL_OR_MARKUP_CHARACTER")
    if hostname:
        name = hostname.rstrip(".").lower()
        if not name or name.endswith((".local", ".internal", ".localhost", ".test")) or name == "localhost":
            blockers.append("PRIVATE_OR_LOCAL_HOSTNAME")
        try:
            ip = ipaddress.ip_address(name)
        except ValueError:
            ip = None
        if ip:
            review.append("LITERAL_IP_ADDRESS_NEEDS_MANUAL_PROVENANCE")
            if not ip.is_global:
                blockers.append("NON_PUBLIC_IP_ADDRESS")
        else:
            try:
                ascii_name = name.encode("idna").decode("ascii")
            except UnicodeError:
                blockers.append("INVALID_HOST_IDNA")
            else:
                if not all(HOST_LABEL.fullmatch(label) for label in ascii_name.split(".")):
                    blockers.append("INVALID_DNS_HOST_LABEL")
                if "." not in ascii_name:
                    blockers.append("SINGLE_LABEL_HOSTNAME")
                if ascii_name != name:
                    review.append("INTERNATIONALIZED_HOSTNAME_NEEDS_IDENTITY_REVIEW")
        if port not in (None, 443):
            review.append("NON_STANDARD_HTTPS_PORT_NEEDS_REVIEW")
    params = [key.lower() for key, _ in parse_qsl(parsed.query, keep_blank_values=True)]
    if any(k in REDIRECT_KEYS for k in params):
        review.append("REDIRECT_PARAMETER_NEEDS_TARGET_REVIEW")
    if any(k in SECRET_KEYS for k in params):
        review.append("QUERY_MAY_CONTAIN_CREDENTIAL_NEEDS_REDACTION_REVIEW")
    return sorted(set(blockers)), sorted(set(review))


def construct(source_report, document_report, dom_report, *, expected=EXPECTED):
    """Pure sealed report reconciliation; synthetic fixtures must use real shapes."""
    need(type(expected) is tuple and len(expected) == 4 and
         all(type(n) is int and n > 0 for n in expected),
         "invalid R70 census")
    sealed(source_report, R67_SCHEMA)
    sealed(document_report, R68_SCHEMA)
    sealed(dom_report, R69_SCHEMA)
    need(document_report.get("source_R67_custody_fingerprint_sha256") ==
         source_report["fingerprint_sha256"] and
         dom_report.get("R68_exact_original_RC_custody_fingerprint_sha256") ==
         document_report["fingerprint_sha256"], "R67/R68/R69 source custody disconnect")
    counts67 = source_report.get("counts", {})
    counts68 = document_report.get("counts", {})
    counts69 = dom_report.get("counts", {})
    need((counts67.get("RC_all_source_rows"),
          counts68.get("original_articles_conserved"),
          counts68.get("candidate_tools"),
          counts68.get("RC_citation_occurrences_UNREVIEWED")) ==
         (expected[2], expected[0], expected[1], expected[3]) and
         counts69.get("candidate_citation_occurrences_accounted_for") ==
         expected[3] and
         counts69.get("candidate_articles") == expected[0] and
         counts69.get("candidate_tools") == expected[1] and
         counts69.get("human_claim_or_safety_checks_performed_BY_R69") == 0 and
         counts68.get("human_source_or_claim_checks_performed_BY_R68") == 0 and
         counts67.get("human_link_checks_performed_BY_THIS_TOOL") == 0,
         "source/document/citation census or human-check status drift")
    source_rows = source_report.get(
        "all_original_and_RC_source_review_work_orders_NOT_APPROVED")
    docs68 = document_report.get(
        "all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED")
    docs69 = dom_report.get(
        "all_document_DOM_text_and_citation_review_orders_NOT_APPROVED")
    need(type(source_rows) is list and len(source_rows) >= expected[2] and
         type(docs68) is list and len(docs68) == expected[0]+expected[1] and
         type(docs69) is list and len(docs69) == len(docs68),
         "source reading or document task loss")
    registry, by_id, by_url = {}, defaultdict(list), defaultdict(list)
    work = []
    for row in source_rows:
        need(type(row) is dict and
             all(row.get(k) == "NOT_REVIEWED" for k in (
                 "human_link_review", "human_claim_support_review",
                 "qualified_safety_review", "independent_QD_review")) and
             type(row.get("source_origin")) is str and
             type(row.get("source_id")) is str,
             "fabricated source-review approval or malformed source identity")
        reading = row.get("candidate_complete_reading_UNABRIDGED")
        if reading is None:
            continue
        origin, sid = row["source_origin"], row["source_id"]
        key = (origin, sid)
        need(key not in registry and reading.get("id") == sid and
             reading.get("human_link_check") is False and
             row.get("candidate_record_sha256") == digest(reading) and
             row.get("candidate_exact_url_NO_ALIAS") == reading.get("url"),
             "candidate source record changed or merged")
        url = reading["url"]
        blockers, review = classify_url(url)
        item = {
            "source_origin":origin, "source_id":sid,
            "candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED":reading,
            "source_record_sha256":row["candidate_record_sha256"],
            "exact_URL_NO_CANONICAL_ALIAS":url,
            "URL_structural_blockers_NOT_HTTP_VERDICT":blockers,
            "URL_manual_review_signals_NOT_VERDICT":review,
            "original_reading_UNABRIDGED_NOT_HUMAN_VERIFIED":
                row.get("original_complete_reading_UNABRIDGED"),
            "original_record_sha256":row.get("original_record_sha256"),
            "human_link_review":"NOT_REVIEWED",
            "human_claim_support_review":"NOT_REVIEWED",
            "qualified_safety_review":"NOT_REVIEWED",
        }
        registry[key] = item
        by_id[sid].append(key)
        by_url[url].append(key)
        work.append(item)
    need(len(registry) == expected[2], "candidate source inventory was reduced")
    shared = {
        url: sorted(keys) for url, keys in by_url.items() if len(keys)>1
    }
    declared = source_report.get("RC_shared_exact_URL_groups_UNRESOLVED")
    need(type(declared) is list and len(declared) ==
         counts67.get("RC_shared_exact_url_groups") == len(shared),
         "R67 shared URL group count drift")
    for group in declared:
        url = group.get("exact_url_NOT_ALIASED")
        keys = [(x["source_origin"], x["source_id"]) for x in
                group.get("distinct_origin_scoped_identities_NOT_MERGED", [])]
        need(url in shared and sorted(keys) == shared[url] and
             group.get("human_review_state") == "NOT_REVIEWED",
             "source shared-URL identity list silently altered or approved")

    d69 = {(d.get("kind"),d.get("slug")): d for d in docs69}
    need(len(d69) == len(docs69), "duplicate R69 document identities")
    citation_work = []
    seen, urls, totals = set(), set(), 0
    for doc in sorted(docs68, key=lambda d: (d.get("kind",""),d.get("slug",""))):
        need(type(doc) is dict and type(doc.get("task_sha256")) is str and
             doc["task_sha256"] ==
             digest({k:v for k,v in doc.items() if k != "task_sha256"}) and
             all(doc.get(k) == "NOT_REVIEWED" for k in (
                 "human_claim_review", "human_source_review",
                 "qualified_safety_review", "independent_QD_review")),
             "R68 document custody or review state altered")
        key = (doc["kind"], doc["slug"])
        url = doc.get("proposed_WordPress_url_DRAFT_ONLY")
        need(key not in seen and url not in urls and type(url) is str and
             url.startswith("/preparedness/") and key in d69,
             "duplicate document or draft URL, or missing R69 mapping")
        seen.add(key)
        urls.add(url)
        matched = d69[key]
        need(matched.get("R68_task_sha256") == doc["task_sha256"] and
             matched.get("R68_HTML_sha256") == doc.get("RC_body_utf8_sha256") and
             matched.get("proposed_url_PRIVATE_DRAFT_ONLY") == url and
             all(matched.get(k) == "NOT_REVIEWED" for k in (
                 "human_source_review", "qualified_safety_review",
                 "independent_QD_review")),
             "R69 document-to-R68 citation scope mismatch")
        uses = doc.get("all_RC_source_uses_and_unabridged_readings_NOT_APPROVED")
        c68 = doc.get("all_RC_citation_occurrences_NOT_CLAIM_SUPPORT")
        c69 = matched.get("citation_visibility_audit_NOT_BROWSER_PROOF")
        need(type(uses) is list and type(c68) is list and
             type(c69) is list and len(c68) == len(c69),
             "lost candidate citation, source use, or DOM provenance")
        local_sources = {}
        for use in uses:
            sid = use["source_id"]
            variants = use.get("all_candidate_source_variants_UNABRIDGED_NOT_APPROVED")
            expected_variants = sorted(by_id.get(sid, []))
            received_variants = [(x["source_origin"],x["source_id"])
                                 for x in variants] if type(variants) is list else []
            need(sid not in local_sources and sorted(received_variants) ==
                 expected_variants and
                 all(x in source_rows for x in variants) and
                 use.get("review_state") == "NOT_REVIEWED",
                 "R68 source variant misbound or dropped")
            local_sources[sid] = use
        for a,b in zip(c68,c69):
            sid = a["source_id"]
            need(sid in local_sources and
                 a.get("ordinal") == b.get("ordinal") and
                 sid == b.get("source_id") and
                 a.get("unicode_codepoint_offset_in_candidate_html") ==
                 b.get("unicode_codepoint_offset") and
                 a.get("exact_citation_token") == b.get("literal_token") and
                 a.get("human_claim_support") == "NOT_REVIEWED" and
                 b.get("human_claim_support_review") == "NOT_REVIEWED",
                 "R68/R69 citation source ID or Unicode offset divergence")
            variant_keys = sorted(by_id[sid])
            actual_variants = sorted(tuple(x) for x in
                a.get("all_possible_origin_and_id_pairs_NOT_MERGED", []))
            dom_variants = sorted(tuple(x) for x in
                b.get("all_source_identity_variants_NOT_ALIASED", []))
            scoped = a.get("scoped_candidate_source_identity_OR_NULL")
            scoped_dom = b.get("candidate_source_identity_OR_NULL")
            need(actual_variants == dom_variants == variant_keys and
                 scoped == scoped_dom and
                 (scoped is None or tuple(scoped) in variant_keys),
                 "citation identity variants were aliased or scope substituted")
            urls_exact = [registry[k]["exact_URL_NO_CANONICAL_ALIAS"]
                          for k in variant_keys]
            flags = sorted(set(flag for k in variant_keys for flag in
                               registry[k]["URL_structural_blockers_NOT_HTTP_VERDICT"]))
            citation_work.append({
                "kind":key[0], "slug":key[1], "draft_url":url,
                "citation_ordinal":a["ordinal"], "source_id":sid,
                "unicode_codepoint_offset":a["unicode_codepoint_offset_in_candidate_html"],
                "DOM_visibility_NOT_BROWSER_VERIFIED":
                    b["DOM_CLASSIFICATION_NOT_BROWSER_PROOF"],
                "preferred_candidate_identity_NOT_APPROVED":scoped,
                "all_candidate_origin_scoped_identities_NOT_ALIASED":
                    [list(k) for k in variant_keys],
                "all_candidate_exact_urls_NOT_DEDUPLICATED":urls_exact,
                "URL_structural_blockers_NOT_SOURCE_VERDICT":flags,
                "human_claim_support_review":"NOT_REVIEWED",
                "qualified_safety_review":"NOT_REVIEWED",
            })
            totals += 1
    need(len(seen) == expected[0]+expected[1] and totals == expected[3],
         "all 35 articles, six tools or 2,173 citations not conserved")
    work.sort(key=lambda r:(r["source_origin"],r["source_id"]))
    flagged = sum(bool(row["URL_structural_blockers_NOT_HTTP_VERDICT"])
                  for row in work)
    report = {
        "schema": SCHEMA, "issue":136, "release_state":"HOLD",
        "machine_only":True,
        "R67_full_source_reading_fingerprint_sha256":source_report["fingerprint_sha256"],
        "R68_complete_original_and_candidate_fingerprint_sha256":
            document_report["fingerprint_sha256"],
        "R69_DOM_citation_context_fingerprint_sha256":dom_report["fingerprint_sha256"],
        "all_244_source_URL_and_reading_work_orders_NOT_APPROVED":work,
        "all_2173_citation_URL_identity_work_orders_NOT_APPROVED":citation_work,
        "counts":{
            "source_records_conserved":len(work),
            "RC_distinct_exact_URLs_NOT_ALIASED":len(by_url),
            "RC_shared_exact_URL_groups_NOT_RESOLVED":len(shared),
            "candidate_articles":expected[0], "candidate_tools":expected[1],
            "citation_occurrences_conserved":totals,
            "source_rows_with_structural_URL_blockers":flagged,
            "citations_touching_structural_URL_blockers":
                sum(bool(row["URL_structural_blockers_NOT_SOURCE_VERDICT"])
                    for row in citation_work),
            "sources_requiring_extra_lexical_URL_review":
                sum(bool(row["URL_manual_review_signals_NOT_VERDICT"]) for row in work),
            "human_url_or_claim_checks_performed_BY_R70":0,
        },
        "limitations":(
            "All URL checks are syntactic and do not access a website, verify "
            "its ownership, check linked passages, detect server redirects, "
            "approve medical/emergency guidance, or validate browser rendering. "
            "Distinct source readings/URLs stay separate. Prior R67/R68/R69 "
            "evidence remains sealed; this is NOT a crosswalk rebaseline, "
            "human source check, independent QD, or publishing permission."
        ),
        **{k:False for k in HOLD},
    }
    report["fingerprint_sha256"] = digest(report)
    return report


def csv_tasks(report, *, citations=False):
    sealed(report, SCHEMA)
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    def safe(v):
        s = "" if v is None else (
            json.dumps(v,sort_keys=True,ensure_ascii=False) if isinstance(v,(list,dict))
            else str(v))
        return "'" + s if s[:1] in ("\t","\r","\n") or s.lstrip().startswith(
            ("=", "+", "-", "@")) else s
    if citations:
        writer.writerow(["kind","slug","draft_url","citation_ordinal",
            "source_id","unicode_offset","origin_scoped_identities_NO_ALIAS",
            "exact_urls_NO_ALIAS","URL_flags_NOT_HUMAN_VERDICT",
            "HUMAN_CLAIM_SUPPORT_NOT_REVIEWED","reviewer_notes_UNTRUSTED"])
        for r in report["all_2173_citation_URL_identity_work_orders_NOT_APPROVED"]:
            writer.writerow([safe(x) for x in (r["kind"],r["slug"],r["draft_url"],
                r["citation_ordinal"],r["source_id"],r["unicode_codepoint_offset"],
                r["all_candidate_origin_scoped_identities_NOT_ALIASED"],
                r["all_candidate_exact_urls_NOT_DEDUPLICATED"],
                r["URL_structural_blockers_NOT_SOURCE_VERDICT"],"NOT_REVIEWED","")])
    else:
        writer.writerow(["origin","source_id","exact_URL_NO_ALIAS",
            "source_record_sha256","URL_blockers_NOT_VERDICTS",
            "URL_review_flags_NOT_VERDICTS","HUMAN_SOURCE_CHECK_NOT_REVIEWED",
            "QUALIFIED_SAFETY_NOT_REVIEWED","reviewer_notes_UNTRUSTED"])
        for r in report["all_244_source_URL_and_reading_work_orders_NOT_APPROVED"]:
            writer.writerow([safe(x) for x in (r["source_origin"],r["source_id"],
                r["exact_URL_NO_CANONICAL_ALIAS"],r["source_record_sha256"],
                r["URL_structural_blockers_NOT_HTTP_VERDICT"],
                r["URL_manual_review_signals_NOT_VERDICT"],"NOT_REVIEWED",
                "NOT_REVIEWED","")])
    return output.getvalue()


def _module(filename):
    path = Path(__file__).with_name(filename)
    need(path.is_file() and not path.is_symlink(), "missing pinned parent: " + filename)
    spec = importlib.util.spec_from_file_location("r70_"+filename.replace(".","_"),path)
    need(spec is not None and spec.loader is not None,
         "unable to import pinned source custody module")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def live_report(repo_root=None):
    repo = Path(repo_root).resolve() if repo_root else Path(__file__).resolve().parents[2]
    r67 = _module("r67_rc_source_custody_crosswalk.py").live_report(repo)
    r68 = _module("r68_rc_document_citation_scope.py").live_report(repo)
    r69 = _module("r69_rc_citation_dom_review.py").construct(r68)
    result = construct(r67,r68,r69)
    need(result == construct(r67,r68,r69), "R70 non-deterministic output")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--source-csv-stdout", action="store_true")
    parser.add_argument("--citation-csv-stdout", action="store_true")
    args = parser.parse_args(argv)
    try:
        need(not (args.source_csv_stdout and args.citation_csv_stdout),
             "choose only one private CSV projection")
        report = live_report(args.repo_root)
        if args.source_csv_stdout:
            sys.stdout.write(csv_tasks(report))
        elif args.citation_csv_stdout:
            sys.stdout.write(csv_tasks(report,citations=True))
        else:
            print(json.dumps({"schema":SCHEMA, "release_state":"HOLD",
                  "fingerprint_sha256":report["fingerprint_sha256"],
                  "counts":report["counts"],"all_publication_clearance":False},
                  sort_keys=True))
        if report["counts"]["source_rows_with_structural_URL_blockers"]:
            print("R70 PRIVATE HOLD: malformed/untrusted URL structures remain",
                  file=sys.stderr)
            return 2
        return 0
    except (ReviewHold,KeyError,TypeError,ValueError,AttributeError,
            UnicodeError,OSError) as exc:
        print("R70 PRIVATE CUSTODY HOLD: "+str(exc), file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
