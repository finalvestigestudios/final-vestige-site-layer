#!/usr/bin/env python3
"""R67 private HOLD: lossless original-vs-RC source custody and machine-probe triage.

A 244-row release candidate is NOT a 244-link human approval. The older 206
tracked checks, R66's 208 cited originals and the RC's 97 machine probes are
different review universes. Preserve every source reading and require human
scope decisions; never normalize URLs to establish equivalence.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "r67-original-to-release-candidate-source-custody-v1"
ORIGINAL_R66_SHA = "646c89531811bb7bc430ef115f857ff5e36bdc5c"
RC_SHA = "ddb3528ba6494dada1fa1c3a142ce746e3a67706"
RC_REF = "integration/preparedness-release-candidate-20261101"
PROBE_PATH = "preparedness/docs/rc/qa/SOURCE-ACCESSIBILITY-CANDIDATE-2026-11-01.json"
ORIGIN_FILES = {
    "base": "preparedness/sources/register.json",
    **{name: "preparedness/sources/fragments/" + name + ".json"
       for name in ("food", "health", "hist-field", "hist-food",
                    "hist-home", "shelter", "start")},
}
EXPECTED = (224, 244, 208, 1959, 30, 32, 97, 20, 2, 0)
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
HOLD = ("may_publish", "independent_QD_approval",
        "qualified_safety_clearance", "human_source_links_verified")


class SourceCustodyHold(ValueError):
    """Research changes, provenance, machine evidence or safety HOLD are invalid."""


def need(ok, why):
    if not ok:
        raise SourceCustodyHold(why)


def digest(value):
    return hashlib.sha256(json.dumps(
        value, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False
    ).encode("utf-8")).hexdigest()


def sha(value):
    return type(value) is str and HEX64.fullmatch(value) is not None


def strict_json(raw):
    def no_duplicate_keys(pairs):
        obj = {}
        for key, val in pairs:
            need(key not in obj, "duplicate JSON key: " + repr(key))
            obj[key] = val
        return obj
    return json.loads(raw, object_pairs_hook=no_duplicate_keys,
                      parse_constant=lambda x: (_ for _ in ()).throw(
                          SourceCustodyHold("non-finite JSON value: " + x)))


def _ledger():
    path = Path(__file__).with_name("r66_cited_source_identity_ledger.py")
    need(path.is_file() and not path.is_symlink(), "R66 original ledger missing")
    spec = importlib.util.spec_from_file_location("r67_parent_r66", path)
    need(spec is not None and spec.loader is not None,
         "cannot load verified R66 original ledger")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _collect(data, label):
    need(type(data) is dict and set(data) == set(ORIGIN_FILES),
         label + ": missing source origin files")
    items = {}
    urls = defaultdict(list)
    for origin in sorted(data):
        source_rows = data[origin]
        need(type(source_rows) is list, label + ": malformed source fragment")
        for row in source_rows:
            need(type(row) is dict and type(row.get("id")) is str
                 and bool(row["id"]) and type(row.get("url")) is str
                 and bool(row["url"]) and row.get("human_link_check") is False
                 and "_origin" not in row,
                 label + ": missing source identity/url, false human approval, or injected origin")
            key = (origin, row["id"])
            need(key not in items, label + ": duplicate origin-scoped source id: " + repr(key))
            items[key] = row
            urls[row["url"]].append(key)
    return items, urls


def _groups(url_map):
    return [{
        "exact_url_NOT_ALIASED": url,
        "distinct_origin_scoped_identities_NOT_MERGED": [
            {"source_origin": o, "source_id": sid} for o,sid in sorted(keys)],
        "human_review_state": "NOT_REVIEWED",
    } for url,keys in sorted(url_map.items()) if len(keys) > 1]


def construct(original, candidate, cited_ledger, machine_probes,
              *, expected=EXPECTED):
    """Pure deterministic test seam. live_report() alone anchors real Git objects.

    This method NEVER verifies external source content, human links, claim support,
    medical or emergency safety, QD, or release authorization.
    """
    need(type(expected) is tuple and len(expected) == 10
         and all(type(x) is int and x >= 0 for x in expected)
         and expected[0] <= expected[1] + expected[9]
         and expected[7] + expected[8] + expected[9] >= 0,
         "invalid source review census")
    old, old_urls = _collect(original, "original R66")
    new, new_urls = _collect(candidate, "release candidate")
    need(type(cited_ledger) is dict and
         cited_ledger.get("schema") ==
         "r66-private-original-cited-source-identity-ledger-v1" and
         cited_ledger.get("release_state") == "HOLD" and
         cited_ledger.get("machine_only") is True and
         all(cited_ledger.get(key) is False for key in HOLD) and
         sha(cited_ledger.get("fingerprint_sha256")) and
         cited_ledger["fingerprint_sha256"] ==
         digest({k:v for k,v in cited_ledger.items() if k != "fingerprint_sha256"}),
         "R66 cited original identity evidence or HOLD forged")
    cited = cited_ledger.get("all_cited_original_source_identitites_NOT_APPROVED")
    need(type(cited) is list and len(cited) == expected[2],
         "missing cited original source identities")
    cited_index = {}
    occurrence_total = 0
    for entry in cited:
        need(type(entry) is dict and
             type(entry.get("source_origin")) is str and
             type(entry.get("source_id")) is str and
             sha(entry.get("source_record_sha256")) and
             entry.get("human_source_retrieval_state") == "NOT_REVIEWED" and
             entry.get("human_claim_support_state") == "NOT_REVIEWED" and
             entry.get("qualified_safety_review_state") == "NOT_REVIEWED",
             "R66 cited source custody or review status changed")
        key = (entry["source_origin"], entry["source_id"])
        need(key in old and key not in cited_index and
             digest({**old[key], "_origin":key[0]}) == entry["source_record_sha256"] and
             entry["original_unabridged_source_record_NOT_HUMAN_VERIFIED"] ==
             {**old[key], "_origin":key[0]},
             "cited source missing from original register or its whole reading changed")
        refs = entry.get("all_original_citation_occurrences_AND_RELATIONSHIPS_UNABRIDGED")
        need(type(refs) is list and bool(refs), "cited original references missing")
        occurrence_total += len(refs)
        cited_index[key] = entry
    need(occurrence_total == expected[3] and
         cited_ledger.get("counts", {}).get("all_original_citation_occurrences")
         == expected[3], "cited source or citation occurrence census changed")
    old_groups, new_groups = _groups(old_urls), _groups(new_urls)
    need((len(old),len(new),len(cited_index),occurrence_total,
          len(old_groups),len(new_groups)) == expected[:6],
         "source row, citation, or distinct URL collision census drift")
    need(type(machine_probes) is list and len(machine_probes) == expected[6],
         "RC machine-source probe universe missing or changed")
    probes = {}
    for row in machine_probes:
        need(type(row) is dict and type(row.get("url")) is str
             and row["url"] in new_urls and row["url"] not in probes
             and type(row.get("ok")) is bool
             and not any(k in row for k in (
                 "human_link_check", "human_verified", "qualified_safety_review",
                 "independent_QD_approval", "may_publish", "reviewer")),
             "machine probe is duplicate, unscoped, or masquerades as human review")
        probes[row["url"]] = row
    need(len(probes) == expected[6], "machine probe URL collision")
    need(not any(row.get("human_link_check") is True for row in old.values())
         and not any(row.get("human_link_check") is True for row in new.values()),
         "unsupported source human approval")

    orders, delta = [], defaultdict(int)
    for origin,sid in sorted(set(old) | set(new)):
        key = (origin,sid)
        before, after = old.get(key), new.get(key)
        if before is None:
            state = "ADDED_TO_RC_NOT_REVIEWED"
        elif after is None:
            state = "REMOVED_FROM_RC_NOT_REVIEWED"
        elif before != after:
            state = "SOURCE_READING_CHANGED_NOT_REVIEWED"
        else:
            state = "IDENTICAL_RECORD_STILL_NOT_HUMAN_VERIFIED"
        delta[state] += 1
        original_url = before["url"] if before is not None else None
        candidate_url = after["url"] if after is not None else None
        order = {
            "source_origin":origin, "source_id":sid,
            "state_NOT_EDITORIAL_VERDICT":state,
            "original_complete_reading_UNABRIDGED":before,
            "candidate_complete_reading_UNABRIDGED":after,
            "original_record_sha256":digest(before) if before is not None else None,
            "candidate_record_sha256":digest(after) if after is not None else None,
            "original_exact_url_NO_ALIAS":original_url,
            "candidate_exact_url_NO_ALIAS":candidate_url,
            "changed_record_keys_REVIEW_REQUIRED": sorted(
                field for field in set(before or {}) | set(after or {})
                if (before or {}).get(field) != (after or {}).get(field)),
            "original_distinct_identities_sharing_exact_url":
                [{"source_origin":o,"source_id":s}
                 for o,s in sorted(old_urls.get(original_url,[]))]
                if original_url is not None else [],
            "candidate_distinct_identities_sharing_exact_url":
                [{"source_origin":o,"source_id":s}
                 for o,s in sorted(new_urls.get(candidate_url,[]))]
                if candidate_url is not None else [],
            "original_cited_R66_evidence_UNABRIDGED_NOT_VERIFIED":
                cited_index.get(key),
            "candidate_machine_probe_URL_ONLY_NOT_HUMAN_VERIFIED":
                probes.get(candidate_url),
            "human_link_review":"NOT_REVIEWED",
            "human_claim_support_review":"NOT_REVIEWED",
            "qualified_safety_review":"NOT_REVIEWED",
            "independent_QD_review":"NOT_REVIEWED",
        }
        order["work_order_sha256"] = digest({
            "source_origin":origin, "source_id":sid,
            "original_record_sha256":order["original_record_sha256"],
            "candidate_record_sha256":order["candidate_record_sha256"],
            "r66_cited_fingerprint":cited_ledger["fingerprint_sha256"]})
        orders.append(order)
    need((delta["ADDED_TO_RC_NOT_REVIEWED"],
          delta["SOURCE_READING_CHANGED_NOT_REVIEWED"],
          delta["REMOVED_FROM_RC_NOT_REVIEWED"]) == expected[7:10],
         "proposed source additions/reading changes/removals require new review census")
    need(len(orders) == len(set(old)|set(new)) and
         sum(x["original_complete_reading_UNABRIDGED"] is not None for x in orders)
         == expected[0] and
         sum(x["candidate_complete_reading_UNABRIDGED"] is not None for x in orders)
         == expected[1] and
         sum(len(x["original_cited_R66_evidence_UNABRIDGED_NOT_VERIFIED"]
                 ["all_original_citation_occurrences_AND_RELATIONSHIPS_UNABRIDGED"])
             for x in orders if x["original_cited_R66_evidence_UNABRIDGED_NOT_VERIFIED"])
         == expected[3], "reading/citation evidence dropped or multiplied")
    report = {
        "schema":SCHEMA, "issue":136,
        "release_state":"HOLD", "machine_only":True,
        "original_R66_fingerprint_sha256":cited_ledger["fingerprint_sha256"],
        "RC_GIT_OBJECT_SHA_PINNED_NOT_RELEASE_APPROVAL":RC_SHA,
        "all_original_and_RC_source_review_work_orders_NOT_APPROVED":orders,
        "original_shared_exact_URL_groups_UNRESOLVED":old_groups,
        "RC_shared_exact_URL_groups_UNRESOLVED":new_groups,
        "RC_machine_source_accessibility_probes_NOT_HUMAN_CHECKS":
            [probes[url] for url in sorted(probes)],
        "counts":{
            "original_all_source_rows":len(old),
            "RC_all_source_rows":len(new),
            "original_distinct_exact_urls":len(old_urls),
            "RC_distinct_exact_urls":len(new_urls),
            "original_shared_exact_url_groups":len(old_groups),
            "RC_shared_exact_url_groups":len(new_groups),
            "distinct_original_cited_source_records":len(cited_index),
            "original_citation_occurrences":occurrence_total,
            "original_uncited_source_records_NOT_DROPPED":len(old)-len(cited_index),
            "new_RC_source_records":delta["ADDED_TO_RC_NOT_REVIEWED"],
            "changed_original_source_readings":delta["SOURCE_READING_CHANGED_NOT_REVIEWED"],
            "removed_original_source_records":delta["REMOVED_FROM_RC_NOT_REVIEWED"],
            "unchanged_original_records_not_approved":
                delta["IDENTICAL_RECORD_STILL_NOT_HUMAN_VERIFIED"],
            "RC_machine_probed_urls_NOT_HUMAN_CHECKS":len(probes),
            "RC_machine_probe_ok_NOT_HUMAN_VERIFICATION":
                sum(1 for p in probes.values() if p["ok"]),
            "RC_machine_probe_failed_NOT_A_HUMAN_LINK_VERDICT":
                sum(1 for p in probes.values() if not p["ok"]),
            "human_link_checks_performed_BY_THIS_TOOL":0,
            "historical_206_link_tasks_RECONCILIATION_PENDING":206,
        },
        "limitations":(
            "Source rows, original cited identities, machine probe URLs and historical "
            "206 human-link work orders are DIFFERENT UNITS. Original 224 and RC 244 "
            "are all record variants, not human-reviewed links. No reading, source "
            "access, editorial support, medical/emergency safety, independent QD or "
            "publication is approved. The original frozen custody baseline is unchanged."
        ),
        **{field:False for field in HOLD},
    }
    report["fingerprint_sha256"] = digest(report)
    return report


def task_csv(report):
    """Untrusted private task projection only; original evidence stays in JSON."""
    need(type(report) is dict and report.get("schema") == SCHEMA
         and report.get("release_state") == "HOLD"
         and all(report.get(k) is False for k in HOLD)
         and sha(report.get("fingerprint_sha256"))
         and report["fingerprint_sha256"] ==
         digest({k:v for k,v in report.items() if k != "fingerprint_sha256"}),
         "unheld/unsigned source task projection")
    def safe(value):
        value = "" if value is None else str(value)
        if value[:1] in ("\t","\n","\r") or value.lstrip().startswith(
                ("=", "+", "-", "@")):
            return "'" + value
        return value
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["origin","source_id","source_status_NOT_APPROVED",
        "original_SHA256","candidate_SHA256","original_URL_EXACT",
        "candidate_URL_EXACT","candidate_probe_MACHINE_ONLY",
        "cited_original_NOT_CLAIM_SUPPORT","changed_fields",
        "HUMAN_LINK_CHECK_NOT_REVIEWED","SAFETY_REVIEW_NOT_REVIEWED",
        "reviewer_notes_UNTRUSTED"])
    for row in report["all_original_and_RC_source_review_work_orders_NOT_APPROVED"]:
        probe = row["candidate_machine_probe_URL_ONLY_NOT_HUMAN_VERIFIED"]
        writer.writerow([safe(v) for v in (
            row["source_origin"],row["source_id"],row["state_NOT_EDITORIAL_VERDICT"],
            row["original_record_sha256"],row["candidate_record_sha256"],
            row["original_exact_url_NO_ALIAS"],row["candidate_exact_url_NO_ALIAS"],
            "PROBE_OK_NOT_HUMAN" if probe and probe["ok"] else
                "PROBE_FAILED_NOT_HUMAN" if probe else "NOT_PROBED",
            bool(row["original_cited_R66_evidence_UNABRIDGED_NOT_VERIFIED"]),
            ";".join(row["changed_record_keys_REVIEW_REQUIRED"]),
            "NOT_REVIEWED","NOT_REVIEWED","",
        )])
    return buffer.getvalue()


def _git_output(repo_root, *args):
    try:
        return subprocess.check_output(["git", *args], cwd=repo_root,
                                       stderr=subprocess.PIPE)
    except (OSError, subprocess.CalledProcessError) as error:
        raise SourceCustodyHold("cannot verify pinned Git evidence: " +
                                str(error)) from error


def _source_lists(repo_root, *, from_rc):
    result = {}
    for origin,path in ORIGIN_FILES.items():
        if from_rc:
            data = _git_output(repo_root,"show",RC_SHA + ":" + path)
        else:
            file = repo_root / path
            need(file.is_file() and not file.is_symlink(),
                 "missing or symlinked frozen source file: " + path)
            data = file.read_bytes()
        root = strict_json(data.decode("utf-8"))
        need(type(root) is dict and type(root.get("sources")) is list,
             "source fragment malformed: " + path)
        result[origin] = root["sources"]
    return result


def live_report(repo_root, remote="origin"):
    """Verify pinned RC branch and independently reconstitute R66 source evidence."""
    repo_root = Path(repo_root).resolve()
    actual = _git_output(repo_root,"rev-parse","--verify",
        "refs/remotes/" + remote + "/" + RC_REF + "^{commit}").decode().strip()
    need(actual == RC_SHA, "RC HEAD SHA DRIFT HOLD: expected " + RC_SHA +
         " got " + actual)
    base = _git_output(repo_root,"merge-base","--is-ancestor",
                        ORIGINAL_R66_SHA,"HEAD")  # fails closed on non-descendant
    need(base == b"", "R66 is not an ancestor")
    cited = _ledger().live_report(repo_root,remote)
    original = _source_lists(repo_root,from_rc=False)
    candidate = _source_lists(repo_root,from_rc=True)
    probes = strict_json(_git_output(repo_root,"show",
                   RC_SHA + ":" + PROBE_PATH).decode("utf-8"))
    report = construct(original,candidate,cited,probes)
    need(report == construct(original,candidate,cited,probes),
         "non-deterministic original/RC source comparison")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root",type=Path,default=ROOT.parent)
    parser.add_argument("--remote",default="origin")
    parser.add_argument("--task-csv-stdout",action="store_true")
    args = parser.parse_args(argv)
    try:
        report = live_report(args.repo_root,args.remote)
        if args.task_csv_stdout:
            sys.stdout.write(task_csv(report))
        else:
            print(json.dumps({"schema":SCHEMA,"release_state":"HOLD",
                "may_publish":False,"no_external_writes":True,
                "fingerprint_sha256":report["fingerprint_sha256"],
                "counts":report["counts"]},sort_keys=True,ensure_ascii=False))
        return 0
    except (SourceCustodyHold, KeyError, ValueError, TypeError, OSError,
            UnicodeError, AttributeError, ImportError) as error:
        print("R67 PRIVATE SOURCE-CUSTODY HOLD: " + str(error),file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
