# for text processing
import re
import os
import pickle
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
# from tensorflow.keras.preprocessing.text import one_hot
from tensorflow.keras.preprocessing.sequence import pad_sequences
# from tensorflow.random import set_seed
# set_seed(1)

# for creating streams (file-like objects)
from io import BytesIO
import base64

# graphs
import matplotlib.pyplot as plt
import seaborn as sns

# df to pdf export
from matplotlib.backends.backend_pdf import PdfPages
from reportlab.pdfgen import canvas
from django.http import HttpResponse

# time
from datetime import datetime

# load my encoder
with open(os.getcwd() + '\encoder', "rb") as f:
    one_hot = pickle.load(f)

print("one hot is on", one_hot)


def preprocessing(data):
    print("one hot is:", one_hot)
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


def get_graph():
    '''

    delete the comments below
    '''

    buffer = BytesIO()
    # here we communicate with plt
    plt.savefig(buffer, format="png")
    # set cursor to the biggining of the stream
    buffer.seek(0)
    # retrieve the entire content of the file
    image_png = buffer.getvalue()
    # encode our bytes-like object - return encoded bytes
    graph = base64.b64encode(image_png)
    # get string out of the bytes
    graph = graph.decode('utf-8')
    # free memory of the buffer
    buffer.close()
    return graph


def get_chart(data, chart_type):
    plt.switch_backend('AGG')
    fig = plt.figure(figsize=(8, 4))
    # turn into datetime format
    data['date_created'] = pd.to_datetime(data['date_created'])
    data['date_created'] = data['date_created'].dt.date
    data = data.set_index('date_created')
    print("data is ", data)
    #data = data.resample("W").sum()
    print("resample data", data)
    #print(type(data['date_created']))

    # set time as the index
    #data.set_index('date_created', inplace=True)

    if chart_type == 'bar_plot':
        plt.title("your day rating")
        sns.barplot(x=data.index, y="rating", data=data,
                    palette="Blues_d")
    elif chart_type == 'line_plot':
        plt.title("mood determined based on your mood description")
        plt.plot(data['sentiment'], marker='o')
    elif chart_type == 'count_plot':
        plt.title("your day rating")
        sns.barplot(x=data.index, y="sentiment", data=data,
                    palette="Blues_d")
    else:
        return "something went wrong"
    plt.tight_layout()
    chart = get_graph()
    return chart

'''
def export_pdf(df_data):
    """
    export table to pdf

    """
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.axis('tight')
    ax.axis('off')
    the_table = ax.table(cellText=df_data.values, colLabels=df_data.columns, loc='center')
    # Create the HttpResponse object with the appropriate PDF headers.
    return the_table

'''
import pandas as pd


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
