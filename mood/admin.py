from django.contrib import admin

from .models import Medication, Sentiment, DeletedMedication

#register your models
admin.site.register(Medication)
admin.site.register(Sentiment)
admin.site.register(DeletedMedication)
#register your models
