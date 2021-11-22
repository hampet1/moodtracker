import re
import os
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from tensorflow.keras.preprocessing.text import one_hot
from tensorflow.keras.preprocessing.sequence import pad_sequences
from keras.models import model_from_json




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