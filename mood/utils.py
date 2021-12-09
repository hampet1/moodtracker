# for text processing
import re
import os
import pickle
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
#from tensorflow.keras.preprocessing.text import one_hot
from tensorflow.keras.preprocessing.sequence import pad_sequences
#from tensorflow.random import set_seed
#set_seed(1)

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
    voc_size=10000
    onehot_repr=[one_hot(words,voc_size)for words in corpus]
    # creating embedding layer as the input layer for our model we fixed lenght set to 20
    sent_length=35
    # pad sequence - we have to always input vector of the same size, but sentences are of
    embedded_words=pad_sequences(onehot_repr,padding='pre',maxlen=sent_length)
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
    fig = plt.figure(figsize=(8,4))
    if chart_type == 'bar_plot':
        plt.title("your day rating")
        sns.barplot(x="date_created", y="rating", data=data,
                    palette="Blues_d")
    elif chart_type == 'line_plot':
        plt.title("mood determined based on your mood description")
        plt.plot(data['date_created'], data['sentiment'], marker='o')
    elif chart_type == 'count_plot':
        plt.title("sum of possitive and negative dayes")
        sns.countplot(x='sentiment', data=data, palette="Set3")
    else:
        return "something went wrong"
    plt.tight_layout()
    chart = get_graph()
    return chart



def export_pdf(df_data):
    """
    export table to pdf

    """
    fig, ax =plt.subplots(figsize=(12,4))
    ax.axis('tight')
    ax.axis('off')
    the_table = ax.table(cellText=df_data.values,colLabels=df_data.columns,loc='center')
    # Create the HttpResponse object with the appropriate PDF headers.
    return the_table




def some_view(df_data):
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="somefilename.pdf"'

    buffer = BytesIO()


    # Create the PDF object, using the BytesIO object as its "file."
    p = canvas.Canvas(buffer)
    # calling another function
    df_data = export_pdf(df_data)
    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 100, df_data)

    # Close the PDF object cleanly.
    p.showPage()
    p.save()

    # Get the value of the BytesIO buffer and write it to the response.
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response