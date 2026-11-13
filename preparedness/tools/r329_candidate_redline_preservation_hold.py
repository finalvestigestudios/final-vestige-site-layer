#!/usr/bin/env python3
"""R329: Candidate-only Article #15 / Tool #104 conservation and redline gate.

No canonical source writes, no WordPress build, and NEVER evidence of safety/QD
approval. Structurally clean redlines remain REVIEW_REQUIRED_HARD_HOLD.
"""
from __future__ import annotations
import argparse
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from preparedness.tools import r319_three_way_custody_hold as custody
from preparedness.tools import r328_article15_tool104_claim_holds as original

SCHEMA = "fv-preparedness-r329-redline-preservation-hard-hold-v1"
RELEASE = dict.fromkeys(("public_publishing", "qualified_safety_review",
    "independent_qd_pass", "child_privacy_review", "source_support_review",
    "tool_release", "paid_offer_approved"), False)
KNOWN_P0 = {
    "a_body": ("call 911 for anything life-threatening",
               "keeps what you type on your own device"),
    "t_body": ("call 911 for anything life-threatening",
               "use text messages rather than calls for everything else",
               "It is not sent or saved", "Closing the tab clears it"),
    "t_meta": ("Nothing is stored.",),
}
CITE = re.compile(r"\{\{cite:([a-z0-9-]+)\}\}")
LINK = re.compile(r"\{\{link:([a-z0-9-]+)\|")
WORD = re.compile(r"\b[\w-]+\b", re.UNICODE)
HARD_HOLD = "REVIEW_REQUIRED_HARD_HOLD"

