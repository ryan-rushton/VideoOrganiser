from django.contrib import admin
from .models import Movie, TvShow, Genre
# Register your models here.

admin.site.register(Movie)
admin.site.register(TvShow)
admin.site.register(Genre)