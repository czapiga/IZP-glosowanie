from django import forms
from .models import Question


class QuestionAdminForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = '__all__'
    
    def clean(self):
        question_text = self.cleaned_data.get('question_text')
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')
        time = self.cleaned_data.get('time')
        max_end_date = Question.objects.latest('end_date').end_date
        if start_date and max_end_date > start_date:
            raise forms.ValidationError('Nie wolno tworzyć ' +
                                        'czasowo nakładających ' +
                                        'się głowowań. ' +
                                        'Najbliższa możliwa ' +
                                        'data rozpoczencia ' +
                                        'nowego głosowania ' +
                                        str(max_end_date))
