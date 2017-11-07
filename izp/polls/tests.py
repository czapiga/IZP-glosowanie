from django.test import TestCase
from .codes import generate_codes

"""
Tests for codes generating module
"""

class CodesTests(TestCase):
    def test_codes_number(self):
        test_codes = generate_codes(5, 10)
        self.assertEqual(len(test_codes), 5)

    def test_codes_length(self):
        test_code = generate_codes(1, 10)[0]
        self.assertEqual(len(test_code), 10)

    def test_codes_characters(self):
        """
        Expected uppercase letters and digits only
        """
        char_base = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        test_codes = generate_codes(10, 100)
        for code in test_codes:
            for char in code:
                self.assertIn(char, char_base)

    def test_unique_part(self):
        """
        Last characters should be digits from 0 to 9
        for first 10 codes
        """
        test_codes = generate_codes(10, 10)
        for i, code in enumerate(test_codes):
            self.assertEqual(code[-1], str(i))
    
    def test_invalid_input(self):
        raised_exception = False
        try:
            generate_codes(100, 1)
        except ValueError:
            raised_exception = True
        self.assertTrue(raised_exception)
