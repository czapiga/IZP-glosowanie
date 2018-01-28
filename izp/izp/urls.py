from django.conf.urls import include, url
from django.contrib import admin
from django.http import HttpResponseRedirect
from . import ajax_views

urlpatterns = [
    url(r'^$', lambda _: HttpResponseRedirect('/polls/')),
    url(r'^polls/', include('polls.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^getquestions$', ajax_views.get_questions, name = 'getquestions'),
    url(r'^getchoices$', ajax_views.get_choices_for_question, name = 'getchoices'),

]
