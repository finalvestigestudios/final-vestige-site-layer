#!/usr/bin/env python3
"""Independent AX-tree and keyboard audit of source-attested EX2 WordPress payload.

OFFLINE CHROMIUM, NOT WORDPRESS, NOT AXE / WCAG CERTIFICATION.
Uses exact bundle hash and parser from PR #1469; blocks every HTTP request.
"""
import argparse
import asyncio
import hashlib
import json
from pathlib import Path
from typing import Any

from playwright.async_api import async_playwright
from verify_pinned_wp_payload_browser import make_fixture, PINNED_BUNDLE_SHA256

WIDTHS = (390, 768, 1440)
FOCUS = "https://finalvestige.com/focus/"


async def ax_roles(page) -> list[dict[str, Any]]:
    session = await page.context.new_cdp_session(page)
    try:
        nodes = (await session.send("Accessibility.getFullAXTree"))["nodes"]
    finally:
        await session.detach()
    return [{"role": x.get("role", {}).get("value", ""),
             "name": x.get("name", {}).get("value", "").strip(),
             "ignored": bool(x.get("ignored"))} for x in nodes]


def inspect_ax(nodes, js, page_dom):
    active = [x for x in nodes if not x["ignored"]]
    links = [x for x in active if x["role"] == "link"]
    buttons = [x for x in active if x["role"] == "button"]
    heads = [x for x in active if x["role"] == "heading"]
    unlabelled = [x for x in links + buttons if not x["name"]]
    chapters = [x for x in links if any(x["name"].startswith(f"{i:02d} ") for i in range(1, 8))]
    named_focus = [x for x in links if "Focus Fieldbook" in x["name"]]
    expected_headings = ["Find what others miss.", "One sheet of paper. Two different worlds.",
                         "A source is not a verdict.", "What if the unreliable witness was your own mind?"]
    missing = [s for s in expected_headings if s not in {x["name"] for x in heads}]
    ok = (not unlabelled and len(chapters) == 7 and len(named_focus) >= 1
          and not missing and page_dom["focus"] == 5 and page_dom["margins"] == 72
          and page_dom["h1"] == 1 and page_dom["duplicate_ids"] == []
          and page_dom["chapter_hrefs_valid"]
          and (page_dom["controls"] >= 8 if js else page_dom["controls"] == 0))
    return {"pass": ok, "chapter_links": len(chapters), "named_focus_links": len(named_focus),
            "links": len(links), "buttons": len(buttons), "headings": len(heads),
            "unlabelled_actions": unlabelled[:12], "missing_source_headings": missing,
            "dom": page_dom}


async def inspect_page(page, js):
    nodes = await ax_roles(page)
    dom = await page.evaluate("""() => {
        const root = document.querySelector('[data-fv-home-flagship]');
        const allIds = [...document.querySelectorAll('[id]')].map(e=>e.id);
        const names=new Set(); const duplicates=[];
        for (const id of allIds) { if (names.has(id)) duplicates.push(id); names.add(id); }
        return {
          focus:root.querySelectorAll('a[href="https://finalvestige.com/focus/"]').length,
          margins:root.querySelectorAll('.fv-margin-strip__item').length,
          h1:root.querySelectorAll('h1').length,
          controls:[...root.querySelectorAll('button')].filter(x=>x.getBoundingClientRect().height>0).length,
          duplicate_ids:duplicates,
          has_main:!!document.querySelector('main,[role="main"]'),
          chapter_hrefs_valid: [...root.querySelectorAll('.fv-hf__chapter-nav a')].map(e=>e.getAttribute('href')).join('|') === "#fv-hf-title|#fv-hf-chronicle|#fv-hf-evidence|#fv-hf-inquiry|#fv-hf-method-title|#fv-hf-observer|#fv-hf-mind-title",
          has_masthead:!!root.querySelector('header.fv-hf__masthead')
        };
      }""")
    return inspect_ax(nodes, js, dom)


async def kb(page, locator, action, expectation):
    el = page.locator(locator)
    await el.focus()
    await el.press(action)
    await page.wait_for_timeout(120)
    return await page.evaluate(expectation)


