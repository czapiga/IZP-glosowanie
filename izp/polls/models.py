from django.db import models
from django.utils import timezone
from .codes import generate_codes


class Poll(models.Model):
    poll_name = models.CharField('Glosowanie', max_length=50)
    date = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=False)

    def save(self, force_insert=False, force_update=False, using=None):
        super(Poll, self).save(force_insert=force_insert,
                               force_update=force_update,
                               using=using)

        if self.id and self.accesscode_set.all().count() == 0:
            for code in generate_codes(82, 8):
                self.accesscode_set.create(code=code)

    def __str__(self):
        return self.poll_name

    def is_code_correct(self, code):
        codes = self.accesscode_set.all()
        for c in codes:
            if code == c.code:
                return True
        return False

    def get_codes(self):
        codes = []
        for code in self.accesscode_set.all():
            codes.append(code.code)
        return codes


class Question(models.Model):
    """
    Base class representing question in the poll.
    """

    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    question_text = models.CharField('Pytanie', max_length=200)

    def save(self, force_insert=False, force_update=False, using=None):
        super(Question, self).save(force_insert=force_insert,
                                    force_update=force_update,
                                    using=using)

    def __str__(self):
        return self.question_text


class SimpleQuestion(Question):
    """
    Question with predefined answers Tak and Nie.
    """

    def save(self, force_insert=False, force_update=False, using=None):
        super(SimpleQuestion, self).save(force_insert=force_insert,
                                         force_update=force_update,
                                         using=using)
        if self.choice_set.all().count() == 0:
            self.choice_set.create(choice_text='Tak')
            self.choice_set.create(choice_text='Nie')


class OpenQuestion(Question):
    """
    Question to which voter may add new choice.
    """

    ...


class Choice(models.Model):
    """
    Class representing answer to a question.
    """

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField('Odpowiedź', max_length=200)
    votes = models.IntegerField('Liczba głosów', default=0)

    def __str__(self):
        return self.choice_text


class AccessCode(models.Model):
    """
    Class representing code used to gain access to the question.
    """

    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    code = models.CharField('Kod', max_length=8)
    counter = models.IntegerField('Liczba użyć', default=0)

    def __str__(self):
        return self.code


class Vote(models.Model):
    """
    Class representing single vote.
    """

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    code = models.ForeignKey(AccessCode, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.question.question_text + ' ' + \
            self.choice.choice_text + ' ' + self.code
