from django.conf.urls import include, url
from django.contrib import admin
from django.http import HttpResponseRedirect

urlpatterns = [
    url(r'^$', lambda _: HttpResponseRedirect('/polls/')),
    url(r'^polls/', include('polls.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^_nested_admin/', include('nested_admin.urls')),
]
