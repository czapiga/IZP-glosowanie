from django.db import models
from django.utils import timezone


class Question(models.Model):
    question_text = models.CharField('Pytanie', max_length=200)
    start_date = models.DateTimeField('Data rozpoczęcia', blank=True, default=timezone.now)
    end_date = models.DateTimeField('Data zakończenia', blank=True)
    time = models.IntegerField('Czas na odpowiedź [minuty]', default=5)
    access_codes = ['AAA', 'BBB', 'CCC']  # TODO generate random codes

    def save(self):
        # TODO validate self.time variable
        if not self.id:
            if self.start_date and self.end_date:
                self.time = (self.end_date - self.start_date) / 60
            if not self.start_date:
                self.start_date = timezone.now()
            if not self.end_date:
                self.end_date = self.start_date + timezone.timedelta(minutes=self.time)
            super(Question, self).save()

    def __str__(self):
        return self.question_text

    def is_code_correct(self, code):
        return code in self.access_codes


class SimpleQuestion(Question):
    def save(self):
        super(SimpleQuestion, self).save()    
        self.choice_set.create(choice_text='Yes')
        self.choice_set.create(choice_text='No')


# TODO Create OpenQuestion class (derived from Question) with no predefined choices

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField('Odpowiedź', max_length=200)
    votes = models.IntegerField('Liczba głosów', default=0)

    def __str__(self):
        return self.choice_text


class Vote(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    code = models.CharField(max_length=10)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.question.question_text + ' ' + self.choice.choice_text + ' ' + self.code
