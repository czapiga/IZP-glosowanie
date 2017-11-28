from django.contrib import admin

from .models import Choice, Poll, Question, SimpleQuestion, OpenQuestion


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2
    verbose_name = 'Odpowiedzi'


class BaseQuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['poll', 'question_text']}),
        ('Termin głosowania', {'fields': ['start_date', 'end_date', 'time']}),
    ]

    list_display = ('question_text', 'start_date', 'end_date')
    list_filter = ['start_date', 'end_date']
    verbose_name = 'Pytanie'


class QuestionAdmin(BaseQuestionAdmin):
    inlines = [ChoiceInline]


class SimpleQuestionInline(admin.StackedInline):
    model = SimpleQuestion
    extra = 2
    vervose_name = "Simple questions"


class PollAdmin(admin.ModelAdmin):
    fields = ('poll_name',)
    inlines = [SimpleQuestionInline]


admin.site.register(Poll, PollAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(SimpleQuestion, BaseQuestionAdmin)
admin.site.register(OpenQuestion, QuestionAdmin)
