"""
Tests for various utilities
"""
from django.test import TestCase
from polls.codes import generate_codes
from polls.views import reformat_code, format_codes_list


class CodesTests(TestCase):
    def test_codes_number_and_length(self):
        codes = generate_codes(10, 10)
        self.assertEqual(len(codes), 10)
        for code in codes:
            self.assertEqual(len(code), 10)

    def test_codes_characters(self):
        code = generate_codes(1, 1000)[0]
        char_base = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for char in code:
            self.assertIn(char, char_base)

    def test_codes_invalid_params(self):
        try:
            generate_codes(10, 1)
        except ValueError:
            return
        else:
            self.fail("Expected ValueError with given params")

    def test_codes_uniqueness(self):
        codes = generate_codes(100, 10)
        while codes:
            code = codes.pop()
            self.assertNotIn(code, codes)


class ReformatCodeTests(TestCase):
    def test_short_code(self):
        code = "OPA"
        formated_code = reformat_code(code)
        self.assertEqual(code, formated_code)

    def test_code_without_separators(self):
        code = "OPAFAJEMDEDJ"
        formated_code = reformat_code(code)
        self.assertEqual(code, formated_code)

    def test_good_code_with_separators(self):
        code = "IZ02-FW4Z"
        code2 = "IZ02-FW4Z-HBQX-JWO"
        formated_code = reformat_code(code)
        formated_code2 = reformat_code(code2)
        self.assertEqual("IZ02FW4Z", formated_code)
        self.assertEqual("IZ02FW4ZHBQXJWO", formated_code2)

    def test_wrong_code_with_separators(self):
        code = "IZ02-FW4Z-"
        code2 = "IZ-02-FW4Z-HBQX-JWO"
        formated_code = reformat_code(code)
        formated_code2 = reformat_code(code2)
        self.assertEqual("", formated_code)
        self.assertEqual("", formated_code2)


class FormatCodeListTests(TestCase):
    def test_format_codes_list(self):
        codes_list = ["IZ02FW4Z", "IZPW", "IZP", "IZ0FW4GEI"]
        formated_codes_list = format_codes_list(codes_list)
        self.assertEqual("IZ02-FW4Z", formated_codes_list[0])
        self.assertEqual("IZPW", formated_codes_list[1])
        self.assertEqual("IZP", formated_codes_list[2])
        self.assertEqual("IZ0F-W4GE-I", formated_codes_list[3])
