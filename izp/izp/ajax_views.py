from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test
from easy_pdf.rendering import render_to_pdf_response
from polls.models import Question, Poll, Choice 
import json


def get_questions(request):
    if request.is_ajax():
        poll_name = request.GET.get('poll_name', None)
        question_name = request.GET.get('question_name', None)
        if poll_name:
            questions = list(Question.objects.filter(
                poll__poll_name = poll_name
            ).exclude(question_text = question_name).values('question_text'))
            return HttpResponse(json.dumps(questions),
                                content_type='application/json')
    questions = []
    return HttpResponse(json.dumps(questions), content_type='application/json')

def get_choices_for_question(request):
    if request.is_ajax():
        question_name = request.GET.get('question_name', None)
        if question_name:
            choices = list( 
                Choice.objects.filter(question__question_text=question_name).values('choice_text')
            )
            return HttpResponse(json.dumps(choices),
                                content_type='application/json')
    choices = []
    return HttpResponse(json.dumps(choices), content_type='application/json')
