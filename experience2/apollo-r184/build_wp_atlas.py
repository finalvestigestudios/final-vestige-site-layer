"""Apollo R184: render R183 NASA-source Atlas as an isolated WordPress shortcode candidate.

Build-only dependencies: beautifulsoup4, tinycss2. Runtime is static PHP + CSS + HTML.
No network access, CMS writes, data collection, analytics, or publishing.
"""
from pathlib import Path
import importlib.util, tempfile, hashlib, json
import tinycss2
from bs4 import BeautifulSoup

HERE = Path(__file__).resolve().parent
R183 = HERE.parent / "apollo-r183" / "reconstruct_atlas.py"
OUT = HERE / "dist"
EXPECTED = "dd09aaeefa1326d2c1ab42d7084a6525a048c167e7de8e013f53c930486b2b27"
SCOPE = "fv-apollo-atlas"

def digest(b):
    return hashlib.sha256(b).hexdigest()

def scope_css(css):
    def rules(nodes):
        out = []
        for n in tinycss2.parse_rule_list(nodes, skip_whitespace=True, skip_comments=True):
            if n.type == "qualified-rule":
                before = tinycss2.serialize(n.prelude)
                selectors = []
                for sel in before.split(","):
                    s = sel.strip()
                    if s in (":root", "html", "body"):
                        selectors.append("." + SCOPE)
                    elif s:
                        selectors.append("." + SCOPE + " " + s)
                out.append(",".join(selectors) + "{" + tinycss2.serialize(n.content) + "}")
            elif n.type == "at-rule" and n.content is not None:
                out.append("@" + n.lower_at_keyword + tinycss2.serialize(n.prelude) + "{" + rules(n.content) + "}")
            else:
                raise RuntimeError("Unexpected CSS syntax: " + str(n))
        return "\n".join(out)
    out = rules(css)
    out += "\n." + SCOPE + "{box-sizing:border-box;display:block;isolation:isolate;max-width:100%;padding:1px 0;overflow-wrap:anywhere}"
    out += "\n." + SCOPE + " *{box-sizing:border-box}"
    out += "\n." + SCOPE + " [id]:target{outline:2px solid var(--accent);outline-offset:4px}"
    out += "\n@media print{." + SCOPE + "{background:#fff!important;color:#000!important}." + SCOPE + " .plate,." + SCOPE + " .source-card{break-inside:avoid;background:#fff!important;color:#000!important;border-color:#444!important}." + SCOPE + " a{color:#000!important}}"
    return "/* Scoped exclusively to the R184 article. */\n" + out + "\n"

def render_php(html_sha, css_sha):
    template = r'''<?php
/**
 * Plugin Name: FV Apollo Experience 2 Atlas (staging R184)
 * Description: Unpublished source-pinned Apollo 1 Atlas shortcode; requires governed staging QA.
 * Version: 0.1.0-r184
 */
if (!defined('ABSPATH')) { exit; }
function fv_ex2_r184_fallback() {
    return '<p class="fv-apollo-fallback">The evidence Atlas is temporarily unavailable. '
        . '<a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the original Apollo 1 investigation</a>.</p>';
}
function fv_ex2_r184_render($atts = array(), $content = null) {
    $root = plugin_dir_path(__FILE__);
    $html = $root . 'templates/atlas-fragment.html';
    $css = $root . 'assets/atlas-scoped.css';
    if (!is_readable($html) || !is_readable($css)) return fv_ex2_r184_fallback();
    if (hash_file('sha256', $html) !== '__HTML__'
        || hash_file('sha256', $css) !== '__CSS__') return fv_ex2_r184_fallback();
    wp_register_style('fv-apollo-r184', plugins_url('assets/atlas-scoped.css', __FILE__), array(), '0.1.0-r184');
    wp_enqueue_style('fv-apollo-r184');
    $output = file_get_contents($html);
    return $output === false ? fv_ex2_r184_fallback() : $output;
}
add_shortcode('fv_ex2_apollo_atlas', 'fv_ex2_r184_render');
'''
    return template.replace("__HTML__", html_sha).replace("__CSS__", css_sha)

def build():
    spec = importlib.util.spec_from_file_location("r183_reconstruct", R183)
    if spec is None or spec.loader is None:
        raise RuntimeError("R183 source reconstruction unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "r183.html"
        if module.reconstruct(path) != EXPECTED or digest(path.read_bytes()) != EXPECTED:
            raise RuntimeError("R183 HTML source identity mismatch")
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    style = soup.find("style")
    main = soup.body.find("main", id="main") if soup.body else None
    if not style or not main:
        raise RuntimeError("Missing original source components")
    css = scope_css(style.get_text())
    for node in soup.body.find_all(True):
        if node.get("id"):
            node["id"] = "fv-apollo-" + node["id"]
        href = node.get("href") or ""
        if href.startswith("#"):
            node["href"] = "#fv-apollo-" + href[1:]
    main.name = "div"  # Do not nest a second <main> landmark within the WP theme.
    main["role"] = "region"
    main["aria-label"] = "Apollo 1 evidence and chronology"
    article = soup.new_tag("article")
    article["class"] = [SCOPE]
    article["aria-labelledby"] = "fv-apollo-page-title"
    for child in list(soup.body.contents):
        article.append(child.extract())
    if len(article.select(".plate")) != 4 or len(article.select(".source-card")) != 4:
        raise RuntimeError("Atlas evidence inventory changed")
    if len(article.select("a.cta")) != 1 or len(article.select("details")) != 8:
        raise RuntimeError("CTA or source details inventory changed")
    ids = [e["id"] for e in article.select("[id]")]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Duplicate IDs")
    if any(a["href"][1:] not in ids for a in article.select("a[href^='#']")):
        raise RuntimeError("Broken evidence anchor")
    OUT.joinpath("templates").mkdir(parents=True, exist_ok=True)
    OUT.joinpath("assets").mkdir(parents=True, exist_ok=True)
    fragment = OUT / "templates" / "atlas-fragment.html"
    stylesheet = OUT / "assets" / "atlas-scoped.css"
    fragment.write_text(str(article) + "\n", encoding="utf-8")
    stylesheet.write_text(css, encoding="utf-8")
    hsha = digest(fragment.read_bytes())
    csha = digest(stylesheet.read_bytes())
    (OUT / "fv-ex2-apollo-r184.php").write_text(render_php(hsha, csha), encoding="utf-8")
    manifest = {"r183_html_sha256": EXPECTED, "fragment_sha256":hsha, "css_sha256":csha,
                "mode":"unpublished isolated staging candidate", "wordpress_installed":False,
                "axe_core_run":False, "commercial_rights_cleared":False}
    (OUT / "manifest.json").write_text(json.dumps(manifest,sort_keys=True,indent=2)+"\n")
    return manifest

if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
