from django.db import models

# Create your models here.


class Genre(models.Model):
    id = models.AutoField
    name = models.TextField


class TvShow(models.Model):
    id = models.AutoField
    name = models.TextField
    seasons = models.IntegerField
    path = models.CharField(max_length=400)
    genre = models.ForeignKey('Genre')


class Movie(models.Model):
    id = models.AutoField
    name = models.TextField
    genre = models.ForeignKey('Genre')
