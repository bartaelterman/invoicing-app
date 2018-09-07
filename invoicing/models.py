import pandas as pd
from datetime import date
from django.contrib.auth.models import User
from django.db import models


class Client(models.Model):
    """
    Contact and invoicing details of the client
    """
    address_line_1 = models.CharField(max_length=100)
    address_line_2 = models.CharField(max_length=100)
    name = models.CharField(max_length=200, unique=True)
    VAT_number = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    """
    Additional attributes that belong to the user of the application. This includes
    details of him/her that should also be mentioned on the invoice. It includes a one-to-one
    relationship with the User model, a built-in model from django's authentication.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    invoice_name = models.CharField(max_length=200)
    address_line_1 = models.CharField(max_length=100)
    address_line_2 = models.CharField(max_length=100)
    bank_account = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField()
    VAT_number = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.invoice_name


class Project(models.Model):
    """
    A user can create one or many projects for a given client. Note that:
      - rate: is the rate agreed for this project between the user and the client. While not explicitly
        stated here, other parts of the application will assume that this is for 8 hours, VAT excluded.
      - togglId: the id of the project in toggl.
    """
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    user = models.ForeignKey(Profile)
    name = models.CharField(max_length=200)
    rate = models.DecimalField(max_digits=5, decimal_places=2)  # daily
    togglId = models.CharField(max_length=20, unique=True)
    timesheet_template = models.CharField(max_length=50, null=True, blank=True)
    invoice_template = models.CharField(max_length=50, null=True, blank=True)
    default_invoice_description = models.CharField(max_length=500, null=True, blank=True)
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2)  # daily

    def __str__(self):
        return self.name


class TimeEntryDFManager(models.Manager):
    """
    Helper manager to get time entries returned as a pandas DataFrame
    """
    def get_queryset_df(self, *args, **kwargs):
        df = pd.DataFrame(list(super(TimeEntryDFManager, self).get_queryset().filter(*args, **kwargs).values()))
        return df


class TimeEntry(models.Model):
    """
    An amount of time worked on a project. Can be billable or not (although at the current state, the invoicing
    logic does not take this into account yet)
    """
    billable = models.BooleanField(default=True)  # todo: make sure time entries with billable = False are not included in time sheets and invoices
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    start = models.DateTimeField()
    duration = models.FloatField()
    duration_unit = models.CharField(choices=(('days', 'days'), ('hours', 'hours'), ('minutes', 'minutes')), default='hours', max_length=10)  # todo: current reports can only handle 'hours'
    togglId = models.CharField(max_length=20, unique=True)

    objects = TimeEntryDFManager()

    def __str__(self):
        return '{0} : {1}'.format(self.project, self.start.isoformat())

    def to_dict(self):
        return {
            'start': self.start,
            'duration': self.duration,
            'duration_unit': self.duration_unit
        }


class Invoice(models.Model):
    """
    A model to store invoice data.
    """
    number = models.IntegerField(unique=True, blank=True, null=True, help_text='autofilled, only fill in yourself if you want to override the default')  # will be autofilled, but is editable
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.21)  # daily
    date = models.DateField(editable=False)
    start = models.DateField()
    end = models.DateField()
    delivery_date = models.DateField(blank=True, null=True)
    days = models.DecimalField(max_digits=5, decimal_places=2)
    paid = models.BooleanField(default=False)
    description = models.CharField(max_length=500, null=True, blank=True)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            if not self.number:
                invoice_highest_number = Invoice.objects.all().order_by('-number').first()
                latest_number = invoice_highest_number.number
                self.number = latest_number + 1
            self.date = date.today()
        return super(Invoice, self).save(*args, **kwargs)

    def __str__(self):
        return '{} - {}: {}'.format(self.date, self.number, self.project)


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)