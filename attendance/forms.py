from django import forms
from django.contrib.admin.widgets import AdminTimeWidget
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.forms import widgets

from attendance.models import Song


def login_validator(value):
    try:
        User.objects.get(username=value)
    except ObjectDoesNotExist:
        raise ValidationError("zły login")


class LoginForm(forms.Form):
    username = forms.CharField(label="Użytkownik:", max_length=50, validators=[login_validator])
    password = forms.CharField(label="password", widget=forms.PasswordInput)


# def HourValidator(value):
#     try:
#         int(value[:1])
#         # int(value[:])
#
#         if value[2] != ":":
#             raise ValidationError("Poprawny format to gg:mm!")
#     except:
#         raise ValidationError("Poprawny format to gg:mm!")



class AddEventForm(forms.Form):
    event_name = forms.CharField(label="Nazwa wydarzenia", max_length=255)
    date = forms.DateField(label="Data", widget = forms.SelectDateWidget())
    start_hour = forms.TimeField(label="Godzina zbiórki", widget=forms.TimeInput)
    end_hour = forms.TimeField(label="Przewidywana godzina zakończenia", widget=forms.TimeInput, required=False)
    place = forms.CharField(label="Miejsce zbiórki", max_length=255)
    description = forms.CharField(widget=forms.Textarea, label= "Opis wydarzenia")
    songs = forms.ModelMultipleChoiceField(required=False,
                                           widget=forms.CheckboxSelectMultiple,
                                           queryset=Song.objects.all().order_by("name"))



def new_login_validator(value):
    try:
        User.objects.get(username=value)
        raise ValidationError("taki login już istnieje!")
    except ObjectDoesNotExist:
        return None


class AddUserForm(forms.Form):
    username = forms.CharField(label="nazwa użytkownika", max_length=50, validators=[new_login_validator])
    password = forms.CharField(label="podaj hasło", max_length=50, widget=forms.PasswordInput)
    passwordRepeat = forms.CharField(label="potwierdź hasło", max_length=50, widget=forms.PasswordInput)
    name = forms.CharField(label="Imię", max_length=50)
    surname = forms.CharField(label="Nazwisko", max_length=50)
    email = forms.EmailField(label="Adres email", required=False)
    phone = forms.CharField(label="Numer telefonu", max_length=20, required=False)
    superuser = forms.BooleanField(label="Użytkownik na prawach administratora?", required=False)



VOICES = (
    ("soprano1", "soprano1"),("soprano2", "soprano2"),("soprano3", "soprano3"),("soprano4", "soprano4"),
    ("alto1", "alto1"), ("alto2", "alto2"), ("alto3", "alto3"), ("alto4", "alto4"),
    ("tenor1", "tenor1"), ("tenor2", "tenor2"), ("tenor3", "tenor3"), ("tenor4", "tenor4"),
    ("bas1", "bas1"), ("bas2", "bas2"), ("bas3", "bas3"), ("bas4", "bas4")
)

class AddSongForm(forms.Form):
    name = forms.CharField(label="Nazwa utworu", max_length=255)
    composer = forms.CharField(label="Kompozytor", max_length=255, required=False)
    # scores = forms.FileField(label="Nuty", required=False)
    # yt_link = forms.CharField(label="Link do youtybe'a", widget=forms.Textarea, required=False)
    description = forms.CharField(label="Opis", required=False, max_length=255)
    voices = forms.MultipleChoiceField(label="Głosy", required=False, widget=forms.CheckboxSelectMultiple,
                                       choices = VOICES)


                                       # ["soprano1", "soprano2", "soprano3", "soprano4",
                                       #            "alto1", "alto2", "alto3", "alto4",
                                       #            "tenor1", "tenor2", "tenor3", "tenor4",
                                       #            "bas1", "bas2", "bas3", "bas4"])


