#!/usr/bin/env python3
"""R470 — read-only authored stylesheet citation-exposure safeguard.

This checks an exact pinned Preparedness stylesheet, including every media/container
branch, for rules that can conceal inline citations, their bibliography, reading
scope or review notices. It complements R469's *literal HTML* scanner. It is not
a browser/computed-style audit, a WordPress theme audit, or release/safety/QD approval.
No files, workflows, CMS data, links, campaigns or live settings are mutated.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

HOLD = 'DRAFT_HARD_HOLD'
STYLE_BLOB = 'e354395cdb7985eb2fe16b99ca9fd66c9885557e'
R469_BLOB = '55b2a41afcb6f37a0df467b77406ec1a49f07409'
AT_CONTAINERS = ('@media ', '@container ', '@supports ', '@layer ', '@scope ', '@starting-style')
CRITICAL_CLASS = re.compile(r'(?<![\w-])\.(?:pa-cite|pa-sources|pa-review|pa-body|pa-shell|pa-src-meta|pa-src-use)(?![\w-])')
ROOT_PA = re.compile(r'(?<![\w-])\.pa(?=\s*(?:\{|$|,|:not\(|:is\(|:where\(|\*|>|\+|~))')
UNSAFE_CSS = {'display', 'visibility', 'content-visibility', 'opacity', 'color',
              'font-size', 'line-height', 'clip', 'clip-path', 'filter',
              'pointer-events', 'user-select', 'transform', 'scale',
              'height', 'max-height', 'width', 'max-width', 'text-indent',
              'left', 'right', 'top', 'bottom', 'inset', 'z-index',
              'content', 'list-style', 'list-style-type', 'animation',
              'animation-name', 'mask', 'mask-image'}

class CSSHold(ValueError):
    pass

def check(ok, why):
    if not ok:
        raise CSSHold(why)

def gitblob(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()

def strip_comments(s):
    """Remove CSS comments without treating comment syntax inside strings as code."""
    out, i, quote = [], 0, None
    while i < len(s):
        ch = s[i]
        if quote:
            out.append(ch)
            if ch == '\\' and i + 1 < len(s):
                out.append(s[i + 1]); i += 2; continue
            if ch == quote:
                quote = None
        elif ch in ('"', "'"):
            quote = ch; out.append(ch)
        elif s.startswith('/*', i):
            end = s.find('*/', i + 2)
            check(end >= 0, 'unterminated CSS comment')
            out.append(' ')
            i = end + 2
            continue
        else:
            out.append(ch)
        i += 1
    check(quote is None, 'unterminated CSS string')
    return ''.join(out)

def split_top(s, sep):
    """Split only outside strings, (), [] — avoids commas in :is() and calc()."""
    parts, start, quote, depth_par, depth_sq = [], 0, None, 0, 0
    i = 0
    while i < len(s):
        ch = s[i]
        if quote:
            if ch == '\\': i += 2; continue
            if ch == quote: quote = None
        elif ch in ('"', "'"): quote = ch
        elif ch == '(': depth_par += 1
        elif ch == ')': depth_par -= 1
        elif ch == '[': depth_sq += 1
        elif ch == ']': depth_sq -= 1
        elif ch == sep and depth_par == 0 and depth_sq == 0:
            parts.append(s[start:i].strip()); start = i + 1
        check(depth_par >= 0 and depth_sq >= 0, 'unbalanced CSS value/selector')
        i += 1
    check(quote is None and depth_par == 0 and depth_sq == 0,
          'unclosed string or parenthetical in CSS')
    parts.append(s[start:].strip())
    return parts

def blocks(text, inherited='base'):
    """Yield (all-environments-scope, selector, declarations) from balanced CSS.

    Every conditional @media/@container branch is inspected, including print.
    @import and unrecognized at-rules fail closed instead of silently skipping.
    """
    css = strip_comments(text)
    i = 0
    while i < len(css):
        while i < len(css) and css[i].isspace(): i += 1
        if i >= len(css): break
        start, quote, paren, bracket = i, None, 0, 0
        while i < len(css):
            ch = css[i]
            if quote:
                if ch == '\\': i += 2; continue
                if ch == quote: quote = None
            elif ch in ('"', "'"): quote = ch
            elif ch == '(': paren += 1
            elif ch == ')': paren -= 1
            elif ch == '[': bracket += 1
            elif ch == ']': bracket -= 1
            if paren < 0 or bracket < 0: raise CSSHold('bad CSS prelude')
            if ch in '{};' and not quote and paren == 0 and bracket == 0: break
            i += 1
        check(i < len(css) and not quote and paren == 0 and bracket == 0, 'CSS rule not terminated')
        selector = css[start:i].strip()
        endchar = css[i]
        check(selector, 'empty CSS selector/prelude')
        if endchar == ';':
            check(not selector.startswith('@'), 'unverified CSS at-rule: ' + selector[:80])
            raise CSSHold('orphan CSS declaration: ' + selector[:80])
        check(endchar == '{', 'unexpected CSS close brace')
        i += 1; start_body = i; depth, quote = 1, None
        while i < len(css) and depth:
            ch = css[i]
            if quote:
                if ch == '\\': i += 2; continue
                if ch == quote: quote = None
            elif ch in ('"', "'"): quote = ch
            elif ch == '{': depth += 1
            elif ch == '}': depth -= 1
            i += 1
        check(depth == 0 and quote is None, 'unbalanced CSS braces')
        body = css[start_body:i-1]
        if selector.startswith('@'):
            check(selector.lower().startswith(AT_CONTAINERS),
                  'unverified CSS at-rule block: ' + selector[:100])
            yield from blocks(body, inherited + ' / ' + selector)
        else:
            yield inherited, selector, body

def important_selector(selector):
    # Bracketed selector and pseudo-function arguments are *not* ignored;
    # this is intentionally a conservative may-affect classifier.
    s = selector.lower()
    if '::before' in s or '::after' in s or '::marker' in s:
        return False  # generated decoration is not the authored source text
    return bool(CRITICAL_CLASS.search(s) or ROOT_PA.search(s))

def _zero(x):
    return bool(re.fullmatch(r'0+(?:\.0+)?(?:px|em|rem|pt|%|vw|vh)?', x))

def unsafe(property_name, value):
    p = property_name.strip().lower(); v = re.sub(r'\s*!important\s*$', '', value.strip().lower())
    if p not in UNSAFE_CSS: return False
    if re.search(r'\bvar\s*\(|\bcalc\s*\(|\benv\s*\(', v): return True
    if p in {'display', 'visibility', 'content-visibility'}:
        return v in {'none', 'hidden', 'collapse'}
    if p in {'opacity', 'font-size', 'line-height', 'height', 'max-height', 'width', 'max-width'}:
        return _zero(v) or (p == 'opacity' and v in {'.0', '0%'})
    if p == 'color': return v in {'transparent', '#0000', '#00000000', 'rgba(0,0,0,0)'}
    if p in {'clip', 'clip-path', 'mask', 'mask-image'}: return v not in {'none', 'auto', 'initial', 'inherit'}
    if p == 'filter': return 'opacity(0' in v
    if p in {'pointer-events', 'user-select'}: return v == 'none'
    if p in {'transform', 'scale'}: return bool(re.search(r'scale(?:3d|x|y)?\(\s*0(?:[,\s)]|$)', v)) or _zero(v)
    if p in {'text-indent', 'left', 'right', 'top', 'bottom', 'inset', 'z-index'}:
        # Large negative displacement on a citation/sources ancestor is a hold.
        return bool(re.search(r'-\s*(?:[1-9]\d{3,}|999)\s*(?:px|em|rem|vw|vh)?\b', v))
    if p in {'list-style', 'list-style-type'}: return v == 'none'
    if p in {'content', 'animation', 'animation-name'}: return v not in {'none', 'normal', 'initial', 'inherit'}
    return False

def audit_css(css):
    check(isinstance(css, str) and css.strip() and len(css) < 300_000, 'missing/oversized CSS')
    check('\0' not in css and '<script' not in css.lower(), 'CSS content injection')
    total, protected, conditions = 0, 0, set()
    for env, selector, raw in blocks(css):
        total += 1
        check(total <= 4000, 'too many CSS rules')
        if not important_selector(selector):
            continue
        protected += 1; conditions.add(env)
        pieces = split_top(raw, ';')
        check(any(piece.strip() for piece in pieces), 'empty critical CSS rule: ' + selector[:80])
        seen = set()
        for declaration in pieces:
            if not declaration: continue
            check(':' in declaration, 'malformed property in ' + selector[:80])
            prop, val = declaration.split(':', 1)
            prop, val = prop.strip().lower(), val.strip()
            check(prop and val and prop not in seen, 'duplicate/empty CSS property in critical rule')
            seen.add(prop)
            check(not unsafe(prop, val), 'citation/scope concealed by ' + selector[:100] + ' ' + prop + ':' + val[:100] + ' in ' + env)
    check(total > 0 and protected > 0, 'no citation/scope stylesheet selectors found')
    return {'state': 'STATIC_STYLESHEET_REVIEW_ONLY', 'rules_inspected': total,
            'protected_rules': protected, 'conditional_scopes': sorted(conditions),
            'browser_verified': False, 'computed_css_verified': False,
            'wordpress_theme_verified': False, 'print_browser_verified': False,
            'source_claim_support_verified': False, 'qualified_qd_pass': False,
            'may_publish': False, 'release_state': HOLD}

def _load_pinned(root, relative, sha):
    root = root.resolve(); p = root / relative
    check(p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(root), 'required source missing: ' + relative)
    raw = p.read_bytes()
    check(gitblob(raw) == sha, 'Git blob mismatch: ' + relative)
    return raw

def native(root):
    css = _load_pinned(root, 'assets/preparedness.css', STYLE_BLOB).decode('utf-8')
    result = audit_css(css)
    # Invoke inherited authentic 35-article literal-visibility gate, not a stub.
    source = root / 'tools/r469_citation_visibility_custody.py'
    _load_pinned(root, 'tools/r469_citation_visibility_custody.py', R469_BLOB)
    spec = importlib.util.spec_from_file_location('r470_parent', source)
    check(spec and spec.loader, 'unloadable R469 parent')
    old = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = old
    spec.loader.exec_module(old)
    receipt = old.native(root)
    check(receipt['article_count'] == 35 and receipt['citation_count'] == 2000, 'R469 article/citation drift')
    result.update({'articles': 35, 'citation_occurrences': 2000,
                   'cited_original_35': True, 'source_truth_verified': False})
    return result

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    opts = ap.parse_args(argv)
    try:
        print(json.dumps(native(opts.root), sort_keys=True))
    except (CSSHold, ValueError, KeyError, TypeError, OSError, UnicodeError) as exc:
        print(json.dumps({'state': 'CSS_CITATION_EXPOSURE_FAILURE_HARD_HOLD',
                          'release_state': HOLD, 'qualified_qd_pass': False,
                          'may_publish': False, 'error': str(exc)}, sort_keys=True))
    return 2  # Structural scan cannot authorize a release.

if __name__ == '__main__':
    sys.exit(main())
