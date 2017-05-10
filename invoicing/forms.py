from invoicing.models import *
from django import forms


class TimesheetForm(forms.Form):
    project = forms.ModelChoiceField(label='Project', queryset=Project.objects.all())
    start = forms.DateField(label='Start date')
    end = forms.DateField(label='End date')
    unit = forms.ChoiceField(choices=(('days', 'days'), ('hours', 'hours')))