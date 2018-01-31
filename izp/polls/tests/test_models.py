"""
Tests for models
"""
import os
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from polls.models import Question, SimpleQuestion, OpenQuestion, \
    PeopleQuestion, Poll
from polls.employers import Employers


class ChoiceUniquenessTests(TestCase):
    def setUp(self):
        poll = Poll.objects.create()
        question = OpenQuestion.objects.create(
            poll=poll, question_text="OpenQuestion")
        question.choice_set.create(choice_text="Odp1")
        question.choice_set.create(choice_text="Odp2")
        question.activate()

    def test_vote_same_open_answer_twice(self):
        """
        If the same open answer is written twice in two votes,
        it counts as one answer with two votes.
        """
        question = OpenQuestion.objects.get(question_text="OpenQuestion")

        s = self.client.session
        s['poll' + str(question.poll.id)] = question.poll.get_codes()[0]
        s.save()

        url = reverse('polls:vote', args=(question.id,))

        response = self.client.post(
            url, {'is_open': True,
                  'new_choice': 'Odp'})

        del s['poll' + str(question.poll.id)]
        s.save()

        s['poll' + str(question.poll.id)] = question.poll.get_codes()[1]
        s.save()

        response = self.client.post(
            url, {'is_open': True,
                  'new_choice': 'Odp'})

        self.assertIs(question.choice_set.filter(votes__exact=2).count(), 1)
        self.assertIs(question.choice_set.filter(votes__exact=0).count(), 2)
        self.assertIs(question.choice_set.all().count(), 3)

    def test_vote_two_similar_answers(self):
        """
        If two similar but not the same open answers are written in two votes,
        it counts as two different answers with one vote each.
        """
        question = OpenQuestion.objects.get(question_text="OpenQuestion")
        url = reverse('polls:vote', args=(question.id,))

        s = self.client.session
        s['poll' + str(question.poll.id)] = question.poll.get_codes()[0]
        s.save()

        response = self.client.post(
            url, {'is_open': True,
                  'new_choice': 'odp3'})

        del s['poll' + str(question.poll.id)]
        s.save()

        s['poll' + str(question.poll.id)] = question.poll.get_codes()[1]
        s.save()

        response = self.client.post(
            url, {'is_open': True,
                  'new_choice': '3odp'})

        self.assertIs(question.choice_set.filter(votes__exact=1).count(), 2)
        self.assertIs(question.choice_set.filter(votes__exact=0).count(), 2)
        self.assertIs(question.choice_set.all().count(), 4)


class QuestionTests(TestCase):
    """
    Tests for Question class methods:
    is_available, is_active, activate, deactivate
    """

    def setUp(self):
        poll = Poll.objects.create()
        question = Question.objects.create(
            poll=poll, question_text="test-question")

    def test_is_available(self):
        question = Question.objects.get(question_text="test-question")
        self.assertTrue(question.is_available())
        question.activate()
        self.assertFalse(question.is_available())
        question.deactivate()
        self.assertFalse(question.is_available())

    def test_is_active_no_deactivation_time(self):
        question = Question.objects.get(question_text="test-question")
        self.assertFalse(question.is_active())
        question.activate()
        self.assertTrue(question.is_active())
        question.deactivate()
        self.assertFalse(question.is_active())

    def test_is_active_given_deactivation_time(self):
        question = Question.objects.get(question_text="test-question")
        self.assertFalse(question.is_active())
        question.activate(minutes=1)
        self.assertTrue(question.is_active())
        question.deactivate()
        self.assertFalse(question.is_active())

    def test_try_to_deativate_inactive_question(self):
        question = Question.objects.get(question_text="test-question")
        question.deactivate()
        self.assertIsNone(question.deactivation_time)


class OpenQuestionTests(TestCase):

    def test_creating_open_question(self):
        poll = Poll.objects.create()
        open_question = OpenQuestion.objects.create(
            poll=poll, question_text="OpenQuestion")
        open_question.choice_set.create(choice_text="Odp1")
        open_question.choice_set.create(choice_text="Odp2")
        self.assertIs(len(open_question.choice_set.all()), 2)
        open_question = map(str, open_question.choice_set.all())
        self.assertIs(
            'Odp1' in open_question and 'Odp2' in open_question, True)

    def test_creating_empty_open_question(self):
        poll = Poll.objects.create()
        open_question = OpenQuestion.objects.create(
            poll=poll, question_text="OpenQuestion")
        self.assertIs(len(open_question.choice_set.all()), 0)


class SimpleQuestionTests(TestCase):
    def test_choices_count(self):
        poll = Poll.objects.create()
        q = SimpleQuestion(poll=poll, question_text="Tak czy nie?")
        q.save()
        self.assertIs(len(q.choice_set.all()), 2)

    def test_choices_content(self):
        poll = Poll.objects.create()
        q = SimpleQuestion(poll=poll, question_text="Tak czy nie?")
        q.save()
        q = map(str, q.choice_set.all())
        self.assertIs('Tak' in q and 'Nie' in q, True)

    def test_initial_votes(self):
        poll = Poll.objects.create()
        q = SimpleQuestion(poll=poll, question_text="Tak czy nie?")
        q.save()
        for choice in q.choice_set.all():
            self.assertIs(choice.votes, 0)


class PollTests(TestCase):
    def test_contains_codes(self):
        poll = Poll.objects.create()
        codes = poll.get_codes()
        self.assertTrue(codes)
        self.assertEqual(len(codes), 82)
        self.assertEqual(len(codes[0]), 8)

    def test_is_code_correct(self):
        poll = Poll.objects.create()
        codes = poll.get_codes()
        for code in codes:
            self.assertTrue(poll.is_code_correct(code))

    def test_adding_question(self):
        poll = Poll.objects.create()
        question = Question.objects.create(
            poll=poll, question_text="test-question")
        self.assertIn(question, poll.question_set.all())

    def test_adding_simple_question(self):
        poll = Poll.objects.create()
        question = SimpleQuestion.objects.create(
            poll=poll, question_text="test-question")
        question_names = map(str, poll.question_set.all())
        self.assertIn(str(question), question_names)

    def test_adding_open_question(self):
        poll = Poll.objects.create()
        question = OpenQuestion.objects.create(
            poll=poll, question_text="test-question")
        question_names = map(str, poll.question_set.all())
        self.assertIn(str(question), question_names)


class EmployersClassTest(TestCase):
    """
    Tests for Employers class
    """

    def test_list_correction(self):
        """
        Test if employers_list is created correctly
        """

        employers_list = Employers.get_list()
        if os.path.exists('polls/static/data/employers'):
            data = []
            with open("polls/static/data/employers") as f:
                data = f.read().split('\n')
            assert data == employers_list
        else:
            assert employers_list == []
