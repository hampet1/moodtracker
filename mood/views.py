from django.shortcuts import render
import json
from .models import Sentiment, Medication, DeletedMedication, check_if_message_exist, update_existing_record, create_record

from django.contrib.auth.models import User
from django.template.defaulttags import register

# keras model manipulation
from keras.models import model_from_json
# other packages
import os
import numpy as np
import pandas as pd


# helper funtions - for embedded layer of our model
from .utils import input_layer, df_to_excell, adjust_time, today_date, check_medication, plot_heatmap, plot_bar, plot_line, plot_count
from .forms import SearchForm


# project root is where setting is exactly placed
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

BASE_DIR = os.path.dirname(PROJECT_ROOT)

# for deep learning model we have to
weights_path = os.path.join(BASE_DIR, 'model.h5')
model_path = os.path.join(BASE_DIR, 'model.json')


@register.filter
def get_range(value):
    """
    this is the way to use range in jinja2 while working with django
    """
    return range(1, value)


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
    4 main variables:
    message_input and rating_input keep track of input values
    any_message, any_rating - check whether a message or a rating have been already submitted on a particular day


    we can submit only one message and rating a day, we can submit them simultaneously or one at a time

    info variable - says that your request (message or rating) was submitted successfuly
    info_posted - says that you've already conducted daily report

    message_new - in edge cases if use has not posted any message yet

    """
    sentiment = None
    rating_input = None
    chart = None
    info = None
    date_today = None
    message = None
    message_new = None
    rating_success = None
    info_both_posted = None
    info_rating_posted = None
    info_message_posted = None
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
        rating_input = request.POST['rating']
        # if we did not pick any number the rating value will be the description itself
        if len(rating_input) > 2:
            rating_input = 0
        # check if we already posted our daily mood and rating
        date_today = today_date()
        # todo allow user additionaly add rating for the same day

        # checking a given message or rating already exists
        message_uploaded = check_if_message_exist(user, date_today)
        print("res of our function is: ", message_uploaded)
        # check if there is a record already
        if message_uploaded is not None:
            if message_uploaded == "no rating":
                print("no rating posted")
                if rating_input:
                    update_existing_record(user, date_today,'rating', rating = rating_input)
                    rating_success = True
                else:
                    print("you have alrady posted that")
                    info_rating_posted = True
            elif message_uploaded == "no message":
                info_message_posted = True
            else:
                # both exists
                info_both_posted = True
            res = Sentiment.objects.filter(user=user).filter(date_created__date=date_today)
            print("it worked: ", res)
            return render(request, "mood/index.html",
                          {
                              'message': message_new,
                              "info": info,
                              "info_both_posted": info_both_posted,
                              "info_rating_posted": info_rating_posted,
                              "info_message_posted": info_message_posted,
                              "rating_success": rating_success,
                          })
        else:
            # if there is no record for today
            # three option message and rating, only rating only massage
            if rating_input and not message_input:
                create_record(user, 'rating', rating=rating_input)
                res = Sentiment.objects.filter(user=user).filter(date_created__date=date_today)
                print("it worked: ", res)
            else:


                print("i have already posted it today !!!! - to prevent from overriting message!")
                # evaluate loaded model on test data
                loaded_model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
                # preprocess text
                text = input_layer(message_input)

                # predictions
                try:
                    pred = (loaded_model.predict(text) > 0.5).astype("int32")
                    # our model prediction

                    if np.average(pred) < 0.5:
                        sentiment = 0
                    else:
                        sentiment = 1
                except Exception as e:
                    print(f"something went wrong: {e}")

                if rating_input != 0:
                    try:
                        if sentiment is not None:
                            print("this one is printing")
                            rating_input = request.POST['rating']
                            Sentiment.objects.create(user=user, message=message_input, sentiment=sentiment,
                                                     rating=int(rating_input))
                            info = True
                    except ValueError as e:
                        Sentiment.objects.create(user=user, rating=0)
                        info = True
                else:
                    try:
                        if sentiment is not None:
                            print("this one is working")
                            rating_input = request.POST['rating']
                            Sentiment.objects.create(user=user, message=message_input, sentiment=sentiment,
                                                     rating=0)
                            info = True
                    except ValueError as e:
                        Sentiment.objects.create(user=user, rating=0)

            #  used in edge case when we do not have any messages for this user
            try:
                message_new = Sentiment.objects.get(pk=user.id)
            except message_new.DoesNotExist:
                message_new = None

        return render(request, "mood/index.html",
                      {
                          'message': message_new,
                          "info": info,
                          "info_both_posted": info_both_posted,
                          "info_rating_posted": info_rating_posted,
                          "info_message_posted": info_message_posted
                      })

    else:
        # in case we're not logged in or so
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


def ajax(request):
    """
    we have to deserialize json
    https://stackoverflow.com/questions/25791913/querydict-always-empty-from-ajax-post
    """
    print("it worked")

    if request.method == "POST" and request.user.is_authenticated:
        user = request.user
        print("our request in get_ajax: ", request.POST)
        # djanco can't deserialize json so we have to do it
        body_unicode = request.body.decode('utf-8')
        received_json = json.loads(body_unicode)
        med_name_session = request.session['med_session']
        med_description_session = request.session['med_description_session']
        if received_json == 'proceed':
            duplicate_check = Medication.objects.filter(user=user, name_of_medication=med_name_session)
            if duplicate_check.exists():
                print("value is duplicated")
            else:
                Medication.objects.create(user=user, name_of_medication=med_name_session, description=med_description_session)
                print("med added")


            return render(request, "mood/mood_history.html")




def medication_update(request):
    med_name_add = None
    med_description = None
    info_med = None
    info_med_error = None
    info_med_duplicate = None
    if request.method == "POST" and request.user.is_authenticated:
        user = request.user
        print("our post is: ", request.POST)
        med_name_add = str(request.POST['med-name-add'])
        # store it into session as well
        session_medication = med_name_add
        request.session['med_session'] = session_medication
        session_description = str(request.POST['med-description'])
        request.session['med_description_session'] = session_description

        # checking using API of national library of medicine whether a given medication exists or not
        if check_medication(med_name_add) == 0:
            # adding medication to the database, if it was found
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
            # if medication was not found ask user if they want to proceed
            info_med_error = True
            print("we are getting there")
            return render(request, "mood/index.html", {'info_med_error': info_med_error,
                                                       })
    else:
        return render(request, "mood/error404.html")



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
    plot_heatmap_ = None
    plot_line_ = None
    plot_bar_ = None
    plot_count_ = None
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
            if len(result) <= 0:
                no_data = True
                return render(request, "mood/results.html", {"no_data": no_data})

            # using values method because results returns dictionary like object
            df_sent = pd.DataFrame(result.values())

            df_sent = df_sent.drop(columns='id')

            try:
                if display_type == '1':
                    plot_bar_ = plot_bar(df_sent)
                    plot_heatmap_ = plot_heatmap(df_sent)
                    plot_line_ = plot_line(df_sent)
                    plot_count_ = plot_count(df_sent)
                    plots = True
                if display_type == '2':
                    # trying to avaid SettingwithCopyWarning for pandas dataframes
                    df_sent_table = df_sent.copy()
                    # store into sessions - used for excel export
                    df_for_session = df_sent_table
                    df_for_session['date_created'] = df_for_session['date_created'].astype(str)
                    dict_obj = df_for_session.to_dict('list')
                    request.session['data'] = dict_obj
                    # adjusting time for sentiment table
                    df_sent_table['index'] = df_sent_table.index + 1
                    df_sent_table['rating'] = df_sent_table['rating'].apply(lambda x: x if (x != 0) else 'no record')
                    df_sent_table['sentiment'] = df_sent_table['sentiment'].apply(lambda x: x if (x in [0, 1]) else 'no record')

                    df_sent_table = adjust_time(df_sent_table)
                    if len(result_medication) > 0:
                        df_med = pd.DataFrame(result_medication.values())
                        df_med = df_med.drop(columns='id')

                        df_med['index'] = df_med.index + 1
                        df_med['description'] = df_med['description'].apply(lambda x: x if (x != '') else 'no record')
                        # creating list for displaying sentiment table
                        for i in range(df_sent_table.shape[0]):
                            temp = df_sent_table.iloc[i]
                            table_data_sent.append(dict(temp))

                        # creating list for displaying medication table
                        for i in range(df_med.shape[0]):
                            temp = df_med.iloc[i]
                            table_medication.append(dict(temp))
                    else:
                        for i in range(df_sent_table.shape[0]):
                            temp = df_sent_table.iloc[i]
                            table_data_sent.append(dict(temp))

            except ValueError as e:
                print(f"the error is: {e}")
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
                              "plots": plots,
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

# todo work on delete medication - create a graph with it and automatically incormorate type of medication using REST API
