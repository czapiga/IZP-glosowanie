from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
from easy_pdf.rendering import render_to_pdf_response

from .models import AccessCode, Choice, Question, Vote, OpenQuestion, Poll


def poll_index(request):
    return render(request, 'polls/poll_index.html',
                  {'polls_list': Poll.objects.all})


def poll_detail(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    return render(request, 'polls/poll_detail.html',
                  {'questions_list': Question.objects.filter(
                      poll__exact=poll).order_by('-end_date', '-start_date')})


def question_detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if question.start_date > timezone.now() \
       or question.end_date < timezone.now():
        return render(request, 'polls/question_detail.html', {
            'question': question, 'error': "Głosowanie nie jest aktywne"})
    try:
        openQuestion = OpenQuestion.objects.get(pk=question_id)
    except OpenQuestion.DoesNotExist:
        return render(request, 'polls/question_detail.html',
                      {'question': question})
    return render(request, 'polls/question_detail.html',
                  {'question': openQuestion, 'is_open': True})


def format_codes_list(codes_list):
    codes = []
    for code in codes_list:
        codes.append(format_code(code))
    return codes


def format_code(code):
    return '-'.join([code[i:i+4] for i in range(0, len(code), 4)])


def question_result(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if timezone.now() < question.end_date:
        return render(request, 'polls/question_result.html',
                      {'error': 'Głosowanie jeszcze się nie zakończyło'})

    choices = Choice.objects.filter(
        question__exact=question).order_by('-votes')
    codes = []
    for code in question.poll.accesscode_set.all():
        last_choice = Vote.objects.filter(
            question__exact=question, code__exact=code).last()
        if last_choice:
            last_choice = last_choice.choice.choice_text
        else:
            last_choice = '-'
        codes.append({'code': format_code(code.code),
                      'num_of_votes': code.counter,
                      'last_choice': last_choice})
    return render(request, 'polls/question_result.html',
                  {'question': question, 'choices': choices, 'codes': codes})


def reformat_code(code):
    if len(code) <= 4 or "-" not in code:
        return code

    newCode = ""
    for l, c in enumerate(code):
        if (l+1) % 5 == 0:
            if l+1 == len(code) or code[l] != "-":
                return ''
        elif code[l] == "-":
            return ''
        else:
            newCode += c
    return newCode


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    is_open = OpenQuestion.objects.filter(pk=question.pk).exists()
    if question.start_date > timezone.now() \
       or question.end_date < timezone.now():
        return render(request,
                      'polls/question_detail.html',
                      {'question': question,
                       'error': "Głosowanie nie jest aktywne",
                       'is_open': is_open})

    code = reformat_code(request.POST['code'])
    if code == '' or not question.poll.is_code_correct(code):
        return render(request,
                      'polls/question_detail.html',
                      {'question': question,
                       'error': "Niewłaściwy kod uwierzytelniający",
                       'is_open': is_open})

    choice = request.POST.get('choice', None)
    new_choice = request.POST.get('new_choice', '')
    if(choice and new_choice != ''):
        return render(
            request,
            'polls/question_detail.html',
            {
                'question': question,
                'error': "Nie można głosować na istniejącą odpowiedź i \
                          jednocześnie proponować nową",
                'is_open': is_open})

    if not choice and new_choice == '':
        return render(request, 'polls/question_detail.html',
                      {
                          'question': question,
                          'error': "Nie wybrano odpowiedzi",
                          'is_open': is_open})

    if choice:
        if question.choice_set.filter(pk=choice).exists():
            choice = question.choice_set.get(pk=choice)
        else:
            return render(
                request, 'polls/question_detail.html',
                {'question': question,
                 'error': "Odpowiedź nie istnieje",
                 'is_open': is_open})

    if not choice and is_open:
        choice = Choice.objects.create(
            question=question, choice_text=new_choice)

    code = AccessCode.objects.get(poll=question.poll, code=code)
    prev_vote = Vote.objects.filter(
        question__exact=question, code__exact=code).last()
    if prev_vote:
        prev_vote.choice.votes -= 1
        prev_vote.choice.save()

    choice = Choice.objects.get(pk=choice.id)
    choice.votes += 1
    choice.save()
    code.counter += 1
    code.save()
    Vote.objects.create(question=question, choice=choice, code=code)
    return HttpResponseRedirect(reverse('polls:poll_detail',
                                        args=(question.poll.id,)))


@user_passes_test(lambda u: u.is_superuser)
def codes(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    question = get_object_or_404(Question, poll__exact=poll)
    return render(request, 'polls/poll_codes_list.html',
                  {"codes_list": format_codes_list(question.poll.get_codes())})


@user_passes_test(lambda u: u.is_superuser)
def codes_pdf(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    question = get_object_or_404(Question, poll__exact=poll)
    return render_to_pdf_response(
        request, 'polls/poll_codes_list.html',
        {"codes_list": format_codes_list(question.poll.get_codes())})
