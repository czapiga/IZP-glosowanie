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


def voting(question, choice, code):
    prev_vote = Vote.objects.filter(question__exact=question, code__exact=code).last()
    if prev_vote:
        prev_vote.choice.votes -= 1
        prev_vote.choice.save()

    choice = Choice.objects.get(pk=choice.id)
    choice.votes += 1
    choice.save()
    Vote.objects.create(question=question, choice=choice, code=code)


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if question.start_date > timezone.now() or question.end_date < timezone.now():
        return render(request, 'polls/detail.html', {
            'question': question, 'error': "Głosowanie nie jest aktywne"})
    try:
        openQuestion = OpenQuestion.objects.get(pk=question_id)
    
    except OpenQuestion.DoesNotExist:   # case for "basic" question
        try:
            choice = question.choice_set.get(pk=request.POST['choice'])
            code = request.POST['code']
            if code == '' or not question.is_code_correct(code):
                raise AttributeError

        except (KeyError, Choice.DoesNotExist):
            return render(request, 'polls/detail.html', {'question': question, 'error': "Nie wybrano odpowiedzi"})

        except AttributeError:
            return render(request, 'polls/detail.html',
                          {'question': question, 'error': "Niewłaściwy kod uwierzytelniający"})

        else:
            voting(question, choice, code)
            return HttpResponseRedirect(reverse('polls:index'))
    else:   #case for OpenQuestion
        try:
            code = request.POST['code']
            if code == '' or not question.is_code_correct(code):
                raise AttributeError
            new_choice = request.POST['new_choice']
            choice = question.choice_set.get(pk=request.POST['choice'])
        except AttributeError:
            return render(request, 'polls/detail.html',
                  {'question': question, 'error': "Niewłaściwy kod uwierzytelniający", 'is_open': True})
        except (KeyError, Choice.DoesNotExist): # case for an unselected radio button
            if new_choice == '':    # no answer
                raise KeyError
            else:                   # new choice selected
                new_choice = question.choice_set.create(choice_text=new_choice)
                voting(question, new_choice, code)
                return HttpResponseRedirect(reverse('polls:index'))

        except (KeyError, Choice.DoesNotExist): # no answer selected
            return render(request, 'polls/detail.html', {'question': question, 'error': "Nie wybrano odpowiedzi", 'is_open': True})
        else:
            if new_choice == '':
                voting(question, choice, code)
                return HttpResponseRedirect(reverse('polls:index'))
            else:
                return render(request, 'polls/detail.html',
                              {'question': question, 'error': "Nie można udzielić dwóch głosów", 'is_open': True})
    