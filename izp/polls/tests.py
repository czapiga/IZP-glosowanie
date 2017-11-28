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


def create_poll(poll_name):
    return Poll.objects.create(poll_name=poll_name)


def create_question(question_text, days=0, start=0, end=0):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """

    poll = create_poll("test-poll")

    if days != 0 and start == 0 and end == 0:
        start = timezone.now() + datetime.timedelta(days=days)
        return Question.objects.create(
            poll=poll, question_text=question_text, start_date=start)
    if days != 0 and start != 0 and end == 0:
        end = start + datetime.timedelta(days=days)
        return Question.objects.create(
            poll=poll,
            question_text=question_text,
            start_date=start,
            end_date=end)
    return Question.objects.create(
        poll=poll, question_text=question_text, start_date=start, end_date=end)


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


class OpenQuestionDetailViewTests(TestCase):
    def setUp(self):
        poll = create_poll("test-poll")
        open_question = OpenQuestion.objects.create(
            poll=poll, question_text="OpenQuestion")
        open_question.choice_set.create(choice_text="Odp1")
        open_question.choice_set.create(choice_text="Odp2")

    def test_open_question_with_choices(self):
        '''
        Test for detail view of open question
        '''
        open_question = OpenQuestion.objects.get(question_text="OpenQuestion")
        url = reverse('polls:detail', args=(open_question.id,))
        response = self.client.get(url)
        basic_check_of_open_question(self, response, open_question)

    def test_open_question_without_choices(self):
        '''
        Test for detail view of empty open question
        '''
        open_question = OpenQuestion.objects.get(question_text="OpenQuestion")
        url = reverse('polls:detail', args=(open_question.id,))
        response = self.client.get(url)
        self.assertContains(response, open_question.question_text)
        self.assertContains(response, 'new_choice')


class QuestionVoteViewTests(TestCase):
    def setUp(self):
        question = create_question("Question")
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
        poll = create_poll("test-poll")
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
        poll = create_poll("test-poll")
        open_question = OpenQuestion.objects.create(
            poll=poll, question_text="OpenQuestion")
        open_question.choice_set.create(choice_text="Odp1")
        open_question.choice_set.create(choice_text="Odp2")
        self.assertIs(len(open_question.choice_set.all()), 2)
        open_question = map(str, open_question.choice_set.all())
        self.assertIs(
            'Odp1' in open_question and 'Odp2' in open_question, True)

    def test_creating_empty_open_question(self):
        poll = create_poll("test-poll")
        open_question = OpenQuestion.objects.create(
            poll=poll, question_text="OpenQuestion")
        self.assertIs(len(open_question.choice_set.all()), 0)


class SimpleQuestionTests(TestCase):
    def test_choices_count(self):
        poll = create_poll("test-poll")
        q = SimpleQuestion(poll=poll, question_text="Tak czy nie?")
        q.save()
        self.assertIs(len(q.choice_set.all()), 2)

    def test_choices_content(self):
        poll = create_poll("test-poll")
        q = SimpleQuestion(poll=poll, question_text="Tak czy nie?")
        q.save()
        q = map(str, q.choice_set.all())
        self.assertIs('Tak' in q and 'Nie' in q, True)

    def test_initial_votes(self):
        poll = create_poll("test-poll")
        q = SimpleQuestion(poll=poll, question_text="Tak czy nie?")
        q.save()
        for choice in q.choice_set.all():
            self.assertIs(choice.votes, 0)


class PollTests(TestCase):
    def test_contains_codes(self):
        poll = create_poll("test-poll")
        codes = poll.get_codes()
        self.assertTrue(codes)
        self.assertEqual(len(codes), 82)
        self.assertEqual(len(codes[0]), 8)

    def test_is_code_correct(self):
        poll = create_poll("test-poll")
        codes = poll.get_codes()
        for code in codes:
            self.assertTrue(poll.is_code_correct(code))

    def test_adding_question(self):
        poll = create_poll("test-poll")
        question = Question.objects.create(
            poll=poll, question_text="test-question")
        self.assertIn(question, poll.question_set.all())

    def test_adding_simple_question(self):
        poll = create_poll("test-poll")
        question = SimpleQuestion.objects.create(
            poll=poll, question_text="test-question")
        question_names = map(str, poll.question_set.all())
        self.assertIn(str(question), question_names)

    def test_adding_open_question(self):
        poll = create_poll("test-poll")
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

        self.q = create_question(question_text="question 1.")

    def test_codes_html_view_as_superuser(self):
        self.client.login(username="user1", password="pswd")
        resp = self.client.get("/polls/" + str(self.q.id) + "/codes/",
                               follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(
            len(resp.context['codes_list']) == len(self.q.poll.get_codes()))
        self.client.logout()

    def test_codes_pdf_view_as_superuser(self):
        self.client.login(username="user1", password="pswd")
        resp = self.client.get("/polls/" + str(self.q.id) + "/codes_pdf/",
                               follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(
            len(resp.context['codes_list']) == len(self.q.poll.get_codes()))
        self.client.logout()

    def test_codes_html_view_as_user(self):
        resp = self.client.get("polls/" + str(self.q.id) + "/codes",
                               follow=True)
        self.assertEqual(resp.status_code, 404)

    def test_codes_pdf_view_as_user(self):
        resp = self.client.get("polls/" + str(self.q.id) + "/codes_pdf",
                               follow=True)
        self.assertEqual(resp.status_code, 404)


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
