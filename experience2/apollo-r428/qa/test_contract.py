"""R428 executed-PHP assertions; no synthetic HTML substitution."""
from pathlib import Path
import subprocess
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
PHP = ROOT / "staging-evidence-bridge.php"


def output():
    proc = subprocess.run(["php", str(ROOT / "qa" / "fixture.php")], capture_output=True, text=True, check=True)
    return BeautifulSoup(proc.stdout, "html.parser")


def test_php_lint():
    subprocess.run(["php", "-l", str(PHP)], check=True, capture_output=True)


def test_entries_and_citations():
    soup = output()
    roots = soup.select("[data-fv-r428]")
    assert len(roots) == 2
    ids = [node.get("id") for node in soup.select("[id]")]
    assert len(ids) == len(set(ids))
    for root in roots:
        assert len(root.select("li.fv-r428__plate")) == 3
        assert len(root.select("details")) == 4
        assert len(root.select("time[datetime]")) == 3
        assert len(root.select('a[href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/"]')) == 1
        assert len(root.select('a[href^="https://www.nasa.gov/"]')) == 4
        assert not root.select("img, script, iframe, canvas, svg, form, input, button")
        assert "did not conclusively" in root.get_text(" ")


def test_disabled_fallback_and_wrong_page():
    s = PHP.read_text()
    assert "FV_R428_ENABLED" in s and "wp_get_environment_type() === 'staging'" in s
    php = """<?php define('ABSPATH',1); function wp_get_environment_type(){return 'production';} function is_singular(){return true;} function get_queried_object_id(){return 2001;} define('FV_R428_ENABLED',true); define('FV_R428_STAGING_PAGE_ID',2001); require '%s'; echo fv_r428_shortcode();""" % PHP.as_posix()
    proc = subprocess.run(["php"], input=php, capture_output=True, text=True, check=True)
    assert "free Apollo 1 investigation" in proc.stdout and 'data-fv-r428' not in proc.stdout


def test_only_one_noncommercial_next_action():
    html = output()
    assert not any("payhip" in a.get("href", "") for a in html.select("a"))
    assert not any("utm_" in a.get("href", "") for a in html.select("a"))
    assert "No original media" not in html.get_text()
