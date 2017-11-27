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
        if not start_date:
            start_date = timezone.now()
        if not end_date:
            end_date = start_date + \
            datetime.timedelta(minutes=time)

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
    contain = Question.objects.filter(
        start_date__gt=start_date,
        end_date__lt=end_date
    )
    if contain:
        return True
    else:
        return False


def is_overlap(date):
    overlap_with = Question.objects.filter(
        start_date__lt=date,
        end_date__gt=date
    )
    if overlap_with:
        return True
    else:
        return False
