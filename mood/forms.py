from django import forms
from .models import Medication
from django.contrib.admin.widgets import AdminDateWidget

'''
GRAPH_CHOICES = (
    ('1', 'line chart'),
    ('2', 'bar chart'),
    ('3', 'count plot'),

)
'''
DISPLAY_CHOICES = (
    ('1', 'chart'),
    ('2', 'table')
)


# todo change the date - day first
class SearchForm(forms.Form):
    date_from = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    display_choice = forms.ChoiceField(choices=DISPLAY_CHOICES)


