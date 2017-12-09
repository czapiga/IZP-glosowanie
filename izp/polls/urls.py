from django.conf.urls import url

from . import views

app_name = 'polls'
urlpatterns = [
    url(r'^$', views.poll_index, name='poll_index'),
    url(r'^(?P<poll_id>[0-9]+)/$', views.poll_detail, name='poll_detail'),
    url(r'^[0-9]+/(?P<question_id>[0-9]+)/$',
        views.question_detail, name='question_detail'),
    url(r'^[0-9]+/(?P<question_id>[0-9]+)/question_result/$',
        views.question_result, name='question_result'),
    url(r'^[0-9]+/(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
    url(r'^(?P<poll_id>[0-9]+)/codes/$', views.codes, name='codes'),
    url(r'^(?P<poll_id>[0-9]+)/codes_pdf/$',
        views.codes_pdf, name='codes_pdf'),
    url(r'^(?P<poll_id>[0-9]+)/logout/$', views.logout, name='logout'),
    url(r'^(?P<poll_id>[0-9]+)/login/$', views.login, name='login'),
]
