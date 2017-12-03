from django import forms
from .models import Question
from django.utils import timezone
import datetime


class QuestionAdminForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = '__all__'

    """
    When we try to create new Question
    function clean() from  QuestionAdminForm in forms.py
    check is our input data valid. If one of properties
    is not valid than function add error to error list.
    """
    def clean(self):
        question_text = self.cleaned_data.get('question_text')
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')
        time = self.cleaned_data.get('time')
        if not start_date and not end_date:
            start_date = timezone.now()
            end_date = start_date + datetime.timedelta(minutes=time)
        if not end_date:
            end_date = start_date + datetime.timedelta(minutes=time)
        if not start_date:
            start_date = timezone.now()
        
        if start_date >= end_date:
            self.add_error('end_date', 
                           'Głosowanie nie odbędzie się ' +
                           'jeśli skończy się przed rozpoczęciem')
        if is_overlap(start_date):
            self.add_error('start_date',
                           'Data rozpoczęcia ' +
                           'nakłada się z innym głosowaniem')

        if is_overlap(end_date):
            self.add_error('end_date',
                           'Data okończenia ' +
                           'nakłada się z innym głosowaniem')

        if voting_between(start_date, end_date):
            self.add_error('start_date',
                           'Data rozpoczęcia ' +
                           'nakłada się z innym głosowaniem')
            self.add_error('end_date',
                           'Data okończenia ' +
                           'nakłada się z innym głosowaniem')


def voting_between(start_date, end_date):
    return Question.objects.filter(
        start_date__gte=start_date,
        end_date__lte=end_date).exists()


def is_overlap(date):
    return Question.objects.filter(
        start_date__lte=date,
        end_date__gte=date).exists()
