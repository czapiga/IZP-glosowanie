from django.test import TestCase
from django.utils import timezone
from .models import SimpleQuestion, Question
from functools import reduce
# Create your tests here.

class SimpleQuestionTests(TestCase):

    def test_choices_count(self):
        q = SimpleQuestion(question_text = "Ultimate Question of Life, the Universe, and Everything")
        q.save()
        self.assertIs(len(q.choice_set.all()), 2)
		
    def test_choices_content(self):
        q = SimpleQuestion(question_text = "Ultimate Question of Life, the Universe, and Everything")
        q.save()
        q = map(str, q.choice_set.all())
        self.assertIs('Yes' in q and 'No' in q, True)   
		
    def test_initial_votes(self):
        q = SimpleQuestion(question_text = "Ultimate Question of Life, the Universe, and Everything")
        q.save()
        vc = 0
        for c in q.choice_set.all():
            vc += c.votes		
        self.assertIs(vc, 0) 