async def run(bundle: Path, out: Path):
    html, source = make_fixture(bundle)
    out.mkdir(parents=True, exist_ok=True)
    rows=[]; keyboard={}; negatives={}; all_requests=[]
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True, executable_path="/usr/bin/chromium", args=["--no-sandbox"])
        try:
            for width in WIDTHS:
                for js in (False, True):
                    for reduced in (False, True):
                        ctx = await browser.new_context(viewport={"width":width,"height":900},
                            java_script_enabled=js, reduced_motion="reduce" if reduced else "no-preference", service_workers="block")
                        page=await ctx.new_page(); errors=[]; calls=[]
                        page.on("pageerror",lambda e: errors.append(str(e)))
                        async def deny(route):
                            calls.append(route.request.url)
                            await route.abort()
                        await ctx.route("**/*",deny)
                        await page.set_content(html,wait_until="domcontentloaded")
                        await page.wait_for_timeout(100)
                        proof = await inspect_page(page, js)
                        proof["pass"] = proof["pass"] and not errors
                        if reduced:
                            margin_css=await page.locator('.fv-margin-strip__item').first.evaluate('e=>[getComputedStyle(e).display,getComputedStyle(e).animationName]')
                            proof["reduced_motion_margin_static"] = margin_css==["block","none"]
                            proof["pass"] = proof["pass"] and proof["reduced_motion_margin_static"]
                        rows.append({"width":width,"js":js,"reduced_motion":reduced,"ax":proof,"js_errors":errors,"network_denied":len(calls),"pass":proof["pass"]})
                        all_requests.extend(calls)
                        if width==390 and reduced:
                            try:
                                keyboard[f"chapter_anchor_js_{js}"] = bool(await kb(page,'.fv-hf__chapter-nav a[href="#fv-hf-evidence"]','Enter',
                                    '() => location.hash==="#fv-hf-evidence" && document.activeElement.id==="fv-hf-evidence"'))
                                if js:
                                    keyboard["case_franklin_enter"] = bool(await kb(page,'[data-fv-case-button="franklin"]','Enter',
                                        '() => !document.querySelector("[data-fv-case=franklin]").hidden && document.querySelector("[data-fv-case-button=franklin]").getAttribute("aria-pressed")==="true"'))
                                    keyboard["case_end_keyboard"] = bool(await kb(page,'[data-fv-case-button="apollo"]','End',
                                        '() => document.activeElement.getAttribute("data-fv-case-button")==="malbone" && document.querySelector("[data-fv-case-button=malbone]").getAttribute("aria-pressed")==="true"'))
                                    keyboard["chronicle_arrow"] = bool(await kb(page,'[data-fv-chronicle-view="original"]','ArrowRight',
                                        '() => document.activeElement.getAttribute("data-fv-chronicle-view")==="addition" && document.querySelector(".fv-hf__chronicle").dataset.fvChronicleMode==="addition"'))
                                    keyboard["observer_arrow"] = bool(await kb(page,'[data-fv-observer-switch="a"]','ArrowRight',
                                        '() => document.activeElement.getAttribute("data-fv-observer-switch")==="b" && document.querySelector("[data-fv-observer-switch=b]").getAttribute("aria-pressed")==="true"'))
                                await page.screenshot(path=str(out/f"keyboard_{'enhanced' if js else 'nojs'}_390.png"),animations="disabled")
                            except Exception as e:
                                keyboard["interaction_error_js_"+str(js)] = str(e)[:300]
                        await ctx.close()
            # Three deliberate DOM corruptions must fail the same AX contract.
            for name, manipulation in {
                "blank_first_focus_action": """() => {const x=document.querySelector('.fv-hf__mast-cta');x.removeAttribute('aria-label');x.textContent='';}""",
                "remove_chapter_anchor": """() => document.querySelector('.fv-hf__chapter-nav a[href="#fv-hf-observer"]').removeAttribute('href')""",
                "duplicate_source_heading_id": """() => document.querySelector('#fv-hf-chronicle').id='fv-hf-title'"""
            }.items():
                ctx=await browser.new_context(viewport={"width":390,"height":900},service_workers="block")
                page=await ctx.new_page();await ctx.route("**/*",lambda route:route.abort())
                await page.set_content(html,wait_until="domcontentloaded")
                await page.evaluate(manipulation)
                result=await inspect_page(page,True)
                negatives[name]={"rejected":not result["pass"],"findings":{
                    "unlabelled_actions":result["unlabelled_actions"],
                    "chapter_links":result["chapter_links"],
                    "duplicate_ids":result["dom"]["duplicate_ids"]}}
                await ctx.close()
        finally:
            await browser.close()
    overall=all(x["pass"] for x in rows) and all(keyboard.values()) and all(x["rejected"] for x in negatives.values())
    report={"source_zip_sha256":PINNED_BUNDLE_SHA256,"segments":source,
        "category":"OFFLINE ACTUAL-PAYLOAD CHROMIUM CDP ACCESSIBILITY SMOKE; NOT WORDPRESS, NOT AXE, NOT WCAG CERTIFIED",
        "offline_browser_smoke_pass":overall,"wordPress_native_execution":"NOT RUN",
        "axe_WCAG_2_2_AA":"NOT RUN; FAIL CLOSED FOR RELEASE","hosted_jetpack":"NOT RUN",
        "axe_release_gate":"HOLD","verified_revenue":"NOT OBSERVED",
        "rows":rows,"keyboard":keyboard,"negative_controls":negatives,
        "offline_html_lacks_main_landmark":"Expected: WordPress theme must supply main; cannot conclude WP production lacks main",
        "network_request_count_blocked":len(all_requests)}
    (out/"ax_keyboard_results.json").write_text(json.dumps(report,indent=2))
    print(json.dumps({"pass":overall,"configurations":len(rows),"keyboard":keyboard,
                      "negative_controls":negatives,"failures":[x for x in rows if not x["pass"]],
                      "status":"OFFLINE only; no WordPress/axe/hosted release qualification"},indent=2))
    return 0 if overall else 2

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('bundle',type=Path);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();raise SystemExit(asyncio.run(run(a.bundle,a.out)))
