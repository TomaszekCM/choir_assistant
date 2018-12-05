from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User, Permission
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.views import View

from attendance.forms import LoginForm, AddEventForm, AddUserForm, AddSongForm, PasswordChangeForm
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

            return redirect('/all_events')

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
        all_active_users = User.objects.filter(is_active=True).order_by("last_name")
        all_inactive_users = User.objects.filter(is_active=False).order_by("last_name")
        return render(request, "all_users.html", {"users":all_active_users, "inactive_users":all_inactive_users})


class current_events_view(View):
    def get(self, request):
        all_events = Event.objects.filter(date__gte=datetime.now()).order_by("date")
        previous_events = Event.objects.filter(date__lt=datetime.now()).order_by("-date")
        return render(request, "all_events.html", {"events":all_events, "previous_events":previous_events})


class user_view(View):
    """Specific user's details. Logged user and admin can see links to change details"""
    def get(self, request, user_id):
        specific_user = User.objects.get(pk = user_id)
        try:
            specific_user_ext = UserExt.objects.get(user=specific_user)
            return render(request, "user_view.html",
                          {"specific_user": specific_user, "specific_user_ext": specific_user_ext})

        except:
            return render(request, "user_view.html",
                          {"specific_user": specific_user})


class user_details_change_view(View):
    """Changing user's details"""
    def get(self, request, user_id):
        user = request.user
        print("id użytkownika to: ")
        print(user.id)
        print(user_id)
        if user.is_superuser or int(user.id) == int(user_id):  # WHY IT WORKS ONLY FOR SUPERUSERS!?!?!?!?!
            specific_user = User.objects.get(pk=user_id)
            try:
                specific_user_ext = UserExt.objects.get(user=specific_user)
                return render(request, "change_user_details.html", {"specific_user":specific_user, "specific_user_ext":specific_user_ext})
            except:
                return render(request, "change_user_details.html", {"specific_user": specific_user})
        else:
            return HttpResponse("Nie twoje - nie dotykaj!")

    def post(self, request, user_id):
        user = request.user
        edited_user = User.objects.get(pk=user_id)
        new_name = request.POST['name']
        new_first = request.POST['first']
        new_last = request.POST['last']
        new_mail = request.POST['email']
        new_phone = request.POST['phone']
        admin = False
        active = False

        try:
            admin = request.POST['admin']
            admin = True
        except:
            pass
        try:
            active = request.POST['active']
            active = True
        except:
            pass



        try:
            User.objects.get(username=new_name)
            alert = "Taki użytkownik już istnieje"
            try:
                specific_user_ext = UserExt.objects.get(user=edited_user)
                return render(request, "change_user_details.html", {"specific_user":edited_user, "specific_user_ext":specific_user_ext, "alert":alert})
            except:
                return render(request, "change_user_details.html", {"specific_user": edited_user, "alert":alert})

        except:
            if user.is_superuser or int(user.id) == int(user_id):
                if new_name:
                    edited_user.username = new_name
                    edited_user.save()
                if new_first:
                    edited_user.first_name = new_first
                    edited_user.save()
                if new_last:
                    edited_user.last_name = new_last
                    edited_user.save()
                if new_mail:
                    edited_user.email = new_mail
                    edited_user.save()
                if new_phone:
                    try:
                        edited_user_ext = UserExt.objects.get(user=edited_user)
                        edited_user_ext.phone = new_phone
                    except:
                        UserExt.objects.create(phone=new_phone, user=edited_user)

                if user.is_superuser:

                    if admin:
                        edited_user.is_superuser = True
                        edited_user.save()
                    else:
                        edited_user.is_superuser = False
                        edited_user.save()

                    if active:
                        edited_user.is_active = True
                        edited_user.save()
                    else:
                        edited_user.is_active = False
                        edited_user.save()

            return redirect('all_users')


class reset_password_view(View):
    """User can change user's password"""
    def get(self, request, user_id):
        form = PasswordChangeForm()
        user = User.objects.get(pk = user_id)
        if int(request.user.id) == int(user_id):
            return render(request, "change_passwd.html", {"form" : form.as_p(), "user":user})
        else:
            return HttpResponse("Nie twoje - nie dotykaj!")

    def post(self, request, user_id):
        if int(request.user.id) == int(user_id):
            form = PasswordChangeForm(request.POST)
            if form.is_valid():
                password = form.cleaned_data['password']
                passwordRepeat = form.cleaned_data['passwordRepeat']
                if password == passwordRepeat:
                    user = User.objects.get(pk = user_id)
                    user.set_password(password)
                    user.save()
                    user = authenticate(request, username=user.username, password=password)
                    login(request, user)

                    return HttpResponseRedirect('/home')

                else:
                    msg = "niepoprawnie potwierdzone hasło (muszą być takie same!)"
                    return render(request, "change_passwd.html", {"form": form.as_p(), "msg": msg})
        else:
            return HttpResponse("Nie twoje - nie dotykaj!")