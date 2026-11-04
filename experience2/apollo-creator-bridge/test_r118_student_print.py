"""R118 negative controls for classroom packet print custody. Offline SOURCE tests."""
from pathlib import Path
import unittest
from qa_r118_student_print import validate, PrintIntegrityError

HTML = Path(__file__).with_name("landing-preview.html").read_text(encoding="utf-8")

class StudentPrintTests(unittest.TestCase):
    def broken(self, old, new):
        self.assertIn(old, HTML)
        with self.assertRaises(PrintIntegrityError):
            validate(HTML.replace(old, new, 1))

    def test_01_actual_source_is_guarded(self):
        result = validate(HTML)
        self.assertEqual(result["production_status"], "STAGING_HOLD")
        self.assertEqual(result["student_prompts"], 3)
        self.assertEqual(result["writing_lines"], 9)
    def test_02_missing_print_article(self):
        self.broken("data-fv-student-print", "data-fv-student-NO")
    def test_03_duplicate_print_attribute(self):
        self.broken('<article class="student-print-sheet"',
                    '<article data-fv-student-print class="student-print-sheet"')
    def test_04_missing_print_visibility(self):
        self.broken(".student-print-sheet{display:block!important", ".student-print-sheet{display:none!important")
    def test_05_teacher_answers_not_suppressed(self):
        self.broken("#classroom-preview .callout{display:none!important}",
                    "#classroom-preview .callout{display:block!important}")
    def test_06_leaks_on_screen(self):
        self.broken(".print-custody,.student-print-sheet{display:none}", ".print-custody{display:none}")
    def test_07_wrong_reading_order(self):
        self.broken("#classroom-preview{break-before:page}", "#classroom-preview{break-before:auto}")
    def test_08_fewer_student_prompts(self):
        self.broken("<ol data-fv-student-prompts>", "<ol>")
    def test_09_missing_writing_lines(self):
        self.broken('<span></span><span></span><span></span>', '<span></span><span></span>')
    def test_10_untrusted_student_source(self):
        self.broken('href="https://www.nasa.gov/apollo-1-resources/">NASA Apollo 1 resources</a>',
                    'href="https://other.test/redirect">NASA Apollo 1 resources</a>')
    def test_11_removed_report_citation(self):
        self.broken('href="https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/">Apollo 204 Review Board report</a>',
                    'href="#classroom-preview">Apollo 204 Review Board report</a>')
    def test_12_duplicate_primary_action(self):
        self.broken('<a class="cta" href="#classroom-preview" data-fv-primary-cta>',
                    '<a class="cta" href="#classroom-preview" data-fv-primary-cta data-fv-primary-cta>')
    def test_13_no_photo_rights_assertion(self):
        self.assertIn("S67-19766 (provisional)", HTML)
        with self.assertRaises(PrintIntegrityError):
            validate(HTML.replace("S67-19766 (provisional)", "S67-19766 (confirmed)"))
    def test_14_missing_source_diversity(self):
        self.broken("Two independently identified sources", "Only one website required")
    def test_15_no_student_chronology(self):
        self.broken("how that differs from the January 27 event chronology",
                    "how that differs from the event chronology")

if __name__ == "__main__":
    unittest.main()
