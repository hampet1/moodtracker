from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request,"mood/index.html")


def logout(request):
    logout(request)
    return render(request, "users/login.html",
                  {
                      "message": "Logged out"
                  })
