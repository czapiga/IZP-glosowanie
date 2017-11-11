from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone

from .models import Choice, Question, Vote, OpenQuestion


def index(request):
    return render(request, 'polls/index.html',
                  {'questions_list': Question.objects.order_by('-end_date', '-start_date')})


def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if question.start_date > timezone.now() or question.end_date < timezone.now():
        return render(request, 'polls/detail.html', {
            'question': question, 'error': "Głosowanie nie jest aktywne"})
    try:
        openQuestion = OpenQuestion.objects.get(pk=question_id)
    except OpenQuestion.DoesNotExist:
        return render(request, 'polls/detail.html', {'question': question})
    return render(request, 'polls/detail.html', {'question': openQuestion, 'is_open': True})
    

def result(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if timezone.now() < question.end_date:
        return render(request, 'polls/result.html', {'error': 'Głosowanie jeszcze się nie zakończyło'})

    choices = Choice.objects.filter(question__exact=question).order_by('-votes')
    codes = []
    for code in question.access_codes:
        num_of_votes = Vote.objects.filter(question__exact=question, code__exact=code).count()
        last_choice = Vote.objects.filter(question__exact=question, code__exact=code).last()
        if last_choice:
            last_choice = last_choice.choice.choice_text
        else:
            last_choice = '-'
        codes.append({'code': code, 'num_of_votes': num_of_votes, 'last_choice': last_choice})
    return render(request, 'polls/result.html', {'question': question, 'choices': choices, 'codes': codes})


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if question.start_date > timezone.now() or question.end_date < timezone.now():
        return render(request, 'polls/detail.html',
                {'question': question, 'error': "Głosowanie nie jest aktywne"})

    code = request.POST['code']
    if code == '' or not question.is_code_correct(code):
        return render(request, 'polls/detail.html',
                {'question': question, 'error': "Niewłaściwy kod uwierzytelniający"})

    choice = request.POST.get('choice', None)
    new_choice = request.POST['new_choice']
    if(choice and new_choice != ''):
        return render(request, 'polls/detail.html',
                {'question': question, 'error': "Nie można głosować na istniejącą odpowiedź i jednocześnie proponować nową"})

    if not choice and new_choice == '':
        return render(request, 'polls/detail.html',
                {'question': question, 'error': "Nie wybrano odpowiedzi"})

    if choice:
        if question.choice_set.filter(pk=choice).exists():
            choice = question.choice_set.get(pk=choice)
        else:
            return render(request, 'polls/detail.html',
                    {'question': question, 'error': "Odpowiedź nie istnieje"})

    if not choice and OpenQuestion.objects.filter(pk=question.pk).exists():
        choice = Choice.objects.create(question=question, choice_text=new_choice)

    prev_vote = Vote.objects.filter(question__exact=question, code__exact=code).last()
    if prev_vote:
        prev_vote.choice.votes -= 1
        prev_vote.choice.save()

    choice = Choice.objects.get(pk=choice.id)
    choice.votes += 1
    choice.save()
    Vote.objects.create(question=question, choice=choice, code=code)
    return HttpResponseRedirect(reverse('polls:index'))