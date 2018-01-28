from django.contrib import admin
import nested_admin

from .models import Choice, Poll, Question, SimpleQuestion, OpenQuestion


class ChoiceInline(admin.TabularInline):
    model = Choice
    fields = ('choice_text', )
    extra = 2
    verbose_name = 'Odpowiedzi'


class BaseQuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['poll', 'question_text', 'depends_on', 'winner_choice']})
    ]

    list_display = ('question_text',)
    verbose_name = 'Pytanie'
    
    class Media:
        js = ['js/question.js']

class QuestionAdmin(BaseQuestionAdmin):
    inlines = [ChoiceInline]
    
    class Media:
        js = ['js/question.js']


class NestedChoiceInline(nested_admin.NestedTabularInline):
    model = Choice
    fields = ("choice_text", )
    extra = 2
    verbose_name = "Odpowiedzi"


class SimpleQuestionInline(nested_admin.NestedStackedInline):
    model = SimpleQuestion
    fields = (("question_text", "depends_on", "winner_choice"), )
    extra = 2
    
    verbose_name = "Pytania zamknięte"


class QuestionInline(nested_admin.NestedStackedInline):
    model = Question
    fields = ("question_text",)
    extra = 1
    verbose_name = "Pytania"
    inlines = [NestedChoiceInline]


class OpenQuestionInline(nested_admin.NestedStackedInline):
    model = OpenQuestion
    fields = ("question_text", )
    extra = 1
    verbose_name = "Pytania otwarte"
    inlines = [NestedChoiceInline]


class PollAdmin(nested_admin.NestedModelAdmin):
    fields = ('poll_name', 'date')
    inlines = [SimpleQuestionInline]
    
    class Media:
        js = ['js/poll.js']



admin.site.register(Poll, PollAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(SimpleQuestion, BaseQuestionAdmin)
admin.site.register(OpenQuestion, QuestionAdmin)
