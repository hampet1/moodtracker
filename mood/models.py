from django.db import models
# using auth model
from django.contrib.auth.models import User
# Create your models here.
from django.db import models
from django.db.models import Q

from django.contrib.auth.models import User


def update_existing_record(user, date_today, column, rating=None, message=None, sentiment=None):
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
    # message_content = Sentiment.objects.filter(user=user).filter(date_created__date=date_today)
    no_record_for_today = False
    message_id = Sentiment.objects.filter(user=user).filter(date_created__date=date_today).values_list('id', flat=True)
    try:
        message_id = message_id[0]
        try:
            my_record = Sentiment.objects.get(pk=message_id)
            message = my_record.message
            rating = my_record.rating
        except Exception as e:
            print(f"the error is {e}")
    except Exception as e:
        print(f"the error is {e}")
        no_record_for_today = True

    if no_record_for_today:
        return None
    elif message != None and rating == 0:
        return "no rating"
    elif message == None and rating != 0:
        return 'no message'
    else:
        return "both exists"


def create_record(user, type_of_input, rating=None, message=None, sentiment=None):
    """
    create record if there is not available record for today
    we can create the whole record (in sense of creating message, sentiment and rating)
    or we can create just rating or just message and its sentiment
    """
    if type_of_input == 'both':
        Sentiment.objects.create(user=user, message=message, sentiment=sentiment,
                                 rating=int(rating))
    elif type_of_input == 'rating':
        Sentiment.objects.create(user=user, message=None, sentiment=None, rating=int(rating))
    elif type_of_input == 'message':
        Sentiment.objects.create(user=user, message=message, sentiment=sentiment,
                                 rating=0)
    else:
        return "it's not valid input"


class Sentiment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sentiment", null=True)
    message = models.TextField(max_length=280, null=True, blank=True)
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
