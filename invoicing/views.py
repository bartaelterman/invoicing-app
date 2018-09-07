import pandas as pd
from collections import defaultdict
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from django.template import RequestContext
from datetime import date, datetime, timedelta
from weasyprint import HTML
from .models import Client, Invoice, Profile, Project, TimeEntry
from .forms import InvoiceForm, TimesheetForm

def generate_timesheet(request):
    form = TimesheetForm()
    context = {'form': form}
    return render(request, 'timesheet_form.html', context)


def display_timesheet(request):
    """
    get all time entries for a project and date range, and generate a timesheet.

    Expected query parameters:
      - project: project id
      - start: start date (yyyy-mm-dd)
      - end: end date (yyyy-mm-dd)
    """
    if request.method == 'GET':
        print(request.GET)
        project_id = request.GET.get('project', '1')
        start_str = request.GET.get('start', '2017-01-01')
        end_str = request.GET.get('end', '2017-12-31')
        time_unit = request.GET.get('unit', 'days')

        project = Project.objects.get(pk=int(project_id))
        client = Client.objects.get(pk=int(project.client_id))
        user = Profile.objects.get(pk=int(project.user_id))
        start = datetime.strptime(start_str, '%Y-%m-%d')
        end = datetime.strptime(end_str, '%Y-%m-%d') + timedelta(days=1)
        print('start: {0}'.format(start.isoformat()))
        print('end: {0}'.format(end.isoformat()))
        entries = TimeEntry.objects.get_queryset_df(start__gte=start, start__lte=end, project=project)
        unit_hours = 8.0 if time_unit == 'days' else 1.0
        entries['date'] = entries['start'].dt.date
        total = entries['duration'].sum() / unit_hours
        # entries['week'] = entries['start'].apply(lambda x: x.isocalendar()[1])
        # entries['weekday'] = entries['start'].apply(lambda x: x.isoweekday())
        entries_by_week_dict = defaultdict(dict)
        for day in pd.date_range(start=start_str, end=end_str):
            duration = entries[(entries['start'] >= day) & (entries['start'] <= day + timedelta(days=1))]['duration'].sum()
            weeknr = str(day.isocalendar()[0]) + '_' + '{:02}'.format(day.isocalendar()[1])
            print(weeknr)
            weekday = ['', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'][day.isocalendar()[2]]
            entries_by_week_dict[weeknr][weekday] = {'date': day.strftime('%d-%m'), 'duration': duration}
        entries_by_week = [entries_by_week_dict[x] for x in sorted(entries_by_week_dict.keys())]

        timeentries = entries.to_dict(orient='records')
        start_out_str = start.strftime('%d-%m-%Y')
        end_out_str = (end - timedelta(days=1)).strftime('%d-%m-%Y')

        context = {
            'client': client,
            'description': 'description',
            'end': end_out_str,
            'start': start_out_str,
            'entries_by_week': entries_by_week,
            'timeentries': timeentries,
            'total': '{0:.1f}'.format(total),
            'time_unit': time_unit,
            'user': user
        }
        template_file = project.timesheet_template if project.timesheet_template else 'calendar_timesheet.html'
        content = loader.render_to_string(template_file, context, request, using=None)
        if request.GET.get('output', '') == 'pdf':
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{project}_timesheet_{start_out_str}_{end_out_str}.pdf"'
            HTML(string=content).write_pdf(response, stylesheets=['invoicing/static/theme.css'])
            return response
        return HttpResponse(content, None, 200)


def generate_invoice(request):
    if request.method == 'GET':
        form = InvoiceForm()
    elif request.method == 'POST':
        # todo: add toaster message
        form = InvoiceForm(initial=request.POST)
        project = Project.objects.get(pk=request.POST.get('project'))
        start_str = request.POST.get('start')
        start = date(*[int(x) for x in start_str.split('-')])
        end_str = request.POST.get('end')
        end = date(*[int(x) for x in end_str.split('-')])
        days = request.POST.get('days')
        delivery_date = request.POST.get('delivery_date')
        invoice = Invoice(project=project, start=start, end=end, days=days, delivery_date=delivery_date)
        invoice.save()
    existing_invoices = Invoice.objects.all().order_by('-number')
    context = {'form': form, 'invoices': existing_invoices}
    return render(request, 'invoice_form.html', context)


def display_invoice(request):
    """
    get all time entries for a project and date range, and generate a invoice.

    Expected query parameters:
      - invoiceId
    """
    if request.method == 'GET':
        invoice_id = request.GET.get('invoiceId', '1')
        invoice = Invoice.objects.get(pk=int(invoice_id))
        invoice_date_format = '%d/%m/%Y'
        total_price = invoice.days * invoice.project.rate
        invoice_items = [
            {'description': '{} dagen ontwikkeling (aan €{} per dag)'.format(invoice.days, invoice.project.rate),
             'price': '{0:.2f}'.format(invoice.days * invoice.project.rate),
             'vat': '{0:.2f}'.format(invoice.days * invoice.project.rate * invoice.vat_rate / 100)}]
        if invoice.invoiceitem_set.all().count() > 0:
            for item in invoice.invoiceitem_set.all():
                invoice_items.append({
                    'description': item.description,
                    'price': '{0:.2f}'.format(item.price),
                    'vat': '{0:.2f}'.format(item.price * invoice.vat_rate / 100)})
                total_price += item.price

        context = {
            'client': invoice.project.client,
            'user': invoice.project.user,
            'invoice_number': invoice.number,
            'start': invoice.start.strftime(invoice_date_format),
            'end': invoice.end.strftime(invoice_date_format),
            'invoice_date': invoice.date.strftime(invoice_date_format),
            'invoice_delivery_date': invoice.delivery_date.strftime(invoice_date_format),
            'invoice_items': invoice_items,
            'description': invoice.description,
            'nr_of_days': '{0:.1f}'.format(invoice.days),
            'rate': '{0:.2f}'.format(invoice.project.rate),
            'total': '{0:.2f}'.format(total_price),
            'vat': '{0:.2f}'.format(float(total_price) * float(invoice.project.vat_rate)),
            'total_vat': '{0:.2f}'.format(float(total_price) * (1 + float(invoice.project.vat_rate))),
            'vat_rate': invoice.vat_rate
        }

        content = loader.render_to_string(invoice.project.invoice_template, context, request, using=None)
        if request.GET.get('output', '') == 'pdf':
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{invoice.number}_invoice_{invoice.project}.pdf"'
            HTML(string=content).write_pdf(response, stylesheets=['invoicing/static/theme.css'])
            return response
        return HttpResponse(content, None, 200)


def get_time_entries(request):
    if request.method == 'GET':
        project_id = request.GET.get('project', '')
        start_str = request.GET.get('start', '')
        end_str = request.GET.get('end', '')

        project = Project.objects.get(pk=int(project_id))
        start = datetime.strptime(start_str, '%Y-%m-%d')
        end = datetime.strptime(end_str, '%Y-%m-%d')
        entries = TimeEntry.objects.get_queryset_df(start__gte=start, start__lte=end, project=project)
        return HttpResponse(entries.T.to_json())