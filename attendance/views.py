from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User, Permission
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.views import View

from attendance.forms import LoginForm, AddEventForm, AddUserForm, AddSongForm
from attendance.models import Song, Event, UserExt, UserSong


class login_view(View):
    """First page, available for all - login into the app"""
    def get(self, request):
        form = LoginForm()
        return render(request, "login.html", {"form" : form.as_p()})

    def post(self, request):
        form = LoginForm(request.POST)
        # username = request.POST['user']
        # password = request.POST['password']
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username = username, password = password)
            if user is not None:
                login(request, user)

                return redirect('home')

            return render(request, "login.html", {"form" : form.as_p()})


        return render(request, "login.html", {"form" : form.as_p()})


def logout_view(request):
    """Simple log out addres, whith no html assigned"""
    logout(request)
    return redirect('login')


class home_view(View):
    """Home page"""
    def get(self, request):
        return render(request, "base.html")


class add_event_view(PermissionRequiredMixin, View):
    """Formular allowing to add new event"""
    permission_required = 'auth_event.add_event'
    raise_exception = True

    def get(self, request):
        form = AddEventForm()
        return render(request, "add_event.html", {"form":form.as_p()})

    def post(self,request):
        form = AddEventForm(request.POST)
        if form.is_valid():
            event_name = form.cleaned_data['event_name']
            date = form.cleaned_data['date']
            start_hour = form.cleaned_data['start_hour']
            end_hour = form.cleaned_data['end_hour']
            place = form.cleaned_data['place']
            description = form.cleaned_data['description']
            songs = form.cleaned_data['songs']

            event = Event.objects.create(name=event_name, date=date, start_hour=start_hour, end_hour=end_hour, place=place, description=description)
            event.songs.set(songs)

            return redirect('home')

        return render(request, "add_event.html", {"form": form.as_p()})


class add_user_view(PermissionRequiredMixin, View):
    """Formular - available only to admins - allowing to create user/superuser"""
    permission_required = 'auth_user.add_user'
    raise_exception = True

    def get(self, request):
        form = AddUserForm()
        return render(request, "add_user.html", {"form":form.as_p()})

    def post(self, request):
        form = AddUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            passwordRepeat = form.cleaned_data['passwordRepeat']
            name = form.cleaned_data['name']
            surname = form.cleaned_data['surname']
            email = form.cleaned_data['email']
            superuser = form.cleaned_data['superuser']
            phone = form.cleaned_data['phone']

            if password == passwordRepeat:
                if superuser:
                    user = User.objects.create_superuser(username, password=password, first_name=name, last_name=surname,
                                                    email=email)
                    if phone:
                        UserExt.objects.create(phone=phone, user_id=user.id)

                else:
                    user = User.objects.create_user(username, password=password, first_name= name, last_name=surname, email=email)
                    if phone:
                        UserExt.objects.create(phone=phone, user_id=user.id)

                return redirect('home')

            else:
                warning = "Niepoprawnie potwierdzone hasło (muszą być takie same!)"
                return render(request, "add_user.html", {"form": form.as_p(), "warning": warning})

        return render(request, "add_user.html", {"form": form.as_p()})


class add_song_view(PermissionRequiredMixin, View):
    """Formular that allows to add song to the choirs resources"""
    permission_required = "attendence_song.add_song"
    raise_exception = True

    def get(self, request):
        form = AddSongForm()
        return render(request, "add_song.html", {"form":form.as_p()})

    def post(self, request):
        form = AddSongForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            composer = form.cleaned_data['composer']
            description = form.cleaned_data['description']
            voices = form.cleaned_data['voices']
            Song.objects.create(name=name, composer=composer, description=description, voices=voices)

            return redirect('home')

        return render(request, "add_song.html", {"form": form.as_p()})


class all_songs_vies(View):
    """Shows list of all available songs"""
    def get(self,request):
        all_songs = Song.objects.all().order_by("name")
        return render(request, "all_songs.html", {"all_songs": all_songs})


class song_view(View):
    """Each song's details with user information about his one's and link to change his declaration"""

    def get(self, request, song_id):
        song = Song.objects.get(pk = song_id)
        user = request.user

        try:
            user_voice = UserSong.objects.filter(song_id=song_id).get(user=user)
            return render(request, "song_view.html", {"song":song, "user_voice":user_voice})

        except:
            alert = "Zadeklaruj jakim głosem śpiewasz!"
            return render(request, "song_view.html", {"song":song, "alert":alert})


class song_declaration_view(View):
    """As currently there is 'no front', it is easier to make such view"""
    def get(self,request, song_id):
        song = Song.objects.get(pk = song_id)
        user = request.user
        return render(request, "song_declaration.html", {"song":song, "user":user})

    def post(self, request, song_id):
        song = Song.objects.get(pk=song_id)
        user = request.user
        voice = request.POST['voice']

        try:
            user_voice = UserSong.objects.filter(song_id=song_id).get(user=user)
            user_voice.voice = voice
            user_voice.save()

        except:
            UserSong.objects.create(song=song, user=user, voice=voice)

        return HttpResponseRedirect("../%s" % song_id)


class all_users_view(View):
    """List of all users"""
    def get(self, request):
        all_users = User.objects.all().order_by("last_name")
        return render(request, "all_users.html", {"users":all_users})


class current_events_view(View):
    def get(self, request):
        all_events = Event.objects.all()
        return render(request, "all_events.html", {"events":all_events})