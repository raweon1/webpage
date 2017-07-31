from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<campaign_name>[A-Za-z0-9]+)/rate/(?P<task_nr>[0-9]+)$', views.rate, name='rate'),
    url(r'^(?P<campaign_name>[A-Za-z0-9]+)/setup/', views.setup, name='setup'),
    url(r'^(?P<campaign_name>[A-Za-z0-9]+)/finish/$', views.finish, name='finish'),
]
