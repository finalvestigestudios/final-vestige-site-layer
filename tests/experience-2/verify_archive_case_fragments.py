#!/usr/bin/env python3
"""Exact-checkout review gate for archive-record deep links. No CMS or network writes.

Requires the committed first-screen harness from PR #1810 and Playwright/Chromium.
Offline --source-dir mode is illustrative, not native WordPress staging.
"""
import argparse
import asyncio
import importlib.util
import json
from pathlib import Path
from playwright.async_api import async_playwright

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("ex2_full", HERE / "verify_integrated_firstscreen.py")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)
CASES = ("apollo", "franklin", "malbone")
WIDTHS = (320, 390, 768, 1440, 1920)
FRAGMENTS = tuple("#fv-hf-" + case for case in CASES) + (
    "#fv-hf-evidence", "#unknown-campaign", "")

async def check(browser, markup, width, js, fragment, rows):
    ctx = await browser.new_context(viewport={"width":width,"height":840},
        java_script_enabled=js, reduced_motion="reduce")
    await ctx.route("**/*", lambda route: route.abort("blockedbyclient"))
    page = await ctx.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    await page.goto("about:blank" + fragment)
    await page.set_content(markup, wait_until="domcontentloaded")
    await page.wait_for_timeout(35)

    async def visible():
        return await page.evaluate("""() => [...document.querySelectorAll('[data-fv-case]')]
            .filter(el => !el.hidden).map(el => el.dataset.fvCase)""")

    def expect(label, actual, expected):
        rows.append({"width":width,"javascript":js,"fragment":fragment,
            "test":label,"actual":actual,"expected":expected,"pass":actual==expected})

    if not js:
        expected = list(CASES)
    elif fragment in ("#fv-hf-" + case for case in CASES):
        expected = [fragment[len("#fv-hf-"):]]
    else:
        expected = ["apollo"]
    expect("landing-case intent", await visible(), expected)
    expect("fragment unchanged", await page.evaluate("location.hash"), fragment)
    expect("no JS exceptions", errors, [])

    if js and width==390 and fragment=="#fv-hf-franklin":
        await page.evaluate("location.hash='#fv-hf-malbone'")
        await page.wait_for_timeout(80)
        expect("hashchange selects Malbone", await visible(), ["malbone"])
        target_visible = await page.evaluate("""() => {
            const r=document.getElementById('fv-hf-malbone').getBoundingClientRect();
            return r.top >= -2 && r.top < 200;
        }""")
        expect("fragment scrolls to revealed case", target_visible, True)
        await page.evaluate("location.hash='#fv-hf-title'")
        await page.wait_for_timeout(80)
        expect("unrelated chapter hash preserves current record", await visible(), ["malbone"])
        await page.evaluate("location.hash='#fv-hf-apollo'")
        await page.wait_for_timeout(80)
        expect("hashchange selects Apollo", await visible(), ["apollo"])
        await page.evaluate("location.hash='#fv-hf-malbone'")
        await page.wait_for_timeout(80)
        expect("forward history selects Malbone", await visible(), ["malbone"])
        await page.go_back()
        await page.wait_for_timeout(80)
        expect("back history restores Apollo", await visible(), ["apollo"])
        await page.locator('[data-fv-case-button="franklin"]').click()
        expect("manual selection preserved", await visible(), ["franklin"])
    await ctx.close()

async def run(args):
    src = args.source_dir if args.source_dir else args.checkout / "experience2/home-flagship"
    markup, head = module.verify_and_assemble(src, args.checkout, args.expected_head)
    rows=[]
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path=args.chromium,args=["--no-sandbox"])
        for width in WIDTHS:
            for js in (True,False):
                for fragment in FRAGMENTS:
                    await check(browser, markup, width, js, fragment, rows)
        await browser.close()
    passed=sum(row["pass"] for row in rows)
    report={"mode":"exact-checkout" if args.checkout else "offline-source-reconstruction",
        "head":head,"scenarios":len(WIDTHS)*2*len(FRAGMENTS),
        "assertions":len(rows),"passed":passed,"failed":len(rows)-passed,
        "media_network":"blocked, not measured","wordpress":False,"axe":False,
        "lighthouse":False,"rows":rows}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2))
    print(f"EX2 record deep links: {passed}/{len(rows)} assertions PASS")
    for row in rows:
        if not row["pass"]: print("FAIL",row)
    if passed != len(rows): raise SystemExit(1)

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--checkout",type=Path)
    mode.add_argument("--source-dir",type=Path)
    parser.add_argument("--expected-head")
    parser.add_argument("--chromium",default="/usr/bin/chromium")
    parser.add_argument("--out",type=Path,default=Path("ex2-case-fragment-receipt.json"))
    asyncio.run(run(parser.parse_args()))
