"""choir_assistant URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path

from attendance.views import login_view, logout_view, home_view, add_event_view, add_user_view, add_song_view, \
    all_songs_vies, song_view, song_declaration_view, all_users_view, current_events_view, user_view, \
    user_details_change_view, reset_password_view, event_view, event_delete_view, event_set_songs_view, edit_event_view, \
    change_declaration_view, prvious_event_check_view, song_delete_view

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^$', login_view.as_view(), name="login"),
    url(r'^logout$', logout_view, name="logout"),
    url(r'^home$', home_view.as_view(), name="home"),
    url(r'^add_event$', add_event_view.as_view(), name="add_event"),
    url(r'^add_user$', add_user_view.as_view(), name="add_user"),
    url(r'^add_song$', add_song_view.as_view(), name="add_song"),
    url(r'^all_songs$', all_songs_vies.as_view(), name="all_songs"),
    url(r'^song/(?P<song_id>(\d)+)$', song_view.as_view(), name="song"),
    url(r'^song/(?P<song_id>(\d)+)/declare$', song_declaration_view.as_view(), name="song_declaration"),
    url(r'^all_users$', all_users_view.as_view(), name="all_users"),
    url(r'^all_events$', current_events_view.as_view(), name="all_events"),
    url(r'^user/(?P<user_id>(\d)+)$', user_view.as_view(), name="user"),
    url(r'^user/(?P<user_id>(\d)+)/change$', user_details_change_view.as_view(), name="change user details"),
    url(r'^user/(?P<user_id>(\d)+)/change_password$', reset_password_view.as_view(), name="reset_password"),
    url(r'^event/(?P<event_id>(\d)+)$', event_view.as_view(), name="event_view"),
    url(r'^event/(?P<event_id>(\d)+)/delete$', event_delete_view.as_view()),
    url(r'^event/(?P<event_id>(\d)+)/set_songs$', event_set_songs_view.as_view()),
    url(r'^event/(?P<event_id>(\d)+)/edit$', edit_event_view.as_view()),
    url(r'^event/(?P<event_id>(\d)+)/declare$', change_declaration_view.as_view()),
    url(r'^event/(?P<event_id>(\d)+)/check$', prvious_event_check_view.as_view()),
    url(r'^song/(?P<song_id>(\d)+)/delete$', song_delete_view.as_view()),

]
