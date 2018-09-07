import numpy as np
import datetime
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Get a count of all remaning business days this year'

    def handle(self, *args, **options):
        now = datetime.date.today()
        end_of_year = datetime.date(now.year, 12, 31)
        remaining_days = np.busday_count(now, end_of_year)
        print(remaining_days)
