import sys
from pathlib import Path
import types
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'evals'))
from simplification_fixtures import CSV_HELPER, DATE_APP, SUMMARY_APP, check
from run_simplification import documents_read


def module(source):
    result = types.ModuleType('fixture')
    exec(source, result.__dict__)
    return result


class SimplificationAcceptanceTests(unittest.TestCase):
    def test_document_read_transport_and_missing_text(self):
        document = '# Guide\r\nKeep validation.\r\n'
        command = {'exit_code': 0, 'aggregated_output': '# Guide\r\r\nKeep validation.\r\r\n'}
        self.assertTrue(documents_read([document], [command]))
        self.assertTrue(documents_read([document], [dict(command, aggregated_output='# Guide\n\nKeep validation.\n\n')]))
        self.assertFalse(documents_read([document], [dict(command, exit_code=1)]))
        self.assertFalse(documents_read([document], [dict(command, aggregated_output='# Guide\n')]))
        self.assertFalse(documents_read([document], [dict(command, aggregated_output='Keep validation.\n# Guide\n')]))

    def test_reference_behavior(self):
        self.assertEqual(check('duplicates', module(SUMMARY_APP)), 94)
        self.assertEqual(check('strict-date', module(DATE_APP)), 94)

    def test_reuse_valid_and_truthiness_regression(self):
        source = CSV_HELPER + '''
def export_all(rows):
    return export_rows(rows)
def export_active(rows):
    return export_rows(row for row in rows if row.get('active') is True)
'''
        self.assertEqual(check('reuse', module(source)), 36)
        with self.assertRaises(AssertionError):
            check('reuse', module(source.replace("row.get('active') is True", "row.get('active')")))

    def test_removed_cancelled_validation_is_detected(self):
        bad = SUMMARY_APP.replace("if type(row['quantity']) is not int or row['quantity'] < 0:",
                                  "if row['status'] == 'paid' and (type(row['quantity']) is not int or row['quantity'] < 0):")
        with self.assertRaises(AssertionError):
            check('duplicates', module(bad))

    def test_native_date_parser_alone_is_not_equivalent(self):
        bad = "from datetime import date\ndef parse_booking_date(value, blocked):\n    return date.fromisoformat(value)\n"
        with self.assertRaises(AssertionError):
            check('strict-date', module(bad))

    def test_changed_error_priority_is_detected(self):
        bad = DATE_APP.replace("    if day.weekday() == 5:", "    if value in blocked:\n        raise ValueError('blocked')\n    if day.weekday() == 5:")
        with self.assertRaises(AssertionError):
            check('strict-date', module(bad))

    def test_input_mutation_is_detected(self):
        bad = SUMMARY_APP.replace('    return output', '    rows.clear()\n    return output')
        with self.assertRaises(AssertionError):
            check('duplicates', module(bad))


if __name__ == '__main__':
    unittest.main()
