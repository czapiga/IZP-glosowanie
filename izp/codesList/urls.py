from django.conf.urls import url
from codesList import views

urlpatterns = [
    url(r'^$', views.code_page_view, name='code_page_view'),   
    url(r'^codes.pdf$', views.perform_pdf, name='perform_pdf'),   
]
