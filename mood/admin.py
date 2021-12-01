from django.contrib import admin

from .models import Message, Medication, Sentiment

#register your models
admin.site.register(Message)
admin.site.register(Medication)
admin.site.register(Sentiment)
#register your models
