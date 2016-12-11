from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^ajax/load_file_system/$', views.load_file_system, name='load_file_system'),
]
