"""
Tests
"""
import datetime
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from .models import Question, SimpleQuestion, OpenQuestion, Poll
from .codes import generate_codes
from django.contrib.auth.models import User
from .views import reformat_code, format_codes_list


def basic_check_of_question(cls, response, quest, error=""):
    cls.assertContains(response, quest.question_text)
    if error != "":
        cls.assertContains(response, error)
    cls.assertContains(response, 'Odp1')
    cls.assertContains(response, 'Odp2')


def basic_check_of_open_question(cls, response, quest, error=""):
    basic_check_of_question(cls, response, quest, error)
    cls.assertContains(response, 'new_choice')


class QuestionIndexViewTests(TestCase):
    """
    Tests for views
    """

    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        poll = Poll.objects.create()
        response = self.client.get(reverse('polls:poll_detail',
                                           args=(poll.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Brak pytań!")
        self.assertQuerysetEqual(response.context['questions_list'], [])

    def test_past_question(self):
        """
        Questions with a start_date in the past are displayed on the
        index page.
        """
        past_time = timezone.now() + datetime.timedelta(days=-30)
        poll = Poll.objects.create()
        Question.objects.create(poll=poll, question_text="Past question",
                                start_date=past_time)
        response = self.client.get(reverse('polls:poll_detail',
                                           args=(poll.id,)))
        self.assertQuerysetEqual(
            response.context['questions_list'],
            ['<Question: Past question>']
        )

    def test_question_with_same_start_and_end_time(self):
        """
        Questions with a start_date which is equal to end_date should not be
        displayed.
        """
        now_time = timezone.now()
        poll = Poll.objects.create()
        Question.objects.create(poll=poll, question_text="Past question",
                                start_date=now_time, end_date=now_time)
        response = self.client.get(reverse('polls:poll_detail',
                                           args=(poll.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Brak pytań!")
        self.assertQuerysetEqual(response.context['questions_list'], [])

    def test_future_question(self):
        """
        Questions with a start_date in the future are displayed on the index
        page.
        """
        future_time = timezone.now() + datetime.timedelta(days=30)
        poll = Poll.objects.create()
        Question.objects.create(poll=poll, question_text="Future question",
                                start_date=future_time)
        response = self.client.get(reverse('polls:poll_detail',
                                           args=(poll.id,)))
        self.assertQuerysetEqual(
            response.context['questions_list'],
            ['<Question: Future question>']
        )

    def test_future_question_and_past_question(self):
        """
        If both past and future questions exist, both are display.
        """
        past_time = timezone.now() + datetime.timedelta(days=-30)
        future_time = timezone.now() + datetime.timedelta(days=30)
        poll = Poll.objects.create()
        Question.objects.create(poll=poll, question_text="Past question",
                                start_date=past_time)
        Question.objects.create(poll=poll, question_text="Future question",
                                start_date=future_time)
        response = self.client.get(reverse('polls:poll_detail',
                                           args=(poll.id,)))
        self.assertQuerysetEqual(
            response.context['questions_list'],
            ['<Question: Future question>', '<Question: Past question>']
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        past_time1 = timezone.now() + datetime.timedelta(days=-30)
        past_time2 = timezone.now() + datetime.timedelta(days=-5)
        poll = Poll.objects.create()
        Question.objects.create(poll=poll, question_text="Past question 1",
                                start_date=past_time1)
        Question.objects.create(poll=poll, question_text="Past question 2",
                                start_date=past_time2)
        response = self.client.get(reverse('polls:poll_detail',
                                           args=(poll.id,)))
        self.assertQuerysetEqual(
            response.context['questions_list'],
            ['<Question: Past question 2>', '<Question: Past question 1>']
        )

    def test_long_time_questions(self):
        """
        The questions index page may display long time questions.
        """
        future_time1 = timezone.now() + datetime.timedelta(days=30)
        future_time2 = timezone.now() + datetime.timedelta(days=5)
        poll = Poll.objects.create()
        Question.objects.create(poll=poll, question_text="Question 1",
                                start_date=future_time1)
        Question.objects.create(poll=poll, question_text="Question 2",
                                start_date=future_time2)
        response = self.client.get(reverse('polls:poll_detail',
                                           args=(poll.id,)))
        self.assertQuerysetEqual(
            response.context['questions_list'],
            ['<Question: Question 1>',
             '<Question: Question 2>']
        )

    def test_short_time_questions(self):
        """
        The questions index page may display short time questions.
        """
        time1 = timezone.now() + datetime.timedelta(minutes=6)
        time2 = timezone.now() + datetime.timedelta(minutes=3)
        time3 = timezone.now() + datetime.timedelta(minutes=5)
        poll = Poll.objects.create()
        Question.objects.create(poll=poll, question_text="Question 1",
                                start_date=timezone.now(), end_date=time1)
        Question.objects.create(poll=poll, question_text="Question 2",
                                start_date=timezone.now(), end_date=time2)
        Question.objects.create(poll=poll, question_text="Question 3",
                                start_date=timezone.now(), end_date=time3)
        response = self.client.get(reverse('polls:poll_detail',
                                           args=(poll.id,)))
        self.assertQuerysetEqual(
            response.context['questions_list'],
            ['<Question: Question 1>',
             '<Question: Question 3>',
             '<Question: Question 2>']
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
        future_time = timezone.now() + datetime.timedelta(days=5)
        poll = Poll.objects.create()
        question = Question.objects.create(poll=poll, start_date=future_time)
        url = reverse('polls:question_detail', args=(question.id,))
        response = self.client.get(url)
        self.assertContains(response, question.question_text)
        self.assertContains(response, "Głosowanie nie jest aktywne")

    def test_past_question(self):
        """
        The detail view of a question with a start_date in the past display
        question and warning, that voting is inactive.
        """
        past_time = timezone.now() + datetime.timedelta(days=-5)
        poll = Poll.objects.create()
        question = Question.objects.create(poll=poll, start_date=past_time)
        url = reverse('polls:question_detail', args=(question.id,))
        response = self.client.get(url)
        self.assertContains(response, question.question_text)
        self.assertContains(response, "Głosowanie nie jest aktywne")

    def test_future_current_and_past_question(self):
        """
        Even if past, current and future questions exist, only current
        questions are able to vote.
        """
        poll = Poll.objects.create()
        future_q = Question.objects.create(
            poll=poll, question_text='Future question',
            start_date=timezone.now() + datetime.timedelta(days=5))
        url = reverse('polls:question_detail', args=(future_q.id,))
        future_response = self.client.get(url)
        self.assertContains(future_response, "Głosowanie nie jest aktywne")

        past_q = Question.objects.create(
            poll=poll, question_text='Past question',
            start_date=timezone.now() + datetime.timedelta(days=-5))
        url = reverse('polls:question_detail', args=(past_q.id,))
        past_response = self.client.get(url)
        self.assertContains(past_response, "Głosowanie nie jest aktywne")

        current_q = Question.objects.create(
            poll=poll, question_text='Current question',
            start_date=timezone.now(),
            end_date=timezone.now() + datetime.timedelta(minutes=5))
        url = reverse('polls:question_detail', args=(current_q.id,))
        current_response = self.client.get(url)
        self.assertNotContains(current_response, "Głosowanie nie jest aktywne")

        response = self.client.get(reverse('polls:poll_detail',
                                           args=(poll.id,)))
        self.assertQuerysetEqual(
            response.context['questions_list'],
            ['<Question: Future question>',
             '<Question: Current question>',
             '<Question: Past question>']
        )


class OpenQuestionDetailViewTests(TestCase):
    def setUp(self):
        poll = Poll.objects.create()
        open_question = OpenQuestion.objects.create(
            poll=poll, question_text="OpenQuestion")
        open_question.choice_set.create(choice_text="Odp1")
        open_question.choice_set.create(choice_text="Odp2")

    def test_open_question_with_choices(self):
        '''
        Test for detail view of open question
        '''
        open_question = OpenQuestion.objects.get(question_text="OpenQuestion")
        url = reverse('polls:question_detail', args=(open_question.id,))
        response = self.client.get(url)
        basic_check_of_open_question(self, response, open_question)

    def test_open_question_without_choices(self):
        '''
        Test for detail view of empty open question
        '''
        open_question = OpenQuestion.objects.get(question_text="OpenQuestion")
        url = reverse('polls:question_detail', args=(open_question.id,))
        response = self.client.get(url)
        self.assertContains(response, open_question.question_text)
        self.assertContains(response, 'new_choice')


class QuestionVoteViewTests(TestCase):
    def setUp(self):
        poll = Poll.objects.create()
        question = Question.objects.create(poll=poll, question_text='Question')
        question.choice_set.create(choice_text="Odp1")
        question.choice_set.create(choice_text="Odp2")

    def test_no_answer_for_question(self):
        question = Question.objects.get(question_text="Question")
        url = reverse('polls:vote', args=(question.id,))
        response = self.client.post(url,
                                    {'code': question.poll.get_codes()[0]})
        basic_check_of_question(self, response, question,
                                "Nie wybrano odpowiedzi")

    def test_invalid_access_code(self):
        question = Question.objects.get(question_text="Question")
        url = reverse('polls:vote', args=(question.id,))
        response = self.client.post(
            url,
            {'choice': question.choice_set.all().last().id,
             'code': ""})
        basic_check_of_question(self, response, question,
                                "Niewłaściwy kod uwierzytelniający")


class OpenQuestionVoteViewTests(TestCase):
    def setUp(self):
        poll = Poll.objects.create()
        open_question = OpenQuestion.objects.create(
            poll=poll, question_text="OpenQuestion")
        open_question.choice_set.create(choice_text="Odp1")
        open_question.choice_set.create(choice_text="Odp2")

    def test_two_answers_for_open_question(self):
        open_question = OpenQuestion.objects.get(question_text="OpenQuestion")
        url = reverse('polls:vote', args=(open_question.id,))
        response = self.client.post(
            url, {'is_open': True,
                  'choice': open_question.choice_set.all().last().id,
                  'new_choice': "sth",
                  'code': open_question.poll.get_codes()[0]})
        basic_check_of_open_question(
            self,
            response,
            open_question,
            "Nie można głosować na istniejącą odpowiedź i \
                          jednocześnie proponować nową")

    def test_no_answers_for_open_question(self):
        open_question = OpenQuestion.objects.get(question_text="OpenQuestion")
        url = reverse('polls:vote', args=(open_question.id,))
        response = self.client.post(
            url, {'is_open': True,
                  'new_choice': '',
                  'code': open_question.poll.get_codes()[0]})
        basic_check_of_open_question(
            self, response, open_question, "Nie wybrano odpowiedzi")

    def test_invalid_access_code_for_open_question(self):
        open_question = OpenQuestion.objects.get(question_text="OpenQuestion")
        url = reverse('polls:vote', args=(open_question.id,))
        response = self.client.post(
            url, {'is_open': True,
                  'choice': open_question.choice_set.all().last().id,
                  'new_choice': '',
                  'code': ""})
        basic_check_of_open_question(
            self, response, open_question, "Niewłaściwy kod uwierzytelniający")


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


class CodesViewsTests(TestCase):
    def setUp(self):
        User.objects.create_superuser(
            'user1',
            'user1@example.com',
            'pswd',
        )

        self.poll = Poll.objects.create()
        self.q = OpenQuestion.objects.create(poll=self.poll,
                                             question_text="question 1")

    def test_codes_html_view_as_superuser(self):
        self.client.login(username="user1", password="pswd")
        url = reverse('polls:codes', args=(self.poll.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            len(response.context['codes_list']) == len(self.poll.get_codes()))
        self.client.logout()

    def test_codes_pdf_view_as_superuser(self):
        self.client.login(username="user1", password="pswd")
        url = reverse('polls:codes_pdf', args=(self.poll.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            len(response.context['codes_list']) == len(self.poll.get_codes()))
        self.client.logout()

    def test_codes_html_view_as_user(self):
        url = reverse('polls:codes', args=(self.poll.id,))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_codes_pdf_view_as_user(self):
        def test_codes_html_view_as_user(self):
            url = reverse('polls:codes_pdf', args=(self.poll.id,))
            response = self.client.get(url, follow=True)
            self.assertEqual(response.status_code, 404)


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
