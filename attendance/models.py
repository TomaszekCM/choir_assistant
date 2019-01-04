from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models



class UserExt(models.Model):
    """additional user information"""
    phone = models.CharField(max_length=20)
    picture = models.ImageField(null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Event(models.Model):
    """details of the specific event"""
    name = models.CharField(max_length=255)
    date = models.DateField()
    start_hour = models.TimeField()
    end_hour = models.TimeField(null=True)
    place = models.CharField(max_length=255)
    description = models.TextField(null=True)
    songs = models.ManyToManyField('Song', through= 'EventSongs')

class EventSongs (models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    song = models.ForeignKey('Song', on_delete=models.CASCADE)
    song_number = models.IntegerField(null=True)  #number of the song within the event


DECLARATIONS = ((-2, "nieusprawiedliwiony występ"),(-1, "nieusprawiedliwione"),
                                           (0, "nie będzie"), (0.75, "spóźni się"), (1, "będzie"))


# DECLARATIONS = {-2: "nieusprawiedliwiony występ", -1 : "nieusprawiedliwione",
#                                            0: "nie będzie", 0.75: "spóźni się", 1: "będzie)"}


class Attendance(models.Model):
    """choir member's declaration on his presence"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    person = models.ForeignKey(User, on_delete=models.CASCADE)
    declaration = models.FloatField(choices=DECLARATIONS, default=1, null=False)
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
    description = models.CharField(max_length=255, null=True)
    scores = models.FileField(null=True)
    yt_link = models.TextField(null=True)
    voices = ArrayField(models.CharField(choices=VOICES, max_length=255), null=True)  # list of voices avaliable for the specific song


    def __str__(self):
        return self.name + "  (" + self.composer + ")"

class UserSong(models.Model):
    """model capturing each singer's choice for the specific song"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    voice = models.CharField(choices=VOICES, max_length=255)   # user will be allowed to use only one of the voices. Form will contain only choices from the Song model.
