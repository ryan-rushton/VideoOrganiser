from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^ajax/load_file_system/$', views.load_file_system, name='load_file_system'),
    url(r'^entry_view/$', views.entry_view, name='entry_view'),
    url(r'^ajax/play_vlc/$', views.play_vlc, name='play_vlc'),
    url(r'^ajax/get_genre/$', views.get_genre, name='get_genre')
]
