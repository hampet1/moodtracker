from django.db import models
# using auth model
from django.contrib.auth.models import User
# Create your models here.
from django.db import models

from django.contrib.auth.models import User

class Message(models.Model):
    # related name means that can access it from a related object
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user", null=True)
    message = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.user},{self.message},{self.date_created}"

class Medication(models.Model):
    user = models.ManyToManyField(User, blank=True, related_name="medication")
    name_of_medication = models.CharField(max_length=64)
    # black true means that it can be empty
    description = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{','.join([str(p) for p in self.user.all()])}, {self.name_of_medication}"


class Sentiment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sentiment", null=True)
    sentiment = models.IntegerField(null=True)
    rating = models.PositiveIntegerField(null=True)
    date_created = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.user}, {self.sentiment}, {self.rating}, {self.date_created}"

