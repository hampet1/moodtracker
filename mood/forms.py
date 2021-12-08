from django import forms
from .models import Medication


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



class SearchForm(forms.Form):
    date_from = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    display_choice = forms.ChoiceField(choices=DISPLAY_CHOICES)


