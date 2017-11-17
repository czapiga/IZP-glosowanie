from django.db import models
from django.utils import timezone
from .codes import generate_codes


class Question(models.Model):
    question_text = models.CharField('Pytanie', max_length=200)
    start_date = models.DateTimeField(
        'Data rozpoczęcia', blank=True, default=timezone.now)
    end_date = models.DateTimeField('Data zakończenia', blank=True)
    # TODO Remove time variable. We need it only as field in form based
    # on which we can calculate end_date if user
    # does not provide one
    time = models.IntegerField('Czas na odpowiedź [minuty]', default=5)
    access_codes = []

    def save(self, force_insert=False, force_update=False, using=None):
        # TODO validate self.time variable
        if not self.id:
            codes = generate_codes(82, 8)
            for code in codes:
                self.access_codes.append(code)

            if self.start_date and self.end_date:
                self.time = (self.end_date -
                             self.start_date).total_seconds() / 60
            if not self.start_date:
                self.start_date = timezone.now()
            if not self.end_date:
                self.end_date = self.start_date + \
                    timezone.timedelta(minutes=self.time)

        if self.start_date != self.end_date:  # TODO better error case handling
            super(Question, self).save(force_insert=force_insert,
                                       force_update=force_update,
                                       using=using)

    def __str__(self):
        return self.question_text

    def is_code_correct(self, code):
        return code in self.access_codes


class SimpleQuestion(Question):
    def save(self, force_insert=False, force_update=False, using=None):
        super(SimpleQuestion, self).save(force_insert=force_insert,
                                         force_update=force_update,
                                         using=using)
        if self.choice_set.all().count() == 0:
            self.choice_set.create(choice_text='Tak')
            self.choice_set.create(choice_text='Nie')


class OpenQuestion(Question):
    ...


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
        return self.question.question_text + ' ' + \
            self.choice.choice_text + ' ' + self.code
