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
from datetime import datetime

# helper funtions - for embedded layer of our model
from .utils import input_layer, get_chart
from .forms import SearchForm

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
                          # pick possible medication
                          'meds': cur_user.medication.all(),
                      })
    else:
        print("user is not registered")

def medication_delete(request):

    #todo add check if medication is not already in the database
    #todo make sure there are no duplicates
    med_name_del = None
    if request.method == "POST" and request.user.is_authenticated:
        user = request.user
        med_name_del = str(request.POST['med-name-del'])
        print("del: ", med_name_del)
        del_item = Medication.objects.filter(user=user).filter(name_of_medication=med_name_del)
        del_item.delete()
        print("deleted")

        # del item
    return render(request,"mood/index.html")



def medication_update(request):


    med_name_add = None
    med_description = None

    if request.method == "POST" and request.user.is_authenticated:
        user = request.user
        med_name_add = str(request.POST['med-name-add'])
        print("med name", med_name_add)
        # adding medication to the database
        # todo add check if medication is not already in the database
        # todo make sure there are no duplicates
        Medication.objects.create(user=user, name_of_medication=med_name_add)
        # adding description to the medication
        med_description = str(request.POST['med-description'])
        Medication.objects.create(user=user, description=med_description)

    return render(request,"mood/index.html")


def message(request):
    """
    pk and id is the same thing
    message - is related_name
    request.method == "POST"
    """
    sentiment = None
    chart = None
    info = None
    if request.method == "POST" and request.user.is_authenticated:
        user = request.user
        message = request.POST['message']
        Message.objects.create(user=user, message=message)

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
        try:
            pred = (loaded_model.predict(text) > 0.5).astype("int32")
            print("pred:,", pred)
            # our model prediction

            if np.average(pred) < 0.5:
                sentiment = 0
            else:
                sentiment = 1
        except Exception as e:
            print(f"something went wrong: {e}")

        # rating
        if 'rating' in request.POST:
            try:
                if sentiment is not None:
                    rating = request.POST['rating']
                    Sentiment.objects.create(user=user, sentiment=sentiment, rating=int(rating))
            except ValueError as e:
                Sentiment.objects.create(user=user, rating=0)
        else:
            Sentiment.objects.create(user=user, rating=0)

        all_sentiment = Sentiment.objects.filter(user=user)

        # it's easier to work with dataframe
        df_1 = pd.DataFrame(all_sentiment)

        # we can bring it to html
        # df_2 = df_2.to_html()
        df_data = pd.DataFrame(all_sentiment.values())
        df_data = df_data.drop(columns='id')

        return render(request, "mood/index.html",
                      {
                          'message': Message.objects.get(pk=user.id),
                          "info": info,
                      })

    else:
        return render(request, 'users/login.html')


def mood_history(request):
    '''
    user - is related_name in our model
    displaying charts and tables
    '''

    count_plot = None
    line_plot = None
    bar_plot = None
    df_result = None
    table = None
    no_data = None
    if request.user.is_authenticated:
        user = request.user
        cur_user = User.objects.get(id=user.id)
        all_messages = User.objects.get(username=user)
        search_form = SearchForm(request.POST or None)

        # getting data from Sentiment model
        if request.method == 'POST':
            # using get cause it's dictionary
            date_from = request.POST.get('date_from')
            date_to = request.POST.get('date_to')
            chart_type = request.POST.get('chart_type')
            display_type = request.POST.get('display_choice')
            result = Sentiment.objects \
                .filter(user=user.id) \
                .filter(date_created__date__lte=date_to, date_created__date__gte=date_from)
            print(result)
            # getting values from our database

            if len(result) > 0:
                # using values method because results returns dictionary like object
                df_result = pd.DataFrame(result.values())
                df_result = df_result.drop(columns='id')
                try:
                    if display_type == '1':
                        count_plot = get_chart(df_result, 'count_plot')
                        line_plot = get_chart(df_result, 'line_plot')
                        bar_plot = get_chart(df_result, 'bar_plot')
                    if display_type == '2':
                        table = df_result.to_html()
                        pass
                except ValueError as e:
                    print('Value Error')

            else:
                no_data = True

            # chart_line = get_chart(result_data, 'lineplot')

        return render(request, "mood/mood_history.html",
                      {
                          "message_history": all_messages.message.all(),
                          "our_class": Message.objects.get(pk=user.id),
                          "search_form": search_form,
                          "count_plot": count_plot,
                          "line_plot": line_plot,
                          "bar_plot": bar_plot,
                          "table":table,
                          "no_data": no_data,
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
