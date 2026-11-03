#!/usr/bin/env python3
"""R101: generate an isolated water-planner PRINT REVIEW CANDIDATE, never publish.

Original authored files are read-only. The candidate is derived in memory from
the exact existing draft after R100's source/citation/safety-state audit. Only
an explicitly supplied external output directory can receive draft files.
This is a UI experiment, not human evidence/medical review or browser QA.
"""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "r101-water-print-context-private-candidate-v1"
FIELDS = (
    ("wp-people", "People in household", "integer", 100),
    ("wp-days", "Days to cover", "integer", 365),
    ("wp-stored", "Gallons already stored", "decimal", 100000),
    ("wp-filled", "Date self-filled containers were filled", "date", None),
    ("wp-hot", "Very hot weather selected", "checkbox", None),
    ("wp-pets", "Number of pets", "integer", 100),
    ("wp-petgal", "Gallons per pet per day (user entered)", "decimal", 100),
    ("wp-extra", "Extra gallons per day (user entered)", "decimal", 100),
)
ANCHOR = '<div id="wp-out" class="pa-tool-out" role="status" aria-live="polite" aria-label="Your water plan"></div>'
SENTINEL = "R101_PRIVATE_PRINT_REVIEW_CANDIDATE_NOT_APPROVED"

# No values are transmitted or persisted; raw user-provided strings are never
# interpolated into markup. The pure calculator's clamping bounds are mirrored
# only for print context; compare this copy to tools/water_planner.js in review.
SCRIPT = r"""
<script data-r101-private-print-review="not-approved">
(function () {
  'use strict';
  var schema = [
    ['wp-people', 'integer', 100], ['wp-days', 'integer', 365],
    ['wp-stored', 'decimal', 100000], ['wp-filled', 'date', 0],
    ['wp-hot', 'checkbox', 0], ['wp-pets', 'integer', 100],
    ['wp-petgal', 'decimal', 100], ['wp-extra', 'decimal', 100]
  ];
  var box = document.getElementById('wp-print-context');
  var form = document.getElementById('wp-form');
  if (!box || !form) return;
  function format(input, kind, max) {
    if (kind === 'checkbox') return input.checked ? 'Yes' : 'No';
    if (kind === 'date') return input.value || 'Not supplied';
    if (input.value === '') return 'Not supplied (calculator uses zero)';
    var n = Number(input.value);
    if (!Number.isFinite(n)) return 'Invalid entry: calculator uses zero';
    var bounded = Math.min(max, Math.max(0, n));
    if (kind === 'integer') bounded = Math.round(bounded);
    var changed = bounded !== n;
    return String(bounded) + (changed ? ' (calculator limit/rounding applied)' : '');
  }
  function snapshot() {
    schema.forEach(function (row) {
      var input = document.getElementById(row[0]);
      var dest = box.querySelector('[data-r101-value="' + row[0] + '"]');
      if (!input || !dest || !form.contains(input)) return;
      dest.textContent = format(input, row[1], row[2]);
    });
    var warning = document.getElementById('wp-print-context-pending');
    if (warning) warning.textContent = 'Snapshot reflects current form inputs at print time. ' +
      'Not a verification of the calculation or of personal/medical water needs.';
  }
  schema.forEach(function (row) {
    var input = document.getElementById(row[0]);
    if (!input || !form.contains(input)) return;
    input.addEventListener('input', snapshot);
    input.addEventListener('change', snapshot);
  });
  window.addEventListener('beforeprint', snapshot);
  snapshot();
})();
</script>
"""

STYLE = r"""
<style data-r101-private-print-review="not-approved">
@media screen {
  .pa #wp-print-context { display: none !important; }
}
@media print {
  .pa #wp-print-context {
    display: block !important;
    color: #000 !important;
    background: #fff !important;
    border: 1.5pt solid #000 !important;
    padding: 10pt !important;
    margin: 12pt 0 !important;
    break-inside: avoid;
  }
  .pa #wp-print-context dt { font-weight: bold; }
  .pa #wp-print-context dd { margin: 0 0 5pt 0; }
}
</style>
"""


