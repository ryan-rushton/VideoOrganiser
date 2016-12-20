from django.db import models

# Create your models here.


class Genre(models.Model):
    genre = models.TextField(primary_key=True)


class TvShow(models.Model):
    title = models.TextField()
    seasons = models.IntegerField()
    path = models.CharField(max_length=400)
    genre = models.ForeignKey('Genre', null=True, blank=True)


class Movie(models.Model):
    title = models.TextField()
    genre = models.ForeignKey('Genre', null=True, blank=True)
