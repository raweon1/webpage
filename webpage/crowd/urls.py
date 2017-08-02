from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^rate/$', views.rate, name='rate'),
    url(r'^setup/', views.setup, name='setup'),
    url(r'^finish/$', views.finish, name='finish'),
]
