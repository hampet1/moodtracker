# for text processing
import re
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from tensorflow.keras.preprocessing.text import one_hot
from tensorflow.keras.preprocessing.sequence import pad_sequences

# for creating streams (file-like objects)
from io import BytesIO
import base64

# graphs
import matplotlib.pyplot as plt




def preprocessing(data):
    ps = PorterStemmer()
    corpus = []
    data = data.split('.')
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
    if chart_type == 'barplot':
        plt.bar(data, height=len(data))
    elif chart_type == 'lineplot':
        plt.plot(data['date_created'], data['sentiment'], marker='o')
    else:
        return "something went wrong"
    plt.tight_layout()
    chart = get_graph()
    return chart
