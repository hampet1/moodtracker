from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout

# Create your views here.
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'users/signup.html'





def index(request):
    # check if user is logged in
    # if not redirect it
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    # rendering different app
    return render(request, "mood/index.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        # for checking users we have special function authenticate
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request,user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "users/login.html",
                          {
                              'message':"invalid credentials"
                          })
    return render(request, "users/login.html")

def logout_view(request):
    logout(request)
    return render(request, "users/login.html",
                  {
                      "message": "You are logged out!"
                  })