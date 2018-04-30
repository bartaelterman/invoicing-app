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
    # TODO: add calendar UI element to select dates
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
        invoice = Invoice(project=project, start=start, end=end, days=days)
        invoice.save()
    existing_invoices = Invoice.objects.all()
    context = {'form': form, 'invoices': existing_invoices}
    return render(request, 'invoice_form.html', context)


def display_invoice(request):
    """
    get all time entries for a project and date range, and generate a invoice.

    Expected query parameters:
      - days: total number of days to be invoiced
      - number: invoice number
      - project: project id
      - start: start date (yyyy-mm-dd)
      - end: end date (yyyy-mm-dd)
    """
    if request.method == 'GET':
        project_id = request.GET.get('project', '1')
        start_str = request.GET.get('start', '2017-01-01')
        end_str = request.GET.get('end', '2017-12-31')
        number = request.GET.get('number', '1')
        total_days = float(request.GET.get('days', '0'))
        description = request.GET.get('description', '')

        invoice_date_format = '%d/%m/%Y'
        out_start = datetime.strptime(start_str, '%Y-%m-%d').strftime(invoice_date_format)
        out_end = datetime.strptime(end_str, '%Y-%m-%d').strftime(invoice_date_format)

        project = Project.objects.get(pk=int(project_id))
        client = Client.objects.get(pk=int(project.client_id))
        user = Profile.objects.get(pk=int(project.user_id))
        total_price = total_days * project.rate

        context = {
            'client': client,
            'user': user,
            'invoice_number': number,
            'invoice_date': date.today().strftime(invoice_date_format),
            'invoice_delivery_date': (date.today().replace(day=1) - timedelta(days=1)).strftime(invoice_date_format),
            'description': '',
            'nr_of_days': '{0:.1f}'.format(total_days),
            'rate': '{0:.2f}'.format(project.rate),
            'total': '{0:.2f}'.format(total_price),
            'vat': '{0:.2f}'.format(total_price * 0.21),
            'total_vat': '{0:.2f}'.format(total_price * 1.21)
        }
        return render(request, 'invoice.html', context)

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