"""
Tests
"""
import datetime
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from .models import Question, SimpleQuestion
from .codes import generate_codes


def create_question(question_text, days=0, start=0, end=0):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    if days != 0 and start == 0 and end == 0:
        start = timezone.now() + datetime.timedelta(days=days)
        return Question.objects.create(
            question_text=question_text, start_date=start)
    if days != 0 and start != 0 and end == 0:
        end = start + datetime.timedelta(days=days)
        return Question.objects.create(
            question_text=question_text, start_date=start, end_date=end)
    return Question.objects.create(
        question_text=question_text, start_date=start, end_date=end)


class QuestionIndexViewTests(TestCase):
    """
    Tests for views
    """

    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Brak ankiet.")
        self.assertQuerysetEqual(response.context['questions_list'], [])

    def test_past_question(self):
        """
        Questions with a start_date in the past are displayed on the
        index page.
        """
        create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['questions_list'],
            ['<Question: Past question.>']
        )

    def test_question_with_same_start_and_end_time(self):
        """
        Questions with a start_date which is equal to end_date should not be
        displayed.
        """
        time = timezone.now()
        create_question(question_text="Current question.",
                        start=time, end=time)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Brak ankiet.")
        self.assertQuerysetEqual(response.context['questions_list'], [])

    def test_future_question(self):
        """
        Questions with a start_date in the future are displayed on the index
        page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['questions_list'],
            ['<Question: Future question.>']
        )

    def test_future_question_and_past_question(self):
        """
        If both past and future questions exist, both are display.
        """
        create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))

        self.assertQuerysetEqual(
            response.context['questions_list'],
            ['<Question: Future question.>', '<Question: Past question.>']
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        create_question(question_text="Past question 1.", days=-30)
        create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['questions_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )

    def test_long_time_questions(self):
        """
        The questions index page may display long time questions.
        """
        create_question(question_text="Long time question 1.",
                        start=timezone.now(), days=30)
        create_question(question_text="Long time question 2.",
                        start=timezone.now(), days=5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['questions_list'],
            ['<Question: Long time question 1.>',
             '<Question: Long time question 2.>']
        )

    def test_short_time_questions(self):
        """
        The questions index page may display short time questions.
        """
        create_question(
            question_text="Short time question 1.",
            start=timezone.now(),
            end=timezone.now() + datetime.timedelta(minutes=6))
        create_question(
            question_text="Short time question 2.",
            start=timezone.now(),
            end=timezone.now() + datetime.timedelta(minutes=3))
        create_question(
            question_text="Short time question 3.",
            start=timezone.now(),
            end=timezone.now() + datetime.timedelta(minutes=5))

        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['questions_list'],
            ['<Question: Short time question 1.>',
             '<Question: Short time question 3.>',
             '<Question: Short time question 2.>']
        )


class QuestionDetailViewTests(TestCase):
    """
    Tests of polls details
    """

    def test_future_question(self):
        """
        The detail view of a question with a start_date in the future display
        question and warning, that voting is inactive.
        """

        future_question = create_question(
            question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertContains(response, future_question.question_text)
        self.assertContains(response, "Głosowanie nie jest aktywne")

    def test_past_question(self):
        """
        The detail view of a question with a start_date in the past display
        question and warning, that voting is inactive.
        """
        past_question = create_question(
            question_text='Past Question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
        self.assertContains(response, "Głosowanie nie jest aktywne")

    def test_future_current_and_past_question(self):
        """
        Even if past, current and future questions exist, only current
        questions are able to vote.
        """

        future_question = create_question(
            question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        future_response = self.client.get(url)
        self.assertContains(future_response, "Głosowanie nie jest aktywne")

        past_question = create_question(
            question_text='Past question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        past_response = self.client.get(url)
        self.assertContains(past_response, "Głosowanie nie jest aktywne")

        current_question = create_question(
            question_text='current question.',
            start=timezone.now(),
            end=timezone.now() + datetime.timedelta(minutes=5))
        url = reverse('polls:detail', args=(current_question.id,))
        current_response = self.client.get(url)
        self.assertNotContains(current_response, "Głosowanie nie jest aktywne")

        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['questions_list'],
            ['<Question: Future question.>',
             '<Question: current question.>',
             '<Question: Past question.>']
        )


class SimpleQuestionTests(TestCase):

    def test_choices_count(self):
        q = SimpleQuestion(question_text="Tak czy nie?")
        q.save()
        self.assertIs(len(q.choice_set.all()), 2)

    def test_choices_content(self):
        q = SimpleQuestion(question_text="Tak czy nie?")
        q.save()
        q = map(str, q.choice_set.all())
        self.assertIs('Tak' in q and 'Nie' in q, True)

    def test_initial_votes(self):
        q = SimpleQuestion(question_text="Tak czy nie?")
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
        code = generate_codes(1, 20)[0]
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
