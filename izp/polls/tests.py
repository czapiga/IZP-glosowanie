"""
Tests
"""
import datetime
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from .models import Question, SimpleQuestion
from .codes import generate_codes
from .forms import QuestionAdminForm
from django.forms import ValidationError


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
        self.assertContains(response, "Brak ankiet!")
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
        self.assertContains(response, "Brak ankiet!")
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


def create_question_form(name, start_date=0, end_date=0, time=0):
    if start_date != 0 and end_date != 0:
        return {'question_text': name,
                'start_date': start_date,
                'end_date': end_date,
                'time': time}

def create_moved_on_delta_minutes_question(start_point, name, start_delta,
                                           end_delta):

    start_date = start_point + datetime.timedelta(minutes=start_delta)
    end_date = start_point + datetime.timedelta(minutes=end_delta)
    create_question(name, 0, start_date, end_date)


class QuestionFormValidationTests(TestCase):
    """
    In this test case we use is_valid() function.
    How does it work?
    When we try to create new Question
    function clean() from  QuestionAdminForm in forms.py
    check is our input data valid. If one of properties
    is not valid than function add error to error list.
    After, is_valid() function check is error list
    empty and return True or False
    """
    start_point = timezone.now()

    def test_correct_question_validation(self):
        """
        It must be able to create question if
        it does not overlap with other.
        We try to create question with time range 10,15
        between qe_1 with time range 0,5
        and qe2 with time range 20,25.
        """

        create_moved_on_delta_minutes_question(self.start_point,
                                               'Q1', 0, 5)

        create_moved_on_delta_minutes_question(self.start_point,
                                               'Q2', 20, 20)


        form_start_date = self.start_point + datetime.timedelta(minutes=10)
        form_end_date = self.start_point + datetime.timedelta(minutes=15)

        form_data  = create_question_form(
            'Qe3',
            form_start_date,
            form_end_date
        )

        form = QuestionAdminForm(data=form_data)

        self.assertTrue(form.is_valid())

    def test_start_overlap(self):
        """
        Case when start_date of new question
        time range 3,8
        overlap with other question time range 0,5
        """
        
        create_moved_on_delta_minutes_question(self.start_point,
                                               'Q1', 0, 5)

        form_start_date = self.start_point + datetime.timedelta(minutes=3)
        form_end_date = self.start_point + datetime.timedelta(minutes=8)

        form_data = create_question_form('Qe2',
                                         form_start_date,
                                         form_end_date)
        form = QuestionAdminForm(data=form_data)

        self.assertFalse(form.is_valid())

    def test_end_overlap(self):
        """
        Case when end_date of new question time range 0,5
        overlap with other question time range -3,1
        """

        create_moved_on_delta_minutes_question(self.start_point,
                                               'Q1', 0, 5)

        form_start_date = self.start_point + datetime.timedelta(minutes=1)
        form_end_date = self.start_point - datetime.timedelta(minutes=3)

        form_data = create_question_form('Qe2',
                                         form_start_date,
                                         form_end_date)
        form = QuestionAdminForm(data=form_data)

        self.assertFalse(form.is_valid())

    def test_end_and_start_overlap(self):
        """
        Case when end_date and start_date of new question
        time range 3,8
        overlap with 2 different questions time ranges
        0,5 and 7,12
        """
        create_moved_on_delta_minutes_question(self.start_point,
                                               'Qe1', 0, 5)

        create_moved_on_delta_minutes_question(self.start_point,
                                               'Qe2', 7, 12)

        form_start_date = self.start_point + datetime.timedelta(minutes=3)
        form_end_date = self.start_point + datetime.timedelta(minutes=8)

        form_data = create_question_form(
            'Qe3',
            form_start_date,
            form_end_date
        )

        form = QuestionAdminForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_voting_inside_voting_overlap(self):
        """
        Case when new question time range 1,7
        is chronologically inside other
        time range 0,8
        """
        create_moved_on_delta_minutes_question(self.start_point,
                                               'Qe1', 0, 8)

        form_start_date = self.start_point + datetime.timedelta(minutes=1)
        form_end_date = self.start_point + datetime.timedelta(minutes=7)

        form_data = create_question_form(
            'Qe2',
            form_start_date,
            form_end_date
        )

        form = QuestionAdminForm(data=form_data)

        self.assertFalse(form.is_valid())
