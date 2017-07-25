from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'(?P<campaign_name>([A-Z]|[a-z]|[0-9])+)/rate/((?P<task_nr>[0-9]+)|$)', views.rate, name='rate'),
]
