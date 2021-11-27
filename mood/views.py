from django.shortcuts import render
from keras.models import model_from_json
from .models import Message, Medication, Sentiment
from django.contrib.auth.models import User
from django.template.defaulttags import register
# keras model manipulation
from keras.models import model_from_json
# other packages
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# helper funtions - for embedded layer of our model
from .utils import input_layer, get_chart

# python stream manipulation
from io import BytesIO

import plotly.graph_objects as go



weights_path = os.getcwd() + '\model.h5'
model_path = os.getcwd() + '\model.json'





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

    chart = None
    if request.method == "POST" and request.user.is_authenticated:
        user = request.user

        cur_user = User.objects.get(id=user.id)
        message = request.POST['message']
        Message.objects.create(user=user, message=message)
        if 'med-type' in request.POST:
            med_type = request.POST['med-type']
        else:
            med_type = False
        rating = request.POST['rating']
        print("rating is ", rating)
        # medication = request.POST['medication']


        # load json and create model
        json_file = open(model_path, 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        loaded_model = model_from_json(loaded_model_json)
        # load weights into new model
        loaded_model.load_weights(weights_path)

        # evaluate loaded model on test data
        loaded_model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        text = input_layer(message)

        # predictions
        pred = (loaded_model.predict(text) > 0.5).astype("int32")
        print("pred:,", pred)
        # our model prediction

        if np.average(pred) < 0.5:
            sentiment = 0
        else:
            sentiment = 1
        Sentiment.objects.create(user=user, sentiment=sentiment, rating=3)

        all_sentiment = Sentiment.objects.filter(user=user)

        # it's easier to work with dataframe
        df_1 = pd.DataFrame(all_sentiment)

        # we can bring it to html
        #df_2 = df_2.to_html()
        df_data = pd.DataFrame(all_sentiment.values())
        df_data = df_data.drop(columns='id')

        # chart
        chart = get_chart(df_data, 'lineplot')

        return render(request, "mood/mood_history.html",
                      {
                          'user': user.username,
                          'message': Message.objects.get(pk=user.id),
                          'bla': df_data,
                          # pick possible medication
                           'chart': chart,

                      })

    else:
        return render(request, 'users/login.html')


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
    return render(request, "mood/mood_boost.html")
