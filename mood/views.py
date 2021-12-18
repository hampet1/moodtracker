from django.shortcuts import render
from keras.models import model_from_json
from .models import Sentiment, Medication
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
from .utils import input_layer, get_chart, df_to_excell, adjust_time
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
    # todo add check if medication is not already in the database
    # todo make sure there are no duplicates
    med_name_del = None
    if request.method == "POST" and request.user.is_authenticated:
        user = request.user
        med_name_del = str(request.POST['med-name-del'])
        print("del: ", med_name_del)
        del_item = Medication.objects.filter(user=user).filter(name_of_medication=med_name_del)
        del_item.delete()
        print("deleted")

        # del item
    return render(request, "mood/index.html")


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
        med_description = str(request.POST['med-description'])
        Medication.objects.create(user=user, name_of_medication=med_name_add, description=med_description)

    return render(request, "mood/index.html")


def message(request):
    """
    pk and id is the same thing
    message - is related_name
    request.method == "POST"
    """
    sentiment = None
    chart = None
    info = None
    message = None
    if request.method == "POST" and request.user.is_authenticated:
        user = request.user
        # load json and create model
        json_file = open(model_path, 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        loaded_model = model_from_json(loaded_model_json)
        # load weights into new model
        loaded_model.load_weights(weights_path)
        # our input message
        message_input = request.POST['message']

        # evaluate loaded model on test data
        loaded_model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        text = input_layer(message_input)

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
                    Sentiment.objects.create(user=user, message=message_input, sentiment=sentiment, rating=int(rating))
                    info = True
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
                          'message': Sentiment.objects.get(pk=user.id),
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
    table_data = []
    if request.user.is_authenticated:
        user = request.user
        cur_user = User.objects.get(id=user.id)
        all_messages = User.objects.get(username=user)
        search_form = SearchForm(request.POST or None)

        return render(request, "mood/mood_history.html",
                      {
                          "search_form": search_form,
                      })
    else:
        print("you're not registered")


def mood_history_result(request):
    count_plot = None
    line_plot = None
    bar_plot = None
    df_result = None
    table = None
    download = None
    no_data = None
    date_from = None
    date_to = None
    table_data = []
    df_sent = None
    table_data_sent = []
    table_medication = []
    if request.user.is_authenticated:
        user = request.user
        all_messages = User.objects.get(username=user)

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

            result_medication = Medication.objects \
                .filter(user=user.id) \
                .filter(date_created__date__lte=date_to, date_created__date__gte=date_from)

            print("result medication is: ", result_medication)
            if len(result) > 0:
                # using values method because results returns dictionary like object
                df_sent = pd.DataFrame(result.values())
                df_sent = df_sent.drop(columns='id')

            if len(result_medication) > 0:
                df_med = pd.DataFrame(result_medication.values())
                df_med = df_med.drop(columns='id')

                try:
                    if display_type == '1':
                        count_plot = get_chart(df_sent, 'count_plot')
                        line_plot = get_chart(df_sent, 'line_plot')
                        bar_plot = get_chart(df_sent, 'bar_plot')
                    if display_type == '2':

                        # store into sessions - used for excel export
                        df_for_session = df_sent
                        print("this one is working")
                        df_for_session['date_created'] = df_for_session['date_created'].astype(str)
                        dict_obj = df_for_session.to_dict('list')
                        request.session['data'] = dict_obj
                        # adjusting time for sentiment table
                        df_sent['index'] = df_sent.index + 1
                        df_sent['rating'] = df_sent['rating'].apply(lambda x: x if (x != 0) else 'nan')
                        df_sent = adjust_time(df_sent)

                        # adjusting time for medication table
                        df_med['index'] = df_med.index + 1
                        df_med['description'] = df_med['description'].apply(lambda x: x if (x != '') else 'nan')
                        # creating list for displaying sentiment table
                        print("df med is: ", df_med)
                        for i in range(df_sent.shape[0]):
                            temp = df_sent.iloc[i]
                            table_data_sent.append(dict(temp))

                        # creating list for displaying medication table
                        for i in range(df_med.shape[0]):
                            temp = df_med.iloc[i]
                            table_medication.append(dict(temp))

                except ValueError as e:
                    no_data = True

        return render(request, "mood/results.html",
                      {
                          "date_from": date_from,
                          "date_to": date_to,
                          "count_plot": count_plot,
                          "line_plot": line_plot,
                          "bar_plot": bar_plot,
                          "table_sentiment": table_data_sent,
                          "table_medication": table_medication,
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


def download_pdf(request):
    """
    download dataframe as xlsx
    """

    if request.user.is_authenticated:
        print("something is happening")
        # getting data from Sentiment model

        if request.method == 'POST':
            try:
                if request.POST['download_csv']:
                    my_session = request.session['data']
                    my_df = pd.DataFrame(my_session)
                    my_df['date_created'] = pd.to_datetime(my_df['date_created'], format='%Y%m%d%H%M%S',
                                                           errors='ignore')
                    # adjusting time
                    my_df = adjust_time(my_df)
                    csv_file = df_to_excell(request, my_df)
                    return csv_file
                else:
                    print("something went wrong")

            except Exception as e:
                print(f"the problem is {e}")


def guideline(request):
    return render(request, 'mood/guideline.html')
