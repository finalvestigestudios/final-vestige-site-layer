#!/usr/bin/env python3
"""Offline, fictional 90-card regression tests; no real source records and no network."""
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("guard", HERE / "research_sources_90_count_guard.py")
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

def fixture():
    cards = []
    for category, count in guard.EXPECTED.items():
        for i in range(count):
            cards.append(
                f'<article class="fv-rs-card" data-cat="{category}">'
                f'<h3>Fictional {category} {i}</h3>'
                f'<a href="https://example.org/{category}/{i}" target="_blank">'
                f'Open fictitious source</a></article>'
            )
    return (
        '<!-- wp:html -->\n<style>.fixture{display:block}</style>\n'
        + "\n".join(old for old, _ in guard.CHANGES)
        + "\n" + "".join(cards)
        + '<script>/* fixture only */</script>\n<!-- /wp:html -->'
    )

def must_fail(label, raw):
    try:
        guard.repair(raw)
    except ValueError:
        return
    raise AssertionError(f"Unsafe input was accepted: {label}")

def run():
    before = fixture()
    after = guard.repair(before)
    assert len(guard.cards(after)) == 90
    assert guard.validate(before) == guard.validate(after)
    for old, new in guard.CHANGES:
        assert before.count(old) == 1 and after.count(new) == 1
        assert after.count(old) == 0
    must_fail("missing source", before.replace(guard.cards(before)[0][3], "", 1))
    must_fail("duplicate URL", before.replace(
        "https://example.org/archives/0", "https://example.org/archives/1"))
    must_fail("unexpected label", before.replace("Search all 60 sources", "Search all sixty sources"))
    must_fail("extra nested source link", before.replace(
        "Open fictitious source</a>",
        '<a href="https://example.org/unapproved">context</a>Open fictitious source</a>', 1))
    must_fail("unsafe URL scheme", before.replace(
        "https://example.org/archives/0", "javascript:alert(1)"))
    must_fail("different category", before.replace(
        'data-cat="archives"', 'data-cat="engineering"', 1))
    must_fail("repeat marker", before + "\nSearch all 60 sources")
    with TemporaryDirectory() as t:
        source = Path(t) / "source.html"
        output = Path(t) / "candidate.html"
        source.write_text(before, encoding="utf-8")
        p = subprocess.run([sys.executable, str(HERE / "research_sources_90_count_guard.py"),
                            str(source), "--write", "--out", str(output)],
                           capture_output=True, text=True, check=True)
        assert '"exact_replacement_count": 11' in p.stdout
        assert output.read_text(encoding="utf-8") == after
        assert source.read_text(encoding="utf-8") == before
        second = subprocess.run([sys.executable, str(HERE / "research_sources_90_count_guard.py"),
                                 str(source), "--write", "--out", str(output)],
                                capture_output=True, text=True)
        assert second.returncode != 0  # refuses overwrite
    print("PASS: exact 11 changes, 90 preserved, 7 adversarial refusals, local-only CLI and overwrite refusal")

if __name__ == "__main__":
    run()
