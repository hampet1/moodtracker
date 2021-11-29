from django import forms

GRAPH_CHOICES = (
    ('1', 'line_chart'),
    ('2', 'bar_chart'),
    ('3', 'heat_map'),

)


class SearchForm(forms.Form):
    date_from = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    chart_type = forms.ChoiceField(choices=GRAPH_CHOICES)
