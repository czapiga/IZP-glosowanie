from django.contrib import admin

from .models import Choice, Poll, Question, SimpleQuestion, OpenQuestion


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2
    verbose_name = 'Odpowiedzi'


class BaseQuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['poll', 'question_text']})
    ]

    list_display = ('question_text', )
    verbose_name = 'Pytanie'


class QuestionAdmin(BaseQuestionAdmin):
    inlines = [ChoiceInline]


class SimpleQuestionInline(admin.StackedInline):
    model = SimpleQuestion
    fields = ("question_text", )
    extra = 2
    vervose_name = "Simple questions"


class PollAdmin(admin.ModelAdmin):
    fields = ('poll_name', 'date')
    inlines = [SimpleQuestionInline]


admin.site.register(Poll, PollAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(SimpleQuestion, BaseQuestionAdmin)
admin.site.register(OpenQuestion, QuestionAdmin)
