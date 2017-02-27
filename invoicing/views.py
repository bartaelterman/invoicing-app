from django.shortcuts import render_to_response
from datetime import date, datetime
from .models import Client, Project, TimeEntry


def generate_timesheet(request):
    """
    get all time entries for a project and date range, and generate a timesheet.

    Expected query parameters:
      - project: project id
      - start: start date (yyyy-mm-dd)
      - end: end date (yyyy-mm-dd)
    """
    if request.method == 'GET':
        project_id = request.GET.get('project', '1')
        start_str = request.GET.get('start', '2017-01-01')
        end_str = request.GET.get('end', '2017-12-31')

        project = Project.objects.get(pk=int(project_id))
        client = Client.objects.get(pk=int(project.client_id))
        start = datetime.strptime(start_str, '%Y-%m-%d')
        end = datetime.strptime(end_str, '%Y-%m-%d')
        entries = TimeEntry.objects.filter(start__gte=start, start__lte=end, project=project)
        print(entries)

        context = {
            'client': client,
            'project_description': 'proj1',
            'description': 'description',
        }
        return render_to_response('timesheet.html', context)

def generate_invoice(request):
    """
    get all time entries for a project and date range, and generate a invoice.

    Expected query parameters:
      - project: project id
      - start: start date (yyyy-mm-dd)
      - end: end date (yyyy-mm-dd)
    """
    if request.method == 'GET':
        project_id = request.GET.get('project', '1')
        start_str = request.GET.get('start', '2017-01-01')
        end_str = request.GET.get('end', '2017-12-31')

        project = Project.objects.get(pk=int(project_id))
        client = Client.objects.get(pk=int(project.client_id))
        start = datetime.strptime(start_str, '%Y-%m-%d')
        end = datetime.strptime(end_str, '%Y-%m-%d')
        entries = TimeEntry.objects.filter(start__gte=start, start__lte=end, project=project)
        print(entries)

        context = {
            'client': client,
            'invoice_number': 1,
            'invoice_date': date.today().isoformat(),
            'invoice_delivery_date': '2010-01-12',
            'project_description': 'proj1',
            'description': 'description',
            'nr_of_days': '14',
            'rate': '14',
            'total': '4000',
            'total_vat': '1000'
        }
        return render_to_response('invoice.html', context)

def get_time_entries(request):
    if request.method == 'GET':
        project_id = request.GET.get('project', '')
        start_str = request.GET.get('start', '')
        end_str = request.GET.get('end', '')

        project = Project.objects.get(pk=int(project_id))
        start = datetime.strptime(start_str, '%Y-%m-%d')
        end = datetime.strptime(end_str, '%Y-%m-%d')
        entries = TimeEntry.objects.filter(start__gte=start, start__lte=end, project__pk=project.id)
        print(entries)
        return entries.to_json()