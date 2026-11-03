"""Render the design-system gallery: every component, with real data, plus tokens and computed contrast."""
from __future__ import annotations

from fvx_lib import CONTRAST_PAIRS, contrast, esc, read_tokens
from render_flagship import _provenance, plate_frame, render_chronology


def _section(title: str, note: str, inner: str, sid: str) -> str:
    return (f'<section class="fv-ex2-gallery__section" id="{sid}" aria-labelledby="{sid}-h"><h2 id="{sid}-h" class="fv-ex2-chapter__title" style="font-size:var(--fvx-fs-h3)">{esc(title)}</h2>'
            f'<p class="fv-ex2-caption" style="max-width:48rem">{note}</p><div class="fv-ex2-gallery__demo">{inner}</div></section>')


def render_gallery(data: dict) -> str:
    tokens = read_tokens()
    rec = data["records"][3]
    policy = data["rights_policy"]
    img = rec["image"]
    swatches = "".join(
        f'<li class="fv-ex2-gallery__swatch"><span class="fv-ex2-gallery__chip" style="background:{esc(v)}"></span><span><code>--fvx-{esc(k)}</code> {esc(v)}</span></li>'
        for k, v in tokens.items())
    rows = "".join(
        f'<tr><td><code>{esc(fg)}</code> on <code>{esc(bg)}</code></td><td>{contrast(tokens[fg], tokens[bg]):.2f}:1</td><td>{minimum:g}:1</td>'
        f'<td>{"pass" if contrast(tokens[fg], tokens[bg]) >= minimum else "FAIL"}</td></tr>'
        for fg, bg, minimum in CONTRAST_PAIRS)
    plate = f'''<div class="fv-ex2-plate" style="max-width:34rem"><figure>{plate_frame(rec, sizes="34rem")}
<figcaption class="fv-ex2-plate__label"><span class="fv-ex2-plate__role">{esc(img["role_label"])}</span><span class="fv-ex2-plate__caption">{esc(img["caption"])}</span>
<span class="fv-ex2-plate__id">NASA {esc(img["nasa_id"])} &middot; {esc(img["credit"])}</span></figcaption></figure>
<details><summary>Source record and rights</summary>{_provenance(rec, policy)}</details></div>'''
    controls = ('<p style="display:flex;flex-wrap:wrap;gap:var(--fvx-s-3)"><a class="fv-ex2-button fv-ex2-button--primary" href="#controls">Primary action</a>'
                '<button type="button" class="fv-ex2-button">Secondary</button><button type="button" class="fv-ex2-button" disabled>Disabled</button>'
                '<button type="button" class="fv-ex2-chip" aria-pressed="true">Chip on</button><button type="button" class="fv-ex2-chip" aria-pressed="false">Chip off</button></p>'
                '<div class="fv-ex2-field" style="max-width:24rem"><label class="fv-ex2-label" for="g-field">Field</label><input class="fv-ex2-field__input" id="g-field" type="search" placeholder="Search"></div>')
    callout = '<div class="fv-ex2-callout" style="max-width:36rem"><span class="fv-ex2-label">Evidence boundary</span><p>Probable is not proven.</p></div>'
    transition = (f'<div class="fv-ex2-transition" style="max-width:36rem"><a class="fv-ex2-transition__next" href="#plate"><span class="fv-ex2-label">Next record &middot; 05</span>'
                  f'<span class="fv-ex2-transition__title">{esc(data["records"][4]["title"])}</span></a></div>')
    badges = "".join(f'<span class="fv-ex2-badge" data-status="{s}">{s.replace("-", " ")}</span> ' for s in ("verified", "partial", "article-only", "editorial-note"))
    body = f'''<div class="fv-ex2 fv-ex2-gallery" data-fvx="gallery">
<style>.fv-ex2-gallery__section{{padding-block:var(--fvx-s-7);border-top:1px solid var(--fvx-line);display:grid;grid-template-columns:minmax(0,1fr);gap:var(--fvx-s-5)}}
.fv-ex2-gallery__chip{{display:inline-block;width:2.5rem;height:2.5rem;border:1px solid var(--fvx-line-strong);flex:none}}
.fv-ex2-gallery__swatch{{display:flex;gap:var(--fvx-s-3);align-items:center;font-size:var(--fvx-fs-small)}}
.fv-ex2-gallery__swatches{{display:grid;grid-template-columns:repeat(auto-fill,minmax(15rem,1fr));gap:var(--fvx-s-3)}}
.fv-ex2-gallery table{{border-collapse:collapse;font-size:var(--fvx-fs-small);width:100%}}.fv-ex2-gallery th,.fv-ex2-gallery td{{text-align:left;padding:var(--fvx-s-2) var(--fvx-s-3);border-bottom:1px solid var(--fvx-line)}}
.fv-ex2-gallery__scroll{{overflow-x:auto}}</style>
<header class="fv-ex2-masthead"><div class="fv-ex2-wrap fv-ex2-masthead__inner"><a class="fv-ex2-masthead__brand" href="https://finalvestige.com/">Final Vestige Studios</a>
<nav class="fv-ex2-nav" aria-label="Experience navigation"><a href="../apollo-1/index.html">Evidence Unfolds</a><a href="../research-desk/index.html">Research Desk</a><a href="../atlas/index.html">Evidence Atlas</a></nav></div></header>
<main><div class="fv-ex2-wrap">
<header class="fv-ex2-desk__head"><p class="fv-ex2-label">Design system &middot; Black Dossier (provisional)</p><h1 class="fv-ex2-desk__title">Components, <em>with the evidence.</em></h1>
<p class="fv-ex2-desk__intro">Every component below renders real Apollo 1 data. Namespaces: selectors begin <code>.fv-ex2</code>, custom properties begin <code>--fvx-</code>, behaviour hooks are <code>data-fvx-*</code>.</p></header>
{_section("Colour tokens", "Read from <code>00-tokens.css</code> at build time.", f'<ul class="fv-ex2-gallery__swatches">{swatches}</ul>', "tokens")}
{_section("Computed contrast", "WCAG 2.2 ratios calculated from the token values for the pairs the CSS actually uses. Text needs 4.5:1; control borders need 3:1.", f'<div class="fv-ex2-gallery__scroll"><table><caption class="fv-ex2-visually-hidden">Contrast ratios</caption><thead><tr><th scope="col">Pair</th><th scope="col">Ratio</th><th scope="col">Minimum</th><th scope="col">Result</th></tr></thead><tbody>{rows}</tbody></table></div>', "contrast")}
{_section("Typography", "Display, lede, body and catalogue label. Sizes are fluid tokens; no webfont is loaded.", '<p class="fv-ex2-label">Label / catalogue</p><p class="fv-ex2-chapter__title">Chapter title scale</p><p class="fv-ex2-chapter__dek">Lede paragraph scale for chapter introductions.</p><p class="fv-ex2-chapter__detail">Body text scale for the narrative itself. It stays readable at 200% zoom and never relies on colour alone.</p>', "type")}
{_section("Evidence plate and provenance", "The plate carries the image role, the caption, the archive identity and a rights basis. The role label states whether the photograph depicts the event.", plate, "plate")}
{_section("Source attribution", "Provenance list used by plates, the source drawer and the Research Desk.", f'<div style="max-width:40rem">{_provenance(rec, policy)}</div>', "provenance")}
{_section("Evidence boundary callout", "Every chapter carries one. Probability, observation and conclusion stay distinct.", callout, "callout")}
{_section("Claim status badges", "Used in the claim crosswalk.", badges, "badges")}
{_section("Section transition", "An explicit hand-off between records.", transition, "transition")}
{_section("Interactive chronology", "Slider enhancement over a complete ordered list. Markers are documented times only.", render_chronology(data["chronology"]), "chronology")}
{_section("Controls", "Buttons, chips and the search field. Minimum target 44px; visible focus ring.", controls, "controls")}
</div></main></div>'''
    return body
