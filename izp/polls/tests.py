from django.test import TestCase
import datetime
from django.utils import timezone
from polls.models import Question
from django.urls import reverse


def create_question(question_text, days=0, start=0, end=0):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    if days != 0 and start == 0 and end == 0:
        time = timezone.now() + datetime.timedelta(days=days)
        return Question.objects.create(question_text=question_text, start_date=time)
    if days != 0 and start != 0 and end == 0:
        time = start + datetime.timedelta(days=days)
        return Question.objects.create(question_text=question_text, start_date=start, end_date=time)
    return Question.objects.create(question_text=question_text, start_date=start, end_date=start)


class QuestionIndexViewTests(TestCase):
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

    def test_future_question(self):
        """
        Questions with a start_date in the future are displayed on the index page.
        """
        """
        Alternative version, in case we don't want to show future questions:
            create_question(question_text="Future question.", days=30)
            response = self.client.get(reverse('polls:index'))
            self.assertContains(response, "Brak ankiet.")
            self.assertQuerysetEqual(response.context['questions_list'], [])
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
            ['<Question: Long time question 2.>',
             '<Question: Long time question 1.>']
        )

    def test_short_time_questions(self):
        """
        The questions index page may display short time questions.
        """
        create_question(question_text="Short time question 1.",
                        start=timezone.now(), end=timezone.now() + datetime.timedelta(minutes=6))
        create_question(question_text="Short time question 2.",
                        start=timezone.now(), end=timezone.now() + datetime.timedelta(minutes=3))
        create_question(question_text="Short time question 3.",
                        start=timezone.now(), end=timezone.now() + datetime.timedelta(minutes=5))

        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['questions_list'],
            ['<Question: Short time question 3.>', '<Question: Short time question 2.>',
             '<Question: Short time question 1.>']
        )


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a start_date in the future display question
        and warning, that voting is inactive.
        """

        future_question = create_question(
            question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertContains(response, future_question.question_text)
        self.assertContains(response, "Głosowanie nie jest aktywne")

    def test_past_question(self):
        """
        The detail view of a question with a start_date in the past display question
        and warning, that voting is inactive.
        """
        past_question = create_question(
            question_text='Past Question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
        self.assertContains(response, "Głosowanie nie jest aktywne")

    def test_future_actual_and_past_question(self):
        """
        Even if past, actual and future questions exist, only actual questions
        are able to vote.
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

        actual_question = create_question(
            question_text='Actual question.', days=0)
        url = reverse('polls:detail', args=(actual_question.id,))
        actual_response = self.client.get(url)
        self.assertNotContains(actual_response, "Głosowanie nie jest aktywne")

        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['questions_list'],
            ['<Question: Future question.>', '<Question: Actual question.>',
             '<Question: Past question.>']
        )
