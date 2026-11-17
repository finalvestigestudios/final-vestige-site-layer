"""Filesystem-only regression for the offline FV 960px staging destination.

No image binaries, HTTP, WordPress writes or paid services. Run from:
  python -m unittest discover -s qa/media-recovery -p 'test_staging_output_root_20261104.py' -v
"""
import tempfile
import unittest
from pathlib import Path
from prepare_hero_derivatives import validated_output_root


class StagedOutputPathTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.home = Path(tmp.name)
        self.sources = self.home / 'originals'
        self.sources.mkdir()

    def test_regular_sibling_staging_is_allowed(self):
        requested = self.home / 'staging'
        self.assertEqual(validated_output_root(requested, self.sources), requested.resolve())
        self.assertFalse(requested.exists())

    def test_staging_under_source_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'output_directory_must_be_separate_from_originals'):
            validated_output_root(self.sources / 'generated', self.sources)

    def test_source_root_itself_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'output_directory_must_be_separate_from_originals'):
            validated_output_root(self.sources, self.sources)

    def test_symlinked_staging_root_is_refused(self):
        elsewhere = self.home / 'elsewhere'
        elsewhere.mkdir()
        link = self.home / 'staging'
        link.symlink_to(elsewhere, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'output_path_symlink_component_refused'):
            validated_output_root(link, self.sources)
        self.assertEqual(list(elsewhere.iterdir()), [])

    def test_symlinked_parent_is_refused(self):
        elsewhere = self.home / 'elsewhere'
        elsewhere.mkdir()
        alias = self.home / 'alias'
        alias.symlink_to(elsewhere, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'output_path_symlink_component_refused'):
            validated_output_root(alias / 'uncreated-child', self.sources)
        self.assertFalse((elsewhere / 'uncreated-child').exists())

    def test_symlink_pointing_into_source_is_refused(self):
        link = self.home / 'alias'
        link.symlink_to(self.sources, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'output_path_symlink_component_refused'):
            validated_output_root(link / 'derived', self.sources)
        self.assertFalse((self.sources / 'derived').exists())


if __name__ == '__main__':
    unittest.main()