class Hold(ValueError):
    """Prevent an ambiguous candidate from being emitted."""


def need(condition, message):
    if not condition:
        raise Hold(message)


def digest(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def canonical(row):
    return json.dumps(row, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False)


class Inventory(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.values = []
        self.scripts = 0
        self.review_marks = 0
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.append(a["id"])
        if "data-r101-value" in a:
            self.values.append(a["data-r101-value"])
        if tag == "script":
            self.scripts += 1
        if a.get("data-r101-private-print-review") == "not-approved":
            self.review_marks += 1


def markup():
    rows = "".join(
        '<dt>' + label + '</dt><dd data-r101-value="' + field +
        '">Not generated (JavaScript unavailable)</dd>'
        for field, label, _kind, _bound in FIELDS
    )
    return (
        '\n<section id="wp-print-context" class="pa-water-print-context" '
        'aria-labelledby="wp-print-context-h" data-r101-status="NOT_REVIEWED">'
        '<h2 id="wp-print-context-h">Water-plan assumptions — private print review candidate</h2>'
        '<p><strong>Draft only; independent source and qualified safety review pending.</strong> '
        'These are the household inputs behind the results above; quantities are '
        'not medical advice. Recheck your local authority and qualified clinician '
        'or veterinarian for household-specific needs.</p>'
        '<dl>' + rows + '</dl>'
        '<p id="wp-print-context-pending">No calculation is available without JavaScript. '
        'Do not interpret a blank result as zero water needed.</p>'
        '<p>Source citations, caveats and the human-review status remain in the '
        'original article below. This experimental preview is not approved for publication.</p>'
        '</section>\n'
    )


def patch_body(body):
    need(type(body) is str and body.count(ANCHOR) == 1,
         "exact original output boundary missing or duplicated")
    need(SENTINEL not in body and 'id="wp-print-context"' not in body,
         "existing candidate markup collision")
    need(body.count("</script>") == 1 and body.count("<script>") == 1,
         "original inline script boundary changed")
    # The only changed region is the output-adjacent review block and appended
    # strictly scoped print-preview CSS/JS. All authored bytes remain ordered.
    out = body.replace(ANCHOR, ANCHOR + markup()) + "\n<!-- " + SENTINEL + " -->" + STYLE + SCRIPT
    inv = Inventory()
    inv.feed(out)
    inv.close()
    need(len(inv.ids) == len(set(inv.ids)), "duplicate ID in print candidate")
    need(inv.values == [f[0] for f in FIELDS], "candidate's eight fields drifted")
    need(inv.review_marks == 2 and inv.scripts == 2, "preview CSS/JS boundary changed")
    need(out.count("{{cite:") == body.count("{{cite:"),
         "candidate lost original source citation token")
    need(out.count("{{link:") == body.count("{{link:"),
         "candidate lost original related-link token")
    need("localStorage" not in SCRIPT and "sessionStorage" not in SCRIPT and
         "fetch(" not in SCRIPT and "XMLHttpRequest" not in SCRIPT and
         "sendBeacon" not in SCRIPT and "innerHTML" not in SCRIPT,
         "candidate must not persist, transmit, or HTML-inject household data")
    return out


def assess(lib, r100, css_gate):
    original = lib.articles["water-planner"]
    original_body = original["_body"]
    original_status = original["status"].get("publish")
    prior = r100.audit(original_body, lib.css, original, css_gate)
    need(prior["release_state"] == "HOLD" and prior["may_publish"] is False,
         "R100 review state unexpected")
    need(original_status == "draft" and
         original["safety_review"]["state"] == "pending",
         "original draft or safety state has changed")
    return original_body, prior


def build_candidate(lib, builder, r100, css_gate):
    original, prior = assess(lib, r100, css_gate)
    candidate = patch_body(original)
    # Replace only in an ephemeral Library object, never on disk.
    lib.articles["water-planner"]["_body"] = candidate
    try:
        built = builder.build_article(lib, "water-planner")
        wordpress = builder.wp_wrap(lib, built["inner"])
        preview = builder.preview_wrap(lib, built["inner"],
                                       "Water planner | PRIVATE PRINT REVIEW — NOT APPROVED",
                                       "Offline draft for independent print and source review.")
    finally:
        lib.articles["water-planner"]["_body"] = original
    need("<!-- wp:html -->" in wordpress and "Safety review pending" in wordpress,
         "WordPress candidate lost draft/safety boundary")
    need(wordpress.count('id="wp-print-context"') == 1 and
         preview.count('id="wp-print-context"') == 1,
         "print context must appear once in both private outputs")
    need(wordpress.count('class="pa-cite"') == built["inner"].count('class="pa-cite"'),
         "rendered citation occurrence mismatch")
    need(prior["source_citation_occurrences"] == len(re.findall(
             r"\{\{cite:[a-z0-9-]+\}\}", original)),
         "original source count drifted")
    receipt = {
        "schema": SCHEMA, "issue": 136, "release_state": "HOLD", "may_publish": False,
        "wordpress_import_authorized": False, "human_source_claim_review": "NOT_REVIEWED",
        "qualified_water_and_medical_safety_review": "NOT_REVIEWED",
        "actual_browser_print_qa": "NOT_REVIEWED",
        "independent_QD": "NOT_REVIEWED",
        "original_body_sha256": digest(original),
        "r100_unapproved_assumption_custody_seal": prior["sha256_seal"],
        "candidate_body_sha256": digest(candidate),
        "candidate_wp_draft_sha256": digest(wordpress),
        "candidate_local_preview_sha256": digest(preview),
        "eight_assumptions": [f[0] for f in FIELDS],
        "original_citation_occurrences": prior["source_citation_occurrences"],
        "candidate_citation_occurrences": built["inner"].count('class="pa-cite"'),
        "warnings": [
            "No browser print, offline, keyboard or screen-reader verification performed.",
            "No independent verification of CDC/Ready.gov claim support or medical allowances.",
            "No public publishing, CMS writes, navigation changes or release permission.",
        ],
    }
    receipt["sha256_seal"] = digest(canonical(receipt))
    return wordpress, preview, receipt


def safe_output_dir(name):
    raw = Path(name).expanduser()
    need(not raw.is_symlink(), "output directory cannot be a symlink")
    out = raw.resolve()
    root = ROOT.resolve()
    need(out != root and root not in out.parents and out not in root.parents,
         "output cannot be inside or be an ancestor of the repository")
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", help="external scratch directory for private draft files")
    parser.add_argument("--inspect-only", action="store_true",
                        help="audit in memory and output sealed HOLD receipt only")
    args = parser.parse_args(argv)
    need(bool(args.out_dir) != bool(args.inspect_only),
         "choose exactly one of --out-dir and --inspect-only")
    sys.path.insert(0, str(ROOT / "tools"))
    import build
    import r100_printed_planner_context_custody as r100
    import r98_print_source_visibility_custody as css_gate
    lib = build.Library()
    wp, preview, receipt = build_candidate(lib, build, r100, css_gate)
    if args.out_dir:
        out = safe_output_dir(args.out_dir)
        out.mkdir(parents=True, exist_ok=True)
        documents = {
            "water-planner-R101-PRIVATE-DRAFT.html": wp,
            "water-planner-R101-LOCAL-REVIEW.html": preview,
            "water-planner-R101-HOLD-receipt.json":
                json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        }
        need(all(not (out / name).exists() and not (out / name).is_symlink()
                 for name in documents),
             "refusing to overwrite existing private review artifact")
        for name, body in documents.items():
            # Exclusive creation prevents a parallel review run from replacing
            # another worker's candidate or receipt, including symlink races.
            with (out / name).open("x", encoding="utf-8", newline="\n") as file:
                file.write(body)
    print(canonical(receipt))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Hold, ValueError, KeyError, OSError) as exc:
        print(canonical({"schema": SCHEMA, "release_state": "HOLD",
                         "may_publish": False, "error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
