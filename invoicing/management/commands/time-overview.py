import numpy as np
import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from invoicing.models import Project, TimeEntry


class Command(BaseCommand):
    help = 'Get an overview of days spent on different projects'

    def entries_to_df(self, entries):
        df = pd.DataFrame(data=entries)
        return df

    def convert_durations_to_hour(self, entries_df):
        if {'hours'} == set(entries_df['duration_unit'].unique()):
            entries_df['duration_hour'] = entries_df['duration']
        else:
            issues = entries_df[entries_df['duration_unit'] != 'hours']
            raise RuntimeError(f'Not all entries have duration_unit = hours. Others found: {set(issues["duration_unit"].unique())}')


    def entries_total_time_by_year(self, entries_df, unit='day'):
        entries_df['year'] = entries_df['start'].dt.year
        grouped = entries_df[['year', 'duration_hour']].groupby('year')
        if unit == 'day':
            return grouped.aggregate(lambda x: np.sum(x) / 8.0).rename(columns={'duration_hour': 'total_days'})
        else:
            raise RuntimeError(f'Not supported: unit {unit}')

    def load_projects(self):
        return Project.objects.all()

    def handle(self, *args, **options):
        projects = Project.objects.all()

        for project in projects:
            time_entries_df = self.entries_to_df([x.to_dict() for x in project.timeentry_set.all()])
            print(f"\n{project.name}\n===============""")
            if len(time_entries_df) > 0:
                self.convert_durations_to_hour(time_entries_df)
                time_by_year = self.entries_total_time_by_year(time_entries_df)
                print(time_by_year.to_csv(sep='\t'))
            else:
                print('-')
