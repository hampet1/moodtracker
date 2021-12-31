from django.shortcuts import render
from keras.models import model_from_json
from .models import Sentiment, Medication, DeletedMedication
from django.contrib.auth.models import User
from django.template.defaulttags import register
from django.http import HttpResponse

# keras model manipulation
from keras.models import model_from_json
# other packages
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

# helper funtions - for embedded layer of our model
from .utils import input_layer, df_to_excell, adjust_time, today_date, check_medication, plot_bar, plot_heatmap, plot_line, plot_count
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
    return range(1,value)


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
        return render(request, "mood/error404.html")




def message(request):
    """
    pk and id is the same thing
    message - is related_name
    request.method == "POST"
    """
    sentiment = None
    chart = None
    info = None
    date_today = None
    message = None
    info_posted = None
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

        # check if we already posted our daily mood and rating
        date_today = today_date()
        any_message = Sentiment.objects.filter(user=1).filter(date_created__date=date_today)

        if any_message.exists():
            info_posted = True
        else:
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
                          "info_posted": info_posted,
                      })

    else:
        return render(request, "mood/error404.html")


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
        return render(request, "mood/error404.html")


def medication_update(request):
    med_name_add = None
    med_description = None
    info_med = None
    info_med_error = None
    info_med_duplicate = None
    if request.method == "POST" and request.user.is_authenticated:
        user = request.user
        med_name_add = str(request.POST['med-name-add'])
        print("med name", med_name_add)
        # checking using API of national library of medicine whether a given medication exists or not

        if check_medication(med_name_add) == 0:
            # adding medication to the database
            med_description = str(request.POST['med-description'])
            # make sure there are no duplicates
            duplicate_check = Medication.objects.filter(user=user, name_of_medication=med_name_add)
            if duplicate_check.exists():
                info_med_duplicate = True
            else:
                Medication.objects.create(user=user, name_of_medication=med_name_add, description=med_description)
                info_med = True
            return render(request, "mood/index.html", {'info_med': info_med,
                                                       'info_med_duplicate': info_med_duplicate})
        else:
            info_med_error = True
            return render(request, "mood/index.html", {'info_med_error': info_med_error,
                                                       })



def medication_delete(request):
    del_item = None
    del_reason = None
    info_med_del = None
    item_not_found = None
    if request.method == "POST" and request.user.is_authenticated:
        user = request.user
        med_name_del = str(request.POST['med-name-del'])
        del_reason = str(request.POST.get('med-del-reason'))
        # store deleted item to keep track of them

        del_item = Medication.objects.filter(user=user).filter(name_of_medication=med_name_del)

        if del_item.exists():
            if del_reason:
                DeletedMedication.objects.create(user=user, name_of_medication=med_name_del, reason=del_reason)
            else:
                DeletedMedication.objects.create(user=user, name_of_medication=med_name_del)
            info_med_del = True
            del_item.delete()
            # delete the record from database
        else:
            item_not_found = True

        del_item.delete()

        # del item
        return render(request, "mood/index.html", {
            'info_med_del': info_med_del,
            'item_not_found': item_not_found
        })







def mood_history_result(request):
    plots = None




    count_plot = None
    line_plot = None
    bar_plot = None
    bar_plot_2 = None
    no_data = None
    date_from = None
    date_to = None
    df_sent = None
    table_data_sent = []
    table_medication = []
    if request.user.is_authenticated:
        user = request.user
        all_messages = User.objects.get(username=user)

        # getting data from Sentiment model
        if request.method == 'POST':
            # using get cause it's dictionary
            # todo fix date day-month-year
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

            if len(result) > 0:
                # using values method because results returns dictionary like object
                df_sent = pd.DataFrame(result.values())
                df_sent = df_sent.drop(columns='id')

            if len(result_medication) > 0:
                df_med = pd.DataFrame(result_medication.values())
                df_med = df_med.drop(columns='id')

                try:
                    if display_type == '1':

                        plot_bar_ = plot_bar(df_sent)
                        plot_heatmap_ = plot_heatmap(df_sent)
                        plot_count_ = plot_count(df_sent)
                        plot_line_ = plot_line(df_sent)


                        plots = True
                    if display_type == '2':

                        # store into sessions - used for excel export
                        df_for_session = df_sent
                        print("this one is working")
                        df_for_session['date_created'] = df_for_session['date_created'].astype(str)
                        dict_obj = df_for_session.to_dict('list')
                        request.session['data'] = dict_obj
                        # adjusting time for sentiment table
                        df_sent['index'] = df_sent.index + 1
                        df_sent['rating'] = df_sent['rating'].apply(lambda x: x if (x != 0) else 'no record')
                        df_sent['sentiment'] = df_sent['sentiment'].apply(lambda x: x if (x in [0, 1]) else 'no record')
                        df_sent = adjust_time(df_sent)

                        # adjusting time for medication table
                        df_med['index'] = df_med.index + 1
                        df_med['description'] = df_med['description'].apply(lambda x: x if (x != '') else 'no record')
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
                              "plot_bar": plot_bar_,
                              "plot_heatmap": plot_heatmap_,
                              "plot_count": plot_count_,
                              "plot_line": plot_line_,
                              "table_sentiment": table_data_sent,
                              "table_medication": table_medication,
                              "no_data": no_data,
                              "plots":plots,
                          })
        else:
            return render(request, "mood/error404.html")


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
    else:
        return render(request, "mood/error404.html")


def guideline(request):
    if request.user.is_authenticated:
        return render(request, 'mood/guideline.html')
    else:
        return render(request, "mood/error404.html")




