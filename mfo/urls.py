from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^ajax/load_file_system/$', views.load_file_system, name='load_file_system'),
    url(r'^map_genre', views.map_genre, name='map_genre'),
    url(r'^play_vlc/$', views.play_vlc, name='play_vlc')
]
