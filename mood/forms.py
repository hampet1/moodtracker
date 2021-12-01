from django import forms

GRAPH_CHOICES = (
    ('1', 'line chart'),
    ('2', 'bar chart'),
    ('3', 'count plot'),

)


class SearchForm(forms.Form):
    date_from = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    chart_type = forms.ChoiceField(choices=GRAPH_CHOICES)
