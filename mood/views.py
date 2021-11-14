from django.shortcuts import render
from django import forms
import sys

from keras.models import model_from_json

from .models import Message, Medication
from django.contrib.auth.models import User
from django.http import JsonResponse
# Create your views here.
from django.template.defaulttags import register

# other packages
import os

# text processing
import re
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from tensorflow.keras.preprocessing.text import one_hot
from tensorflow.keras.preprocessing.sequence import pad_sequences



weights_path = os.getcwd() + '\model.h5'
model_path = os.getcwd() + '\model.json'




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
    if request.method == "POST" and request.user.is_authenticated:
        user = request.user

        cur_user = User.objects.get(id=user.id)
        message = request.POST['message']

        if 'med-type' in request.POST:
            med_type = request.POST['med-type']
        else:
            med_type = False
        rating = request.POST['rating']
        # medication = request.POST['medication']
        # user is the related name
        print("med type is", med_type)
        print("rating is: ", rating)
        print("mesage is ", message)

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
        # our model prediction
        print("our prediction is: ",pred)
        Message.objects.create(user=user, message=message)
        return render(request, "mood/mood_history.html",
                      {
                          'user': user.username,
                          'message': Message.objects.get(pk=user.id)
                          # pick possible medication
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
