from django.shortcuts import render
from django import forms

from .models import Message, Medication
from django.contrib.auth.models import User
from django.http import JsonResponse
# Create your views here.


from django.template.defaulttags import register

@register.filter
def get_range(value):
    """
    this is the way to use range in jinja2 while working with django
    """
    return range(value)


def index(request):
    if request.user.is_authenticated:
        user = request.user
        cur_user = User.objects.get(id=user.id)

        return render(request, "mood/index.html",
                      {
                          'user': user.username,
                          # pick possible medication
                          'meds': cur_user.medication.all()

                      })



def message(request):
    """
    pk and id is the same thing
    message - is related_name
    request.method == "POST"
    """
    if request.method == "POST" and request.user.is_authenticated:
        user = request.user

        cur_user = User.objects.get(id=user.id)
        message = request.POST['message']

        if 'med-type' in request.POST:
            med_type = request.POST['med-type']
        else:
            med_type = False
        rating = request.POST['rating']
        #medication = request.POST['medication']
        # user is the related name
        print("med type is", med_type)
        print("rating is: ", rating)
        Message.objects.create(user=user, message=message)
        return render(request, "mood/index.html",
                      {
                          'user':user.username,
                          'message':Message.objects.get(pk=user.id)
                          # pick possible medication

                      })

    else:
        return render(request,'users/login.html')



def mood_history(request):
    '''
    user - is related_name in our model
    '''
    if request.user.is_authenticated:
        user = request.user
        cur_user = User.objects.get(id=user.id)
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

def mood_boosts(request):
    return render(request,"mood/mood_boost.html")