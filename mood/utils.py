# for text processing

import re
import os
import copy
import pickle
import nltk

nltk.download('stopwords')
from nltk.corpus import stopwords

from nltk.stem.porter import PorterStemmer
from tensorflow.keras.preprocessing.text import one_hot
from tensorflow.keras.preprocessing.sequence import pad_sequences
# from tensorflow.random import set_seed
# set_seed(1)

# for creating streams (file-like objects)
from io import BytesIO
import base64

# graphs
import plotly.express as px

# pandas
import pandas as pd
import requests

# df to pdf export

from reportlab.pdfgen import canvas
from django.http import HttpResponse

# time
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)

# load my encoder - to ensure the portability
#with open(BASE_DIR + '\encoder', "rb") as f:
#    one_hot = pickle.load(f)
#print(BASE_DIR + 'encoder')



def preprocessing(data):
    #   print("one hot is:", one_hot)
    ps = PorterStemmer()
    data = data.split('.')
    corpus = []
    for i in data:
        review = re.sub('[^a-zA-Z]', ' ', i)
        review = review.lower()
        review = review.split()
        review = [ps.stem(word) for word in review if not word in stopwords.words('english')]
        review = ' '.join(review)
        if review != '':
            corpus.append(review)
    return corpus


def vectorize_sentence(corpus):
    # Vocabulary size
    voc_size = 10000
    onehot_repr = [one_hot(words, voc_size) for words in corpus]
    # creating embedding layer as the input layer for our model we fixed lenght set to 20
    sent_length = 35
    # pad sequence - we have to always input vector of the same size, but sentences are of
    embedded_words = pad_sequences(onehot_repr, padding='pre', maxlen=sent_length)
    return embedded_words


def input_layer(data):
    corpus = preprocessing(data)
    embedded_input = vectorize_sentence(corpus)
    print("embedded_input: ", embedded_input)
    return embedded_input


def check_medication(name_of_med):
    """
    checking whether a given medication has a valid name using publicly aceessible API
    https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getRxNormName.html
    The whole API documentation accessible: https://lhncbc.nlm.nih.gov/RxNav/APIs/
    if the medication is in the database return 0 if not return 1
    """
    try:
        query = {'name': name_of_med}
        response = requests.get('https://rxnav.nlm.nih.gov/REST/rxcui.json?', params=query)
        response.raise_for_status()
        try:
            result = response.json()['idGroup']['rxnormId']
            return 0
        except KeyError:
            return 1

        # Code here will only run if the request is successful
    except requests.exceptions.HTTPError as error:
        print(error)