class WitnessHTML(HTMLParser):
    """Structural inventory, never HTML security clearance."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.headings, self.hrefs, self.names = [], [], [], []
        self.forms, self.scripts, self.embeds, self.handlers = [], [], [], []
        self.network, self.inline_script, self.styles, self.text_parts = [], [], [], []
        self.skip = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.append(a["id"])
            if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
                self.headings.append(a["id"])
        if "href" in a: self.hrefs.append(a["href"])
        if "name" in a: self.names.append(a["name"])
        if tag == "form":
            self.forms.append((a.get("method"), a.get("action"), a.get("target")))
        if tag == "script" and "src" in a: self.scripts.append(a["src"])
        if tag in ("iframe", "object", "embed", "base", "meta"):
            self.embeds.append(tag)
        self.handlers.extend((tag, k, v) for k, v in attrs if k.lower().startswith("on"))
        self.network.extend((tag, k, a[k]) for k in ("src", "srcset", "formaction",
                                                      "action", "target") if k in a)
        if tag in ("script", "style"): self.skip = tag

    def handle_endtag(self, tag):
        if tag == self.skip: self.skip = None

    def handle_data(self, data):
        if self.skip == "script": self.inline_script.append(data)
        elif self.skip == "style": self.styles.append(data)
        else: self.text_parts.append(data)

    def words(self):
        return len(WORD.findall(" ".join(self.text_parts)))

def parse_html(raw):
    d = WitnessHTML()
    d.feed(raw.decode("utf-8", "strict"))
    d.close()
    return d

def issue_report(errors, witnesses=()):
    errors = sorted(set(errors))
    return {"schema": SCHEMA, "state": "INVALID_HARD_HOLD" if errors else HARD_HOLD,
            "errors": errors, "witnesses": list(witnesses),
            "qualified_approval": False, "source_support_verified": False,
            "native_export_parity": "NOT_EXECUTED", "release": RELEASE.copy()}

def inspect(originals, proposed):
    if type(originals) is not dict or type(proposed) is not dict or \
       set(originals) != set(original.DOCS) or set(proposed) != set(original.DOCS):
        return issue_report(["EXACT_FOUR_DOCUMENT_ROLES_REQUIRED"])
    if any(type(originals[k]) is not bytes or type(proposed[k]) is not bytes for k in original.DOCS):
        return issue_report(["SOURCE_AND_CANDIDATE_MUST_BE_BYTES"])
    errors, witnesses = [], []
    try:
        text_orig = {k: originals[k].decode("utf-8", "strict") for k in original.DOCS}
        text_new = {k: proposed[k].decode("utf-8", "strict") for k in original.DOCS}
    except UnicodeError:
        return issue_report(["NON_UTF8_SOURCE_OR_CANDIDATE"])
    for role, snippets in KNOWN_P0.items():
        for snippet in snippets:
            if snippet in text_orig[role] and snippet in text_new[role]:
                errors.append("KNOWN_P0_UNRESOLVED_" + role.upper() + "_" +
                              re.sub(r"[^A-Z0-9]+", "_", snippet.upper())[:52])
    for stem in ("a", "t"):
        try:
            before = original.strict_json(originals[stem + "_meta"])
            after = original.strict_json(proposed[stem + "_meta"])
            if type(before) is not dict or type(after) is not dict:
                raise ValueError("non-object metadata")
            for key in ("n", "slug", "section", "track", "kind"):
                if key in before and (type(before[key]) is not type(after.get(key)) or
                                     before[key] != after.get(key)):
                    errors.append("IMMUTABLE_IDENTITY_" + stem.upper() + "_" + key.upper())
            if after.get("status") != {"editorial": "drafted", "publish": "draft"} or \
               type(after.get("safety_review")) is not dict or \
               after["safety_review"].get("state") != "pending" or \
               after["safety_review"].get("reviewer") is not None or \
               after["safety_review"].get("date") is not None:
                errors.append("DRAFT_SAFETY_STATE_INVALID_" + stem.upper())
            b_rel, a_rel = before.get("related"), after.get("related")
            if type(b_rel) is not list or type(a_rel) is not list or \
               len(a_rel) != len(set(a_rel)) or not set(b_rel).issubset(a_rel):
                errors.append("RELATED_DESTINATIONS_REMOVED_" + stem.upper())
            b_use, a_use = before.get("source_use"), after.get("source_use")
            if type(b_use) is not dict or type(a_use) is not dict:
                errors.append("SOURCE_USE_OBJECT_REQUIRED_" + stem.upper())
            else:
                b_cites = Counter(CITE.findall(text_orig[stem + "_body"]))
                a_cites = Counter(CITE.findall(text_new[stem + "_body"]))
                if any(a_cites[k] < n for k, n in b_cites.items()):
                    errors.append("CITED_OCCURRENCE_LOST_" + stem.upper())
                if not set(b_use).issubset(a_use) or set(a_cites) != set(a_use):
                    errors.append("SOURCE_USE_CITATION_PARITY_LOST_" + stem.upper())
                witnesses.append({"role": stem, "source_ids_before": len(b_cites),
                                  "source_ids_after": len(a_cites),
                                  "citations_before": sum(b_cites.values()),
                                  "citations_after": sum(a_cites.values())})
        except (ValueError, TypeError, KeyError, UnicodeError):
            errors.append("MALFORMED_METADATA_" + stem.upper())
        try:
            b, a = parse_html(originals[stem + "_body"]), parse_html(proposed[stem + "_body"])
            if len(b.ids) != len(set(b.ids)) or len(a.ids) != len(set(a.ids)):
                errors.append("DUPLICATE_HTML_IDS_" + stem.upper())
            if not set(b.ids).issubset(a.ids) or not set(b.headings).issubset(a.headings):
                errors.append("HEADING_ANCHOR_REMOVED_" + stem.upper())
            if not Counter(b.hrefs) <= Counter(a.hrefs):
                errors.append("HREF_DESTINATION_REMOVED_" + stem.upper())
            if not Counter(LINK.findall(text_orig[stem + "_body"])) <= \
                   Counter(LINK.findall(text_new[stem + "_body"])):
                errors.append("INTERNAL_LINK_PLACEHOLDER_REMOVED_" + stem.upper())
            if Counter(b.names) != Counter(a.names):
                errors.append("FORM_FIELD_NAMES_CHANGED_" + stem.upper())
            if Counter(b.forms) != Counter(a.forms):
                errors.append("FORM_SUBMISSION_CHANGED_" + stem.upper())
            for key in ("scripts", "embeds", "handlers", "network", "inline_script", "styles"):
                if getattr(b, key) != getattr(a, key):
                    errors.append("UNREVIEWED_RUNTIME_SURFACE_" + stem.upper() + "_" + key.upper())
            if b.words() == 0 or a.words() < int(b.words() * .95):
                errors.append("READING_DEPTH_LOST_" + stem.upper())
            witnesses.append({"role": stem + "_body", "words_before": b.words(),
                              "words_after": a.words(), "heading_count_before": len(b.headings),
                              "heading_count_after": len(a.headings)})
        except (ValueError, TypeError, UnicodeError):
            errors.append("MALFORMED_HTML_" + stem.upper())
    if originals["a_body"] == proposed["a_body"] or originals["t_body"] == proposed["t_body"]:
        errors.append("NO_REVIEWED_BODY_CHANGE")
    return issue_report(errors, witnesses)

def audit(original_reader, candidate_reader):
    originals, candidate, errors = {}, {}, []
    for role, (path, sha) in original.DOCS.items():
        try:
            content = original_reader(path)
            if type(content) is not bytes or custody.blob(content) != sha:
                raise ValueError("original Git blob mismatch")
            originals[role] = content
        except (OSError, ValueError, TypeError):
            errors.append("ORIGINAL_GIT_PIN_UNAVAILABLE_" + role.upper())
        try:
            content = candidate_reader(path)
            if type(content) is not bytes: raise ValueError("candidate absent")
            candidate[role] = content
        except (OSError, ValueError, TypeError):
            errors.append("CANDIDATE_MISSING_" + role.upper())
    result = inspect(originals, candidate)
    result["errors"] = sorted(set(result["errors"] + errors))
    if errors: result["state"] = "INVALID_HARD_HOLD"
    result["original_blobs_verified"] = len(originals)
    result["candidate_files_present"] = len(candidate)
    return result

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    p.add_argument("--candidate-root", type=Path)
    args = p.parse_args()
    root = args.root.resolve()
    candidate = args.candidate_root.resolve() if args.candidate_root else None
    if candidate is None or candidate == root or root in candidate.parents or candidate in root.parents:
        result = issue_report(["SEPARATE_CANDIDATE_TREE_REQUIRED"])
    else:
        def read(parent, path):
            content = custody.safe_bytes(parent, path)
            if content is None: raise OSError("missing or symlink path")
            return content
        result = audit(lambda path: read(root, path), lambda path: read(candidate, path))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 2 if result["state"] == HARD_HOLD else 1

if __name__ == "__main__":
    raise SystemExit(main())
