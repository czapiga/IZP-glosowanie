from django.contrib import admin

from .models import Choice, Question, SimpleQuestion, OpenQuestion


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2
    verbose_name = 'Odpowiedzi'


class BaseQuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['question_text']}),
        ('Termin głosowania',  {'fields': ['start_date', 'end_date', 'time']}),
    ]

    list_display = ('question_text', 'start_date', 'end_date')
    list_filter = ['start_date', 'end_date']
    verbose_name = 'Pytanie'
	
class QuestionAdmin(BaseQuestionAdmin):
    inlines = [ChoiceInline]


admin.site.register(Question, QuestionAdmin)
admin.site.register(SimpleQuestion, BaseQuestionAdmin)
admin.site.register(OpenQuestion, QuestionAdmin)
