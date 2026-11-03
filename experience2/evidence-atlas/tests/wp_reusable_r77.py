#!/usr/bin/env python3
"""R77 genuine local WordPress synced-pattern parity; no hosted CMS assertions.

This helper runs only inside the existing loopback-bound WordPress Playground.
A published two-level core/block -> wp_block -> shortcode chain is served by
real WordPress; the negative control references a non-Apollo synced pattern.
No external requests, network destinations, credentials or WordPress writes.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

REUSABLE_SLUG = 'fv-apollo-synced-review-private'
NEGATIVE_SLUG = 'fv-apollo-unrelated-review-private'

# Strictly public, source-controlled assertion identifiers. Never copy a raw
# exception string, browser error, URL, DOM fragment, cookie, or local path
# into an uploaded CI artifact.
R81_FAILURE_CODES = frozenset((
    'R77_LOCAL_FIXTURE_NOT_FOUND', 'R77_NOT_TOP_LEVEL',
    'R77_UNEXPECTED_NETWORK_OR_JS_ERROR', 'R77_OVERFLOW',
    'R77_NEGATIVE_SUITE_RENDERED', 'R77_UNRELATED_PAGE_LOADED_APOLLO_CSS',
    'R77_NESTED_SHORTCODE_MISSING', 'R77_SUITE_CSS_NOT_IN_HEAD',
    'R77_ATLAS_CSS_NOT_IN_HEAD', 'R77_DESK_CSS_NOT_IN_HEAD',
    'R77_DESK_RECORDS_MISSING', 'R77_ATLAS_RECORDS_MISSING',
    'R77_DESK_CUSTODY_LOST', 'R77_ATLAS_CUSTODY_LOST',
    'R77_UNCLEARED_MEDIA', 'R77_SPECULATIVE_GEO',
    'R77_CSS_NOT_APPLIED', 'R77_ENHANCEMENT_MISSING',
    'R77_FILTER_FAIL', 'R77_RESET_FAIL', 'R77_AXE_VIOLATIONS',
    'R77_LCP_LAB_GATE', 'R77_CLS_LAB_GATE', 'R77_NOJS_DESK_LOST',
    'R77_NOJS_ATLAS_LOST',
))
R81_PHASES = frozenset((
    'NAVIGATION', 'NETWORK', 'ASSET_DISCOVERY', 'CUSTODY',
    'INTERACTION', 'ACCESSIBILITY', 'PERFORMANCE', 'PRINT',
))
def write_r81_safe_failure(output: Path, exc: Exception, *,
                           width: int, js: bool, expected_apollo: bool,
                           phase: str, completed_cases: int) -> dict:
    """Persist only allowlisted diagnostic dimensions from a local browser test.

    Failures remain hard failures. This artifact enables investigation of an
    intermittent real-WordPress R77 assertion without disclosing Playground
    state or weakening any release gate.
    """
    raw = str(exc) if isinstance(exc, AssertionError) else ''
    code = raw if raw in R81_FAILURE_CODES else 'UNCLASSIFIED_ASSERTION'
    kind = type(exc).__name__
    if kind not in ('AssertionError', 'TimeoutError', 'Error',
                    'TargetClosedError', 'ValueError', 'TypeError'):
        kind = 'OTHER_EXCEPTION'
    locations = []
    tb = exc.__traceback__
    while tb is not None:
        frame = tb.tb_frame
        if Path(frame.f_code.co_filename).name == 'wp_reusable_r77.py':
            locations.append({'function': frame.f_code.co_name, 'line': tb.tb_lineno})
        tb = tb.tb_next
    receipt = {
        'schema': 'fv.apollo.r81.synced-pattern-failure.v1',
        'release': 'STAGING_HOLD', 'accepted': False,
        'authentic_wordpress_gate_passed': False,
        'width': width if width in (390, 1440) else None,
        'javascript_enabled': bool(js), 'expected_apollo': bool(expected_apollo),
        'checkpoint': phase if phase in R81_PHASES else 'UNCLASSIFIED_PHASE',
        'assertion_code': code, 'exception_kind': kind,
        'completed_r77_cases': max(0, min(int(completed_cases), 5)),
        'code_locations_only': locations[-3:],
        'public_wordpress_writes': False,
        'raw_browser_exception_uploaded': False,
        'private_login_or_url_uploaded': False,
    }
    (output / 'R81_SYNCED_PATTERN_HOLD.json').write_text(
        json.dumps(receipt, sort_keys=True, indent=2) + '\n')
    return receipt



def accept_synced_patterns(browser, storage_state, output: Path, base: str,
                           is_loopback, axe: Path, verify_pdf, verify_native):
    # Separate from the legacy 14 R68-R76 width/JS cases; keep their ledger honest.
    configurations = (
        (390, False, True),
        (390, True, True),
        (1440, False, True),
        (1440, True, True),
        (1440, True, False),
    )
    receipt = {'schema': 'fv.apollo.r77.synced-pattern-wordpress.v1',
               'release': 'STAGING_HOLD',
               'fixture': 'TWO_LEVEL_PUBLISHED_CORE_BLOCK_REFERENCE',
               'genuine_local_wordpress': True,
               'hosted_wordpress_tested': False,
               'public_wordpress_writes': False,
               'individual_nasa_photo_rights_cleared': 0,
               'cases': [], 'screenshots_sha256': {}}
    for width, js, expected_apollo in configurations:
        context = browser.new_context(viewport={'width': width, 'height': 900},
            storage_state=storage_state, java_script_enabled=js,
            reduced_motion='reduce', is_mobile=width <= 390, has_touch=width <= 390)
        phase = 'NAVIGATION'
        try:
            if js:
                context.add_init_script("""(()=>{
                  window.__r77lab={lcp:null,cls:0};
                  try{new PerformanceObserver(o=>{const e=o.getEntries();
                    if(e.length)window.__r77lab.lcp=e[e.length-1].startTime;
                  }).observe({type:'largest-contentful-paint',buffered:true});}catch(e){}
                  try{new PerformanceObserver(o=>{for(const e of o.getEntries())
                    if(!e.hadRecentInput)window.__r77lab.cls+=e.value;
                  }).observe({type:'layout-shift',buffered:true});}catch(e){}
                })();""")
            page = context.new_page()
            errors = []
            outbound = []
            page.on('pageerror', lambda error: errors.append('JS_ERROR'))
            def route(request):
                if is_loopback(request.request.url):
                    request.continue_()
                else:
                    outbound.append(request.request.resource_type)
                    request.abort()
            page.route('**/*', route)
            slug = REUSABLE_SLUG if expected_apollo else NEGATIVE_SLUG
            response = page.goto(base + '?pagename=' + slug,
                                 wait_until='networkidle', timeout=45000)
            assert response is not None and response.status == 200, 'R77_LOCAL_FIXTURE_NOT_FOUND'
            assert page.evaluate('window.top===window.self && innerWidth') == width, 'R77_NOT_TOP_LEVEL'
            phase = 'NETWORK'
            assert not outbound and not errors, 'R77_UNEXPECTED_NETWORK_OR_JS_ERROR'
            assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+2'), 'R77_OVERFLOW'
            case = {'width': width, 'javascript_enabled': js,
                    'expected_apollo': expected_apollo,
                    'off_origin_requests': len(outbound), 'page_errors': len(errors),
                    'horizontal_overflow': False}
            phase = 'ASSET_DISCOVERY'
            # The CSS MUST be emitted in <head>, not after synced block renders.
            suite_css = page.locator('head link#fv-ex2-apollo-suite-css').count()
            if not expected_apollo:
                assert page.locator('.fv-ex2-apollo-suite').count() == 0, 'R77_NEGATIVE_SUITE_RENDERED'
                assert suite_css == 0, 'R77_UNRELATED_PAGE_LOADED_APOLLO_CSS'
                case['prehead_suite_css'] = False
            else:
                assert page.locator('.fv-ex2-apollo-suite').count() == 1, 'R77_NESTED_SHORTCODE_MISSING'
                assert suite_css == 1, 'R77_SUITE_CSS_NOT_IN_HEAD'
                assert page.locator('head link#fv-ex2-evidence-atlas-css').count() == 1, 'R77_ATLAS_CSS_NOT_IN_HEAD'
                assert page.locator('head link#fv-ex2-research-desk-css').count() == 1, 'R77_DESK_CSS_NOT_IN_HEAD'
                assert page.locator('[data-fvx-record]').count() == 6, 'R77_DESK_RECORDS_MISSING'
                assert page.locator('[data-fva-record]').count() == 6, 'R77_ATLAS_RECORDS_MISSING'
                assert page.locator('.fv-ex2-ledger__custody dd').count() == 30, 'R77_DESK_CUSTODY_LOST'
                assert page.locator('[data-fva-drawer] dd').count() == 54, 'R77_ATLAS_CUSTODY_LOST'
                assert page.locator('.fv-ex2-apollo-suite img').count() == 0, 'R77_UNCLEARED_MEDIA'
                assert page.locator('.fv-ex2-apollo-suite [data-lat],[data-lon],[data-geo-edge]').count() == 0, 'R77_SPECULATIVE_GEO'
                assert page.locator('.fv-ex2-apollo-suite').evaluate(
                    'e=>getComputedStyle(e).backgroundColor') == 'rgb(9, 10, 10)', 'R77_CSS_NOT_APPLIED'
                phase = 'CUSTODY'
                case['prehead_suite_css'] = True
                case['source_records'] = 12
                case['custody_values'] = 84
                if js:
                    phase = 'INTERACTION'
                    assert page.locator('[data-fva-atlas]').get_attribute('data-fva-ready') == 'yes', 'R77_ENHANCEMENT_MISSING'
                    proof = page.locator('[data-fva-proof-filter="provisional"]')
                    (proof.tap() if width <= 390 else proof.click())
                    assert page.locator('[data-fva-record]:visible').count() == 1, 'R77_FILTER_FAIL'
                    clear = page.locator('[data-fva-proof-filter="all"]')
                    (clear.tap() if width <= 390 else clear.click())
                    assert page.locator('[data-fva-record]:visible').count() == 6, 'R77_RESET_FAIL'
                    phase = 'ACCESSIBILITY'
                    page.add_script_tag(path=str(axe))
                    accessibility = page.evaluate("""async()=>{
                      const r=await axe.run(document.querySelector('.fv-ex2-apollo-suite'),{
                        runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});
                      return {violations:r.violations.map(v=>({id:v.id,nodes:v.nodes.length})), passes:r.passes.length};
                    }""")
                    assert not accessibility['violations'], 'R77_AXE_VIOLATIONS'
                    case['axe'] = accessibility
                    phase = 'PERFORMANCE'
                    page.wait_for_function('window.__r77lab && Number.isFinite(window.__r77lab.lcp)', timeout=10000)
                    case['lab_not_field_cwv'] = page.evaluate('window.__r77lab')
                    assert case['lab_not_field_cwv']['lcp'] <= 2500, 'R77_LCP_LAB_GATE'
                    assert case['lab_not_field_cwv']['cls'] <= .1, 'R77_CLS_LAB_GATE'
                    screenshot = page.screenshot(full_page=True, animations='disabled')
                    filename = f'R77_SYNCED_PATTERN_{width}.png'
                    (output / filename).write_bytes(screenshot)
                    receipt['screenshots_sha256'][filename] = hashlib.sha256(screenshot).hexdigest()
                else:
                    assert page.locator('[data-fvx-record]:visible').count() == 6, 'R77_NOJS_DESK_LOST'
                    assert page.locator('[data-fva-record]:visible').count() == 6, 'R77_NOJS_ATLAS_LOST'
                    if width == 1440:
                        phase = 'PRINT'
                        page.emulate_media(media='print')
                        assert page.locator('.fv-ex2-ledger__custody dd:visible').count() == 30
                        assert page.locator('[data-fva-drawer] dd:visible').count() == 54
                        path = output / 'R77_SYNCED_PATTERN_NATIVE_PRINT_1440.pdf'
                        case['native_pdf_custody'] = verify_pdf(page, path)
                        case['native_pdf'] = verify_native(page, path.read_bytes(),
                            output / 'R77_SYNCED_PATTERN_PRINT_LAST_PAGE.png')
            case['pass'] = True
            receipt['cases'].append(case)
        except Exception as exc:
            write_r81_safe_failure(output, exc, width=width, js=js,
                expected_apollo=expected_apollo, phase=phase,
                completed_cases=len(receipt['cases']))
            raise
        finally:
            context.close()
    assert len(receipt['cases']) == 5 and all(c['pass'] for c in receipt['cases'])
    (output / 'R77_REUSABLE_BLOCK_WORDPRESS_RECEIPT.json').write_text(
        json.dumps(receipt, sort_keys=True, indent=2) + '\n')
    return receipt
