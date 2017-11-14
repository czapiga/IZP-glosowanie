from django.test import TestCase
from django.utils import timezone
from .models import SimpleQuestion, Question
from .codes import generate_codes

class SimpleQuestionTests(TestCase):

    def test_choices_count(self):
        q = SimpleQuestion(question_text = "Ultimate Question of Life, the Universe, and Everything")
        q.save()
        self.assertIs(len(q.choice_set.all()), 2)
		
    def test_choices_content(self):
        q = SimpleQuestion(question_text = "Ultimate Question of Life, the Universe, and Everything")
        q.save()
        q = map(str, q.choice_set.all())
        self.assertIs('Tak' in q and 'Nie' in q, True)   
		
    def test_initial_votes(self):
        q = SimpleQuestion(question_text = "Ultimate Question of Life, the Universe, and Everything")
        q.save()
        for choice in q.choice_set.all():
            self.assertIs(choice.votes, 0)

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
        while codes: # codes equals true if its not empty
            code = codes.pop()
            self.assertNotIn(code, codes)
