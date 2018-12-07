from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.models import User, Permission
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.views import View

from attendance.forms import LoginForm, AddEventForm, AddUserForm, AddSongForm, PasswordChangeForm, AddSongsToEventForm, \
    DeclarationForm
from attendance.models import Song, Event, UserExt, UserSong, Attendance


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


class home_view(LoginRequiredMixin, View):
    """Home page"""
    login_url = 'login'

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

            all_active_users = User.objects.filter(is_active=True)

            for user in all_active_users:
                Attendance.objects.create(event=event, person=user)

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


class all_songs_vies(LoginRequiredMixin, View):
    """Shows list of all available songs"""
    login_url = 'login'

    def get(self,request):
        all_songs = Song.objects.all().order_by("name")
        return render(request, "all_songs.html", {"all_songs": all_songs})


class song_view(LoginRequiredMixin, View):
    """Each song's details with user information about his one's and link to change his declaration"""
    login_url = 'login'


    def get(self, request, song_id):
        song = Song.objects.get(pk = song_id)
        user = request.user

        try:
            user_voice = UserSong.objects.filter(song_id=song_id).get(user=user)
            return render(request, "song_view.html", {"song":song, "user_voice":user_voice})

        except:
            alert = "Zadeklaruj jakim głosem śpiewasz!"
            return render(request, "song_view.html", {"song":song, "alert":alert})


class song_declaration_view(LoginRequiredMixin, View):
    """As currently there is 'no front', it is easier to make such view"""
    login_url = 'login'

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


class all_users_view(LoginRequiredMixin, View):
    """List of all users"""
    login_url = 'login'

    def get(self, request):
        all_active_users = User.objects.filter(is_active=True).order_by("last_name")
        all_inactive_users = User.objects.filter(is_active=False).order_by("last_name")
        return render(request, "all_users.html", {"users":all_active_users, "inactive_users":all_inactive_users})


class current_events_view(LoginRequiredMixin, View):
    """All events - the future ones have links to their details"""
    login_url = 'login'

    def get(self, request):
        all_events = Event.objects.filter(date__gte=datetime.now()).order_by("date")
        previous_events = Event.objects.filter(date__lt=datetime.now()).order_by("-date")
        return render(request, "all_events.html", {"events":all_events, "previous_events":previous_events})


class user_view(LoginRequiredMixin, View):
    """Specific user's details. Logged user and admin can see links to change details"""
    login_url = 'login'

    def get(self, request, user_id):
        specific_user = User.objects.get(pk = user_id)
        try:
            specific_user_ext = UserExt.objects.get(user=specific_user)
            return render(request, "user_view.html",
                          {"specific_user": specific_user, "specific_user_ext": specific_user_ext})

        except:
            return render(request, "user_view.html",
                          {"specific_user": specific_user})


class user_details_change_view(LoginRequiredMixin, View):
    """Changing user's details"""
    login_url = 'login'

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


class reset_password_view(LoginRequiredMixin, View):
    """User can change user's password"""
    login_url = 'login'

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







class event_view(LoginRequiredMixin, View):
    """Details of the event: all available singers, all songs"""
    login_url = 'login'

    def get(self, request, event_id):
        event = Event.objects.get(pk = event_id)
        present_users = Attendance.objects.filter(event=event).filter(declaration__gt=0.5).order_by("person__last_name")
        absent_users = Attendance.objects.filter(event=event).filter(declaration__lt=0.5).order_by("person__last_name")

        present_users_ids = []
        for user in present_users:
            present_users_ids.append(user.person.id)

        # print(present_users_ids)   # id all present users

        list_of_voices = []
        songs_available_voices = {}

        for song in event.songs.all():   # song - Song model object   - all songs on specific event
            voice_declarations = UserSong.objects.filter(song=song)  # all declarations in each song
            for declaration in voice_declarations:  #each person's voice declaration in specific song
                for i in present_users_ids:
                    if i == declaration.user.id:
                        list_of_voices.append(declaration.voice)
                        songs_available_voices[song.id] = list_of_voices  # here we have all available voices for each song
            list_of_voices = []

        # print(songs_available_voices)
        # for i in songs_available_voices:
        #     print(i)
        # for i in songs_available_voices:
        #     print(songs_available_voices[i])

        ctx = {"event": event,
               "present_users": present_users,
               "absent_users": absent_users,
               "songs_available_voices" : songs_available_voices,
               }

        return render(request, "event_view.html", ctx)



