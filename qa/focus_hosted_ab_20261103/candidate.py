#!/usr/bin/env python3
"""GET-only live Focus: baseline vs narrowly patched browser-memory response.

No email entered or submitted, no authentication, no CMS/WordPress writes.
Candidate differs only in the two malformed && expressions inside one script.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse
from baseline import URL, Tags, safe_request, run as baseline_run

OLD_CHECK = r"function check(){if(c&#038;&#038;/\bis-subscriber\b/.test(c.className)){show();}}"
NEW_CHECK = r"function check(){if(c){if(/\bis-subscriber\b/.test(c.className)){show();}}}"
OLD_OBSERVER = "check();if(c&#038;&#038;window.MutationObserver){new MutationObserver(check).observe(c,{attributes:true,attributeFilter:['class']});}"
NEW_OBSERVER = "check();if(c){if(window.MutationObserver){new MutationObserver(check).observe(c,{attributes:true,attributeFilter:['class']});}}"
SCRIPT = re.compile(r"(<script\b[^>]*>)(.*?)(</script\s*>)", re.I | re.S)
EXPECTED_BASELINE = {
    "390/js-True:gift_inline_syntax",
    "390/js-True:actual_browser_syntax_error",
    "1440/js-True:gift_inline_syntax",
    "1440/js-True:actual_browser_syntax_error",
}

def patch_document(document):
    """Strict one-script, two-expression replacement; never relax CSP."""
    if not isinstance(document, str) or "<script" not in document.lower():
        raise ValueError("document_without_scripts")
    candidates = []
    def change(match):
        open_tag, code, close_tag = match.groups()
        if not ("fvf-gift" in code and "URLSearchParams" in code):
            return match.group(0)
        candidates.append(code)
        if len(candidates) != 1:
            raise ValueError("duplicate_conditional_gift_scripts")
        if code.count(OLD_CHECK) != 1 or code.count(OLD_OBSERVER) != 1:
            raise ValueError("exact_saved_script_no_longer_matches")
        updated = code.replace(OLD_CHECK, NEW_CHECK).replace(OLD_OBSERVER, NEW_OBSERVER)
        if "&#038;" in updated or "&#38;" in updated:
            raise ValueError("unrepaired_ampersand_entity")
        return open_tag + updated + close_tag
    result = SCRIPT.sub(change, document)
    if len(candidates) != 1 or result == document:
        raise ValueError("conditional_gift_patch_missing_or_ambiguous")
    script_before = candidates[0]
    script_after = script_before.replace(OLD_CHECK, NEW_CHECK).replace(OLD_OBSERVER, NEW_OBSERVER)
    return result, {
        "replacements": 2,
        "source_sha256": hashlib.sha256(script_before.encode()).hexdigest(),
        "candidate_sha256": hashlib.sha256(script_after.encode()).hexdigest(),
    }

def candidate_grade(rows):
    if len(rows) != 2 or {r.get("width") for r in rows} != {390, 1440}:
        return ["candidate_matrix_incomplete"]
    errors = []
    for r in rows:
        key = str(r["width"])
        if r.get("error"):
            errors.append(key + ":observation_failed")
        if r.get("http") != 200 or r.get("host") != "finalvestige.com" or r.get("path") != "/focus/":
            errors.append(key + ":public_route_or_http")
        if r.get("blocks") != 1 or r.get("links", 0) < 1 or r.get("target") is not True:
            errors.append(key + ":subscriber_structure")
        if r.get("syntax") != "PASS" or r.get("browser_syntax_errors"):
            errors.append(key + ":conditional_script_still_failing")
        if r.get("overflow") is not False:
            errors.append(key + ":horizontal_overflow")
        if r.get("initially_hidden") is not True or r.get("visible_after_mock_class") is not True:
            errors.append(key + ":gift_behavior_not_confirmed")
        if r.get("patch_replacements") != 2 or not r.get("source_sha256") or not r.get("candidate_sha256"):
            errors.append(key + ":unverified_exact_source_patch")
    return errors

def candidate_case(browser, width, output):
    ctx = browser.new_context(viewport={"width": width, "height": 850},
                              java_script_enabled=True, reduced_motion="reduce",
                              service_workers="block")
    row = {"width": width, "kind": "in_memory_only"}
    def routing(route):
        request = route.request
        if not safe_request(request):
            route.abort()
            return
        if request.is_navigation_request() and request.url == URL:
            try:
                upstream = route.fetch(timeout=25000, max_redirects=2)
                patched, proof = patch_document(upstream.text())
                row.update(patch_replacements=proof["replacements"],
                           source_sha256=proof["source_sha256"],
                           candidate_sha256=proof["candidate_sha256"],
                           upstream_http=upstream.status)
                headers = {key: value for key, value in upstream.headers.items()
                           if key.lower() not in ("content-length", "content-encoding",
                                                  "etag", "transfer-encoding")}
                route.fulfill(status=upstream.status, headers=headers, body=patched)
            except Exception as err:
                row["error"] = "intercept:" + type(err).__name__ + ":" + str(err)[:90]
                route.abort()
            return
        route.continue_()
    try:
        ctx.route("**/*", routing)
        page = ctx.new_page()
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)[:150]))
        resp = None
        try:
            resp = page.goto(URL, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(750)
            dom = page.evaluate("""() => {
              const scripts=[...document.querySelectorAll('script:not([src])')];
              const match=scripts.filter(s=>s.textContent.includes('fvf-gift') && s.textContent.includes('URLSearchParams'));
              let syntax='MISSING_OR_DUPLICATE';
              if(match.length===1){try{new Function(match[0].textContent);syntax='PASS';}
              catch(e){syntax='FAIL:'+e.name;}}
              return {syntax,
                initially_hidden:document.getElementById('fvf-gift')?.hidden ?? null,
                overflow:document.documentElement.scrollWidth>innerWidth+1};
            }""")
            row.update(dom)
            parser = Tags()
            parser.feed(page.content())
            row.update(blocks=parser.blocks, links=parser.anchors, target=parser.target)
            element = page.locator(".wp-block-jetpack-subscriptions__container")
            if element.count() == 1:
                element.evaluate("(el) => el.classList.add('is-subscriber')")
                page.wait_for_timeout(200)
                row["visible_after_mock_class"] = page.evaluate(
                    "() => document.getElementById('fvf-gift')?.hidden === false")
            else:
                row["visible_after_mock_class"] = False
            page.screenshot(path=str(output / f"candidate-{width}.png"),
                            full_page=False, timeout=12000)
        except Exception as err:
            row.setdefault("error", "browser:" + type(err).__name__ + ":" + str(err)[:90])
        parsed = urlparse(page.url)
        row.update(http=resp.status if resp else None, host=parsed.hostname,
                   path=parsed.path,
                   browser_syntax_errors=[msg for msg in errors
                       if "SyntaxError" in msg or "Invalid or unexpected token" in msg])
    finally:
        ctx.close()
    return row

def run(output):
    from playwright.sync_api import sync_playwright
    output.mkdir(parents=True, exist_ok=True)
    baseline_output = output / "baseline"
    baseline_result = baseline_run(baseline_output)
    baseline_evidence = json.loads((baseline_output / "focus-hosted-dom.json").read_text())
    baseline_failures = set(baseline_evidence.get("failures", []))
    errors = []
    if baseline_result != 1 or baseline_failures != EXPECTED_BASELINE:
        errors.append("baseline_did_not_reproduce_exact_prior_browser_failure")
    rows = []
    if not errors:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                for width in (390, 1440):
                    rows.append(candidate_case(browser, width, output))
            finally:
                browser.close()
        errors.extend(candidate_grade(rows))
    receipt = {
        "kind": "read_only_public_html_in_memory_two_operator_ab",
        "live_wordpress_mutations": 0, "subscriber_form_submissions": 0,
        "email_receipt": "NOT_TESTED", "pdf_bytes": "NOT_TESTED",
        "production_release": "HOLD",
        "candidate_status": "HOSTED_BROWSER_PASS_ONLY" if not errors else "HOLD",
        "baseline_failures": sorted(baseline_failures),
        "cases": rows, "failures": errors,
        "note": "Manipulated DOM class is a simulated state, not subscription confirmation."
    }
    (output / "focus-ab-result.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"candidate_status": receipt["candidate_status"], "failures": errors,
                      "production_release": "HOLD"}))
    return 1 if errors else 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(run(args.out))
