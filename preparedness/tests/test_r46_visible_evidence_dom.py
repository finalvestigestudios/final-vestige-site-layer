"""R46: fail-closed browser-visible HOLD placement and readable evidence.

R45's original permitted-tag census did not enforce a browser DOM scaffold:
a re-hashed offline ZIP could carry a single valid warning in <head>, a valid
back link buried inside source evidence, or bidi/nonprinting control marks.
None of those states is adequate for independent human citation review.
All test fixtures are synthetic; never mutate original Claude source records.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import reviewer_html_semantic_gate as gate
import reviewer_private_zip_gate as r44


BODY = '<section><h2>Evidence</h2><p>Evidence visible.</p>' \
       '<article><dl><dt>Source scope</dt><dd><pre>Original context retained.</pre>' \
       '</dd></dl></article></section>'
ARTICLE = r44.r43.page('Synthetic offline article', BODY, '../index.html')
INDEX = r44.r43.page(
    'Private reviewer index',
    '<section><h2>Original review rows</h2>'
    '<p><a href="global-source-variants.html">Shared variants</a></p>'
    '<ol><li><a href="articles/sample.html">Sample</a></li></ol></section>')
SHARED = r44.r43.page(
    'Shared-source groups',
    '<section><h2>Original source variants</h2>'
    '<article><dl><dt>URL</dt><dd><pre>Uncited shared variant retained.</pre>'
    '</dd></dl></article></section>', 'index.html')
WARNING = re.search(r'<p class="hold">.*?</p>', ARTICLE, re.DOTALL).group()
BACK = '<p><a href="../index.html">Private index</a></p>'
GLOBAL_BACK = '<p><a href="index.html">Private index</a></p>'


def moving_warning(original, marker):
    return original.replace(WARNING, '', 1).replace(marker, WARNING + marker, 1)


class ValidOriginals(unittest.TestCase):
    def test_original_article(self):
        self.assertEqual(gate.inspect_page('articles/sample.html', ARTICLE),
                         ('../index.html',))

    def test_original_index(self):
        self.assertEqual(gate.inspect_page('index.html', INDEX),
                         ('global-source-variants.html', 'articles/sample.html'))

    def test_original_shared_source(self):
        self.assertEqual(gate.inspect_page('global-source-variants.html', SHARED),
                         ('index.html',))

    def test_original_full_html_source_markup_remains_inert(self):
        body = BODY.replace('Evidence visible.',
                            'Evidence &lt;script&gt;import x&lt;/script&gt; '
                            '&lt;a href="javascript:alert(1)"&gt; literal only.')
        page = r44.r43.page('Literal original source', body, '../index.html')
        self.assertEqual(gate.inspect_page('articles/sample.html', page),
                         ('../index.html',))

    def test_printable_unusual_source_terminology_remains_intact(self):
        text = 'Cañón • łéʼééʼ • 清水 • 𐎀𐎁 • °C — 1805–1806.'
        body = BODY.replace('Evidence visible.', text)
        page = r44.r43.page('Multilingual original', body, '../index.html')
        self.assertIn(text, page)
        self.assertEqual(gate.inspect_page('articles/sample.html', page),
                         ('../index.html',))

    def test_legitimate_line_spacing_controls_preserved(self):
        for codepoint in (9, 10, 13):
            with self.subTest(codepoint=codepoint):
                body = BODY.replace('Evidence visible.',
                                    'Evidence' + chr(codepoint) + ' visible.')
                page = r44.r43.page('Safe whitespace', body, '../index.html')
                self.assertEqual(gate.inspect_page('articles/sample.html', page),
                                 ('../index.html',))


class HostileStructure(unittest.TestCase):
    def reject(self, name, original, altered):
        self.assertNotEqual(original, altered, 'negative transform must do work')
        with self.assertRaises(gate.SemanticHold):
            gate.inspect_page(name, altered)

    def test_warning_moved_into_head(self):
        self.reject('articles/sample.html', ARTICLE,
                    moving_warning(ARTICLE, '</head>'))

    def test_warning_moved_after_main(self):
        self.reject('articles/sample.html', ARTICLE,
                    moving_warning(ARTICLE, '</body>'))

    def test_warning_nested_in_main_section(self):
        self.reject('articles/sample.html', ARTICLE,
                    ARTICLE.replace(WARNING, '', 1)
                    .replace('<section>', '<section>' + WARNING, 1))

    def test_warning_moved_after_h1_but_before_body(self):
        self.reject('articles/sample.html', ARTICLE,
                    moving_warning(ARTICLE, '<body>'))

    def test_warning_moved_into_title(self):
        self.reject('articles/sample.html', ARTICLE,
                    ARTICLE.replace(WARNING, '', 1)
                    .replace('</title>', WARNING + '</title>', 1))

    def test_main_moved_after_body(self):
        whole = re.search(r'<main>.*?</main>', ARTICLE, re.DOTALL).group()
        self.reject('articles/sample.html', ARTICLE,
                    ARTICLE.replace(whole, '', 1)
                    .replace('</body>', '</body>' + whole, 1))

    def test_h1_moved_into_main(self):
        heading = re.search(r'<h1>.*?</h1>', ARTICLE, re.DOTALL).group()
        self.reject('articles/sample.html', ARTICLE,
                    ARTICLE.replace(heading, '', 1)
                    .replace('<main>', '<main>' + heading, 1))

    def test_h1_moved_to_head(self):
        heading = re.search(r'<h1>.*?</h1>', ARTICLE, re.DOTALL).group()
        self.reject('articles/sample.html', ARTICLE,
                    ARTICLE.replace(heading, '', 1)
                    .replace('</head>', heading + '</head>', 1))

    def test_title_moved_into_body(self):
        title = re.search(r'<title>.*?</title>', ARTICLE, re.DOTALL).group()
        self.reject('articles/sample.html', ARTICLE,
                    ARTICLE.replace(title, '', 1)
                    .replace('<body>', '<body>' + title, 1))

    def test_reordered_meta_tags(self):
        one = '<meta charset="utf-8">'
        two = '<meta http-equiv="Content-Security-Policy" content="' \
              + gate.CSP + '">'
        self.assertIn(one + two, ARTICLE)
        self.reject('articles/sample.html', ARTICLE,
                    ARTICLE.replace(one + two, two + one, 1))

    def test_reordered_title_and_style(self):
        pair = re.search(r'(<title>.*?</title>)(<style>.*?</style>)',
                         ARTICLE, re.DOTALL)
        self.assertIsNotNone(pair)
        self.reject('articles/sample.html', ARTICLE,
                    ARTICLE.replace(pair.group(), pair.group(2) + pair.group(1), 1))

    def test_article_back_link_moved_into_evidence(self):
        self.assertIn(BACK, ARTICLE)
        self.reject('articles/sample.html', ARTICLE,
                    ARTICLE.replace(BACK, '', 1)
                    .replace('<section>', '<section>' + BACK, 1))

    def test_shared_back_link_moved_into_evidence(self):
        self.assertIn(GLOBAL_BACK, SHARED)
        self.reject('global-source-variants.html', SHARED,
                    SHARED.replace(GLOBAL_BACK, '', 1)
                    .replace('<section>', '<section>' + GLOBAL_BACK, 1))

    def test_index_shared_source_link_moved_into_article_list(self):
        old = '<p><a href="global-source-variants.html">Shared variants</a></p>'
        new = '<ol><li><a href="global-source-variants.html">' \
              'Shared variants</a></li></ol>'
        self.reject('index.html', INDEX, INDEX.replace(old, new, 1))

    def test_index_article_link_moved_into_paragraph(self):
        old = '<li><a href="articles/sample.html">Sample</a></li>'
        new = '<li>Sample</li></ol><p>' \
              '<a href="articles/sample.html">Sample</a></p><ol>'
        self.reject('index.html', INDEX, INDEX.replace(old, new, 1))

    def test_index_section_moved_into_head(self):
        section = re.search(r'<section>.*?</section>', INDEX, re.DOTALL).group()
        self.reject('index.html', INDEX,
                    INDEX.replace(section, '', 1)
                    .replace('</head>', section + '</head>', 1))

    def test_source_dl_moved_directly_under_main(self):
        rows = re.search(r'<article><dl>.*?</dl></article>',
                         ARTICLE, re.DOTALL).group()
        self.reject('articles/sample.html', ARTICLE,
                    ARTICLE.replace(rows, '', 1)
                    .replace('</main>', rows + '</main>', 1))

    def test_nested_source_article_inside_paragraph(self):
        rows = re.search(r'<article><dl>.*?</dl></article>',
                         ARTICLE, re.DOTALL).group()
        self.reject('articles/sample.html', ARTICLE,
                    ARTICLE.replace(rows, '', 1)
                    .replace('Evidence visible.</p>',
                             'Evidence visible.' + rows + '</p>', 1))

    def test_source_pre_directly_under_section(self):
        self.reject('articles/sample.html', ARTICLE,
                    ARTICLE.replace('<dd><pre>', '<dd></dd><pre>', 1)
                    .replace('</pre></dd>', '</pre>', 1))

    def test_source_heading_moved_below_dl(self):
        self.reject('articles/sample.html', ARTICLE,
                    ARTICLE.replace('<h2>Evidence</h2>', '', 1)
                    .replace('<dt>Source scope</dt>',
                             '<dt>Source scope</dt><h2>Evidence</h2>', 1))


class HostileSourceControls(unittest.TestCase):
    def assertRejected(self, altered):
        self.assertNotEqual(ARTICLE, altered)
        with self.assertRaises(gate.SemanticHold):
            gate.inspect_page('articles/sample.html', altered)

    def test_source_html_encoded_bidi_override(self):
        self.assertRejected(ARTICLE.replace('Evidence visible.',
                                             'Evidence&#x202e; visible.', 1))

    def test_source_html_encoded_isolate(self):
        self.assertRejected(ARTICLE.replace('Evidence visible.',
                                             'Evidence&#x2067; visible.', 1))

    def test_warning_html_encoded_bidi_override(self):
        self.assertRejected(ARTICLE.replace(
            'PRIVATE / UNVERIFIED / HOLD.',
            'PRIVATE / UNVERIFIED / HOLD.&#x202e;', 1))

    def test_title_html_encoded_bidi_override(self):
        self.assertRejected(ARTICLE.replace(
            'Synthetic offline article',
            'Synthetic&#x202e; offline article', 1))

    def test_original_source_visible_evidence_not_deleted(self):
        self.assertIn('Evidence visible.', ARTICLE)
        self.assertIn('Original context retained.', ARTICLE)


# Every control is its own independent native unittest, not one subTest count.
# Original source content is never silently normalized, stripped, truncated,
# URL-deduplicated, considered medically safe, or human-verified.
CONTROL_CODEPOINTS = (
    list(range(0x01, 0x09)) + [0x0b, 0x0c] +
    list(range(0x0e, 0x20)) + list(range(0x7f, 0xa0)) +
    [0x00ad, 0x061c, 0x200b, 0x200e, 0x200f, 0x2060, 0xfeff] +
    list(range(0x202a, 0x202f)) + list(range(0x2066, 0x206a))
)


def control_method(cp):
    def execute(self):
        altered = ARTICLE.replace('Evidence visible.',
                                  'Evidence' + chr(cp) + ' visible.', 1)
        self.assertRejected(altered)
    execute.__name__ = 'test_reject_invisible_or_bidi_control_U%04X' % cp
    return execute


for _point in CONTROL_CODEPOINTS:
    setattr(HostileSourceControls,
            'test_reject_control_U%04X' % _point, control_method(_point))


if __name__ == '__main__':
    unittest.main()