def df_to_excell(request, df):
    # The easiest way to create a binary stream is with open() with 'b' in the mode string
    with BytesIO() as b:
        # Use the StringIO object as the filehandle.
        writer = pd.ExcelWriter(b, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Sheet1')
        writer.save()
        # Set up the Http response.
        filename = 'my_mood.xlsx'
        response = HttpResponse(
            b.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        # attachment means to download
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

    return response


def adjust_time(df):
    """
    getting rid of microseconds in our pandas dataframe
    """
    for i in range(df.shape[0]):
        df['date_created'].loc[i] = df['date_created'].loc[i].split('.')[0]
    return df


def today_date():
    time_now = datetime.now()
    return datetime.strftime(time_now, '%Y-%m-%d')


def months_convertor(month):
    if month == 1:
        return "January"
    elif month == 2:
        return "February"
    elif month == 3:
        return "March"
    elif month == 4:
        return "April"
    elif month == 5:
        return "May"
    elif month == 6:
        return "June"
    elif month == 7:
        return "July"
    elif month == 8:
        return "August"
    elif month == 9:
        return "September"
    elif month == 10:
        return "October"
    elif month == 11:
        return "November"
    elif month == 12:
        return "December"
    else:
        return "this is not valid month"


def preprocess_df_heatmap(data):
    data['date_created'] = pd.to_datetime(data['date_created'], errors='coerce')
    data['day'] = data['date_created'].dt.day
    data['month'] = data['date_created'].dt.month
    data['year'] = data['date_created'].dt.year
    data = data.drop_duplicates(subset="date_created")
    # making deep copy while dealing with SettingWithCopyWarning, or just copy
    data_modified = copy.deepcopy(data)
    data_modified['month_name'] = data_modified.apply(lambda row: months_convertor(row['month']), axis=1)
    data_modified.set_index('date_created')
    return data_modified


def preprocess_df(data):
    data['date_created'] = pd.to_datetime(data['date_created']).copy()
    data['date_created'] = data['date_created'].dt.date
    data = data.drop_duplicates(subset="date_created")
    data = data.set_index('date_created')
    return data


def plot_bar(data):
    """
View demonstrating how to display a graph object
on a web page with Plotly.
"""
    data = preprocess_df(data)
    mean_rating = round(data['rating'].mean(), 2)
    # List of graph objects for figure.
    # Each object will contain on series of data.

    fig = px.bar(data, x=data.index, y="rating")
    layout = {
        'title': 'my new plot',
        'xaxis_title': 'data',
        'yaxis_title': 'rating',
        'height': 620,
        'width': 860,
    }

    fig.update_layout(
        title={
            'text': f"Personal mood rating, on average {mean_rating} out of 10",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
        },
        xaxis_title="date",
        yaxis_title="rating",
        legend_title="Legend Title",
        font=dict(
            family="Courier New, monospace",
            size=14,
            color="RebeccaPurple",
        )
    )
    # Getting HTML needed to render the plot.

    return fig.to_html()


def plot_heatmap(data):
    """
View demonstrating how to display a graph object
on a web page with Plotly.
"""

    data = preprocess_df_heatmap(data)
    # List of graph objects for figure.
    # Each object will contain on series of data.

    fig = px.density_heatmap(data, x="month_name", y="day", z=data['rating'], nbinsx=2, nbinsy=30,
                             color_continuous_scale='viridis')
    config = {'responsive': True}
    layout = {
        'title': 'my new plot',
        'xaxis_title': 'data',
        'yaxis_title': 'rating',
        'height': 620,
        'width': 860,
    }

    fig.update_layout(
        title={
            'text': f"Personal mood rating (heatmap)",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
        },
        xaxis_title="date",
        yaxis_title="day",
        legend_title="Legend Title",
        font=dict(
            family="Courier New, monospace",
            size=14,
            color="RebeccaPurple",
        )
    )
    # Getting HTML needed to render the plot.

    return fig.to_html(config=config)


def plot_count(data):
    """
    View demonstrating how to display a graph object
    on a web page with Plotly.
    """

    data = preprocess_df(data)

    # List of graph objects for figure.
    # Each object will contain on series of data.
    negative = 0
    positive = 0
    try:
        negative = data['sentiment'].value_counts()[1]
    except Exception as e:
        print(f"key error [{e}] : one (positive or negative count) or both counts are 0")
    try:
        positive = data['sentiment'].value_counts()[0]
    except Exception as e:
        print(f"key error [{e}] : one (positive or negative count) or both counts are 0")



    # List of graph objects for figure.
    # Each object will contain on series of data.

    categories = [positive, negative]

    fig = px.histogram(x=['negative', 'positive'], y=[positive, negative], color=categories, text_auto=True)
    layout = {
        'title': 'my new plot',
        'xaxis_title': 'data',
        'yaxis_title': 'rating',
        'height': 620,
        'width': 860,
    }

    fig.update_layout(
        title={
            'text': "Sentiment generated based on your day descriptions",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
        },
        xaxis_title="sentiment",
        yaxis_title="count",
        legend_title="Count",
        font=dict(
            family="Courier New, monospace",
            size=14,
            color="RebeccaPurple",
        )
    )
    # Getting HTML needed to render the plot.

    return fig.to_html()


def plot_line(data):
    """
View demonstrating how to display a graph object
on a web page with Plotly.
"""

    data = preprocess_df(data)

    # List of graph objects for figure.
    # Each object will contain on series of data.

    fig = px.line(data, x=data.index, y='sentiment', markers=True)
    layout = {
        'title': 'my new plot',
        'xaxis_title': 'data',
        'yaxis_title': 'rating',
        'height': 620,
        'width': 860,
    }

    fig.update_layout(
        title={
            'text': "Sentiment generated based on your day descriptions",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
        },
        xaxis_title="date",
        yaxis_title="rating",
        legend_title="Legend Title",
        font=dict(
            family="Courier New, monospace",
            size=14,
            color="RebeccaPurple",
        )
    )
    # Getting HTML needed to render the plot.

    return fig.to_html()
