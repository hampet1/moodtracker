from django.db import models
# using auth model
from django.contrib.auth.models import User
# Create your models here.
from django.db import models
from django.db.models import Q

from django.contrib.auth.models import User



def update_existing_record(user, date_today, column, rating = None, message = None, sentiment = None):
    """
    update record in our database in case just rating or sentiment exists
    """
    message_id = Sentiment.objects.filter(user=user).filter(date_created__date=date_today).values_list('id', flat=True)
    try:
        my_record = Sentiment.objects.get(pk=int(message_id[0]))
    except IndexError as e:
        print(f"the exception is: {e}")

    if column == 'rating':
        my_record.rating = rating
        my_record.save()
    if column == 'message':
        my_record.message = message
        my_record.sentiment = sentiment
        my_record.save()

def check_if_message_exist(user, date_today):
    """
    check if message and rating was already uploaded
    """
    # allow just one record per day
    message_content = Sentiment.objects.filter(user=user).filter(date_created__date=date_today)
    print("message content is: ", message_content)
    try:
        any_message = str(message_content[0]).split(",")[1].strip()
    except IndexError as e:
        print(f"the error is {e}")
        any_message = ''
    try:
        any_rating = str(message_content[0]).split(",")[3].strip()
    except IndexError as e:
        print(f"the error is {e}")
        any_rating = '0'
    if any_message == '' and any_rating == '0':
        return None
    elif any_message != '' and any_rating == '0':
        return "no rating"
    elif any_message == '' and any_rating != '0':
        return 'no message'
    else:
        return "both exists"



class Sentiment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sentiment", null=True)
    message = models.TextField(max_length=280)
    sentiment = models.IntegerField(null=True)
    rating = models.PositiveIntegerField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.user}, {self.message}, {self.sentiment}, {self.rating}, {self.date_created}"




class Medication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="medication", null=True)
    name_of_medication = models.CharField(max_length=64)
    # black true means that it can be empty
    description = models.TextField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.user}, {self.name_of_medication}, {self.description}"


class DeletedMedication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="medication_delete", null=True)
    name_of_medication = models.CharField(max_length=64)
    # black true means that it can be empty
    reason = models.TextField(null=True, blank=True)
    date_deleted = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.user}, {self.name_of_medication}, {self.reason}, {self.date_deleted}"