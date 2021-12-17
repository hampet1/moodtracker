from django.db import models
# using auth model
from django.contrib.auth.models import User
# Create your models here.
from django.db import models
from django.db.models import Q

from django.contrib.auth.models import User

class Sentiment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sentiment", null=True)
    message = models.TextField()
    sentiment = models.IntegerField(null=True)
    rating = models.PositiveIntegerField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.user}, {self.message}, {self.sentiment}, {self.rating}, {self.date_created}"


    def get_sentiment(self):
        return self.sentiment


class Medication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="medication", null=True)
    name_of_medication = models.CharField(max_length=64)
    # black true means that it can be empty
    description = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.user}, {self.name_of_medication}, {self.description}"

