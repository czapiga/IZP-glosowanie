from django.test import TestCase
from django.utils import timezone
from .models import SimpleQuestion, Question

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
