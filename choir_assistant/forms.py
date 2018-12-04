from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError


def login_validator(value):
    try:
        User.objects.get(username=value)
    except ObjectDoesNotExist:
        raise ValidationError("zły login")


class LoginForm(forms.Form):
    username = forms.CharField(label="Użytkownik:", max_length=50, validators=[login_validator])
    password = forms.CharField(label="password", widget=forms.PasswordInput)