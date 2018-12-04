from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import View

from choir_assistant.forms import LoginForm


class login_view(View):
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
    logout(request)
    return redirect('login')



class home_view(View):

    def get(self, request):
        return render(request, "home.html")