import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from data_import_checks import analyze, load_schema, valid_type, safe_export_report


class ImportDoctorRegressionTests(unittest.TestCase):
    def setup_files(self, folder, csv_text, schema=None):
        root = Path(folder)
        source = root / 'source.csv'
        source.write_text(csv_text, encoding='utf-8')
        config = root / 'schema.json'
        if schema is not None:
            config.write_text(json.dumps(schema), encoding='utf-8')
        return source, (config if schema is not None else None)

    def test_existing_default_preflight(self):
        with tempfile.TemporaryDirectory() as d:
            csv, schema = self.setup_files(d,
                'id,amount,date,status\nA1,12.50,2026-10-27,open\nA1,broken,2026-02-30,unknown\n,2.00,2026-01-01,open\nA4,1,2026-01-01\n',
                {'required_columns':['id','amount'],'keys':['id'], 'types':{'amount':'decimal','date':'date'}, 'allowed_values':{'status':['open','closed']}})
            r = analyze(csv,schema)
            self.assertEqual(r['row_count'], 4)
            for key in ('duplicate_key','invalid_type','invalid_allowed_value','blank_key','blank_required_value','column_count_mismatch'):
                self.assertIn(key,r['issue_counts'])
            self.assertEqual(r['status'],'ISSUES')

    def test_clean_semicolon_bom(self):
        with tempfile.TemporaryDirectory() as d:
            csv, schema = self.setup_files(d,'\ufeffid;amount\nA;3.50\nB;4.25\n',{'keys':['id'],'types':{'amount':'decimal'}})
            r=analyze(csv,schema)
            self.assertEqual(r['delimiter'],';')
            self.assertEqual(r['status'],'PASS')
            self.assertEqual(r['row_count'],2)
            self.assertEqual(len(r['source_sha256']),64)

    def test_header_only_not_pass(self):
        with tempfile.TemporaryDirectory() as d:
            csv,_=self.setup_files(d,'id,amount\n')
            r=analyze(csv)
            self.assertEqual(r['status'],'INCOMPLETE')
            self.assertIn('no_data_rows',r['issue_counts'])

    def test_whitespace_only_file_not_pass(self):
        with tempfile.TemporaryDirectory() as d:
            csv,_=self.setup_files(d,' \n')
            r=analyze(csv)
            self.assertNotEqual(r['status'],'PASS')

    def test_invalid_csv_is_incomplete(self):
        with tempfile.TemporaryDirectory() as d:
            csv,_=self.setup_files(d,'id,amount\n1,"unclosed\n')
            r=analyze(csv)
            self.assertEqual(r['status'],'INCOMPLETE')
            self.assertIn('csv_parse_error',r['issue_counts'])

    def test_multiline_physical_line_references(self):
        with tempfile.TemporaryDirectory() as d:
            csv,schema=self.setup_files(d,'id,description\nA,"two\nphysical lines"\nA,duplicate\n',{'keys':['id']})
            r=analyze(csv,schema)
            self.assertEqual(r['row_count'],2)
            duplicate=next(x for x in r['examples'] if x['code']=='duplicate_key')
            self.assertEqual(duplicate['row'],4)
            self.assertIn('line 2', duplicate['message'])

    def test_case_and_unicode_header_collision_is_incomplete(self):
        with tempfile.TemporaryDirectory() as d:
            csv,_=self.setup_files(d,'AMOUNT,amount\n1,2\n')
            self.assertEqual(analyze(csv)['status'],'INCOMPLETE')
            csv.write_text('caf\u00e9,cafe\u0301\na,b\n',encoding='utf-8')
            self.assertIn('duplicate_header',analyze(csv)['issue_counts'])

    def test_invalid_numeric_formats_rejected(self):
        self.assertFalse(valid_type('1,2,3','decimal'))
        self.assertFalse(valid_type('NaN','decimal'))
        self.assertFalse(valid_type('Infinity','decimal'))
        self.assertFalse(valid_type('1e9','decimal'))
        self.assertFalse(valid_type('\u0661\u0662','integer'))
        self.assertTrue(valid_type('1,234.50','decimal'))
        self.assertTrue(valid_type('-12.25','decimal'))

    def test_schema_rejects_unknown_and_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'rules.json'
            p.write_text('{"keys":["id"],"keys":["name"]}',encoding='utf-8')
            with self.assertRaises(ValueError):load_schema(p)
            p.write_text('{"keyz":["id"]}',encoding='utf-8')
            with self.assertRaises(ValueError):load_schema(p)
            p.write_text('{"types":{"amount":"float-eval"}}',encoding='utf-8')
            with self.assertRaises(ValueError):load_schema(p)
            p.write_text('{"keys":["id","id"]}',encoding='utf-8')
            with self.assertRaises(ValueError):load_schema(p)

    def test_safe_export_writes_without_overwriting_existing(self):
        with tempfile.TemporaryDirectory() as d:
            csv,_=self.setup_files(d,'id,amount\na,1\n')
            r=analyze(csv)
            target=Path(d)/'report.json'
            safe_export_report(r,target,csv)
            self.assertEqual(json.loads(target.read_text())['status'],'PASS')
            with self.assertRaises(FileExistsError):safe_export_report(r,target,csv)
            with self.assertRaises(ValueError):safe_export_report(r,csv,csv)
            self.assertEqual(csv.read_text(),'id,amount\na,1\n')

    def test_reject_stale_source(self):
        with tempfile.TemporaryDirectory() as d:
            csv,_=self.setup_files(d,'id\na\n')
            r=analyze(csv)
            csv.write_text('id\nb\n',encoding='utf-8')
            with self.assertRaises(ValueError):safe_export_report(r,Path(d)/'report.json',csv)

    def test_reject_stale_schema(self):
        with tempfile.TemporaryDirectory() as d:
            csv,schema=self.setup_files(d,'id\na\n',{'keys':['id']})
            r=analyze(csv,schema)
            schema.write_text('{"keys":[]}',encoding='utf-8')
            with self.assertRaises(ValueError):safe_export_report(r,Path(d)/'report.json',csv,schema)

    def test_invalid_rule_column_not_pass(self):
        with tempfile.TemporaryDirectory() as d:
            csv,schema=self.setup_files(d,'id\na\n',{'types':{'missing':'date'}})
            r=analyze(csv,schema)
            self.assertEqual(r['status'],'ISSUES')
            self.assertIn('missing_rule_column',r['issue_counts'])

    def test_row_limit_is_incomplete(self):
        with tempfile.TemporaryDirectory() as d:
            csv,_=self.setup_files(d,'id\na\nb\nc\n')
            with patch('data_import_checks.MAX_ROWS',2):
                r=analyze(csv)
            self.assertEqual(r['status'],'INCOMPLETE')
            self.assertIn('row_limit_exceeded',r['issue_counts'])

    def test_field_size_limit_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            csv,_=self.setup_files(d,'id\nabcdefghij0123456789\n')
            with patch('data_import_checks.MAX_FIELD_CHARS',12):
                r=analyze(csv)
            self.assertEqual(r['status'],'INCOMPLETE')
            self.assertIn('csv_parse_error',r['issue_counts'])

    def test_source_size_limit(self):
        with tempfile.TemporaryDirectory() as d:
            csv,_=self.setup_files(d,'id\nabcdefghij\n')
            with patch('data_import_checks.MAX_SOURCE_BYTES',4):
                with self.assertRaises(ValueError):analyze(csv)

    def test_reject_symlink_output_target(self):
        with tempfile.TemporaryDirectory() as d:
            csv,_=self.setup_files(d,'id\na\n')
            r=analyze(csv)
            out=Path(d)/'out.json'
            out.symlink_to(csv)
            with self.assertRaises((ValueError,FileExistsError)):
                safe_export_report(r,out,csv)
            self.assertEqual(csv.read_text(),'id\na\n')

    def test_does_not_modify_input_or_schema(self):
        with tempfile.TemporaryDirectory() as d:
            csv,schema=self.setup_files(d,'id,amount\na,100\n',{'keys':['id']})
            before=(csv.read_bytes(),schema.read_bytes())
            analyze(csv,schema)
            self.assertEqual(before,(csv.read_bytes(),schema.read_bytes()))


if __name__=='__main__':
    unittest.main()
