from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models



class User_ext(models.Model):
    """additional user information"""
    phone = models.CharField(max_length=20)
    picture = models.ImageField(null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Event(models.Model):
    """details of the specific event"""
    date = models.DateField()
    start_hour = models.TimeField()
    end_hour = models.TimeField()
    place = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    songs = models.ManyToManyField('Song')


class Attendance(models.Model):
    """choir member's declaration on his presence"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    person = models.ForeignKey(User, on_delete=models.CASCADE)
    be_or_not = models.FloatField(choices=((-2, "Nieusprawiedliwiony występ"),(-1, "Nieusprawiedliwione"),
                                           (0, "Nie będzie"), (0.75, "Spóźni się"), (1, "Będzie)")), default=1, null=False)
    comment = models.CharField(max_length=255)
    date_of_declaration = models.DateTimeField(auto_now=True)


VOICES = (
    ("soprano1", "soprano1"),("soprano2", "soprano2"),("soprano3", "soprano3"),("soprano4", "soprano4"),
    ("alto1", "alto1"), ("alto2", "alto2"), ("alto3", "alto3"), ("alto4", "alto4"),
    ("tenor1", "tenor1"), ("tenor2", "tenor2"), ("tenor3", "tenor3"), ("tenor4", "tenor4"),
    ("bas1", "bas1"), ("bas2", "bas2"), ("bas3", "bas3"), ("bas4", "bas4")
)


class Song(models.Model):
    """each song on choir's repertoire"""
    name = models.CharField(max_length=255)
    composer = models.CharField(max_length=255, null=True)
    scores = models.FileField(null=True)
    yt_link = models.TextField()
    voices = ArrayField(models.CharField(choices=VOICES))  # list of voices avaliable for the specific song


class User_song(models.Model):
    """model capturing each singer's choice for the specific song"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    voice = models.CharField(choices=VOICES)   # user will be allowed to use only one of the voices. Form will contain only choices from the Song model.
