from django.shortcuts import render
from django import forms

from .models import Message, Medication
from django.contrib.auth.models import User

# Create your views here.


def index(request):
    return render(request,"mood/index.html")



def message(request):
    """
    pk and id is the same thing
    message - is related_name
    """
    if request.method == "POST" and request.user.is_authenticated:
        user = request.user
        message = request.POST['message']
        #medication = request.POST['medication']
        # user is the related name
        Message.objects.create(user=user, message=message)
        cur_user = User.objects.get(username="petr")
        return render(request, "mood/index.html",
                      {
                          'user':user.username,
                          'message':Message.objects.get(pk=user.id),
                          # pick possible medication
                          'meds':cur_user.medication.all()

                      })

    else:
        return render(request,'users/login.html')



def mood_history(request):
    '''
    user - is related_name in our model
    '''
    if request.user.is_authenticated:
        user = request.user
        all_messages = User.objects.get(username=user)
        return render(request, "mood/mood_history.html",
                      {
                          "message_history": all_messages.user.all(),
                          "our_class": Message.objects.get(id=1)
                      })
    else:
        pass


def logout(request):
    logout(request)
    return render(request, "users/login.html",
                  {
                      "message": "Logged out"
                  })
