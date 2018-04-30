from invoicing.models import *
from django import forms


class TimesheetForm(forms.Form):
    project = forms.ModelChoiceField(label='Project', queryset=Project.objects.all())
    start = forms.DateField(label='Start date', widget=forms.TextInput(attrs={'class':'datepicker'}))
    end = forms.DateField(label='End date', widget=forms.TextInput(attrs={'class':'datepicker'}))
    unit = forms.ChoiceField(choices=(('days', 'days'), ('hours', 'hours')))


class InvoiceForm(forms.Form):
    project = forms.ModelChoiceField(label='Project', queryset=Project.objects.all())
    start = forms.DateField(label='Start date')
    end = forms.DateField(label='End date')
    delivery_date = forms.DateField(label='Delivery date')
    days = forms.DecimalField(min_value=0, decimal_places=2)