class event_delete_view(PermissionRequiredMixin, View):
    """Smple view used to delete event"""
    permission_required = "attendence_event.add_event"
    raise_exception = True

    def get(self, request, event_id):
        if request.user.is_superuser:
            event = Event.objects.get(pk = event_id)
            return render(request, "delete_event.html", {"event":event})
        else:
            return HttpResponse("You have no power here")

    def post(self, request, event_id):
        if request.user.is_superuser:
            event_to_remove = Event.objects.get(pk = event_id)
            event_to_remove.delete()
            return redirect('all_events')
        else:
            return HttpResponse("Nice try!")


class event_set_songs_view(PermissionRequiredMixin, View):
    """Admin can change list of songs for the event"""
    permission_required = "attendence_song.add_song"
    raise_exception = True

    def get(self, request, event_id):
        if request.user.is_superuser:
            form = AddSongsToEventForm()
            event = Event.objects.get(pk = event_id)
            return render(request, "add_songs_to_event.html", {"form":form, "event" :event})
        else:
            return HttpResponse("You have no power here")

    def post(self, request, event_id):
        if request.user.is_superuser:
            event = Event.objects.get(pk = event_id)
            form = AddSongsToEventForm(request.POST)
            if form.is_valid():
                songs = form.cleaned_data['songs']

                event.songs.set(songs)
                event.save()

                return redirect("/event/%s" %event.id)


class edit_event_view(PermissionRequiredMixin, View):
    """Admin can change event details"""
    permission_required = "attendence_song.add_song"
    raise_exception = True

    def get(self, request, event_id):
        if request.user.is_superuser:
            event = Event.objects.get(pk=event_id)
            return render(request, "change_event.html", {"event":event})

    def post(self, request, event_id):
        if request.user.is_superuser:
            event = Event.objects.get(pk=event_id)
            name = request.POST['name']
            date = request.POST['date']
            start_hour = request.POST['start_time']
            end_time = request.POST['end_time']
            place = request.POST['place']
            description = request.POST['description']

            if name:
                event.name = name
                event.save()
            if date:
                event.date = date
                event.save()
            if start_hour:
                event.start_hour = start_hour
                event.save()
            if end_time:
                event.end_hour = end_time
                event.save()
            if place:
                event.place = place
                event.save()
            if description:
                event.description = description
                event.save()

            return redirect("/event/%s" % event.id)


class change_declaration_view(LoginRequiredMixin, View):
    """User can change his declaration about attendance - by default for each new event it is '1' : 'będzie'"""
    login_url = 'login'

    def get(self, request, event_id):
        event = Event.objects.get(pk=event_id)
        # user = request.user
        form = DeclarationForm()

        ctx = {
            "event":event,
            "form":form.as_p()
        }
        return render(request, "event_declaration.html", ctx)

    def post(self, request, event_id):
        event = Event.objects.get(pk=event_id)
        user = request.user
        form = DeclarationForm(request.POST)
        if form.is_valid():
            declaration = form.cleaned_data['declaration']
            comment = form.cleaned_data['comment']
            attendance = Attendance.objects.filter(event=event).get(person=user)

            if declaration:
                attendance.declaration = form.cleaned_data['declaration']
                attendance.date_of_declaration = datetime.now()
                attendance.save()
            if comment:
                attendance.comment = form.cleaned_data['comment']
                attendance.date_of_declaration = datetime.now()
                attendance.save()

            return HttpResponseRedirect("/event/%s" %event.id)


class prvious_event_check_view(PermissionRequiredMixin, View):
    """Admin can check presence for the past events"""
    permission_required = "attendence_event.add_event"
    raise_exception = True

    def get(self, request, event_id):
        all_users = User.objects.filter(is_active=True).order_by("last_name")
        event = Event.objects.get(pk = event_id)
        all_attendances_event = Attendance.objects.filter(event=event).order_by("-date_of_declaration")

        return render(request, "event_check.html", {"all_users":all_users, "event":event, "attendances":all_attendances_event})

    def post(self, request, event_id):
        all_users = User.objects.filter(is_active=True).order_by("last_name")
        event = Event.objects.get(pk = event_id)

        for user in all_users:
            attendance = 8
            attendance = request.POST['%s' % user.id]
            comment = ""
            checked = "spr."
            try:
                comment = request.POST['%s_comment' % user.id]

            except:
                pass
            print(attendance)
            print(comment)

            if attendance != "8":
                comment += checked
                Attendance.objects.create(person=user, event=event, declaration=attendance, comment=comment)

        return redirect("all_events")



class song_delete_view(PermissionRequiredMixin, View):
    """Admin can delete the song"""
    permission_required = "attendence_song.add_song"
    raise_exception = True

    def get(self, request, song_id):
        if request.user.is_superuser:
            song = Song.objects.get(pk=song_id)
            song.delete()
            return redirect("all_songs")
        else:
            HttpResponse("NAWET NIE PRÓBUJ!!!")

