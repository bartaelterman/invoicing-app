from invoicing.models import *
from django import forms


class TimesheetForm(forms.Form):
    project = forms.ModelChoiceField(label='Project', queryset=Project.objects.all())
    start = forms.DateField(label='Start date')
    end = forms.DateField(label='End date')
    unit = forms.ChoiceField(choices=(('days', 'days'), ('hours', 'hours')))


class InvoiceForm(forms.Form):
    project = forms.ModelChoiceField(label='Project', queryset=Project.objects.all())
    start = forms.DateField(label='Start date')
    end = forms.DateField(label='End date')
    days = forms.DecimalField(min_value=0, decimal_places=2)