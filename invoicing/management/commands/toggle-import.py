import os
import pandas as pd

from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import IntegrityError
from jinja2 import Template
from utils.TogglPy import Toggl
from invoicing.models import Project, TimeEntry
from dateutil.parser import parse

class Command(BaseCommand):
    help = 'Retrieve time entries for a given project and period'

    def add_arguments(self, parser):
        parser.add_argument('start_date', type=str)
        parser.add_argument('end_date', type=str)


    def entries_to_df(self, entries):
        df = pd.DataFrame(entries)
        return df

    def load_projects(self):
        return Project.objects.all()

    def check_entries(self, entries_df):
        entries_df['start_date'] = entries_df['start'].str[:10]
        entries_df['stop_date'] = entries_df['stop'].str[:10]
        entries_df['duration_h'] = entries_df['duration'] / (60.0 * 60)
        incorrect_date_entries = entries_df[entries_df['start_date'] != entries_df['stop_date']]
        too_long_entries = entries_df[entries_df['duration_h'] > 12]

        if len(incorrect_date_entries) > 0 or len(too_long_entries) > 0:
            print('incorrect date entries')
            print(incorrect_date_entries)
            print('too long entries')
            print(too_long_entries)
            raise RuntimeError('incorrect time entries found')

    def print_timesheet(self, entries_df):
        print('==> TIMESHEET DATA <==\n')
        print(entries_df[['start_date', 'duration_h', 'description']].to_csv(sep='\t'))

    def print_invoice(self, entries, project):
        days_worked = sum(map(lambda x: x['duration'] / (60.0 * 60 * 8), entries))
        print('==> INVOICE DATA <==')
        print('''
        project name: {project}
        client name: {client_name}
        client address:
        {client_addr1}
        {client_addr2}
        client VAT number: {client_VAT}
        daily rate: {rate}

        total days: {days}
        total: {total}
        total (VAT incl): {total_vat}
        '''.format(
            project=project['project'],
            client_name=project['billing']['name'],
            client_addr1=project['billing']['address_line_1'],
            client_addr2=project['billing']['address_line_2'],
            client_VAT=project['billing']['VAT'],
            rate=project['rate'],
            days=days_worked,
            total=(days_worked * project['rate']),
            total_vat=(days_worked * project['rate'] * 1.21)
        ))

    def render_invoice(self, entries, project):
        days_worked = sum(map(lambda x: x['duration'] / (60.0 * 60 * 8), entries))
        template = Template(open('templates/invoice.html').read())
        invoice_html = template.render(
            client=project['billing'],
            invoice_number=1,
            invoice_date='2017-01-02',
            invoice_delivery_date='2017-01-02',
            project_description='test description',
            description='work done',
            nr_of_days=days_worked,
            rate=project['rate'],
            total=(days_worked * project['rate']),
            total_vat=(days_worked * project['rate'] * 1.21)
        )
        print(invoice_html)

    def handle(self, *args, **options):
        start_str = options['start_date']
        start = datetime.strptime(start_str, '%Y-%m-%d')
        end_str = options['end_date']
        end = datetime.strptime(end_str, '%Y-%m-%d')

        # create a Toggl object and set our API key
        toggl = Toggl()
        toggl.setAPIKey(settings.TOGGL_API_KEY)

        entries = toggl.getTimeEntries(start, end)
        projects_hash = {}
        for entry in entries:
            if not 'pid' in entry.keys():
                raise RuntimeError('entry has no project: {}'.format(entry))
            if projects_hash.get(entry['pid']):
                project = projects_hash.get(entry['pid'])
            else:
                try:
                    project = Project.objects.get(togglId=entry['pid'])
                    projects_hash[entry['pid']] = project
                    entry_start = parse(entry['start'])
                    duration = entry['duration'] / 3600.0
                    db_entry = TimeEntry(
                        project=project,
                        start=entry_start,
                        duration=duration,
                        togglId=entry['id']
                    )
                    db_entry.save()
                except Project.DoesNotExist:
                    print('unknown project: {}'.format(entry['pid']))
                    continue
                except IntegrityError as ex:
                    pass