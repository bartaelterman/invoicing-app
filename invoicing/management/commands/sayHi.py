from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'just say hi'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        print('hi')