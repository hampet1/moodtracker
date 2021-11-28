from django import forms


GRAPH_CHOICES = (
    ('1', 'line_chart'),
    ('2', 'bar_chart'),

)


class SearchForm(forms.Form):
    data_from = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    date_to = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    chart_type = forms.ChoiceField(choices=GRAPH_CHOICES)