from django.conf.urls import url

from . import views

app_name = 'polls'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<poll_id>[0-9]+)/$', views.questions, name='poll_detail'),
    url(r'^(?P<poll_id>[0-9]+)/questions/$', views.questions, name='poll_detail'),
    url(r'^(?P<poll_id>[0-9]+)/poll_result/$', views.questions, name='poll_result'),
    url(r'^(?P<poll_id>[0-9]+)/(?P<question_id>[0-9]+)/$', views.question_detail, name='question_detail'),
    url(r'^(?P<poll_id>[0-9]+)/(?P<question_id>[0-9]+)/detail/$', views.question_detail, name='question_detail'),
    url(r'^(?P<poll_id>[0-9]+)/(?P<question_id>[0-9]+)/result/$', views.question_result, name='question_result'),
    url(r'^(?P<poll_id>[0-9]+)/(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
    url(r'^(?P<poll_id>[0-9]+)/(?P<question_id>[0-9]+)/codes/$', views.codes, name='codes'),
    url(r'^(?P<poll_id>[0-9]+)/(?P<question_id>[0-9]+)/codes_pdf/$', views.codes_pdf,
        name='codes_pdf'),
]
