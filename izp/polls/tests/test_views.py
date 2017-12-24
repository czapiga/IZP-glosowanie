"""
Tests for views
"""
import datetime
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from polls.models import Question, SimpleQuestion, OpenQuestion, Poll
from django.contrib.auth.models import User


def basic_check_of_question(cls, response, quest, error=""):
    cls.assertContains(response, quest.question_text)
    if error != "":
        cls.assertContains(response, error)
    cls.assertContains(response, 'Odp1')
    cls.assertContains(response, 'Odp2')


def basic_check_of_open_question(cls, response, quest, error=""):
    basic_check_of_question(cls, response, quest, error)
    cls.assertContains(response, 'new_choice')


class PollDetailViewTests(TestCase):
    """
    Tests for Poll detail view
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

    def test_one_question(self):
        """
        The questions index view lists one question
        """
        poll = Poll.objects.create()
        Question.objects.create(poll=poll, question_text="Question")
        response = self.client.get(reverse('polls:poll_detail',
                                           args=(poll.id,)))
        self.assertQuerysetEqual(
            response.context['questions_list'],
            ['<Question: Question>']
        )

    def test_multiple_question(self):
        """
        The questions index view lists many questions.
        """
        poll = Poll.objects.create()
        Question.objects.create(poll=poll, question_text="Question 1")
        Question.objects.create(poll=poll, question_text="Question 2")
        Question.objects.create(poll=poll, question_text="Question 3")
        response = self.client.get(reverse('polls:poll_detail',
                                           args=(poll.id,)))
        self.assertQuerysetEqual(
            response.context['questions_list'],
            ['<Question: Question 3>',
             '<Question: Question 2>',
             '<Question: Question 1>'],
            ordered=False
        )


class QuestionDetailViewTests(TestCase):
    """
    Tests for Question detail view
    """

    def test_active_question(self):
        poll = Poll.objects.create()
        question = Question.objects.create(poll=poll)
        question.activate()
        url = reverse('polls:question_detail', args=(question.id,))
        response = self.client.get(url)
        self.assertContains(response, question.question_text)
        self.assertNotContains(response, "Głosowanie nie jest aktywne")

    def test_inactive_question(self):
        poll = Poll.objects.create()
        question = Question.objects.create(poll=poll)
        url = reverse('polls:question_detail', args=(question.id,))
        response = self.client.get(url)
        self.assertContains(response, question.question_text)
        self.assertContains(response, "Głosowanie nie jest aktywne")


class OpenQuestionDetailViewTests(TestCase):
    def setUp(self):
        poll = Poll.objects.create()
        open_question = OpenQuestion.objects.create(
            poll=poll, question_text="OpenQuestion")
        open_question.activate()
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
        question = Question.objects.create(
            poll=poll, question_text='Question')
        question.activate()
        question.choice_set.create(choice_text="Odp1")
        question.choice_set.create(choice_text="Odp2")

        s = self.client.session
        s['poll' + str(question.poll.id)] = poll.get_codes()[0]
        s.save()

    def test_no_answer_for_question(self):
        question = Question.objects.get(question_text="Question")
        url = reverse('polls:vote', args=(question.id,))
        password = self.client.session['poll' + str(question.poll.id)]
        response = self.client.post(url, {'code': password})
        basic_check_of_question(self, response, question,
                                "Nie wybrano odpowiedzi")


class OpenQuestionVoteViewTests(TestCase):
    def setUp(self):
        poll = Poll.objects.create()
        open_question = OpenQuestion.objects.create(
            poll=poll, question_text="OpenQuestion")
        open_question.activate()
        open_question.choice_set.create(choice_text="Odp1")
        open_question.choice_set.create(choice_text="Odp2")

        s = self.client.session
        s['poll' + str(open_question.poll.id)] = poll.get_codes()[0]
        s.save()

    def test_two_answers_for_open_question(self):
        open_question = OpenQuestion.objects.get(question_text="OpenQuestion")
        url = reverse('polls:vote', args=(open_question.id,))
        response = self.client.post(
            url, {'is_open': True,
                  'choice': open_question.choice_set.all().last().id,
                  'new_choice': "sth"})

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
                  'code': self.client.session['poll'
                                              + str(open_question.poll.id)]})
        basic_check_of_open_question(
            self, response, open_question, "Nie wybrano odpowiedzi")


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
